'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { getGraphData } from '@/app/services/api';
import type { GraphData, GraphNode, GraphEdge } from '@/app/types';
import { Search, Loader2, ZoomIn, ZoomOut, Maximize2, Filter, Info, X, RotateCcw } from 'lucide-react';

const NODE_COLORS: Record<string, { fill: string; stroke: string; bg: string; text: string }> = {
  equipment: { fill: '#3b82f6', stroke: '#60a5fa', bg: 'bg-blue-500/20', text: 'text-blue-400' },
  failure: { fill: '#ef4444', stroke: '#f87171', bg: 'bg-red-500/20', text: 'text-red-400' },
  incident: { fill: '#f97316', stroke: '#fb923c', bg: 'bg-orange-500/20', text: 'text-orange-400' },
  regulation: { fill: '#22c55e', stroke: '#4ade80', bg: 'bg-green-500/20', text: 'text-green-400' },
  person: { fill: '#a855f7', stroke: '#c084fc', bg: 'bg-purple-500/20', text: 'text-purple-400' },
  personnel: { fill: '#a855f7', stroke: '#c084fc', bg: 'bg-purple-500/20', text: 'text-purple-400' },
  document: { fill: '#eab308', stroke: '#facc15', bg: 'bg-yellow-500/20', text: 'text-yellow-400' },
};

const EDGE_COLORS: Record<string, string> = {
  FAILED_IN: '#ef4444',
  CAUSES: '#f97316',
  CONNECTED_TO: '#3b82f6',
  INSPECTED_BY: '#a855f7',
  REQUIRES: '#22c55e',
  SIMILAR_TO: '#eab308',
  LOCATED_IN: '#06b6d4',
  DESCRIBED_BY: '#64748b',
  REFERENCES: '#64748b',
};

interface SimNode extends GraphNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
  fx?: number | null;
  fy?: number | null;
  radius: number;
}

interface TooltipInfo {
  node: SimNode;
  x: number;
  y: number;
}

const SUGGESTIONS = [
  'PUMP-001', 'pump', 'motor', 'valve', 'compressor',
  'turbine', 'boiler', 'pipeline', 'bearing', 'filter',
];

function useForceSimulation(nodes: GraphNode[], edges: GraphEdge[], width: number, height: number) {
  const [simNodes, setSimNodes] = useState<SimNode[]>([]);
  const [simEdges, setSimEdges] = useState<GraphEdge[]>([]);
  const animRef = useRef<number>(0);
  const nodesRef = useRef<SimNode[]>([]);

  useEffect(() => {
    if (nodes.length === 0) { setSimNodes([]); setSimEdges([]); return; }

    const cx = width / 2;
    const cy = height / 2;
    const initialNodes: SimNode[] = nodes.map((n, i) => {
      const angle = (2 * Math.PI * i) / nodes.length;
      const r = Math.min(width, height) * 0.3;
      const connections = edges.filter(e => e.source === n.id || e.target === n.id).length;
      return {
        ...n,
        x: cx + r * Math.cos(angle) + (Math.random() - 0.5) * 40,
        y: cy + r * Math.sin(angle) + (Math.random() - 0.5) * 40,
        vx: 0, vy: 0,
        radius: Math.max(20, Math.min(35, 18 + connections * 3)),
      };
    });
    nodesRef.current = initialNodes;
    setSimEdges(edges);

    let iteration = 0;
    const maxIterations = 300;
    const alpha = 0.3;
    const repulsion = 3000;
    const attraction = 0.005;
    const damping = 0.85;
    const centerGravity = 0.01;

    function tick() {
      const ns = nodesRef.current;
      for (let i = 0; i < ns.length; i++) {
        if (ns[i].fx != null) { ns[i].x = ns[i].fx!; ns[i].y = ns[i].fy!; ns[i].vx = 0; ns[i].vy = 0; continue; }
        let fx = 0, fy = 0;
        // Repulsion
        for (let j = 0; j < ns.length; j++) {
          if (i === j) continue;
          const dx = ns[i].x - ns[j].x;
          const dy = ns[i].y - ns[j].y;
          const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1);
          const force = repulsion / (dist * dist);
          fx += (dx / dist) * force;
          fy += (dy / dist) * force;
        }
        // Attraction (edges)
        for (const e of edges) {
          let other = -1;
          if (e.source === ns[i].id) other = ns.findIndex(n => n.id === e.target);
          else if (e.target === ns[i].id) other = ns.findIndex(n => n.id === e.source);
          if (other >= 0 && other < ns.length) {
            const dx = ns[other].x - ns[i].x;
            const dy = ns[other].y - ns[i].y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            fx += dx * attraction * dist;
            fy += dy * attraction * dist;
          }
        }

        // Center gravity
        fx += (cx - ns[i].x) * centerGravity;
        fy += (cy - ns[i].y) * centerGravity;

        ns[i].vx = (ns[i].vx + fx * alpha) * damping;
        ns[i].vy = (ns[i].vy + fy * alpha) * damping;
        ns[i].x += ns[i].vx;
        ns[i].y += ns[i].vy;
        // Bounds
        ns[i].x = Math.max(40, Math.min(width - 40, ns[i].x));
        ns[i].y = Math.max(40, Math.min(height - 40, ns[i].y));
      }
      iteration++;
      setSimNodes([...ns]);
      if (iteration < maxIterations) {
        animRef.current = requestAnimationFrame(tick);
      }
    }
    animRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animRef.current);
  }, [nodes, edges, width, height]);

  const updateNodePosition = useCallback((id: string, x: number, y: number, fix: boolean) => {
    const ns = nodesRef.current;
    const node = ns.find(n => n.id === id);
    if (node) {
      node.x = x; node.y = y;
      if (fix) { node.fx = x; node.fy = y; }
      else { node.fx = null; node.fy = null; }
      setSimNodes([...ns]);
    }
  }, []);

  return { simNodes, simEdges, updateNodePosition };
}

function GraphCanvas({
  data, onNodeSelect,
}: { data: GraphData; onNodeSelect: (node: GraphNode | null) => void }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [dragging, setDragging] = useState<string | null>(null);
  const [panning, setPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [filters, setFilters] = useState<Set<string>>(new Set());

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const obs = new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width: Math.max(600, width), height: Math.max(400, height) });
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  const filteredNodes = filters.size > 0
    ? data.nodes.filter(n => filters.has(n.type.toLowerCase()))
    : data.nodes;
  const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = data.edges.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));

  const { simNodes, simEdges, updateNodePosition } = useForceSimulation(
    filteredNodes, filteredEdges, dimensions.width, dimensions.height
  );

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(z => Math.max(0.3, Math.min(3, z * delta)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0 && !dragging) {
      setPanning(true);
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (panning && !dragging) {
      setPan({ x: e.clientX - panStart.x, y: e.clientY - panStart.y });
    }
    if (dragging) {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        const x = (e.clientX - rect.left - pan.x) / zoom;
        const y = (e.clientY - rect.top - pan.y) / zoom;
        updateNodePosition(dragging, x, y, true);
      }
    }
  };

  const handleMouseUp = () => {
    if (dragging) {
      updateNodePosition(dragging, 0, 0, false);
      const node = simNodes.find(n => n.id === dragging);
      if (node) updateNodePosition(dragging, node.x, node.y, false);
    }
    setPanning(false);
    setDragging(null);
  };

  const handleNodeMouseDown = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    setDragging(nodeId);
  };

  const handleNodeClick = (node: SimNode) => {
    setSelectedNode(node.id === selectedNode ? null : node.id);
    onNodeSelect(node.id === selectedNode ? null : node);
  };

  const toggleFilter = (type: string) => {
    setFilters(prev => {
      const next = new Set(prev);
      if (next.has(type)) next.delete(type);
      else next.add(type);
      return next;
    });
  };

  const resetView = () => { setZoom(1); setPan({ x: 0, y: 0 }); };

  const nodeTypes = [...new Set(data.nodes.map(n => n.type.toLowerCase()))];

  const getEdgePath = (source: SimNode, target: SimNode) => {
    const dx = target.x - source.x;
    const dy = target.y - source.y;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (dist === 0) return '';
    const sr = source.radius + 2;
    const tr = target.radius + 8;
    const sx = source.x + (dx / dist) * sr;
    const sy = source.y + (dy / dist) * sr;
    const tx = target.x - (dx / dist) * tr;
    const ty = target.y - (dy / dist) * tr;
    // Slight curve
    const mx = (sx + tx) / 2 + (dy / dist) * 15;
    const my = (sy + ty) / 2 - (dx / dist) * 15;
    return `M ${sx} ${sy} Q ${mx} ${my} ${tx} ${ty}`;
  };

  return (
    <div className="relative rounded-xl border border-slate-800 overflow-hidden bg-slate-950" ref={containerRef} style={{ height: '500px' }}>
      {/* Toolbar */}
      <div className="absolute top-3 right-3 z-10 flex gap-2">
        <button onClick={() => setZoom(z => Math.min(3, z * 1.2))} className="p-2 bg-slate-800/90 rounded-lg hover:bg-slate-700 text-slate-300"><ZoomIn size={16} /></button>
        <button onClick={() => setZoom(z => Math.max(0.3, z * 0.8))} className="p-2 bg-slate-800/90 rounded-lg hover:bg-slate-700 text-slate-300"><ZoomOut size={16} /></button>
        <button onClick={resetView} className="p-2 bg-slate-800/90 rounded-lg hover:bg-slate-700 text-slate-300"><Maximize2 size={16} /></button>
      </div>

      {/* Filter chips */}
      <div className="absolute top-3 left-3 z-10 flex flex-wrap gap-1.5">
        {nodeTypes.map(type => {
          const colors = NODE_COLORS[type] || NODE_COLORS.equipment;
          const active = filters.size === 0 || filters.has(type);
          return (
            <button key={type} onClick={() => toggleFilter(type)}
              className={`px-2.5 py-1 rounded-full text-[11px] font-medium border transition-all ${active ? `${colors.bg} ${colors.text} border-current` : 'bg-slate-800/50 text-slate-600 border-slate-700'}`}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          );
        })}
        {filters.size > 0 && (
          <button onClick={() => setFilters(new Set())} className="px-2 py-1 rounded-full text-[11px] text-slate-500 hover:text-slate-300 border border-slate-700">
            <RotateCcw size={10} className="inline mr-1" />Clear
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="absolute bottom-3 left-3 z-10 px-3 py-1.5 bg-slate-800/90 rounded-lg text-[11px] text-slate-400">
        {simNodes.length} nodes · {simEdges.length} edges · {zoom.toFixed(1)}x
      </div>

      {/* SVG Canvas */}
      <svg
        width="100%" height="100%"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="cursor-grab active:cursor-grabbing"
      >
        <defs>
          {Object.entries(EDGE_COLORS).map(([type, color]) => (
            <marker key={type} id={`arrow-${type}`} markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill={color} opacity={0.8} />
            </marker>
          ))}
          <marker id="arrow-default" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto">
            <polygon points="0 0, 8 3, 0 6" fill="#475569" opacity={0.8} />
          </marker>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>

        <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
          {/* Edges */}
          {simEdges.map((edge, i) => {
            const source = simNodes.find(n => n.id === edge.source);
            const target = simNodes.find(n => n.id === edge.target);
            if (!source || !target) return null;
            const edgeColor = EDGE_COLORS[edge.type] || '#475569';
            const isHighlighted = selectedNode === edge.source || selectedNode === edge.target;
            const path = getEdgePath(source, target);
            return (
              <g key={`edge-${i}`} opacity={selectedNode && !isHighlighted ? 0.15 : 1}>
                <path d={path} stroke={edgeColor} strokeWidth={isHighlighted ? 2.5 : 1.5}
                  fill="none" markerEnd={`url(#arrow-${edge.type in EDGE_COLORS ? edge.type : 'default'})`}
                  strokeDasharray={edge.type === 'SIMILAR_TO' ? '4 3' : undefined} />
                <text dy={-6} fill={edgeColor} fontSize={8} fontWeight={500} opacity={isHighlighted ? 1 : 0.7}>
                  <textPath href={`#epath-${i}`} startOffset="50%" textAnchor="middle">{edge.type.replace(/_/g, ' ')}</textPath>
                </text>
                <path id={`epath-${i}`} d={path} fill="none" stroke="none" />
              </g>
            );
          })}

          {/* Nodes */}
          {simNodes.map(node => {
            const type = node.type.toLowerCase();
            const colors = NODE_COLORS[type] || NODE_COLORS.equipment;
            const isSelected = selectedNode === node.id;
            const isConnected = selectedNode && simEdges.some(e =>
              (e.source === selectedNode && e.target === node.id) ||
              (e.target === selectedNode && e.source === node.id)
            );
            const dimmed = selectedNode && !isSelected && !isConnected;
            return (
              <g key={node.id} opacity={dimmed ? 0.2 : 1}
                onMouseDown={(e) => handleNodeMouseDown(e, node.id)}
                onClick={() => handleNodeClick(node)}
                onMouseEnter={(e) => setTooltip({ node, x: e.clientX, y: e.clientY })}
                onMouseLeave={() => setTooltip(null)}
                className="cursor-pointer">
                {isSelected && <circle cx={node.x} cy={node.y} r={node.radius + 6} fill="none" stroke={colors.stroke} strokeWidth={2} opacity={0.5} filter="url(#glow)" />}
                <circle cx={node.x} cy={node.y} r={node.radius} fill={colors.fill}
                  stroke={isSelected ? '#fff' : colors.stroke} strokeWidth={isSelected ? 2.5 : 1.5} opacity={0.9} />
                <text x={node.x} y={node.y + 1} textAnchor="middle" dominantBaseline="middle"
                  fill="white" fontSize={node.radius > 25 ? 9 : 8} fontWeight={600}>
                  {node.label.length > 10 ? node.label.slice(0, 10) + '…' : node.label}
                </text>
                <text x={node.x} y={node.y + node.radius + 12} textAnchor="middle"
                  fill="#94a3b8" fontSize={7}>{type}</text>
              </g>
            );
          })}
        </g>
      </svg>

      {/* Tooltip */}
      {tooltip && (
        <div className="absolute z-20 pointer-events-none px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg shadow-xl text-xs max-w-[200px]"
          style={{ left: tooltip.x - (containerRef.current?.getBoundingClientRect().left || 0) + 12, top: tooltip.y - (containerRef.current?.getBoundingClientRect().top || 0) - 10 }}>
          <p className="font-semibold text-white">{tooltip.node.label}</p>
          <p className="text-slate-400 mt-0.5">Type: {tooltip.node.type}</p>
          <p className="text-slate-500 mt-0.5">Connections: {simEdges.filter(e => e.source === tooltip.node.id || e.target === tooltip.node.id).length}</p>
        </div>
      )}
    </div>
  );
}

function NodeDetailPanel({ node, edges, nodes, onClose }: {
  node: GraphNode; edges: GraphEdge[]; nodes: GraphNode[]; onClose: () => void;
}) {
  const type = node.type.toLowerCase();
  const colors = NODE_COLORS[type] || NODE_COLORS.equipment;
  const connectedEdges = edges.filter(e => e.source === node.id || e.target === node.id);
  const neighbors = connectedEdges.map(e => {
    const neighborId = e.source === node.id ? e.target : e.source;
    const neighbor = nodes.find(n => n.id === neighborId);
    return { edge: e, neighbor };
  }).filter(x => x.neighbor);

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-4 h-4 rounded-full`} style={{ backgroundColor: colors.fill }} />
          <div>
            <h3 className="text-white font-semibold">{node.label}</h3>
            <p className="text-xs text-slate-500">{node.type} · {connectedEdges.length} connections</p>
          </div>
        </div>
        <button onClick={onClose} className="p-1 hover:bg-slate-800 rounded"><X size={16} className="text-slate-400" /></button>
      </div>
      <div className="space-y-2 max-h-48 overflow-y-auto">
        {neighbors.map(({ edge, neighbor }, i) => {
          const nType = neighbor!.type.toLowerCase();
          const nColors = NODE_COLORS[nType] || NODE_COLORS.equipment;
          const direction = edge.source === node.id ? '→' : '←';
          return (
            <div key={i} className="flex items-center gap-2 py-1.5 px-2 rounded bg-slate-800/50 text-xs">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: nColors.fill }} />
              <span className="text-slate-300 truncate">{neighbor!.label}</span>
              <span className="text-slate-600 ml-auto shrink-0">{direction} {edge.type.replace(/_/g, ' ')}</span>
            </div>
          );
        })}
        {neighbors.length === 0 && <p className="text-xs text-slate-500">No connections found</p>}
      </div>
    </div>
  );
}

function GraphStatsPanel({ data }: { data: GraphData }) {
  const typeCounts: Record<string, number> = {};
  data.nodes.forEach(n => {
    const t = n.type.toLowerCase();
    typeCounts[t] = (typeCounts[t] || 0) + 1;
  });
  const edgeTypeCounts: Record<string, number> = {};
  data.edges.forEach(e => { edgeTypeCounts[e.type] = (edgeTypeCounts[e.type] || 0) + 1; });

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 p-5">
      <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
        <Info size={14} />Graph Statistics
      </h3>
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="text-center p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xl font-bold text-white">{data.nodes.length}</p>
          <p className="text-[11px] text-slate-500">Nodes</p>
        </div>
        <div className="text-center p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xl font-bold text-white">{data.edges.length}</p>
          <p className="text-[11px] text-slate-500">Edges</p>
        </div>
      </div>
      <div className="space-y-1.5">
        <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-1">Node Types</p>
        {Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).map(([type, count]) => {
          const colors = NODE_COLORS[type] || NODE_COLORS.equipment;
          return (
            <div key={type} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: colors.fill }} />
                <span className="text-slate-300 capitalize">{type}</span>
              </div>
              <span className="text-slate-500">{count}</span>
            </div>
          );
        })}
      </div>
      {Object.keys(edgeTypeCounts).length > 0 && (
        <div className="space-y-1.5 mt-4">
          <p className="text-[11px] text-slate-500 uppercase tracking-wider mb-1">Relationship Types</p>
          {Object.entries(edgeTypeCounts).sort((a, b) => b[1] - a[1]).map(([type, count]) => (
            <div key={type} className="flex items-center justify-between text-xs">
              <span className="text-slate-300">{type.replace(/_/g, ' ')}</span>
              <span className="text-slate-500">{count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function GraphPage() {
  const [equipmentId, setEquipmentId] = useState('');
  const [data, setData] = useState<GraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleSearch = async (id?: string) => {
    const searchId = id || equipmentId.trim();
    if (!searchId) return;
    setEquipmentId(searchId);
    setLoading(true);
    setError(null);
    setData(null);
    setSelectedNode(null);
    setShowSuggestions(false);
    try {
      const result = await getGraphData(searchId);
      if (result.nodes.length === 0) {
        setError(`No graph data found for "${searchId}". Try: pump, motor, valve, compressor`);
      } else {
        setData(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch graph data');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') { handleSearch(); setShowSuggestions(false); }
    if (e.key === 'Escape') setShowSuggestions(false);
  };

  const filteredSuggestions = SUGGESTIONS.filter(s =>
    s.toLowerCase().includes(equipmentId.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Knowledge Graph</h1>
        <p className="text-slate-400 mt-1">Explore relationships between equipment, failures, incidents, and regulations</p>
      </div>

      {/* Search */}
      <div className="flex gap-3 relative">
        <div className="relative flex-1 max-w-lg">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={equipmentId}
            onChange={(e) => { setEquipmentId(e.target.value); setShowSuggestions(true); }}
            onFocus={() => setShowSuggestions(true)}
            onKeyDown={handleKeyDown}
            placeholder="Enter equipment ID or keyword (e.g., PUMP-001, motor, valve)"
            className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500/20 transition-all"
          />
          {showSuggestions && equipmentId && filteredSuggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-30 overflow-hidden">
              {filteredSuggestions.map(s => (
                <button key={s} onClick={() => handleSearch(s)}
                  className="w-full px-4 py-2 text-left text-sm text-slate-300 hover:bg-slate-700 transition-colors">
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
        <button onClick={() => handleSearch()} disabled={loading || !equipmentId.trim()}
          className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
          Explore
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20 gap-3">
          <Loader2 size={32} className="text-blue-400 animate-spin" />
          <p className="text-sm text-slate-400">Building knowledge graph...</p>
        </div>
      )}

      {/* Graph View */}
      {data && !loading && (
        <div className="space-y-6">
          <GraphCanvas data={data} onNodeSelect={setSelectedNode} />

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              {selectedNode ? (
                <NodeDetailPanel node={selectedNode} edges={data.edges} nodes={data.nodes} onClose={() => setSelectedNode(null)} />
              ) : (
                <div className="bg-slate-900 rounded-xl border border-slate-800 p-5">
                  <p className="text-sm text-slate-500 text-center py-4">Click a node to view its connections and details</p>
                </div>
              )}
            </div>
            <GraphStatsPanel data={data} />
          </div>
        </div>
      )}

      {/* Empty state */}
      {!data && !loading && !error && (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-20 h-20 rounded-full bg-slate-800/50 flex items-center justify-center mb-5">
            <Search size={32} className="text-slate-600" />
          </div>
          <p className="text-slate-300 font-medium text-lg">Explore your Knowledge Graph</p>
          <p className="text-sm text-slate-500 mt-2 max-w-md">
            Enter an equipment ID or keyword to visualize relationships between equipment, failures, incidents, and regulatory standards.
          </p>
          <div className="flex flex-wrap gap-2 mt-5 justify-center">
            {SUGGESTIONS.slice(0, 6).map(s => (
              <button key={s} onClick={() => handleSearch(s)}
                className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-full text-xs text-slate-400 hover:text-white hover:border-blue-500/50 transition-all">
                {s}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
