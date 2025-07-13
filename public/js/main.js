// Main JavaScript for AI Predictions 7
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeNavigation();
    initializeSmoothScrolling();
    initializeAnimations();
    initializeContactForm();
    initializeNewsletterForm();
    loadDailyPicks();
    updateLastUpdateTime();
    
    // Update time every minute
    setInterval(updateLastUpdateTime, 60000);
});

// Navigation functionality
function initializeNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    
    // Mobile menu toggle
    hamburger.addEventListener('click', function() {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
    
    // Close mobile menu when clicking on a link
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        });
    });
    
    // Active navigation highlighting
    window.addEventListener('scroll', function() {
        const sections = document.querySelectorAll('section[id]');
        const scrollPos = window.scrollY + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            const navLink = document.querySelector(`.nav-link[href="#${sectionId}"]`);
            
            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                navLinks.forEach(link => link.classList.remove('active'));
                if (navLink) navLink.classList.add('active');
            }
        });
    });
}

// Smooth scrolling for navigation links
function initializeSmoothScrolling() {
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                const offsetTop = targetSection.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Scroll to section function
function scrollToSection(sectionId) {
    const section = document.querySelector(`#${sectionId}`);
    if (section) {
        const offsetTop = section.offsetTop - 80;
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    }
}

// Initialize animations
function initializeAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.stat-card, .tipster-card, .pick-card');
    animateElements.forEach(el => observer.observe(el));
}

// Contact form functionality
function initializeContactForm() {
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('.submit-btn');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
            submitBtn.disabled = true;
            
            // Simulate form submission (replace with actual API call)
            setTimeout(() => {
                showNotification('¡Mensaje enviado con éxito! Te responderemos pronto.', 'success');
                this.reset();
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
}

// Newsletter form functionality
function initializeNewsletterForm() {
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const email = this.querySelector('input[type="email"]').value;
            const submitBtn = this.querySelector('button');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            submitBtn.disabled = true;
            
            // Simulate subscription (replace with actual API call)
            setTimeout(() => {
                showNotification('¡Te has suscrito exitosamente! Recibirás nuestras mejores predicciones.', 'success');
                this.reset();
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
}

// Load daily picks
function loadDailyPicks() {
    const picksContainer = document.getElementById('picksContainer');
    const picksCount = document.getElementById('picksCount');
    
    if (!picksContainer) return;
    
    // Show loading state
    picksContainer.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Cargando pronósticos...</p>
        </div>
    `;
    
    // Fetch picks from API
    fetch('https://myfootballpredictions.onrender.com/api/daily-picks')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.picks && data.picks.length > 0) {
                displayPicks(data.picks);
                if (picksCount) picksCount.textContent = data.picks.length;
            } else {
                showNoPicks();
                if (picksCount) picksCount.textContent = '0';
            }
        })
        .catch(error => {
            console.error('Error loading picks:', error);
            showNoPicks();
            if (picksCount) picksCount.textContent = '0';
        });
}

// Display picks
function displayPicks(picks) {
    const picksContainer = document.getElementById('picksContainer');
    
    const picksHTML = picks.map(pick => `
        <div class="pick-card fade-in">
            <div class="pick-header">
                <div class="pick-competition ${pick.competition?.toLowerCase().includes('euro') ? 'womens-euro' : 'la-liga'}">
                    ${pick.competition || 'Liga Española'}
                </div>
                <div class="pick-confidence">
                    ${Math.round(pick.confidence * 100)}% Confianza
                </div>
            </div>
            
            <div class="pick-match">
                ${pick.home_team} vs ${pick.away_team}
            </div>
            
            <div class="pick-time">
                <i class="fas fa-clock"></i>
                ${formatMatchTime(pick.match_time)}
            </div>
            
            <div class="pick-details">
                <div class="pick-detail">
                    <div class="pick-detail-label">Predicción</div>
                    <div class="pick-detail-value">${pick.prediction}</div>
                </div>
                <div class="pick-detail">
                    <div class="pick-detail-label">Tipo</div>
                    <div class="pick-detail-value">${formatPredictionType(pick.prediction_type)}</div>
                </div>
                <div class="pick-detail">
                    <div class="pick-detail-label">Cuota</div>
                    <div class="pick-detail-value">${pick.odds ? pick.odds.toFixed(2) : 'N/A'}</div>
                </div>
            </div>
            
            ${pick.reasoning ? `
                <div class="pick-reasoning">
                    <h4><i class="fas fa-lightbulb"></i> Análisis</h4>
                    <p>${pick.reasoning}</p>
                </div>
            ` : ''}
            
            <div class="pick-footer">
                <div class="pick-tipster">
                    <i class="fas fa-user-tie"></i>
                    ${pick.tipster || 'AI Predictions 7'}
                </div>
                ${pick.result_status ? `
                    <div class="pick-result ${pick.result_status}">
                        <i class="fas fa-${pick.result_status === 'correct' ? 'check-circle' : 'times-circle'}"></i>
                        ${pick.result_status === 'correct' ? 'Correcto' : 'Incorrecto'}
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
    
    picksContainer.innerHTML = picksHTML;
}

// Show no picks message
function showNoPicks() {
    const picksContainer = document.getElementById('picksContainer');
    
    picksContainer.innerHTML = `
        <div class="no-picks">
            <i class="fas fa-calendar-times"></i>
            <h3>No hay picks disponibles</h3>
            <p>No hay pronósticos disponibles para hoy. Vuelve más tarde o suscríbete para recibir picks premium.</p>
            <button class="cta-btn primary" onclick="openSubscriptionModal()">
                <i class="fas fa-crown"></i>
                Suscribirse para Picks Premium
            </button>
        </div>
    `;
}

// Format match time
function formatMatchTime(timeString) {
    if (!timeString) return 'Hora por confirmar';
    
    try {
        const date = new Date(timeString);
        return date.toLocaleString('es-ES', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return timeString;
    }
}

// Format prediction type
function formatPredictionType(type) {
    const types = {
        'match_winner': 'Ganador del Partido',
        'over_under': 'Más/Menos Goles',
        'both_teams_score': 'Ambos Marcan',
        'correct_score': 'Resultado Exacto',
        'first_goalscorer': 'Primer Goleador',
        'half_time_result': 'Resultado al Descanso',
        'double_chance': 'Doble Oportunidad'
    };
    
    return types[type] || type;
}

// Update last update time
function updateLastUpdateTime() {
    const lastUpdate = document.getElementById('lastUpdate');
    const lastPicksUpdate = document.getElementById('lastPicksUpdate');
    
    if (lastUpdate) {
        lastUpdate.textContent = 'hace 2 min';
    }
    
    if (lastPicksUpdate) {
        lastPicksUpdate.textContent = 'hace 5 min';
    }
}

// Modal functions
function openSubscriptionModal() {
    const modal = document.getElementById('subscriptionModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeSubscriptionModal() {
    const modal = document.getElementById('subscriptionModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function openSinglePickModal() {
    const modal = document.getElementById('singlePickModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeSinglePickModal() {
    const modal = document.getElementById('singlePickModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Process subscription
function processSubscription() {
    // This will be handled by the Stripe integration
    console.log('Processing subscription...');
    // For now, show a notification
    showNotification('Redirigiendo a Stripe para completar la suscripción...', 'info');
}

// Process single pick
function processSinglePick() {
    openSinglePickModal();
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        z-index: 3000;
        animation: slideInRight 0.3s ease;
        max-width: 400px;
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Close modals when clicking outside
window.addEventListener('click', function(event) {
    const subscriptionModal = document.getElementById('subscriptionModal');
    const singlePickModal = document.getElementById('singlePickModal');
    
    if (event.target === subscriptionModal) {
        closeSubscriptionModal();
    }
    
    if (event.target === singlePickModal) {
        closeSinglePickModal();
    }
});

// Close modals with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeSubscriptionModal();
        closeSinglePickModal();
    }
});

// Add notification styles
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .notification-content button {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0;
        margin-left: auto;
    }
    
    .notification-content i:first-child {
        font-size: 1.2rem;
    }
`;
document.head.appendChild(notificationStyles);

// Telegram link handler
function openTelegram(username) {
    try {
        // Handle group links (starting with +)
        if (username.startsWith('+')) {
            const telegramUrl = `https://t.me/${username}`;
            
            // Check if we're on mobile
            if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                // For groups, we need to use the invite link directly
                window.open(telegramUrl, '_blank');
            } else {
                // Desktop: open in new tab
                window.open(telegramUrl, '_blank');
            }
        } else {
            // Handle user/channel links
            const telegramUrl = `https://t.me/${username}`;
            
            // Check if we're on mobile
            if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
                // Try to open Telegram app first
                window.location.href = `tg://resolve?domain=${username}`;
                
                // Fallback to web after a short delay
                setTimeout(() => {
                    window.open(telegramUrl, '_blank');
                }, 1000);
            } else {
                // Desktop: open in new tab
                window.open(telegramUrl, '_blank');
            }
        }
    } catch (error) {
        console.error('Error opening Telegram:', error);
        // Fallback: show message to user
        alert('Para unirte a nuestro grupo de Telegram, usa el enlace: https://t.me/+101AkcLj0SYxOTZk');
    }
}
