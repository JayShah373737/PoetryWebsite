// Modal functionality for poems
function setupPoemModals() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2 class="modal-title"></h2>
            <div class="full-poem-content"></div>
            <div class="poem-meta"></div>
        </div>
    `;
    document.body.appendChild(modal);

    // Close modal when clicking X
    modal.querySelector('.close-modal').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside content
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Add click handlers to all poem cards
    document.addEventListener('click', (e) => {
        const card = e.target.closest('.poem-card');
        if (card) {
            const title = card.querySelector('h3').textContent;
            const content = card.dataset.fullContent;
            const category = card.dataset.category;
            const date = card.dataset.date;
            
            modal.querySelector('.modal-title').textContent = title;
            modal.querySelector('.full-poem-content').textContent = content;
            modal.querySelector('.poem-meta').innerHTML = `
                <span>${category} • ${date}</span>
            `;
            modal.style.display = 'block';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    setupPoemModals();
    // Your existing code...
});

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu');
    const nav = document.querySelector('nav');
    
    mobileMenuBtn.addEventListener('click', function() {
        nav.classList.toggle('active');
    });
    
    // Smooth scrolling for navigation links
    document.querySelectorAll('nav a').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if(targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
                
                // Close mobile menu if open
                nav.classList.remove('active');
            }
        });
    });
    
    // Category selection
    const categoryCards = document.querySelectorAll('.category-card');
    const poemsContainer = document.getElementById('poems-list');
    
    categoryCards.forEach(card => {
        card.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            loadPoems(category);
            
            // Scroll to poems section
            document.getElementById('poems-container').scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Load poems function
    function loadPoems(category) {
        fetch(`/get_poems/${category}`)
            .then(response => response.text())
            .then(html => {
                poemsContainer.innerHTML = html;
                
                // Add animation to loaded poems
                const poemCards = document.querySelectorAll('.poem-card');
                poemCards.forEach((card, index) => {
                    card.style.animationDelay = `${index * 0.1}s`;
                    card.classList.add('animated', 'fadeInUp');
                });
            })
            .catch(error => {
                console.error('Error loading poems:', error);
                poemsContainer.innerHTML = '<p class="error">Failed to load poems. Please try again later.</p>';
            });
    }
    
    // Contact form submission
    const contactForm = document.getElementById('contact-form');
    if(contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Here you would typically send the form data to your server
            alert('Thank you for your message! I will get back to you soon.');
            this.reset();
        });
    }
    
    // Admin form submission
    const poemForm = document.getElementById('poem-form');
    if(poemForm) {
        poemForm.addEventListener('submit', function(e) {
            // Client-side validation can be added here
        });
    }
    
    // Header scroll effect
    window.addEventListener('scroll', function() {
        const header = document.querySelector('header');
        if(window.scrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    // Initialize particles.js if available
    if(typeof particlesJS !== 'undefined') {
        particlesJS.load('particles-js', 'js/particles-config.json', function() {
            console.log('Particles.js loaded');
        });
    }
});

// Add this to your main.js
document.addEventListener('DOMContentLoaded', function() {
    // Handle delete confirmation
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this poem?')) {
                e.preventDefault();
            }
        });
    });
});

// In main.js
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('Are you sure?')) {
            fetch(this.parentElement.action, { method: 'POST' })
                .then(response => window.location.reload())
        }
    });
});

// Modal functionality
function setupModals() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2 class="modal-title"></h2>
            <div class="full-poem-content"></div>
        </div>
    `;
    document.body.appendChild(modal);

    // Close modal when clicking X
    modal.querySelector('.close-modal').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal when clicking outside content
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Add click handlers to all read more buttons
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('read-more-btn')) {
            const card = e.target.closest('.poem-card');
            const title = card.querySelector('h3').textContent;
            const content = card.dataset.fullContent;
            
            modal.querySelector('.modal-title').textContent = title;
            modal.querySelector('.full-poem-content').textContent = content;
            modal.style.display = 'block';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize modals
    setupModals();
    
    // Your existing code...
    // Mobile menu, category selection, etc.
});

// In main.js - add to setupModals()
let currentPoemIndex = 0;
const allPoems = Array.from(document.querySelectorAll('.poem-card'));

// Add navigation buttons
const navHTML = `
    <button class="modal-nav prev">&larr;</button>
    <button class="modal-nav next">&rarr;</button>
`;
modal.querySelector('.modal-content').insertAdjacentHTML('beforeend', navHTML);

// Add navigation handlers
modal.querySelector('.next').addEventListener('click', showNextPoem);
modal.querySelector('.prev').addEventListener('click', showPrevPoem);

function showNextPoem() {
    currentPoemIndex = (currentPoemIndex + 1) % allPoems.length;
    updateModalContent();
}

function showPrevPoem() {
    currentPoemIndex = (currentPoemIndex - 1 + allPoems.length) % allPoems.length;
    updateModalContent();
}