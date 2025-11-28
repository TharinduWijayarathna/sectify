import React, { useState } from 'react';
import {
    ChevronDown, ChevronUp, Tag, FileText, ThumbsUp, ThumbsDown,
    Download, Filter
} from 'lucide-react';
import api from '../api/client';

export default function SectionDisplay({ documents, trainingMode }) {
    const [threshold, setThreshold] = useState(0.5);
    const [expandedSections, setExpandedSections] = useState(new Set());
    const [feedbackGiven, setFeedbackGiven] = useState(new Set());

    const toggleSection = (docId, sectionId) => {
        const key = `${docId}-${sectionId}`;
        const newExpanded = new Set(expandedSections);
        if (newExpanded.has(key)) {
            newExpanded.delete(key);
        } else {
            newExpanded.add(key);
        }
        setExpandedSections(newExpanded);
    };

    const handleFeedback = async (docId, sectionId, isRelevant) => {
        try {
            await api.submitFeedback(docId, sectionId, isRelevant);
            setFeedbackGiven(new Set(feedbackGiven).add(`${docId}-${sectionId}`));
        } catch (error) {
            console.error('Feedback error:', error);
        }
    };

    const handleExport = async (docId, format) => {
        try {
            await api.exportResults(docId, format, threshold);
        } catch (error) {
            console.error('Export error:', error);
            alert('Error exporting results');
        }
    };

    const getScoreClass = (score) => {
        if (score >= 0.7) return 'high';
        if (score >= 0.4) return 'medium';
        return 'low';
    };

    const getScoreColor = (score) => {
        if (score >= 0.7) return 'text-emerald-400';
        if (score >= 0.4) return 'text-yellow-400';
        return 'text-red-400';
    };

    return (
        <div className="max-w-6xl mx-auto">
            {documents.map((doc) => {
                const filteredSections = doc.sections.filter(s => s.relevance_score >= threshold);

                return (
                    <div key={doc.document_id} className="mb-8">
                        {/* Document Header */}
                        <div className="card mb-6">
                            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                                <div>
                                    <h2 className="text-2xl font-bold text-white mb-2">
                                        {doc.document_name}
                                    </h2>
                                    <div className="flex flex-wrap gap-4 text-sm text-slate-300">
                                        <span>Total Sections: <strong className="text-white">{doc.total_sections}</strong></span>
                                        <span>Relevant: <strong className="text-emerald-400">{filteredSections.length}</strong></span>
                                        <span>Processing Time: <strong className="text-primary-400">{doc.processing_time?.toFixed(2)}s</strong></span>
                                    </div>
                                </div>

                                {/* Export Buttons */}
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => handleExport(doc.document_id, 'json')}
                                        className="btn-secondary flex items-center gap-2"
                                    >
                                        <Download className="w-4 h-4" />
                                        JSON
                                    </button>
                                    <button
                                        onClick={() => handleExport(doc.document_id, 'txt')}
                                        className="btn-secondary flex items-center gap-2"
                                    >
                                        <Download className="w-4 h-4" />
                                        TXT
                                    </button>
                                </div>
                            </div>

                            {/* Threshold Slider */}
                            <div className="mt-6 pt-6 border-t border-slate-700">
                                <div className="flex items-center gap-4">
                                    <Filter className="w-5 h-5 text-slate-400" />
                                    <div className="flex-1">
                                        <label className="block text-sm font-semibold text-slate-300 mb-2">
                                            Filter Threshold: {threshold.toFixed(2)}
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
                                    <div className="text-sm text-slate-300">
                                        Showing <strong className="text-white">{filteredSections.length}</strong> sections
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Sections List */}
                        <div className="space-y-3">
                            {filteredSections.map((section) => {
                                const key = `${doc.document_id}-${section.id}`;
                                const isExpanded = expandedSections.has(key);
                                const hasFeedback = feedbackGiven.has(key);

                                return (
                                    <div
                                        key={section.id}
                                        className={`section-card ${getScoreClass(section.relevance_score)}`}
                                    >
                                        {/* Section Header */}
                                        <div
                                            className="flex items-start justify-between gap-4 cursor-pointer"
                                            onClick={() => toggleSection(doc.document_id, section.id)}
                                        >
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-3 mb-2">
                                                    <h3 className="text-lg font-semibold text-white truncate">
                                                        {section.title}
                                                    </h3>
                                                    {section.page_number && (
                                                        <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-300">
                                                            Page {section.page_number}
                                                        </span>
                                                    )}
                                                </div>

                                                {/* Tags */}
                                                <div className="flex flex-wrap gap-2 mb-2">
                                                    {section.tags?.map((tag) => (
                                                        <span
                                                            key={tag}
                                                            className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full bg-primary-500/20 text-primary-300"
                                                        >
                                                            <Tag className="w-3 h-3" />
                                                            {tag}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-4">
                                                {/* Score */}
                                                <div className="text-right">
                                                    <div className={`text-2xl font-bold ${getScoreColor(section.relevance_score)}`}>
                                                        {(section.relevance_score * 100).toFixed(0)}%
                                                    </div>
                                                    <div className="text-xs text-slate-400">relevance</div>
                                                </div>

                                                {/* Expand Icon */}
                                                {isExpanded ? (
                                                    <ChevronUp className="w-6 h-6 text-slate-400" />
                                                ) : (
                                                    <ChevronDown className="w-6 h-6 text-slate-400" />
                                                )}
                                            </div>
                                        </div>

                                        {/* Expanded Content */}
                                        {isExpanded && (
                                            <div className="mt-4 pt-4 border-t border-slate-700">
                                                <div className="prose prose-invert max-w-none mb-4">
                                                    <p className="text-slate-300 whitespace-pre-wrap line-clamp-10">
                                                        {section.content}
                                                    </p>
                                                </div>

                                                {/* Training Mode Feedback */}
                                                {trainingMode && !hasFeedback && (
                                                    <div className="flex items-center gap-4 mt-4 p-4 rounded-lg bg-slate-800/50">
                                                        <span className="text-sm text-slate-300 font-semibold">
                                                            Is this section relevant?
                                                        </span>
                                                        <div className="flex gap-2">
                                                            <button
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    handleFeedback(doc.document_id, section.id, true);
                                                                }}
                                                                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 transition-colors"
                                                            >
                                                                <ThumbsUp className="w-4 h-4" />
                                                                Yes
                                                            </button>
                                                            <button
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    handleFeedback(doc.document_id, section.id, false);
                                                                }}
                                                                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-500/20 text-red-300 hover:bg-red-500/30 transition-colors"
                                                            >
                                                                <ThumbsDown className="w-4 h-4" />
                                                                No
                                                            </button>
                                                        </div>
                                                    </div>
                                                )}

                                                {hasFeedback && (
                                                    <div className="mt-4 text-sm text-emerald-400 font-semibold">
                                                        ✓ Feedback submitted
                                                    </div>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>

                        {filteredSections.length === 0 && (
                            <div className="card text-center py-12">
                                <FileText className="w-16 h-16 mx-auto mb-4 text-slate-600" />
                                <p className="text-xl text-slate-400">
                                    No sections match the current threshold
                                </p>
                                <p className="text-sm text-slate-500 mt-2">
                                    Try lowering the threshold to see more sections
                                </p>
                            </div>
                        )}
                    </div>
                );
            })}
        </div>
    );
}
