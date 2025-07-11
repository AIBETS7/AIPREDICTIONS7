// API Integration for AI Football Predictions

class FootballAPI {
    constructor(baseURL = 'http://localhost:5000/api') {
        this.baseURL = baseURL;
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    // Generic API request method
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API request failed for ${endpoint}:`, error);
            throw error;
        }
    }

    // Check if data is cached and not expired
    getCachedData(key) {
        const cached = this.cache.get(key);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        return null;
    }

    // Cache data with timestamp
    setCachedData(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    // Health check
    async healthCheck() {
        return await this.makeRequest('/health');
    }

    // Get system status
    async getStatus() {
        const cached = this.getCachedData('status');
        if (cached) return cached;

        const data = await this.makeRequest('/status');
        this.setCachedData('status', data);
        return data;
    }

    // Get AI predictions
    async getPredictions() {
        const cached = this.getCachedData('predictions');
        if (cached) return cached;

        const data = await this.makeRequest('/predictions');
        this.setCachedData('predictions', data);
        return data;
    }

    // Get matches
    async getMatches() {
        const cached = this.getCachedData('matches');
        if (cached) return cached;

        const data = await this.makeRequest('/matches');
        this.setCachedData('matches', data);
        return data;
    }

    // Get teams
    async getTeams() {
        const cached = this.getCachedData('teams');
        if (cached) return cached;

        const data = await this.makeRequest('/teams');
        this.setCachedData('teams', data);
        return data;
    }

    // Trigger data collection
    async collectData(daysBack = 7, daysForward = 7) {
        const data = await this.makeRequest('/collect-data', {
            method: 'POST',
            body: JSON.stringify({
                days_back: daysBack,
                days_forward: daysForward
            })
        });

        // Clear cache after data collection
        this.cache.clear();
        return data;
    }

    // Train AI models
    async trainModels() {
        return await this.makeRequest('/train-models', {
            method: 'POST'
        });
    }

    // Format prediction for display
    formatPrediction(prediction) {
        return {
            id: prediction.id,
            match: `${prediction.home_team} vs ${prediction.away_team}`,
            prediction: prediction.prediction,
            confidence: (prediction.confidence * 100).toFixed(1) + '%',
            odds: prediction.odds,
            reasoning: prediction.reasoning,
            tipster: prediction.tipster,
            type: prediction.prediction_type,
            created_at: new Date(prediction.created_at).toLocaleString()
        };
    }

    // Get predictions grouped by match
    async getPredictionsByMatch() {
        const response = await this.getPredictions();
        if (!response.success) return [];

        const predictions = response.predictions;
        const grouped = {};

        predictions.forEach(pred => {
            const matchKey = `${pred.home_team} vs ${pred.away_team}`;
            if (!grouped[matchKey]) {
                grouped[matchKey] = {
                    match: matchKey,
                    home_team: pred.home_team,
                    away_team: pred.away_team,
                    match_time: pred.match_time,
                    predictions: []
                };
            }
            grouped[matchKey].predictions.push(this.formatPrediction(pred));
        });

        return Object.values(grouped);
    }

    // Get top predictions by confidence
    async getTopPredictions(limit = 10) {
        const response = await this.getPredictions();
        if (!response.success) return [];

        return response.predictions
            .sort((a, b) => b.confidence - a.confidence)
            .slice(0, limit)
            .map(pred => this.formatPrediction(pred));
    }

    // Get predictions by type
    async getPredictionsByType(type) {
        const response = await this.getPredictions();
        if (!response.success) return [];

        return response.predictions
            .filter(pred => pred.prediction_type === type)
            .sort((a, b) => b.confidence - a.confidence)
            .map(pred => this.formatPrediction(pred));
    }

    // Get team statistics
    async getTeamStats(teamName) {
        const response = await this.getTeams();
        if (!response.success) return null;

        return response.teams.find(team => team.name === teamName);
    }

    // Get upcoming matches
    async getUpcomingMatches(limit = 10) {
        const response = await this.getMatches();
        if (!response.success) return [];

        return response.matches
            .filter(match => match.status === 'scheduled')
            .slice(0, limit);
    }

    // Get live matches
    async getLiveMatches() {
        const response = await this.getMatches();
        if (!response.success) return [];

        return response.matches.filter(match => match.status === 'live');
    }

    // Get finished matches
    async getFinishedMatches(limit = 20) {
        const response = await this.getMatches();
        if (!response.success) return [];

        return response.matches
            .filter(match => match.status === 'finished')
            .slice(0, limit);
    }

    // Clear cache
    clearCache() {
        this.cache.clear();
    }

    // Refresh all data
    async refreshAllData() {
        try {
            await this.collectData();
            this.clearCache();
            return true;
        } catch (error) {
            console.error('Error refreshing data:', error);
            return false;
        }
    }
}

// Global API instance
const footballAPI = new FootballAPI();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FootballAPI;
}
