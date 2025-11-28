import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, FileText, Loader2 } from 'lucide-react';
import api from '../api/client';

export default function DocumentUpload({ onUploadSuccess }) {
    const [uploading, setUploading] = useState(false);
    const [threshold, setThreshold] = useState(0.5);
    const [batchMode, setBatchMode] = useState(false);

    const onDrop = async (acceptedFiles) => {
        if (acceptedFiles.length === 0) return;

        setUploading(true);

        try {
            if (batchMode && acceptedFiles.length > 1) {
                // Batch upload
                const result = await api.uploadBatch(acceptedFiles, threshold);

                // Get results for each document
                const documents = await Promise.all(
                    result.document_ids.map(id => api.getDocument(id))
                );

                onUploadSuccess(documents);
            } else {
                // Single upload
                const result = await api.uploadDocument(acceptedFiles[0], threshold);
                const document = await api.getDocument(result.document_id);
                onUploadSuccess([document]);
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Error uploading document: ' + (error.response?.data?.detail || error.message));
        } finally {
            setUploading(false);
        }
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'text/plain': ['.txt'],
        },
        multiple: batchMode,
    });

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
                <h1 className="text-5xl font-display font-bold mb-4 gradient-text">
                    Sectify
                </h1>
                <p className="text-xl text-slate-300">
                    AI-Powered Document Section Extraction
                </p>
            </div>

            {/* Settings */}
            <div className="card mb-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <div className="flex-1">
                        <label className="block text-sm font-semibold text-slate-300 mb-2">
                            Relevance Threshold: {threshold.toFixed(2)}
                        </label>
                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.05"
                            value={threshold}
                            onChange={(e) => setThreshold(parseFloat(e.target.value))}
                            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
                        />
                    </div>

                    <div className="flex items-center gap-2">
                        <input
                            type="checkbox"
                            id="batch"
                            checked={batchMode}
                            onChange={(e) => setBatchMode(e.target.checked)}
                            className="w-5 h-5 rounded accent-primary-500"
                        />
                        <label htmlFor="batch" className="text-sm font-semibold text-slate-300 cursor-pointer">
                            Batch Mode
                        </label>
                    </div>
                </div>
            </div>

            {/* Upload Area */}
            <div
                {...getRootProps()}
                className={`
          relative overflow-hidden rounded-2xl p-12 text-center cursor-pointer
          transition-all duration-300 border-2 border-dashed
          ${isDragActive
                        ? 'border-primary-400 bg-primary-500/10 scale-105'
                        : 'border-slate-600 glass-dark hover:border-primary-500 hover:bg-slate-800/50'
                    }
        `}
            >
                <input {...getInputProps()} />

                {/* Animated Background */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary-500/5 to-accent-500/5 animate-gradient opacity-50" />

                {/* Content */}
                <div className="relative z-10">
                    {uploading ? (
                        <div className="flex flex-col items-center gap-4">
                            <Loader2 className="w-16 h-16 text-primary-400 animate-spin" />
                            <p className="text-xl font-semibold text-white">Processing...</p>
                        </div>
                    ) : (
                        <>
                            <Upload className="w-16 h-16 mx-auto mb-4 text-primary-400 animate-float" />

                            <h2 className="text-2xl font-bold text-white mb-2">
                                {isDragActive ? 'Drop files here' : 'Upload Documents'}
                            </h2>

                            <p className="text-slate-300 mb-6">
                                {batchMode
                                    ? 'Drag & drop multiple files or click to browse'
                                    : 'Drag & drop a file or click to browse'
                                }
                            </p>

                            <div className="flex items-center justify-center gap-6 text-sm text-slate-400">
                                <div className="flex items-center gap-2">
                                    <File className="w-5 h-5" />
                                    <span>PDF</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <FileText className="w-5 h-5" />
                                    <span>DOCX</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <FileText className="w-5 h-5" />
                                    <span>TXT</span>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>

            {/* Info */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="glass-dark rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-primary-400 mb-1">Smart</div>
                    <div className="text-sm text-slate-300">ML-powered relevance detection</div>
                </div>
                <div className="glass-dark rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-accent-400 mb-1">Fast</div>
                    <div className="text-sm text-slate-300">Process documents in seconds</div>
                </div>
                <div className="glass-dark rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-emerald-400 mb-1">Accurate</div>
                    <div className="text-sm text-slate-300">Learns from your feedback</div>
                </div>
            </div>
        </div>
    );
}
