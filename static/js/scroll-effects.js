// Scroll animation effects
document.addEventListener('DOMContentLoaded', function() {
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animated-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if(elementPosition < windowHeight - 100) {
                element.classList.add('animated', 'fadeInUp');
            }
        });
    };
    
    // Initial check
    animateOnScroll();
    
    // Check on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Add class to elements that should animate on scroll
    document.querySelectorAll('.category-card, .poem-card, .about-content, #contact-form').forEach(element => {
        element.classList.add('animated-on-scroll');
    });
});