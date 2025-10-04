'use client';

import { useState, useEffect, useRef } from 'react';
import { 
  CloudArrowUpIcon, 
  DocumentIcon, 
  FolderIcon,
  ShareIcon,
  TrashIcon,
  EyeIcon,
  TagIcon,
  FunnelIcon,
  XMarkIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

interface File {
  id: string;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  is_public: boolean;
  is_encrypted: boolean;
  tags: string[];
  download_count: number;
  last_accessed: string | null;
  created_at: string;
  updated_at: string;
}

interface FileShare {
  id: string;
  file_id: string;
  share_token: string;
  permission: string;
  expires_at: string | null;
  access_count: number;
  created_at: string;
}

interface StorageStats {
  total_files: number;
  total_size: number;
  total_size_mb: number;
  mime_types: Record<string, number>;
}

export function FileManager() {
  const [files, setFiles] = useState<File[]>([]);
  const [stats, setStats] = useState<StorageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Upload states
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Filter states
  const [selectedTeam, setSelectedTeam] = useState<string>('');
  const [selectedMimeType, setSelectedMimeType] = useState<string>('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modal states
  const [showShareModal, setShowShareModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [shareExpiry, setShareExpiry] = useState<string>('');
  const [sharePermission, setSharePermission] = useState('read');

  useEffect(() => {
    loadFiles();
    loadStats();
  }, [selectedTeam, selectedMimeType, selectedTags]);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedTeam) params.append('team_id', selectedTeam);
      if (selectedMimeType) params.append('mime_type', selectedMimeType);
      if (selectedTags.length > 0) params.append('tags', selectedTags.join(','));
      
      const response = await fetch(`/api/files?${params}`, {
        headers: { 'Authorization': `Bearer ${await getAuthToken()}` }
      });
      
      if (!response.ok) throw new Error('Failed to load files');
      
      const filesData = await response.json();
      setFiles(filesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/files/stats', {
        headers: { 'Authorization': `Bearer ${await getAuthToken()}` }
      });
      
      if (!response.ok) throw new Error('Failed to load stats');
      
      const statsData = await response.json();
      setStats(statsData);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleFileUpload = async (files: FileList) => {
    if (!files.length) return;

    setUploading(true);
    setUploadProgress(0);
    setError(null);
    setSuccess(null);

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('is_public', 'false');
        formData.append('tags', JSON.stringify(['uploaded']));

        const response = await fetch('/api/files/upload', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${await getAuthToken()}` },
          body: formData,
        });

        if (!response.ok) throw new Error(`Failed to upload ${file.name}`);

        setUploadProgress(((i + 1) / files.length) * 100);
      }

      setSuccess(`Successfully uploaded ${files.length} file(s)`);
      await loadFiles();
      await loadStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files);
    }
  };

  const downloadFile = async (file: File) => {
    try {
      const response = await fetch(`/api/files/${file.id}/download`, {
        headers: { 'Authorization': `Bearer ${await getAuthToken()}` }
      });
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.original_filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed');
    }
  };

  const deleteFile = async (file: File) => {
    if (!confirm(`Are you sure you want to delete "${file.original_filename}"?`)) return;

    try {
      const response = await fetch(`/api/files/${file.id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${await getAuthToken()}` }
      });
      
      if (!response.ok) throw new Error('Delete failed');
      
      setSuccess('File deleted successfully');
      await loadFiles();
      await loadStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  const shareFile = async () => {
    if (!selectedFile) return;

    try {
      const response = await fetch(`/api/files/${selectedFile.id}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getAuthToken()}`,
        },
        body: JSON.stringify({
          permission: sharePermission,
          expires_at: shareExpiry ? new Date(shareExpiry).toISOString() : null,
        }),
      });
      
      if (!response.ok) throw new Error('Share failed');
      
      const shareData = await response.json();
      setSuccess(`File shared! Share link: ${window.location.origin}/api/files/shared/${shareData.share_token}`);
      setShowShareModal(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Share failed');
    }
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType.startsWith('image/')) return '🖼️';
    if (mimeType.startsWith('video/')) return '🎥';
    if (mimeType.startsWith('audio/')) return '🎵';
    if (mimeType.includes('pdf')) return '📄';
    if (mimeType.includes('text/')) return '📝';
    if (mimeType.includes('zip') || mimeType.includes('rar')) return '📦';
    return '📁';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getAuthToken = async (): Promise<string> => {
    // This would typically get the token from your auth system
    return 'your-auth-token-here';
  };

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.original_filename.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  if (loading && files.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <XMarkIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4">
          <div className="flex">
            <CheckIcon className="h-5 w-5 text-green-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Success</h3>
              <p className="mt-1 text-sm text-green-700">{success}</p>
            </div>
          </div>
        </div>
      )}

      {/* Storage Stats */}
      {stats && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Storage Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{stats.total_files}</div>
              <div className="text-sm text-gray-500">Total Files</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{stats.total_size_mb} MB</div>
              <div className="text-sm text-gray-500">Storage Used</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{Object.keys(stats.mime_types).length}</div>
              <div className="text-sm text-gray-500">File Types</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {Object.values(stats.mime_types).reduce((a, b) => a + b, 0)}
              </div>
              <div className="text-sm text-gray-500">Total Files</div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <label htmlFor="file-upload" className="cursor-pointer">
            <span className="mt-2 block text-sm font-medium text-gray-900">
              Drop files here or click to upload
            </span>
            <span className="mt-1 block text-sm text-gray-500">
              Supports all file types
            </span>
          </label>
          <input
            ref={fileInputRef}
            id="file-upload"
            name="file-upload"
            type="file"
            multiple
            className="sr-only"
            onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
            disabled={uploading}
          />
        </div>
        {uploading && (
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="mt-2 text-sm text-gray-600">Uploading... {Math.round(uploadProgress)}%</p>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
            <input
              type="text"
              placeholder="Search files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <select
            value={selectedMimeType}
            onChange={(e) => setSelectedMimeType(e.target.value)}
            className="border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Types</option>
            <option value="image">Images</option>
            <option value="video">Videos</option>
            <option value="audio">Audio</option>
            <option value="application/pdf">PDFs</option>
            <option value="text">Text Files</option>
          </select>
        </div>
      </div>

      {/* Files Grid */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Your Files</h3>
        </div>
        
        {filteredFiles.length === 0 ? (
          <div className="text-center py-12">
            <DocumentIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No files</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by uploading a file.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 p-6">
            {filteredFiles.map((file) => (
              <div key={file.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{getFileIcon(file.mime_type)}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {file.original_filename}
                        </p>
                        <p className="text-xs text-gray-500">{formatFileSize(file.file_size)}</p>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center space-x-2 text-xs text-gray-500">
                      <span>{formatDate(file.created_at)}</span>
                      <span>•</span>
                      <span>{file.download_count} downloads</span>
                    </div>
                    {file.tags && file.tags.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {file.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="mt-4 flex justify-between">
                  <button
                    onClick={() => downloadFile(file)}
                    className="text-blue-600 hover:text-blue-900 text-sm font-medium"
                  >
                    <EyeIcon className="h-4 w-4 inline mr-1" />
                    Download
                  </button>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setSelectedFile(file);
                        setShowShareModal(true);
                      }}
                      className="text-green-600 hover:text-green-900 text-sm font-medium"
                    >
                      <ShareIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => deleteFile(file)}
                      className="text-red-600 hover:text-red-900 text-sm font-medium"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Share Modal */}
      {showShareModal && selectedFile && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Share "{selectedFile.original_filename}"
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Permission</label>
                  <select
                    value={sharePermission}
                    onChange={(e) => setSharePermission(e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="read">Read Only</option>
                    <option value="write">Read & Write</option>
                    <option value="admin">Full Access</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Expires At (Optional)</label>
                  <input
                    type="datetime-local"
                    value={shareExpiry}
                    onChange={(e) => setShareExpiry(e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => setShowShareModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  onClick={shareFile}
                  className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
                >
                  Share File
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
