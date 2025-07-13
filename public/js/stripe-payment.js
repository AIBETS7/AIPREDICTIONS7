// Stripe Payment Integration for AI Predictions 7
class StripePaymentHandler {
    constructor() {
        this.stripe = null;
        this.elements = null;
        this.cardElement = null;
        this.isProcessing = false;
        this.init();
    }

    async init() {
        try {
            // Get publishable key from backend
            const response = await fetch('https://myfootballpredictions.onrender.com/api/stripe-config');
            const config = await response.json();
            
            if (config.success && config.publishable_key) {
                this.stripe = Stripe(config.publishable_key);
                this.setupElements();
            } else {
                console.error('Failed to get Stripe configuration');
                this.showError('Error configuring payment system');
            }
        } catch (error) {
            console.error('Error initializing Stripe:', error);
            this.showError('Error initializing payment system');
        }
    }

    setupElements() {
        if (!this.stripe) return;

        this.elements = this.stripe.elements();
        
        // Create card element
        this.cardElement = this.elements.create('card', {
            style: {
                base: {
                    fontSize: '16px',
                    color: '#424770',
                    '::placeholder': {
                        color: '#aab7c4',
                    },
                    iconColor: '#6772e5',
                },
                invalid: {
                    iconColor: '#fa755a',
                    color: '#fa755a',
                },
            },
        });

        // Mount card element
        const cardContainer = document.querySelector('.card-element');
        if (cardContainer) {
            this.cardElement.mount(cardContainer);
        }
    }

    async processSubscription(email) {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        this.showLoading(true);

        try {
            // Create payment intent
            const response = await fetch('https://myfootballpredictions.onrender.com/api/create-subscription', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    price_id: 'price_1RkT8uLgWyziDhelTj4PyhNd' // Subscription price ID
                })
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.message || 'Error creating subscription');
            }

            // Confirm payment
            const { error, paymentIntent } = await this.stripe.confirmCardPayment(result.client_secret, {
                payment_method: {
                    card: this.cardElement,
                    billing_details: {
                        email: email,
                    },
                }
            });

            if (error) {
                throw new Error(error.message);
            }

            if (paymentIntent.status === 'succeeded') {
                this.showSuccess('¡Suscripción completada con éxito! Ya tienes acceso a todos los picks premium.');
                this.savePaymentStatus(email, 'subscription');
                closeSubscriptionModal();
            } else {
                throw new Error('Payment failed');
            }

        } catch (error) {
            console.error('Subscription error:', error);
            this.showError(error.message || 'Error processing subscription');
        } finally {
            this.isProcessing = false;
            this.showLoading(false);
        }
    }

    async processSinglePick(email) {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        this.showLoading(true);

        try {
            // Create payment intent for single pick
            const response = await fetch('https://myfootballpredictions.onrender.com/api/create-single-pick-payment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    price_id: 'price_1RkT8vLgWyziDhelUuw6X0pv' // Single pick price ID
                })
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.message || 'Error creating payment');
            }

            // Confirm payment
            const { error, paymentIntent } = await this.stripe.confirmCardPayment(result.client_secret, {
                payment_method: {
                    card: this.cardElement,
                    billing_details: {
                        email: email,
                    },
                }
            });

            if (error) {
                throw new Error(error.message);
            }

            if (paymentIntent.status === 'succeeded') {
                this.showSuccess('¡Pago completado! Tu pick único ha sido enviado a tu email.');
                this.savePaymentStatus(email, 'single_pick');
                closeSinglePickModal();
            } else {
                throw new Error('Payment failed');
            }

        } catch (error) {
            console.error('Single pick payment error:', error);
            this.showError(error.message || 'Error processing payment');
        } finally {
            this.isProcessing = false;
            this.showLoading(false);
        }
    }

    savePaymentStatus(email, type) {
        const paymentData = {
            email: email,
            type: type,
            timestamp: new Date().toISOString(),
            status: 'active'
        };

        // Save to localStorage
        const payments = JSON.parse(localStorage.getItem('payments') || '[]');
        payments.push(paymentData);
        localStorage.setItem('payments', JSON.stringify(payments));

        // Update UI
        this.updatePaymentUI();
    }

    checkPaymentStatus(email) {
        const payments = JSON.parse(localStorage.getItem('payments') || '[]');
        const userPayments = payments.filter(p => p.email === email);
        
        if (userPayments.length === 0) return null;

        // Check for active subscription
        const subscription = userPayments.find(p => p.type === 'subscription' && p.status === 'active');
        if (subscription) {
            return { type: 'subscription', active: true };
        }

        // Check for recent single pick
        const singlePick = userPayments.find(p => p.type === 'single_pick' && p.status === 'active');
        if (singlePick) {
            const pickDate = new Date(singlePick.timestamp);
            const today = new Date();
            const diffTime = today - pickDate;
            const diffDays = diffTime / (1000 * 60 * 60 * 24);
            
            if (diffDays <= 1) { // Pick is valid for 24 hours
                return { type: 'single_pick', active: true };
            }
        }

        return { type: null, active: false };
    }

    updatePaymentUI() {
        // Update paywall visibility based on payment status
        const paywall = document.querySelector('.picks-paywall');
        const picksContainer = document.querySelector('.picks-container');
        
        if (paywall && picksContainer) {
            // Check if user has active payment
            const userEmail = localStorage.getItem('userEmail');
            if (userEmail) {
                const paymentStatus = this.checkPaymentStatus(userEmail);
                if (paymentStatus && paymentStatus.active) {
                    paywall.style.display = 'none';
                    picksContainer.style.display = 'block';
                } else {
                    paywall.style.display = 'block';
                    picksContainer.style.display = 'none';
                }
            }
        }
    }

    showLoading(show) {
        const submitButtons = document.querySelectorAll('.subscribe-btn, .single-pick-btn');
        submitButtons.forEach(btn => {
            if (show) {
                btn.disabled = true;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            } else {
                btn.disabled = false;
                btn.innerHTML = btn.dataset.originalText || 'Suscribirse';
            }
        });
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

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    validateCard() {
        if (!this.cardElement) return false;
        
        const { error } = this.cardElement._component;
        return !error;
    }
}

// Initialize Stripe payment handler
let stripeHandler = null;

document.addEventListener('DOMContentLoaded', function() {
    stripeHandler = new StripePaymentHandler();
});

// Global functions for payment processing
window.processSubscription = function() {
    const emailInput = document.querySelector('#subscription-email');
    if (!emailInput || !stripeHandler) return;

    const email = emailInput.value.trim();
    
    if (!stripeHandler.validateEmail(email)) {
        stripeHandler.showError('Por favor, introduce un email válido');
        return;
    }

    if (!stripeHandler.validateCard()) {
        stripeHandler.showError('Por favor, completa los datos de la tarjeta correctamente');
        return;
    }

    stripeHandler.processSubscription(email);
};

window.processSinglePick = function() {
    const emailInput = document.querySelector('#single-pick-email');
    if (!emailInput || !stripeHandler) return;

    const email = emailInput.value.trim();
    
    if (!stripeHandler.validateEmail(email)) {
        stripeHandler.showError('Por favor, introduce un email válido');
        return;
    }

    if (!stripeHandler.validateCard()) {
        stripeHandler.showError('Por favor, completa los datos de la tarjeta correctamente');
        return;
    }

    stripeHandler.processSinglePick(email);
};

// Form submission handlers
document.addEventListener('DOMContentLoaded', function() {
    // Subscription form
    const subscriptionForm = document.querySelector('#subscription-form');
    if (subscriptionForm) {
        subscriptionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processSubscription();
        });
    }

    // Single pick form
    const singlePickForm = document.querySelector('#single-pick-form');
    if (singlePickForm) {
        singlePickForm.addEventListener('submit', function(e) {
            e.preventDefault();
            processSinglePick();
        });
    }

    // Store original button text
    const buttons = document.querySelectorAll('.subscribe-btn, .single-pick-btn');
    buttons.forEach(btn => {
        btn.dataset.originalText = btn.innerHTML;
    });
});

// Payment status check on page load
document.addEventListener('DOMContentLoaded', function() {
    if (stripeHandler) {
        stripeHandler.updatePaymentUI();
    }
});

// Export for global access
window.StripePaymentHandler = StripePaymentHandler; 