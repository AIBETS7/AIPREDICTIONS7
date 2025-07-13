// API handling for AI Predictions 7
class APIService {
    constructor() {
        this.baseURL = 'https://myfootballpredictions.onrender.com/api';
        this.timeout = 10000; // 10 seconds
    }

    // Generic fetch method with error handling
    async fetchWithTimeout(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            
            throw error;
        }
    }

    // Get daily picks
    async getDailyPicks() {
        try {
            const data = await this.fetchWithTimeout(`${this.baseURL}/daily-picks`);
            return {
                success: true,
                picks: data.picks || [],
                message: 'Picks loaded successfully'
            };
        } catch (error) {
            console.error('Error fetching daily picks:', error);
            return {
                success: false,
                picks: [],
                message: 'Error loading picks: ' + error.message
            };
        }
    }

    // Get AI statistics
    async getAIStats() {
        try {
            const data = await this.fetchWithTimeout(`${this.baseURL}/ai-stats`);
            return {
                success: true,
                stats: data.stats || {},
                message: 'Stats loaded successfully'
            };
        } catch (error) {
            console.error('Error fetching AI stats:', error);
            return {
                success: false,
                stats: {},
                message: 'Error loading stats: ' + error.message
            };
        }
    }

    // Get predictions preview
    async getPredictionsPreview() {
        try {
            const data = await this.fetchWithTimeout(`${this.baseURL}/predictions-preview`);
            return {
                success: true,
                predictions: data.predictions || [],
                message: 'Predictions loaded successfully'
            };
        } catch (error) {
            console.error('Error fetching predictions preview:', error);
            return {
                success: false,
                predictions: [],
                message: 'Error loading predictions: ' + error.message
            };
        }
    }

    // Check payment status
    async checkPaymentStatus() {
        try {
            const data = await this.fetchWithTimeout(`${this.baseURL}/payment-status`);
            return {
                success: true,
                status: data.status || 'unknown',
                message: 'Payment status checked successfully'
            };
        } catch (error) {
            console.error('Error checking payment status:', error);
            return {
                success: false,
                status: 'unknown',
                message: 'Error checking payment status: ' + error.message
            };
        }
    }

    // Get system status
    async getSystemStatus() {
        try {
            const data = await this.fetchWithTimeout(`${this.baseURL}/status`);
            return {
                success: true,
                status: data,
                message: 'System status loaded successfully'
            };
        } catch (error) {
            console.error('Error fetching system status:', error);
            return {
                success: false,
                status: null,
                message: 'Error loading system status: ' + error.message
            };
        }
    }

    // Submit contact form
    async submitContactForm(formData) {
        try {
            const data = await this.fetchWithTimeout(`${this.baseURL}/contact`, {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            return {
                success: true,
                message: 'Message sent successfully'
            };
        } catch (error) {
            console.error('Error submitting contact form:', error);
            return {
                success: false,
                message: 'Error sending message: ' + error.message
            };
        }
    }

    // Subscribe to newsletter
    async subscribeNewsletter(email) {
        try {
            const data = await this.fetchWithTimeout(`${this.baseURL}/newsletter`, {
                method: 'POST',
                body: JSON.stringify({ email })
            });
            return {
                success: true,
                message: 'Newsletter subscription successful'
            };
        } catch (error) {
            console.error('Error subscribing to newsletter:', error);
            return {
                success: false,
                message: 'Error subscribing to newsletter: ' + error.message
            };
        }
    }
}

// Initialize API service
const apiService = new APIService();

// Export for use in other files
window.apiService = apiService;

// Utility functions for data formatting
const DataFormatter = {
    // Format prediction type for display
    formatPredictionType(type) {
        const types = {
            'match_winner': 'Ganador del Partido',
            'over_under': 'Más/Menos Goles',
            'both_teams_score': 'Ambos Marcan',
            'correct_score': 'Resultado Exacto',
            'first_goalscorer': 'Primer Goleador',
            'half_time_result': 'Resultado al Descanso',
            'double_chance': 'Doble Oportunidad',
            'draw_no_bet': 'Empate No Válido',
            'exact_goals': 'Goles Exactos',
            'clean_sheet': 'Portería a Cero'
        };
        
        return types[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    },

    // Format match time
    formatMatchTime(timeString) {
        if (!timeString) return 'Hora por confirmar';
        
        try {
            const date = new Date(timeString);
            const now = new Date();
            const diffTime = date - now;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays < 0) {
                return 'Partido finalizado';
            } else if (diffDays === 0) {
                return `Hoy a las ${date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;
            } else if (diffDays === 1) {
                return `Mañana a las ${date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })}`;
            } else {
                return date.toLocaleDateString('es-ES', {
                    weekday: 'long',
                    day: 'numeric',
                    month: 'long',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            }
        } catch (error) {
            return timeString;
        }
    },

    // Format confidence percentage
    formatConfidence(confidence) {
        if (typeof confidence === 'number') {
            return Math.round(confidence * 100) + '%';
        }
        return confidence || 'N/A';
    },

    // Format odds
    formatOdds(odds) {
        if (typeof odds === 'number') {
            return odds.toFixed(2);
        }
        return odds || 'N/A';
    },

    // Get competition color class
    getCompetitionClass(competition) {
        if (!competition) return 'la-liga';
        
        const competitionLower = competition.toLowerCase();
        
        if (competitionLower.includes('euro') || competitionLower.includes('uefa')) {
            return 'womens-euro';
        } else if (competitionLower.includes('champions')) {
            return 'champions-league';
        } else if (competitionLower.includes('premier')) {
            return 'premier-league';
        } else if (competitionLower.includes('bundesliga')) {
            return 'bundesliga';
        } else if (competitionLower.includes('serie a')) {
            return 'serie-a';
        } else {
            return 'la-liga';
        }
    },

    // Get result status class
    getResultStatusClass(status) {
        if (!status) return '';
        
        switch (status.toLowerCase()) {
            case 'correct':
                return 'correct';
            case 'incorrect':
                return 'incorrect';
            case 'pending':
                return 'pending';
            default:
                return '';
        }
    }
};

// Export formatter
window.DataFormatter = DataFormatter;

// Error handling utilities
const ErrorHandler = {
    // Show user-friendly error message
    showError(error, context = '') {
        console.error(`Error in ${context}:`, error);
        
        let message = 'Ha ocurrido un error inesperado.';
        
        if (error.message.includes('timeout')) {
            message = 'La solicitud ha tardado demasiado. Inténtalo de nuevo.';
        } else if (error.message.includes('network')) {
            message = 'Error de conexión. Verifica tu internet.';
        } else if (error.message.includes('404')) {
            message = 'Recurso no encontrado.';
        } else if (error.message.includes('500')) {
            message = 'Error del servidor. Inténtalo más tarde.';
        }
        
        // Show notification
        if (window.showNotification) {
            window.showNotification(message, 'error');
        } else {
            alert(message);
        }
    },

    // Retry function with exponential backoff
    async retry(fn, maxRetries = 3, delay = 1000) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await fn();
            } catch (error) {
                if (i === maxRetries - 1) throw error;
                
                await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)));
            }
        }
    }
};

// Export error handler
window.ErrorHandler = ErrorHandler;

// Cache management
const CacheManager = {
    cache: new Map(),
    
    // Set cache item
    set(key, value, ttl = 300000) { // 5 minutes default
        this.cache.set(key, {
            value,
            expiry: Date.now() + ttl
        });
    },
    
    // Get cache item
    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        if (Date.now() > item.expiry) {
            this.cache.delete(key);
            return null;
        }
        
        return item.value;
    },
    
    // Clear cache
    clear() {
        this.cache.clear();
    },
    
    // Clear expired items
    cleanup() {
        const now = Date.now();
        for (const [key, item] of this.cache.entries()) {
            if (now > item.expiry) {
                this.cache.delete(key);
            }
        }
    }
};

// Export cache manager
window.CacheManager = CacheManager;

// Clean up cache periodically
setInterval(() => CacheManager.cleanup(), 60000); // Every minute
