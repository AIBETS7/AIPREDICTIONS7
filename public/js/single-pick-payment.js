// Single Pick Payment with Stripe
let stripe;
let singlePickCardElement;
let singlePickCardErrors;

// Initialize Stripe for single pick payment
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Stripe (replace with your publishable key)
    stripe = Stripe('pk_test_your_publishable_key_here');
    
    // Create card element for single pick payment
    singlePickCardElement = stripe.elements().create('card', {
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
    
    // Mount the card element
    singlePickCardElement.mount('#single-pick-card-element');
    
    // Handle real-time validation errors
    singlePickCardElement.addEventListener('change', function(event) {
        if (event.error) {
            singlePickCardErrors.textContent = event.error.message;
        } else {
            singlePickCardErrors.textContent = '';
        }
    });
    
    // Handle single pick form submission
    const singlePickForm = document.getElementById('single-pick-form');
    if (singlePickForm) {
        singlePickForm.addEventListener('submit', handleSinglePickPayment);
    }
});

// Handle single pick payment
async function handleSinglePickPayment(event) {
    event.preventDefault();
    
    const submitButton = document.getElementById('single-pick-submit-button');
    const buttonText = document.getElementById('single-pick-button-text');
    const spinner = document.getElementById('single-pick-spinner');
    const email = document.getElementById('single-pick-email').value;
    
    // Disable button and show spinner
    submitButton.disabled = true;
    buttonText.textContent = 'Procesando...';
    spinner.classList.remove('hidden');
    
    try {
        // Create payment method
        const { paymentMethod, error } = await stripe.createPaymentMethod({
            type: 'card',
            card: singlePickCardElement,
            billing_details: {
                email: email,
            },
        });
        
        if (error) {
            throw new Error(error.message);
        }
        
        // Send payment to your backend
        const response = await fetch('/api/create-single-pick-payment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                payment_method_id: paymentMethod.id,
                email: email,
                amount: 399, // €3.99 in cents
            }),
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Payment successful
            handleSinglePickPaymentSuccess();
        } else {
            throw new Error(result.error || 'Payment failed');
        }
        
    } catch (error) {
        console.error('Payment error:', error);
        singlePickCardErrors.textContent = error.message;
        
        // Re-enable button
        submitButton.disabled = false;
        buttonText.textContent = 'Pagar €3.99';
        spinner.classList.add('hidden');
    }
}

// Simulate payment success for demo purposes
function simulateSinglePickPayment() {
    const submitButton = document.getElementById('single-pick-submit-button');
    const buttonText = document.getElementById('single-pick-button-text');
    const spinner = document.getElementById('single-pick-spinner');
    
    // Disable button and show spinner
    submitButton.disabled = true;
    buttonText.textContent = 'Procesando...';
    spinner.classList.remove('hidden');
    
    // Simulate payment processing
    setTimeout(() => {
        handleSinglePickPaymentSuccess();
    }, 2000);
}

// Override the form submission for demo
document.addEventListener('DOMContentLoaded', function() {
    const singlePickForm = document.getElementById('single-pick-form');
    if (singlePickForm) {
        singlePickForm.addEventListener('submit', function(e) {
            e.preventDefault();
            simulateSinglePickPayment();
        });
    }
}); 