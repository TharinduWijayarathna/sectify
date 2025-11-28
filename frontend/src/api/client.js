/**
 * API client for backend communication
 */
import axios from 'axios';

const API_BASE_URL = '/api';

const client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    /**
     * Upload a document for processing
     */
    uploadDocument: async (file, threshold = 0.5) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('threshold', threshold.toString());

        const response = await client.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    },

    /**
     * Upload multiple documents
     */
    uploadBatch: async (files, threshold = 0.5) => {
        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });
        formData.append('threshold', threshold.toString());

        const response = await client.post('/batch', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    },

    /**
     * Get document processing results
     */
    getDocument: async (documentId, threshold = null) => {
        const params = threshold !== null ? { threshold } : {};
        const response = await client.get(`/documents/${documentId}`, { params });
        return response.data;
    },

    /**
     * Submit section feedback
     */
    submitFeedback: async (documentId, sectionId, isRelevant) => {
        const response = await client.post('/feedback', {
            document_id: documentId,
            section_id: sectionId,
            is_relevant: isRelevant,
        });
        return response.data;
    },

    /**
     * Export document results
     */
    exportResults: async (documentId, format, threshold) => {
        const response = await client.post('/export', {
            document_id: documentId,
            format,
            threshold,
        }, {
            responseType: 'blob',
        });

        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `sections.${format}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    },

    /**
     * Health check
     */
    healthCheck: async () => {
        const response = await client.get('/health');
        return response.data;
    },
};

export default api;
