'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Brain, FileText, MessageSquare, Share2, Shield, TrendingUp,
  Zap, Search, GitBranch, Bot, ChevronRight, ArrowRight,
  Database, Cpu, Layers, BarChart3, Users, Award,
} from 'lucide-react';

function AnimatedCounter({ end, duration = 2000, suffix = '' }: { end: number; duration?: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const increment = end / (duration / 16);
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) { setCount(end); clearInterval(timer); }
      else setCount(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [end, duration]);
  return <span>{count}{suffix}</span>;
}

function FadeInSection({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);
  return (
    <div className={`transition-all duration-700 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
      {children}
    </div>
  );
}

const features = [
  { icon: Brain, title: 'Multi-Agent AI System', description: 'LangGraph-powered supervisor orchestrates Expert, RCA, Compliance, and Lessons agents for specialized intelligence.', color: 'blue' },
  { icon: Search, title: 'Hybrid Search (40/40/20)', description: '40% Vector (Qdrant) + 40% Graph (Neo4j) + 20% BM25 keyword search with score fusion.', color: 'purple' },
  { icon: Share2, title: 'Knowledge Graph', description: 'Interactive force-directed graph visualizing Equipment, Failures, Incidents, Regulations, and Personnel relationships.', color: 'green' },
  { icon: FileText, title: 'Document Intelligence', description: 'Full OCR pipeline: Upload → Extract → Chunk → Embed → Index → Graph Build. Supports PDF, DOCX, XLSX, images.', color: 'orange' },
  { icon: Shield, title: 'Compliance Intelligence', description: 'Automated compliance checking against OISD, ISO 9001, Factory Act, and PESO regulations.', color: 'red' },
  { icon: GitBranch, title: 'Root Cause Analysis', description: '5-Why methodology with failure pattern detection, incident correlation, and corrective recommendations.', color: 'cyan' },
];

const agents = [
  { name: 'Supervisor Agent', role: 'Intent Detection & Task Routing', icon: Cpu, desc: 'Classifies user intent and routes to specialist agents via LangGraph conditional edges.' },
  { name: 'Expert Copilot', role: 'Equipment & SOP Intelligence', icon: Bot, desc: 'Retrieves maintenance procedures, manufacturer guidelines, and troubleshooting steps.' },
  { name: 'RCA Agent', role: 'Failure Analysis', icon: Search, desc: 'Applies 5-why methodology to trace failure chains and identify root causes.' },
  { name: 'Compliance Agent', role: 'Regulatory Audit', icon: Shield, desc: 'Checks against OISD, ISO, Factory Act, PESO standards and identifies gaps.' },
  { name: 'Lessons Agent', role: 'Pattern Intelligence', icon: TrendingUp, desc: 'Mines historical incidents, near-misses, and recurring failures for prevention.' },
];

const techStack = [
  { name: 'Next.js 16', category: 'Frontend' },
  { name: 'FastAPI', category: 'Backend' },
  { name: 'LangGraph', category: 'AI Orchestration' },
  { name: 'Groq LLM', category: 'Language Model' },
  { name: 'Qdrant', category: 'Vector Database' },
  { name: 'Neo4j', category: 'Graph Database' },
  { name: 'FastEmbed', category: 'Embeddings' },
  { name: 'TailwindCSS', category: 'Styling' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-white overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
          {/* Grid pattern */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.03)_1px,transparent_1px)] bg-[size:60px_60px]" />
        </div>

        <div className="relative text-center max-w-5xl mx-auto">
          <FadeInSection delay={100}>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/20 rounded-full mb-8">
              <Zap size={14} className="text-blue-400" />
              <span className="text-sm text-blue-300">ET AI Hackathon 2026</span>
            </div>
          </FadeInSection>

          <FadeInSection delay={300}>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
                IntelliPlant AI
              </span>
            </h1>
          </FadeInSection>

          <FadeInSection delay={500}>
            <p className="text-xl md:text-2xl text-slate-300 mb-4 font-light">
              AI-Powered Industrial Knowledge Intelligence Platform
            </p>
            <p className="text-lg text-slate-500 max-w-2xl mx-auto mb-10">
              Transform fragmented industrial documents into a unified operational brain.
              Reduce information retrieval from 60 minutes to 20 seconds.
            </p>
          </FadeInSection>

          <FadeInSection delay={700}>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/" className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-xl text-lg font-medium transition-all hover:scale-105 shadow-lg shadow-blue-500/20">
                Launch Platform <ArrowRight size={20} />
              </Link>
              <Link href="/landing#features" className="inline-flex items-center gap-2 px-8 py-4 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-xl text-lg font-medium transition-all">
                Explore Features <ChevronRight size={20} />
              </Link>
            </div>
          </FadeInSection>

          <FadeInSection delay={900}>
            <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="text-center">
                <p className="text-3xl font-bold text-white"><AnimatedCounter end={589} /></p>
                <p className="text-sm text-slate-500 mt-1">Documents Indexed</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-white"><AnimatedCounter end={5} /></p>
                <p className="text-sm text-slate-500 mt-1">AI Agents</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-white"><AnimatedCounter end={20} suffix="s" /></p>
                <p className="text-sm text-slate-500 mt-1">Avg Response</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-white"><AnimatedCounter end={95} suffix="%" /></p>
                <p className="text-sm text-slate-500 mt-1">AI Confidence</p>
              </div>
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <FadeInSection delay={100}>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Powerful Features</h2>
              <p className="text-slate-400 max-w-xl mx-auto">Built with cutting-edge AI to solve real industrial challenges</p>
            </div>
          </FadeInSection>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              const colorMap: Record<string, string> = {
                blue: 'from-blue-500/20 to-blue-500/5 border-blue-500/20 text-blue-400',
                purple: 'from-purple-500/20 to-purple-500/5 border-purple-500/20 text-purple-400',
                green: 'from-green-500/20 to-green-500/5 border-green-500/20 text-green-400',
                orange: 'from-orange-500/20 to-orange-500/5 border-orange-500/20 text-orange-400',
                red: 'from-red-500/20 to-red-500/5 border-red-500/20 text-red-400',
                cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/20 text-cyan-400',
              };
              const colors = colorMap[feature.color] || colorMap.blue;
              return (
                <FadeInSection key={feature.title} delay={200 + i * 100}>
                  <div className={`p-6 rounded-2xl border bg-gradient-to-br ${colors} hover:scale-[1.02] transition-transform duration-300`}>
                    <Icon size={28} className="mb-4" />
                    <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                    <p className="text-sm text-slate-400 leading-relaxed">{feature.description}</p>
                  </div>
                </FadeInSection>
              );
            })}
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section className="py-24 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <FadeInSection delay={100}>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">LangGraph Workflow</h2>
              <p className="text-slate-400 max-w-xl mx-auto">Stateful multi-agent orchestration with 7 specialized nodes</p>
            </div>
          </FadeInSection>
          <FadeInSection delay={300}>
            <div className="relative bg-slate-900 border border-slate-800 rounded-2xl p-8 overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 via-transparent to-purple-500/5" />
              <div className="relative flex flex-wrap justify-center gap-4">
                {['Input + Query Rewriter', 'Supervisor', 'Hybrid Retrieval', 'Agent Execution', 'Context Fusion', 'LLM Reasoning', 'Citation Generation'].map((node, i) => (
                  <div key={node} className="flex items-center gap-2">
                    <div className="px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-sm font-medium text-slate-200 hover:border-blue-500/50 transition-colors">
                      <span className="text-blue-400 mr-2 text-xs font-bold">{i + 1}</span>
                      {node}
                    </div>
                    {i < 6 && <ArrowRight size={16} className="text-slate-600 hidden md:block" />}
                  </div>
                ))}
              </div>
              <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-blue-500/10 rounded-xl border border-blue-500/20">
                  <Database size={20} className="text-blue-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-blue-300">Vector Search</p>
                  <p className="text-xs text-slate-500">Qdrant · 40% weight</p>
                </div>
                <div className="p-4 bg-green-500/10 rounded-xl border border-green-500/20">
                  <Share2 size={20} className="text-green-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-green-300">Graph Search</p>
                  <p className="text-xs text-slate-500">Neo4j · 40% weight</p>
                </div>
                <div className="p-4 bg-orange-500/10 rounded-xl border border-orange-500/20">
                  <Search size={20} className="text-orange-400 mx-auto mb-2" />
                  <p className="text-sm font-medium text-orange-300">BM25 Search</p>
                  <p className="text-xs text-slate-500">Keyword · 20% weight</p>
                </div>
              </div>
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* Agents Section */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <FadeInSection delay={100}>
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">AI Agent System</h2>
              <p className="text-slate-400 max-w-xl mx-auto">Specialized agents collaborate under a Supervisor for intelligent task decomposition</p>
            </div>
          </FadeInSection>
          <div className="space-y-4">
            {agents.map((agent, i) => {
              const Icon = agent.icon;
              return (
                <FadeInSection key={agent.name} delay={200 + i * 100}>
                  <div className="flex items-start gap-5 p-5 bg-slate-900 border border-slate-800 rounded-xl hover:border-slate-700 transition-colors group">
                    <div className="p-3 bg-blue-500/10 rounded-xl group-hover:bg-blue-500/20 transition-colors shrink-0">
                      <Icon size={22} className="text-blue-400" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <h3 className="text-white font-semibold">{agent.name}</h3>
                        <span className="px-2 py-0.5 bg-slate-800 rounded-full text-[10px] text-slate-400 font-medium">{agent.role}</span>
                      </div>
                      <p className="text-sm text-slate-400">{agent.desc}</p>
                    </div>
                  </div>
                </FadeInSection>
              );
            })}
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-24 px-6 bg-slate-900/50">
        <div className="max-w-6xl mx-auto">
          <FadeInSection delay={100}>
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Technology Stack</h2>
              <p className="text-slate-400">Modern, scalable architecture built for production</p>
            </div>
          </FadeInSection>
          <FadeInSection delay={300}>
            <div className="flex flex-wrap justify-center gap-3">
              {techStack.map((tech) => (
                <div key={tech.name} className="px-5 py-3 bg-slate-800 border border-slate-700 rounded-xl hover:border-blue-500/40 transition-colors group">
                  <p className="text-sm font-medium text-white group-hover:text-blue-300 transition-colors">{tech.name}</p>
                  <p className="text-[10px] text-slate-500">{tech.category}</p>
                </div>
              ))}
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* About / Creator Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <FadeInSection delay={100}>
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold mb-4">Built By</h2>
            </div>
          </FadeInSection>
          <FadeInSection delay={300}>
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 md:p-12">
              <div className="flex flex-col md:flex-row items-center gap-8">
                {/* Photo */}
                <div className="shrink-0">
                  <div className="w-40 h-40 rounded-2xl overflow-hidden border-4 border-blue-500/30 shadow-xl shadow-blue-500/10">
                    <img src="/images/narayan.jpg" alt="Narayan Parab" className="w-full h-full object-cover" />
                  </div>
                </div>
                {/* Info */}
                <div className="text-center md:text-left">
                  <h3 className="text-2xl font-bold text-white mb-1">Narayan Parab</h3>
                  <p className="text-blue-400 font-medium mb-4">Data Analyst | Full Stack Developer | AI Engineer</p>
                  <p className="text-slate-400 text-sm leading-relaxed mb-6">
                    B.E. in Information Technology from Atharva College of Engineering, Mumbai.
                    Passionate about transforming complex data into actionable insights and building
                    intelligent systems that solve real-world problems. Strong foundation in data analytics,
                    full-stack development, and AI/ML with a keen analytical mindset.
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                    <span className="px-3 py-1 bg-blue-500/10 border border-blue-500/20 rounded-full text-xs text-blue-300">Python</span>
                    <span className="px-3 py-1 bg-purple-500/10 border border-purple-500/20 rounded-full text-xs text-purple-300">React / Next.js</span>
                    <span className="px-3 py-1 bg-green-500/10 border border-green-500/20 rounded-full text-xs text-green-300">FastAPI</span>
                    <span className="px-3 py-1 bg-orange-500/10 border border-orange-500/20 rounded-full text-xs text-orange-300">LangGraph</span>
                    <span className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full text-xs text-cyan-300">Power BI</span>
                    <span className="px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-full text-xs text-red-300">SQL</span>
                  </div>
                  <div className="mt-6 flex flex-wrap gap-4 justify-center md:justify-start text-xs text-slate-500">
                    <span className="flex items-center gap-1"><Users size={12} /> Mumbai, India</span>
                    <span className="flex items-center gap-1"><Award size={12} /> ET AI Hackathon 2026</span>
                    <span>narayanp1501@gmail.com</span>
                  </div>
                </div>
              </div>
            </div>
          </FadeInSection>
        </div>
      </section>

      {/* Footer CTA */}
      <section className="py-16 px-6 border-t border-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            Transform Documents into Industrial Intelligence
          </h2>
          <p className="text-slate-500 mb-8">Ready to experience the future of industrial knowledge management?</p>
          <Link href="/" className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-xl text-lg font-medium transition-all hover:scale-105 shadow-lg shadow-blue-500/20">
            Enter Platform <ArrowRight size={20} />
          </Link>
          <p className="text-xs text-slate-600 mt-8">© 2026 IntelliPlant AI — Narayan Parab | ET AI Hackathon</p>
        </div>
      </section>
    </div>
  );
}
