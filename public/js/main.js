// Mobile Navigation Toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navMenu.classList.toggle('active');
});

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
    hamburger.classList.remove('active');
    navMenu.classList.remove('active');
}));

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Subscription Modal Functions
function openSubscriptionModal() {
    document.getElementById('subscriptionModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeSubscriptionModal() {
    document.getElementById('subscriptionModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('subscriptionModal');
    if (event.target === modal) {
        closeSubscriptionModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeSubscriptionModal();
    }
});

// Single Pick Modal Functions
function openSinglePickModal() {
    document.getElementById('singlePickModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeSinglePickModal() {
    document.getElementById('singlePickModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close single pick modal when clicking outside
window.addEventListener('click', (event) => {
    const modal = document.getElementById('singlePickModal');
    if (event.target === modal) {
        closeSinglePickModal();
    }
});

// Close single pick modal with Escape key
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeSinglePickModal();
    }
});

// Check if user has paid access
function checkPaymentAccess() {
    // Check localStorage for payment status
    const hasSubscription = localStorage.getItem('hasSubscription');
    const hasSinglePick = localStorage.getItem('hasSinglePick');
    const singlePickDate = localStorage.getItem('singlePickDate');
    
    const today = new Date().toDateString();
    
    // If user has subscription, show picks
    if (hasSubscription === 'true') {
        showDailyPicks();
        return;
    }
    
    // If user has single pick for today, show picks
    if (hasSinglePick === 'true' && singlePickDate === today) {
        showDailyPicks();
        return;
    }
    
    // Otherwise show paywall
    showPaywall();
}

// Show paywall
function showPaywall() {
    document.getElementById('dailyPicksPaywall').style.display = 'block';
    document.getElementById('dailyPicksContainer').style.display = 'none';
}

// Show daily picks
function showDailyPicks() {
    document.getElementById('dailyPicksPaywall').style.display = 'none';
    document.getElementById('dailyPicksContainer').style.display = 'block';
    loadDailyPicks();
}

// Handle single pick payment success
function handleSinglePickPaymentSuccess() {
    localStorage.setItem('hasSinglePick', 'true');
    localStorage.setItem('singlePickDate', new Date().toDateString());
    closeSinglePickModal();
    showDailyPicks();
    
    // Show success message
    alert('¡Pago exitoso! Ya puedes ver tu pronóstico premium.');
}

// Handle subscription payment success
function handleSubscriptionPaymentSuccess() {
    localStorage.setItem('hasSubscription', 'true');
    closeSubscriptionModal();
    showDailyPicks();
    
    // Show success message
    alert('¡Suscripción exitosa! Ya tienes acceso a todos los pronósticos.');
}

// Sample predictions data - Empty array to show no example matches
const samplePredictions = [];

// Load predictions into the grid
function loadPredictions() {
    const predictionsGrid = document.getElementById('predictionsGrid');
    if (!predictionsGrid) return;

    predictionsGrid.innerHTML = samplePredictions.map(prediction => `
        <div class="prediction-card">
            <div class="prediction-header">
                <h4>${prediction.match}</h4>
                <span class="confidence-badge">${prediction.confidence}</span>
            </div>
            <div class="prediction-details">
                <div class="prediction-main">
                    <span class="prediction-text">${prediction.prediction}</span>
                    <span class="odds">@ ${prediction.odds}</span>
                </div>
                <div class="tipster-name">${prediction.tipster}</div>
                <div class="reasoning">${prediction.reasoning}</div>
            </div>
        </div>
    `).join('');
}

// Update last update time
function updateLastUpdate() {
    const lastUpdateElement = document.getElementById('lastUpdate');
    if (lastUpdateElement) {
        const now = new Date();
        const minutes = Math.floor(Math.random() * 10) + 1;
        lastUpdateElement.textContent = `${minutes} min ago`;
    }
}

// Daily Picks Functions
async function loadDailyPicks() {
    const container = document.getElementById('dailyPicksContainer');
    const updateTime = document.getElementById('picksUpdateTime');
    const picksCount = document.getElementById('picksCount');
    
    if (!container) return;
    
    // Show loading state
    container.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Loading today's picks...</p>
        </div>
    `;
    
    try {
        // Use production API URL or fallback to localhost for development
        const apiUrl = window.location.hostname === 'localhost' 
            ? 'http://localhost:8000/api/daily-picks'
            : 'https://myfootballpredictions.onrender.com/api/daily-picks';
        
        const response = await fetch(apiUrl);
        
        if (!response.ok) {
            throw new Error('Failed to load picks');
        }
        
        const picks = await response.json();
        
        // Update timestamp
        if (updateTime) {
            updateTime.textContent = new Date().toLocaleString();
        }
        
        // Update count
        if (picksCount) {
            picksCount.textContent = picks.length;
        }
        
        if (picks.length === 0) {
            container.innerHTML = `
                <div class="no-picks">
                    <i class="fas fa-calendar-times"></i>
                    <h3>No picks available today</h3>
                    <p>Check back later for new predictions or try refreshing the page.</p>
                </div>
            `;
            return;
        }
        
        // Display picks
        container.innerHTML = picks.map(pick => `
            <div class="pick-card">
                <div class="pick-header">
                    <div class="pick-competition ${pick.competition === 'Women\'s Euro' ? 'womens-euro' : 'la-liga'}">
                        <i class="fas ${pick.competition === 'Women\'s Euro' ? 'fa-trophy' : 'fa-futbol'}"></i>
                        ${pick.competition}
                    </div>
                    <div class="pick-confidence">${pick.confidence}%</div>
                </div>
                
                <div class="pick-match">${pick.home_team} vs ${pick.away_team}</div>
                <div class="pick-time">
                    <i class="fas fa-clock"></i>
                    ${new Date(pick.match_time).toLocaleString()}
                </div>
                
                <div class="pick-details">
                    <div class="pick-detail">
                        <span class="pick-detail-label">Prediction:</span>
                        <span class="pick-detail-value">${pick.prediction}</span>
                    </div>
                    <div class="pick-detail">
                        <span class="pick-detail-label">Odds:</span>
                        <span class="pick-detail-value">@ ${pick.odds}</span>
                    </div>
                    <div class="pick-detail">
                        <span class="pick-detail-label">Stake:</span>
                        <span class="pick-detail-value">€${pick.stake}</span>
                    </div>
                </div>
                
                <div class="pick-reasoning">
                    <h4><i class="fas fa-lightbulb"></i> AI Reasoning</h4>
                    <p>${pick.reasoning}</p>
                </div>
                
                <div class="pick-footer">
                    <div class="pick-tipster">
                        <i class="fas fa-robot"></i>
                        Generated by AI Tipster
                    </div>
                    <div class="pick-id">#${pick.id}</div>
                </div>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading daily picks:', error);
        container.innerHTML = `
            <div class="no-picks">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Error loading picks</h3>
                <p>Unable to load today's predictions. Please try again later.</p>
                <button class="refresh-btn" onclick="loadDailyPicks()" style="margin-top: 1rem;">
                    <i class="fas fa-sync-alt"></i>
                    Try Again
                </button>
            </div>
        `;
    }
}

// Load daily picks when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Simulate form submission
            console.log('Contact form submitted:', data);
            
            // Show success message
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
        });
    }

    // Payment form submission
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Simulate payment processing
            console.log('Payment form submitted:', data);
            
            // Show success message
            alert('Thank you for subscribing! You will receive a confirmation email shortly.');
            closeSubscriptionModal();
            this.reset();
        });
    }

    // Newsletter form submission
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            console.log('Newsletter subscription:', email);
            
            alert('Thank you for subscribing to our newsletter!');
            this.reset();
        });
    }

    // Load initial data
    loadPredictions();
    updateLastUpdate();
    
    // Update time every 5 minutes
    setInterval(updateLastUpdate, 300000);
    
    // Check payment access and show appropriate content
    checkPaymentAccess();
    
    // Auto-refresh picks every 30 minutes (only if user has access)
    setInterval(() => {
        if (localStorage.getItem('hasSubscription') === 'true' || 
            (localStorage.getItem('hasSinglePick') === 'true' && 
             localStorage.getItem('singlePickDate') === new Date().toDateString())) {
            loadDailyPicks();
        }
    }, 1800000);
});

// Legal page functions
function showTerms() {
    alert('Terms of Service\n\n1. This service provides AI-powered football predictions for entertainment purposes only.\n2. Users are responsible for their own betting decisions.\n3. We do not guarantee any specific results.\n4. Subscription fees are non-refundable.\n5. Users must be 18+ to use this service.');
}

function showPrivacy() {
    alert('Privacy Policy\n\n1. We collect only necessary information for service provision.\n2. Your data is encrypted and securely stored.\n3. We do not share your information with third parties.\n4. You can request data deletion at any time.\n5. We use cookies to improve user experience.');
}

function showDisclaimer() {
    alert('Disclaimer\n\nThis website provides AI-powered football predictions for informational purposes only. We do not guarantee the accuracy of predictions, and users should not rely solely on this information for betting decisions. Please gamble responsibly and within your means.');
}

function showResponsible() {
    alert('Responsible Gambling\n\n1. Only gamble with money you can afford to lose.\n2. Set limits on time and money spent.\n3. Never chase losses.\n4. Take regular breaks.\n5. If you have a gambling problem, seek help from professional organizations.');
}

// Add some interactive animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate stats on scroll
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all stat cards
    document.querySelectorAll('.stat-card, .tipster-card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// Add CSS for prediction cards
const style = document.createElement('style');
style.textContent = `
    .prediction-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2563eb;
    }

    .prediction-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .prediction-header h4 {
        margin: 0;
        color: #1e293b;
        font-size: 1rem;
    }

    .confidence-badge {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .prediction-main {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .prediction-text {
        font-weight: 600;
        color: #2563eb;
    }

    .odds {
        background: #f1f5f9;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.9rem;
        color: #64748b;
    }

    .tipster-name {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 0.5rem;
    }

    .reasoning {
        font-size: 0.9rem;
        color: #475569;
        font-style: italic;
    }
`;
document.head.appendChild(style);
