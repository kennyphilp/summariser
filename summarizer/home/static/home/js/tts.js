// Enhanced TTS functionality with loading states and better UX
document.addEventListener('DOMContentLoaded', function() {
    // Loading overlay management
    function showLoading(button, text = 'Processing...') {
        button.disabled = true;
        button.setAttribute('data-original-text', button.textContent);
        button.innerHTML = `<span class="loading-spinner"></span> ${text}`;
        button.classList.add('loading');
    }

    function hideLoading(button) {
        button.disabled = false;
        button.innerHTML = button.getAttribute('data-original-text');
        button.classList.remove('loading');
    }

    // Form submission handling with loading states
    const forms = document.querySelectorAll('#summary-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                showLoading(submitBtn, 'Summarizing...');
                // Set timeout to prevent indefinite loading
                setTimeout(() => {
                    if (submitBtn.classList.contains('loading')) {
                        hideLoading(submitBtn);
                    }
                }, 30000);
            }
        });
    });

    // TTS functionality
    const speakBtn = document.getElementById('speak-btn');
    if (speakBtn) {
        speakBtn.addEventListener('click', function() {
            const summaryText = document.getElementById('summary-text');
            if (!summaryText) return;

            const text = summaryText.textContent.trim();
            if (!text) {
                alert('No text to speak');
                return;
            }

            showLoading(speakBtn, 'Speaking...');

            // Browser TTS fallback
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 0.9;
                utterance.pitch = 1;
                utterance.volume = 0.8;
                
                utterance.onend = () => hideLoading(speakBtn);
                utterance.onerror = () => {
                    hideLoading(speakBtn);
                    alert('Speech synthesis failed');
                };

                speechSynthesis.speak(utterance);
            } else {
                hideLoading(speakBtn);
                alert('Speech synthesis not supported in this browser');
            }
        });
    }

    // Blog creation functionality
    const blogBtn = document.getElementById('blog-btn');
    if (blogBtn) {
        blogBtn.addEventListener('click', function() {
            const summaryText = document.getElementById('summary-text');
            if (!summaryText) return;

            const text = summaryText.textContent.trim();
            if (!text) {
                alert('No summary text available to create blog');
                return;
            }

            showLoading(blogBtn, 'Creating Blog...');

            // Get the URL from the form if it exists, otherwise use empty string
            const urlInput = document.querySelector('input[name="url"]');
            const sourceUrl = urlInput ? urlInput.value : '';

            // Send AJAX request to create blog
            fetch('/create-blog/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    summary: text,
                    source_url: sourceUrl
                })
            })
            .then(response => response.json())
            .then(data => {
                hideLoading(blogBtn);
                if (data.success) {
                    // Open the generated blog in a new tab
                    window.open(data.blog_url, '_blank');
                } else {
                    alert('Error creating blog: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                hideLoading(blogBtn);
                console.error('Blog creation error:', error);
                alert('Error creating blog. Please try again.');
            });
        });
    }

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 400) + 'px';
        });
    });

    // Character counter for textarea
    textareas.forEach(textarea => {
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.textContent = '0 characters';
        textarea.parentNode.insertBefore(counter, textarea.nextSibling);

        textarea.addEventListener('input', function() {
            const count = this.value.length;
            counter.textContent = `${count.toLocaleString()} characters`;
            counter.style.color = count > 10000 ? '#dc2626' : '#6b7280';
        });
    });
});

// Copy to clipboard functionality
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const text = element.textContent;
    
    if (navigator.clipboard && window.isSecureContext) {
        // Modern clipboard API
        navigator.clipboard.writeText(text).then(() => {
            showCopyFeedback('Copied to clipboard!');
        }).catch(err => {
            fallbackCopyToClipboard(text);
        });
    } else {
        // Fallback for older browsers
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showCopyFeedback('Copied to clipboard!');
    } catch (err) {
        showCopyFeedback('Failed to copy text');
    }
    
    document.body.removeChild(textArea);
}

function showCopyFeedback(message) {
    // Create or update feedback element
    let feedback = document.getElementById('copy-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.id = 'copy-feedback';
        feedback.className = 'copy-feedback';
        document.body.appendChild(feedback);
    }
    
    feedback.textContent = message;
    feedback.classList.add('show');
    
    setTimeout(() => {
        feedback.classList.remove('show');
    }, 2000);
}