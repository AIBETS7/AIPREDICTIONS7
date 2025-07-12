// Stripe Payment Integration
let stripe;
let elements;
let card;
let paymentIntent;

// Initialize Stripe
async function initializeStripe() {
    try {
        // Get publishable key from your backend
        const response = await fetch('https://myfootballpredictions.onrender.com/api/create-payment-intent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: 1500, // €15.00 in cents
                currency: 'eur'
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        // Initialize Stripe
        stripe = Stripe(data.publishable_key);
        
        // Create card element
        elements = stripe.elements();
        card = elements.create('card', {
            style: {
                base: {
                    fontSize: '16px',
                    color: '#424770',
                    '::placeholder': {
                        color: '#aab7c4',
                    },
                },
                invalid: {
                    color: '#9e2146',
                },
            },
        });
        
        // Mount card element
        card.mount('#card-element');
        
        // Handle real-time validation errors
        card.addEventListener('change', function(event) {
            const displayError = document.getElementById('card-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = '';
            }
        });
        
    } catch (error) {
        console.error('Error initializing Stripe:', error);
        document.getElementById('card-errors').textContent = 'Error initializing payment system. Please try again.';
    }
}

// Handle form submission
async function handlePaymentSubmission(event) {
    event.preventDefault();
    
    const submitButton = document.getElementById('submit-button');
    const buttonText = document.getElementById('button-text');
    const spinner = document.getElementById('spinner');
    
    // Disable button and show spinner
    submitButton.disabled = true;
    buttonText.textContent = 'Processing...';
    spinner.classList.remove('hidden');
    
    try {
        // Get email
        const email = document.getElementById('email').value;
        
        // Create payment intent
        const response = await fetch('https://myfootballpredictions.onrender.com/api/create-payment-intent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: 1500,
                currency: 'eur',
                email: email
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error);
        }
        
        // Confirm payment
        const { error, paymentIntent } = await stripe.confirmCardPayment(data.client_secret, {
            payment_method: {
                card: card,
                billing_details: {
                    email: email,
                },
            }
        });
        
        if (error) {
            throw new Error(error.message);
        }
        
        // Payment successful
        showPaymentSuccess();
        
    } catch (error) {
        console.error('Payment error:', error);
        document.getElementById('card-errors').textContent = error.message;
        
        // Re-enable button
        submitButton.disabled = false;
        buttonText.textContent = 'Pagar €15/mes';
        spinner.classList.add('hidden');
    }
}

// Show payment success
function showPaymentSuccess() {
    const modal = document.getElementById('subscriptionModal');
    const modalContent = modal.querySelector('.modal-content');
    
    modalContent.innerHTML = `
        <div class="payment-success">
            <i class="fas fa-check-circle"></i>
            <h2>¡Pago Exitoso!</h2>
            <p>Tu suscripción ha sido activada. Recibirás nuestras predicciones premium diariamente.</p>
            <button onclick="closeSubscriptionModal()" class="btn-primary">Continuar</button>
        </div>
    `;
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Stripe when subscription modal is opened
    const subscriptionModal = document.getElementById('subscriptionModal');
    if (subscriptionModal) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'style') {
                    if (subscriptionModal.style.display === 'block') {
                        initializeStripe();
                    }
                }
            });
        });
        
        observer.observe(subscriptionModal, {
            attributes: true
        });
    }
    
    // Handle form submission
    const paymentForm = document.getElementById('payment-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', handlePaymentSubmission);
    }
}); 