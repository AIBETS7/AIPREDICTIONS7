// Single Pick Payment Handler for AI Predictions 7
class SinglePickPaymentHandler {
    constructor() {
        this.isProcessing = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSinglePickPreview();
    }

    setupEventListeners() {
        // Single pick form submission
        const singlePickForm = document.getElementById('single-pick-form');
        if (singlePickForm) {
            singlePickForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleSinglePickPayment();
            });
        }

        // Email input validation
        const emailInput = document.getElementById('single-pick-email');
        if (emailInput) {
            emailInput.addEventListener('input', (e) => {
                this.validateEmail(e.target.value);
            });
        }
    }

    async handleSinglePickPayment() {
        if (this.isProcessing) return;

        const emailInput = document.getElementById('single-pick-email');
        const submitButton = document.getElementById('single-pick-submit-button');
        
        if (!emailInput || !submitButton) return;

        const email = emailInput.value.trim();

        // Validate email
        if (!this.validateEmail(email)) {
            this.showError('Por favor, introduce un email válido');
            return;
        }

        this.isProcessing = true;
        this.showLoading(true, submitButton);

        try {
            // Check if user already has access
            const hasAccess = this.checkUserAccess(email);
            if (hasAccess) {
                this.showSuccess('Ya tienes acceso a picks premium. Revisa tu email.');
                closeSinglePickModal();
                return;
            }

            // Process payment
            const result = await this.processPayment(email);
            
            if (result.success) {
                this.showSuccess('¡Pago completado! Tu pick único ha sido enviado a tu email.');
                this.saveUserAccess(email, 'single_pick');
                closeSinglePickModal();
                
                // Send pick to user (simulated)
                this.sendPickToUser(email);
            } else {
                throw new Error(result.message);
            }

        } catch (error) {
            console.error('Single pick payment error:', error);
            this.showError(error.message || 'Error procesando el pago');
        } finally {
            this.isProcessing = false;
            this.showLoading(false, submitButton);
        }
    }

    async processPayment(email) {
        try {
            // Create payment intent
            const response = await fetch('https://myfootballpredictions.onrender.com/api/create-single-pick-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    price_id: 'price_1RkT8vLgWyziDhelUuw6X0pv'
                })
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.message || 'Error creating payment');
            }

            // For demo purposes, simulate successful payment
            // In production, this would integrate with Stripe
            return {
                success: true,
                message: 'Payment processed successfully'
            };

        } catch (error) {
            throw error;
        }
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(email);
        
        // Update UI feedback
        const emailInput = document.getElementById('single-pick-email');
        if (emailInput) {
            if (email && !isValid) {
                emailInput.style.borderColor = '#ef4444';
            } else if (email && isValid) {
                emailInput.style.borderColor = '#10b981';
            } else {
                emailInput.style.borderColor = '#e5e7eb';
            }
        }
        
        return isValid;
    }

    checkUserAccess(email) {
        const payments = JSON.parse(localStorage.getItem('payments') || '[]');
        const userPayments = payments.filter(p => p.email === email);
        
        if (userPayments.length === 0) return false;

        // Check for active subscription
        const subscription = userPayments.find(p => p.type === 'subscription' && p.status === 'active');
        if (subscription) return true;

        // Check for recent single pick (valid for 24 hours)
        const singlePick = userPayments.find(p => p.type === 'single_pick' && p.status === 'active');
        if (singlePick) {
            const pickDate = new Date(singlePick.timestamp);
            const today = new Date();
            const diffTime = today - pickDate;
            const diffHours = diffTime / (1000 * 60 * 60);
            
            if (diffHours <= 24) {
                return true;
            }
        }

        return false;
    }

    saveUserAccess(email, type) {
        const paymentData = {
            email: email,
            type: type,
            timestamp: new Date().toISOString(),
            status: 'active'
        };

        const payments = JSON.parse(localStorage.getItem('payments') || '[]');
        payments.push(paymentData);
        localStorage.setItem('payments', JSON.stringify(payments));

        // Save user email for future reference
        localStorage.setItem('userEmail', email);
    }

    async sendPickToUser(email) {
        try {
            // Get today's best pick
            const response = await fetch('https://myfootballpredictions.onrender.com/api/daily-picks');
            const data = await response.json();
            
            if (data.success && data.picks && data.picks.length > 0) {
                const bestPick = data.picks[0]; // Get the first (best) pick
                
                // In a real implementation, this would send an email
                console.log('Sending pick to user:', email, bestPick);
                
                // For demo purposes, show the pick in a notification
                this.showSuccess(`Pick enviado: ${bestPick.home_team} vs ${bestPick.away_team} - ${bestPick.prediction}`);
            }
        } catch (error) {
            console.error('Error sending pick to user:', error);
        }
    }

    async loadSinglePickPreview() {
        try {
            const response = await fetch('https://myfootballpredictions.onrender.com/api/daily-picks');
            const data = await response.json();
            
            if (data.success && data.picks && data.picks.length > 0) {
                const bestPick = data.picks[0];
                this.updatePickPreview(bestPick);
            }
        } catch (error) {
            console.error('Error loading pick preview:', error);
        }
    }

    updatePickPreview(pick) {
        const previewContainer = document.querySelector('.pick-preview');
        if (!previewContainer) return;

        const previewHTML = `
            <h3>Tu Pick Premium del Día</h3>
            <div class="pick-preview-content">
                <div class="pick-match-preview">
                    <strong>${pick.home_team} vs ${pick.away_team}</strong>
                </div>
                <div class="pick-prediction-preview">
                    <span class="prediction-label">Predicción:</span>
                    <span class="prediction-value">${pick.prediction}</span>
                </div>
                <div class="pick-confidence-preview">
                    <span class="confidence-label">Confianza:</span>
                    <span class="confidence-value">${Math.round(pick.confidence * 100)}%</span>
                </div>
            </div>
        `;

        previewContainer.innerHTML = previewHTML;
    }

    showLoading(show, button) {
        if (!button) return;

        if (show) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando Pago...';
        } else {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-credit-card"></i> Pagar €3.99 y Recibir Pick';
        }
    }

    showSuccess(message) {
        if (window.showNotification) {
            window.showNotification(message, 'success');
        } else {
            alert(message);
        }
    }

    showError(message) {
        if (window.showNotification) {
            window.showNotification(message, 'error');
        } else {
            alert('Error: ' + message);
        }
    }
}

// Initialize single pick payment handler
let singlePickHandler = null;

document.addEventListener('DOMContentLoaded', function() {
    singlePickHandler = new SinglePickPaymentHandler();
});

// Global function for single pick payment
window.processSinglePickPayment = function() {
    if (singlePickHandler) {
        singlePickHandler.handleSinglePickPayment();
    }
};

// Export for global access
window.SinglePickPaymentHandler = SinglePickPaymentHandler; 