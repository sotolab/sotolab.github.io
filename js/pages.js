// ============================================
// SotoLab 2026 - Pages JavaScript
// 서브 페이지 전용 스크립트
// ============================================

// Project Filtering
const filterTabs = document.getElementById('filterTabs');
const projectsGrid = document.getElementById('projectsGrid');

if (filterTabs && projectsGrid) {
    const filterButtons = filterTabs.querySelectorAll('.filter-btn');
    const projectCards = projectsGrid.querySelectorAll('.project-card');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Update active button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Get filter value
            const filter = button.getAttribute('data-filter');
            
            // Filter projects
            projectCards.forEach(card => {
                const category = card.getAttribute('data-category');
                
                if (filter === 'all' || category === filter) {
                    card.style.display = 'block';
                    setTimeout(() => {
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, 10);
                } else {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
}

// SOTE Timeline Animation
const soteSteps = document.querySelectorAll('.sote-step');

const soteObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateX(0)';
            }, index * 200);
            soteObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.2
});

soteSteps.forEach((step, index) => {
    step.style.opacity = '0';
    step.style.transform = index % 2 === 0 ? 'translateX(-50px)' : 'translateX(50px)';
    step.style.transition = 'all 0.6s ease';
    soteObserver.observe(step);
});

// Book Cards Animation
const bookCards = document.querySelectorAll('.book-card, .book-card-small');

const bookObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'scale(1)';
            bookObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1
});

bookCards.forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'scale(0.9)';
    card.style.transition = 'all 0.5s ease';
    bookObserver.observe(card);
});

// Review Cards Animation
const reviewCards = document.querySelectorAll('.review-card');

const reviewObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }, index * 100);
            reviewObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1
});

reviewCards.forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'all 0.6s ease';
    reviewObserver.observe(card);
});

// Stats Counter Animation (for reviews page)
const statsSection = document.querySelector('.stats-section');
if (statsSection) {
    const statNumbers = statsSection.querySelectorAll('.stat-number[data-target]');
    
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                statNumbers.forEach(num => {
                    if (!num.classList.contains('animated')) {
                        num.classList.add('animated');
                        animateCounter(num);
                    }
                });
                statsObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.5
    });
    
    statsObserver.observe(statsSection);
}

function animateCounter(element) {
    const target = parseInt(element.getAttribute('data-target'));
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;
    
    const updateCounter = () => {
        current += increment;
        if (current < target) {
            element.textContent = Math.floor(current);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target;
        }
    };
    
    updateCounter();
}

// Course Highlights Toggle
const courseHighlights = document.querySelectorAll('.course-highlights ul li');
courseHighlights.forEach((item, index) => {
    item.style.opacity = '0';
    item.style.transform = 'translateX(-20px)';
    setTimeout(() => {
        item.style.transition = 'all 0.5s ease';
        item.style.opacity = '1';
        item.style.transform = 'translateX(0)';
    }, index * 100);
});

// Contact Method Cards Hover Effect
const contactMethods = document.querySelectorAll('.contact-method');
contactMethods.forEach(method => {
    method.addEventListener('mouseenter', () => {
        method.style.transform = 'translateX(10px)';
    });
    method.addEventListener('mouseleave', () => {
        method.style.transform = 'translateX(0)';
    });
});

// Form Validation
const forms = document.querySelectorAll('form');
forms.forEach(form => {
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(input => {
        input.addEventListener('blur', () => {
            if (!input.value) {
                input.style.borderColor = '#FF6B6B';
            } else {
                input.style.borderColor = '';
            }
        });
        
        input.addEventListener('input', () => {
            if (input.value) {
                input.style.borderColor = '#2E5BFF';
            }
        });
    });
});

// Lazy Loading for YouTube iframes
const videoObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const iframe = entry.target;
            if (iframe.dataset.src) {
                iframe.src = iframe.dataset.src;
                iframe.removeAttribute('data-src');
            }
            videoObserver.unobserve(iframe);
        }
    });
}, {
    rootMargin: '50px'
});

document.querySelectorAll('iframe[data-src]').forEach(iframe => {
    videoObserver.observe(iframe);
});

// Smooth reveal on scroll
const revealElements = document.querySelectorAll('.service-card, .impact-card, .key-card, .core-card, .benefit-item');

const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
            revealObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
});

revealElements.forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(30px)';
    element.style.transition = 'all 0.6s ease';
    revealObserver.observe(element);
});

console.log('📄 Pages script loaded successfully!');