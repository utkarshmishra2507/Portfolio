// Mobile Navigation
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');
const mobileMenu = document.querySelector('.mobile-menu');
const menuBtn = document.querySelector('.menu-btn');
const navMenu = document.querySelector('.nav-menu');
const data = await response.json();

// Handle hamburger menu
if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        // Prevent body scrolling when menu is open
        document.body.classList.toggle('no-scroll');
    });
    
    // Close menu when clicking on a link
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            mobileMenu.classList.remove('active');
            document.body.classList.remove('no-scroll');
        });
    });
}

// Handle menu button (legacy support)
if (menuBtn && navMenu) {
    menuBtn.addEventListener('click', () => {
        navMenu.classList.toggle('show');
        menuBtn.classList.toggle('active');
    });
}

// Smooth Scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        // Get the target element
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
            // Close mobile menu if open
            if (hamburger && mobileMenu) {
                hamburger.classList.remove('active');
                mobileMenu.classList.remove('active');
                document.body.classList.remove('no-scroll');
            }
            
            // Scroll to the target
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Form Handling
const contactForm = document.getElementById('contactForm') || document.getElementById('contact-form');
const submitBtn = contactForm ? contactForm.querySelector('.submit-btn') : null;

if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // If there's a submit button with loading animation
        if (submitBtn) {
            // Change button text and add loading state
            const originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            submitBtn.disabled = true;
            
            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                subject: document.getElementById('subject').value || 'Contact Form Submission',
                message: document.getElementById('message').value
            };

            try {
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    // Success feedback
                    submitBtn.innerHTML = '<i class="fas fa-check"></i> Message Sent!';
                    submitBtn.style.backgroundColor = '#10b981'; // Success green color
                    
                    // Show success message
                    const successMessage = document.createElement('div');
                    successMessage.className = 'form-success-message';
                    successMessage.innerHTML = `
                        <div class="success-icon"><i class="fas fa-check-circle"></i></div>
                        <h4>Thank you for your message!</h4>
                        <p>I'll get back to you as soon as possible.</p>
                    `;
                    
                    // Insert after form
                    contactForm.insertAdjacentElement('afterend', successMessage);
                    
                    // Reset form
                    contactForm.reset();
                    
                    // Hide form
                    contactForm.style.display = 'none';
                    
                    // Show form again after 5 seconds and reset button
                    setTimeout(() => {
                        contactForm.style.display = 'block';
                        successMessage.remove();
                        submitBtn.innerHTML = originalBtnText;
                        submitBtn.disabled = false;
                        submitBtn.style.backgroundColor = '';
                    }, 5000);
                } else {
                    throw new Error('Failed to send message');
                }
            } catch (error) {
                submitBtn.innerHTML = '<i class="fas fa-times"></i> Error!';
                submitBtn.style.backgroundColor = '#ef4444'; // Error red color
                
                alert('Error sending message. Please try again later.');
                console.error('Error:', error);
                
                // Reset button after 3 seconds
                setTimeout(() => {
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                    submitBtn.style.backgroundColor = '';
                }, 3000);
            }
        } else {
            // Simple form submission without fancy animations
            // Get form data
            const formData = new FormData(contactForm);
            const name = formData.get('name');
            const email = formData.get('email');
            const message = formData.get('message');
            
            // Validate form
            if (!name || !email || !message) {
                showAlert('Please fill in all fields', 'error');
                return;
            }
            
            try {
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ name, email, message }),
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    showAlert('Message sent successfully!', 'success');
                    contactForm.reset();
                } else {
                    showAlert(data.error || 'Something went wrong', 'error');
                }
            } catch (error) {
                showAlert('Failed to send message', 'error');
                console.error('Error:', error);
            }
        }
    });
}

// Show alert message
function showAlert(message, type) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert ${type}`;
    alertContainer.textContent = message;
    
    document.body.appendChild(alertContainer);
    
    // Remove alert after 3 seconds
    setTimeout(() => {
        alertContainer.classList.add('fade-out');
        setTimeout(() => {
            document.body.removeChild(alertContainer);
        }, 500);
    }, 3000);
}

// Resume Download
const downloadResume = document.getElementById('downloadResume');

downloadResume.addEventListener('click', async (e) => {
    e.preventDefault();
    
    // Add download animation
    downloadResume.classList.add('downloading');
    
    try {
        const response = await fetch('/api/download-resume');
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'resume.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Success feedback
            downloadResume.innerHTML = '<i class="fas fa-check"></i> Downloaded!';
            setTimeout(() => {
                downloadResume.innerHTML = '<i class="fas fa-download"></i> Download Resume';
                downloadResume.classList.remove('downloading');
            }, 2000);
        } else {
            throw new Error('Failed to download resume');
        }
    } catch (error) {
        downloadResume.innerHTML = '<i class="fas fa-times"></i> Download Failed';
        setTimeout(() => {
            downloadResume.innerHTML = '<i class="fas fa-download"></i> Download Resume';
            downloadResume.classList.remove('downloading');
        }, 2000);
        
        alert('Error downloading resume. Please try again later.');
        console.error('Error:', error);
    }
});

// Tab Switching
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Initialize tabs
function initializeTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    if (!tabBtns.length || !tabContents.length) {
        console.log("Tab buttons or contents not found - this is expected with the new structure");
        return;
    }
    
    console.log("Initializing tabs with", tabBtns.length, "buttons and", tabContents.length, "content divs");
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.getAttribute('data-target');
            console.log("Tab clicked:", target);
            
            // Remove active class from all buttons and contents
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            const targetContent = document.getElementById(target);
            if (targetContent) {
                targetContent.classList.add('active');
                console.log("Activated tab content:", target);
            } else {
                console.error("Could not find tab content with id:", target);
            }
        });
    });
}

// Initialize skill bars animation
const initializeSkillBars = () => {
    // This function is no longer needed since we're using skill tags instead of animated bars
    console.log("Skill bars animation disabled - using skill tags instead");
};

// Animate skill bars on scroll
const animateSkillBars = () => {
    // This function is no longer needed
    return;
};

// Scroll Animation
const sections = document.querySelectorAll('.section');
const projectItems = document.querySelectorAll('.portfolio-item');

const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            
            // No need to animate skills anymore
        }
    });
}, observerOptions);

sections.forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(30px)';
    section.style.transition = 'all 0.6s ease';
    observer.observe(section);
});

// Portfolio animations - Update for new project row layout
const projectRows = document.querySelectorAll('.project-row');

projectRows.forEach(row => {
    const image = row.querySelector('.project-image');
    const content = row.querySelector('.project-content');
    
    if (image && content) {
        // Add hover effects and animations
        row.addEventListener('mouseenter', () => {
            image.querySelector('img').style.transform = 'scale(1.05)';
            content.style.transform = 'translateY(-5px)';
        });
        
        row.addEventListener('mouseleave', () => {
            image.querySelector('img').style.transform = 'scale(1)';
            content.style.transform = 'translateY(0)';
        });
    }
});

// Update Portfolio Navigation for new project layout
function updatePortfolioNavigation() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const projectRows = document.querySelectorAll('.project-row');
    
    if (!filterButtons.length || !projectRows.length) {
        return;
    }
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Filter projects
            projectRows.forEach(row => {
                if (filter === 'all' || row.classList.contains(filter)) {
                    row.style.display = 'flex';
                    row.style.opacity = '1';
                    row.style.animation = 'fadeIn 0.5s ease-in-out forwards';
                } else {
                    row.style.display = 'none';
                    row.style.opacity = '0';
                }
            });
        });
    });
}

// Replace old portfolio mobile navigation with responsive handling
function handleResponsivePortfolio() {
    const width = window.innerWidth;
    const projectRows = document.querySelectorAll('.project-row');
    
    if (width <= 768) {
        // In mobile view, make sure all rows have column direction
        projectRows.forEach(row => {
            row.style.flexDirection = 'column';
        });
    } else {
        // In desktop view, restore the alternating layout
        projectRows.forEach((row, index) => {
            if (index % 2 === 0) { // Even rows (0-indexed)
                row.style.flexDirection = 'row';
            } else { // Odd rows (0-indexed)
                row.style.flexDirection = 'row-reverse';
            }
        });
    }
}

// Update the responsive check function
const checkResponsive = () => {
    const width = window.innerWidth;
    
    if (width <= 768) {
        document.body.classList.add('mobile');
    } else {
        document.body.classList.remove('mobile');
    }
    
    // Handle portfolio layout on resize
    handleResponsivePortfolio();
};

// Initialize page elements
document.addEventListener('DOMContentLoaded', function() {
    console.log("Document loaded, initializing components");
    
    // Initialize existing tabs if present (backward compatibility)
    initializeTabs();
    
    // No need to initialize skill bars anymore
    
    // No need for scroll event listener for skill animations
    
    // Portfolio navigation
    updatePortfolioNavigation();
    
    // Check for responsive layout
    checkResponsive();
    
    // Check URL parameters for form submission status
    checkFormSubmissionStatus();
    
    // Add observers for project rows to animate them when they come into view
    const projectRows = document.querySelectorAll('.project-row');
    
    if (projectRows.length) {
        const projectObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('in-view');
                    projectObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.25,
            rootMargin: '0px 0px -100px 0px'
        });
        
        projectRows.forEach(row => {
            row.style.opacity = '0';
            row.style.transform = 'translateY(30px)';
            projectObserver.observe(row);
        });
    }
});

// Check for form submission status in URL parameters
function checkFormSubmissionStatus() {
    const urlParams = new URLSearchParams(window.location.search);
    const message = urlParams.get('message');
    
    if (message === 'success') {
        showAlert('Message sent successfully! I will get back to you soon.', 'success');
        // Scroll to contact section
        setTimeout(() => {
            document.querySelector('#contact').scrollIntoView({
                behavior: 'smooth'
            });
        }, 500);
    } else if (message === 'error') {
        showAlert('There was a problem sending your message. Please try again or email me directly.', 'error');
        // Scroll to contact section
        setTimeout(() => {
            document.querySelector('#contact').scrollIntoView({
                behavior: 'smooth'
            });
        }, 500);
    }
}

// Handle window resize for responsiveness
window.addEventListener('resize', checkResponsive);

// Portfolio filtering
document.addEventListener('DOMContentLoaded', () => {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');
    
    // Add click event to filter buttons
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            button.classList.add('active');
            
            // Get filter value
            const filterValue = button.getAttribute('data-filter');
            
            // Filter portfolio items
            portfolioItems.forEach(item => {
                if (filterValue === 'all' || item.classList.contains(filterValue)) {
                    item.style.display = 'block';
                    // Add animation
                    item.classList.add('fade-in');
                    setTimeout(() => {
                        item.classList.remove('fade-in');
                    }, 500);
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
    
    // Initially set "All" as active
    document.querySelector('[data-filter="all"]').click();
});

// Add fade-in animation class
document.addEventListener('DOMContentLoaded', () => {
    // Add styles for the fade-in animation
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 0.5s ease forwards;
        }
    `;
    document.head.appendChild(style);
});

// Check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
} 