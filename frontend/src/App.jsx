import React, { useState } from 'react';
import { FileText, TrendingUp, ArrowLeft } from 'lucide-react';
import DocumentUpload from './components/DocumentUpload';
import SectionDisplay from './components/SectionDisplay';
import './index.css';

function App() {
    const [documents, setDocuments] = useState([]);
    const [trainingMode, setTrainingMode] = useState(false);
    const [view, setView] = useState('upload'); // 'upload' or 'results'

    const handleUploadSuccess = (uploadedDocs) => {
        setDocuments(uploadedDocs);
        setView('results');
    };

    const handleNewUpload = () => {
        setDocuments([]);
        setView('upload');
    };

    return (
        <div className="min-h-screen py-8 px-4">
            {/* Header */}
            <header className="max-w-6xl mx-auto mb-8">
                <div className="flex items-center justify-between">
                    {view === 'results' && (
                        <button
                            onClick={handleNewUpload}
                            className="flex items-center gap-2 glass-dark px-4 py-2 rounded-lg hover:bg-slate-800/70 transition-colors"
                        >
                            <ArrowLeft className="w-5 h-5" />
                            New Upload
                        </button>
                    )}

                    {view === 'results' && (
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2">
                                <input
                                    type="checkbox"
                                    id="training"
                                    checked={trainingMode}
                                    onChange={(e) => setTrainingMode(e.target.checked)}
                                    className="w-5 h-5 rounded accent-primary-500"
                                />
                                <label
                                    htmlFor="training"
                                    className="text-sm font-semibold text-slate-300 cursor-pointer flex items-center gap-2"
                                >
                                    <TrendingUp className="w-4 h-4" />
                                    Training Mode
                                </label>
                            </div>
                        </div>
                    )}
                </div>
            </header>

            {/* Main Content */}
            <main>
                {view === 'upload' ? (
                    <DocumentUpload onUploadSuccess={handleUploadSuccess} />
                ) : (
                    <SectionDisplay documents={documents} trainingMode={trainingMode} />
                )}
            </main>

            {/* Footer */}
            <footer className="max-w-6xl mx-auto mt-16 text-center text-slate-500 text-sm">
                <p>Built with FastAPI, React, spaCy, and scikit-learn</p>
            </footer>
        </div>
    );
}

export default App;
