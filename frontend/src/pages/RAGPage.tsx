import React, { useCallback, useEffect, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { ragService, UploadedFile } from '../services/ragService';

const RAGPage: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const data = await ragService.listFiles();
      setFiles(data);
    } catch (error) {
      toast.error('Failed to load files');
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      setUploading(true);
      try {
        await ragService.uploadFile(file);
        toast.success(`${file.name} uploaded successfully!`);
        loadFiles();
      } catch (error: any) {
        toast.error(error.response?.data?.detail || `Failed to upload ${file.name}`);
      } finally {
        setUploading(false);
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
  });

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const response = await ragService.searchDocuments(searchQuery);
      setSearchResults(response.results);
    } catch (error) {
      toast.error('Failed to search');
    } finally {
      setSearching(false);
    }
  };

  const handleDelete = async (fileId: string) => {
    if (!window.confirm('Are you sure you want to delete this file?')) return;

    try {
      await ragService.deleteFile(fileId);
      toast.success('File deleted');
      loadFiles();
    } catch (error) {
      toast.error('Failed to delete file');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload documents to build your private knowledge base for agents to reference
        </p>
      </div>

      {/* Upload Area */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400'
          }`}
        >
          <input {...getInputProps()} />
          <div className="space-y-2">
            <div className="text-4xl">📁</div>
            <p className="text-lg font-medium text-gray-700">
              {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
            </p>
            <p className="text-sm text-gray-500">or click to browse</p>
            <p className="text-xs text-gray-400 mt-2">
              Supported: PDF, TXT, MD, DOC, DOCX (max 100MB)
            </p>
          </div>
        </div>
        {uploading && (
          <div className="mt-4 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="text-sm text-gray-600 mt-2">Uploading and indexing...</p>
          </div>
        )}
      </div>

      {/* Search */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Search Knowledge Base</h2>
        <form onSubmit={handleSearch} className="flex space-x-3">
          <input
            type="text"
            className="input flex-1"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for information..."
          />
          <button type="submit" disabled={searching} className="btn-primary">
            {searching ? 'Searching...' : '🔍 Search'}
          </button>
        </form>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="mt-6 space-y-4">
            <h3 className="font-semibold text-gray-900">Search Results:</h3>
            {searchResults.map((result, idx) => (
              <div key={idx} className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <span className="text-xs text-gray-500">{result.filename}</span>
                  <span className="text-xs font-medium text-primary-600">
                    Score: {(result.score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-sm text-gray-700">{result.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Files List */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Uploaded Files ({files.length})</h2>
        {files.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No files uploaded yet</p>
        ) : (
          <div className="space-y-3">
            {files.map((file) => (
              <div key={file.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{file.original_filename}</h3>
                  <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                    <span>📊 {formatFileSize(file.file_size_bytes)}</span>
                    <span>📦 {file.chunks_count} chunks</span>
                    <span>📅 {new Date(file.uploaded_at).toLocaleDateString()}</span>
                    <span className={`px-2 py-1 rounded ${
                      file.status === 'indexed' ? 'bg-green-100 text-green-800' :
                      file.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {file.status}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(file.id)}
                  className="text-red-600 hover:text-red-800 px-3 py-1 rounded hover:bg-red-50"
                >
                  🗑️ Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RAGPage;
