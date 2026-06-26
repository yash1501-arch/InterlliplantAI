'use client';

import { useEffect, useState, useRef } from 'react';
import { uploadDocument, listDocuments, getDocument, deleteDocument } from '@/app/services/api';
import type { DocumentMeta, DocumentDetail } from '@/app/types';
import { FileText, Upload, Search, Trash2, X, Eye, FileDown, Loader2 } from 'lucide-react';

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    completed: 'bg-green-500/20 text-green-400',
    processing: 'bg-yellow-500/20 text-yellow-400',
    failed: 'bg-red-500/20 text-red-400',
    uploaded: 'bg-blue-500/20 text-blue-400',
  };
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colors[status] || 'bg-slate-500/20 text-slate-400'}`}>
      {status}
    </span>
  );
}

function DocumentSkeleton() {
  return (
    <div className="bg-slate-900 rounded-xl p-5 border border-slate-800 animate-pulse">
      <div className="flex items-start gap-4">
        <div className="w-10 h-10 bg-slate-800 rounded-lg shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="h-5 w-3/4 bg-slate-800 rounded mb-2" />
          <div className="h-3 w-1/2 bg-slate-800 rounded mb-1" />
          <div className="h-3 w-1/4 bg-slate-800 rounded" />
        </div>
      </div>
    </div>
  );
}

function DeleteConfirm({ onConfirm, onCancel }: { onConfirm: () => void; onCancel: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onCancel}>
      <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 max-w-sm mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-lg font-semibold text-white mb-2">Delete Document</h3>
        <p className="text-sm text-slate-400 mb-6">Are you sure you want to delete this document? This action cannot be undone.</p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg text-sm font-medium hover:bg-red-500/30 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}

function DocumentModal({ doc, onClose }: { doc: DocumentDetail; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4" onClick={onClose}>
      <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-2xl max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-6 border-b border-slate-800">
          <div className="flex items-center gap-3 min-w-0">
            <FileText size={20} className="text-blue-400 shrink-0" />
            <h2 className="text-lg font-semibold text-white truncate">{doc.name}</h2>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-slate-800 rounded-lg transition-colors">
            <X size={18} className="text-slate-400" />
          </button>
        </div>
        <div className="p-6 space-y-4">
          <div className="flex gap-4 text-sm">
            <div>
              <span className="text-slate-500">Size:</span>
              <span className="text-slate-300 ml-2">{formatSize(doc.size)}</span>
            </div>
            <div>
              <span className="text-slate-500">Status:</span>
              <span className="ml-2"><StatusBadge status={doc.status} /></span>
            </div>
          </div>
          {doc.preview && (
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-2">Preview</h3>
              <p className="text-sm text-slate-300 bg-slate-950 rounded-lg p-4">{doc.preview}</p>
            </div>
          )}
          {doc.text && (
            <div>
              <h3 className="text-sm font-medium text-slate-400 mb-2">Content</h3>
              <div className="text-sm text-slate-300 bg-slate-950 rounded-lg p-4 max-h-64 overflow-y-auto whitespace-pre-wrap font-mono text-xs">
                {doc.text}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentMeta[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [uploading, setUploading] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [detailDoc, setDetailDoc] = useState<DocumentDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listDocuments();
      setDocuments(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      await uploadDocument(file);
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((d) => d.id !== id));
      setDeleteId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  const handleViewDetail = async (id: string) => {
    setDetailLoading(true);
    try {
      const doc = await getDocument(id);
      setDetailDoc(doc);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load document');
    } finally {
      setDetailLoading(false);
    }
  };

  const filtered = documents.filter((doc) =>
    doc.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Documents</h1>
          <p className="text-slate-400 mt-1">Manage your industrial documents</p>
        </div>
        <div className="flex items-center gap-3">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.csv,.json"
            className="hidden"
            onChange={handleFileChange}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? <Loader2 size={16} className="animate-spin" /> : <Upload size={16} />}
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          placeholder="Search documents..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
        />
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-sm text-red-400">
          {error}
          <button onClick={() => setError(null)} className="ml-2 underline">Dismiss</button>
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <DocumentSkeleton key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <FileText size={48} className="text-slate-700 mb-4" />
          <p className="text-slate-400 font-medium">
            {search ? 'No documents match your search' : 'No documents yet'}
          </p>
          <p className="text-sm text-slate-500 mt-1">
            {search ? 'Try a different search term' : 'Upload your first document to get started'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((doc) => (
            <div
              key={doc.id}
              className="bg-slate-900 rounded-xl p-5 border border-slate-800 hover:border-slate-700 transition-colors group"
            >
              <div className="flex items-start gap-4">
                <div className="p-2 bg-blue-500/10 rounded-lg shrink-0">
                  <FileText size={18} className="text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-semibold text-white truncate">{doc.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-slate-500">{formatSize(doc.size)}</span>
                    <StatusBadge status={doc.status} />
                  </div>
                  {doc.preview && (
                    <p className="text-xs text-slate-500 mt-2 line-clamp-2">{doc.preview}</p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-800 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleViewDetail(doc.id)}
                  disabled={detailLoading}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                >
                  <Eye size={14} />
                  View
                </button>
                <button
                  onClick={() => setDeleteId(doc.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {deleteId && (
        <DeleteConfirm
          onConfirm={() => handleDelete(deleteId)}
          onCancel={() => setDeleteId(null)}
        />
      )}

      {detailLoading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <Loader2 size={32} className="text-blue-400 animate-spin" />
        </div>
      )}

      {detailDoc && !detailLoading && (
        <DocumentModal doc={detailDoc} onClose={() => setDetailDoc(null)} />
      )}
    </div>
  );
}
