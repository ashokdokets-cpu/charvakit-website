// ========== Navbar Scroll Effect ==========
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// ========== Smooth Scrolling for Anchor Links ==========
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href && href !== '#' && href.length > 1) {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// ========== Scroll to Top Button ==========
const scrollToTopBtn = document.createElement('button');
scrollToTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
scrollToTopBtn.className = 'scroll-to-top';
scrollToTopBtn.setAttribute('aria-label', 'Scroll to top');
document.body.appendChild(scrollToTopBtn);

window.addEventListener('scroll', function() {
    if (window.scrollY > 300) {
        scrollToTopBtn.classList.add('visible');
    } else {
        scrollToTopBtn.classList.remove('visible');
    }
});

scrollToTopBtn.addEventListener('click', function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// ========== Intersection Observer for Animations ==========
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            // Don't unobserve - keep elements visible after animation
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', function() {
    const elementsToAnimate = document.querySelectorAll('.feature-card, .service-card, .stat-card, .step-card, .ai-feature-card, .value-card, .feature-box');
    elementsToAnimate.forEach(element => {
        element.style.opacity = '1'; // Start visible
        element.style.transform = 'translateY(0)';
        observer.observe(element);
    });
});

// ========== Form Validation ==========
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.querySelector('form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic form validation
            const name = document.getElementById('name');
            const email = document.getElementById('email');
            const subject = document.getElementById('subject');
            const message = document.getElementById('message');
            
            let isValid = true;
            
            if (name && !name.value.trim()) {
                showError(name, 'Please enter your name');
                isValid = false;
            }
            
            if (email && !isValidEmail(email.value)) {
                showError(email, 'Please enter a valid email address');
                isValid = false;
            }
            
            if (subject && !subject.value.trim()) {
                showError(subject, 'Please enter a subject');
                isValid = false;
            }
            
            if (message && !message.value.trim()) {
                showError(message, 'Please enter your message');
                isValid = false;
            }
            
            if (isValid) {
                // Show success message
                showSuccess('Message sent successfully! We will get back to you soon.');
                contactForm.reset();
            }
        });
    }
});

function showError(input, message) {
    const formGroup = input.closest('.col-12, .col-md-6');
    input.classList.add('is-invalid');
    
    // Remove existing error message
    const existingError = formGroup.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    input.parentNode.appendChild(errorDiv);
    
    // Remove error on input
    input.addEventListener('input', function() {
        input.classList.remove('is-invalid');
        const error = input.parentNode.querySelector('.invalid-feedback');
        if (error) {
            error.remove();
        }
    }, { once: true });
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showSuccess(message) {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        <i class="bi bi-check-circle me-2"></i>' + message + '
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at top of form
    const form = document.querySelector('form');
    form.insertBefore(alertDiv, form.firstChild);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// ========== Active Nav Link ==========
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentPath || 
            (currentPath !== '/' && linkPath !== '/' && currentPath.startsWith(linkPath))) {
            link.classList.add('active');
        }
    });
});

// ========== Counter Animation for Stats ==========
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);
    
    function updateCounter() {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    }
    
    updateCounter();
}

// Animate stats when visible
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumbers = entry.target.querySelectorAll('.stat-number');
            statNumbers.forEach(stat => {
                const target = parseInt(stat.getAttribute('data-target'));
                if (target) {
                    animateCounter(stat, target);
                }
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

document.addEventListener('DOMContentLoaded', function() {
    const statsSection = document.querySelector('.stats-grid');
    if (statsSection) {
        statsObserver.observe(statsSection);
    }
});

// ========== Page Load Complete ==========
window.addEventListener('load', function() {
    // Remove any loading states
    document.body.classList.add('loaded');
    
    console.log('Charvakit - Digital Solutions');
    console.log('Website loaded successfully!');
});

// ========== Session A-2: signal that main.js is fully loaded ==========
// Base.html listens for this event to safely call checkLoginState
// (replaces a polling loop)
window.dispatchEvent(new Event('charvak:mainready'));

// ============================================================
// Session G6 — global 401/402 handler for credit-gated requests
// ============================================================
// When any fetch receives 401 or 402, dispatch a custom event so
// templates can react (show login prompt, paywall modal, etc.).
// Non-blocking: the original response is always returned.
(function () {
    var _originalFetch = window.fetch.bind(window);
    window.fetch = function (url, options) {
        options = options || {};
        return _originalFetch(url, options).then(function (res) {
            if (res.status === 401) {
                window.dispatchEvent(new CustomEvent('charvak:401', {
                    detail: { url: String(url) }
                }));
            } else if (res.status === 402) {
                // Clone to read body without consuming the original stream
                res.clone().json().then(function (d) {
                    window.dispatchEvent(new CustomEvent('charvak:402', { detail: d }));
                }).catch(function () {
                    window.dispatchEvent(new CustomEvent('charvak:402', { detail: {} }));
                });
            }
            return res;
        });
    };
})();
