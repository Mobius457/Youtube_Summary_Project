// YouTube Video Summarizer JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const urlForm = document.getElementById('url-form');
    const youtubeUrl = document.getElementById('youtube-url');
    const summarizeBtn = document.getElementById('summarize-btn');
    const spinner = document.getElementById('spinner');
    const resultsDiv = document.getElementById('results');
    const summaryText = document.getElementById('summary-text');
    const keywordsText = document.getElementById('keywords-text');

    // Form submission handler
    urlForm.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent page reload
        
        const url = youtubeUrl.value.trim();
        
        // Validate URL
        if (!url) {
            showError('Please enter a YouTube URL');
            return;
        }
        
        if (!isValidYouTubeUrl(url)) {
            showError('Please enter a valid YouTube URL');
            return;
        }

        // Reset UI and show loading state
        setLoadingState(true);
        hideResults();
        hideMessages();

        try {
            const response = await fetch('/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Something went wrong');
            }
            
            const data = await response.json();
            
            // Display results
            displayResults(data.summary, data.keywords);
            showSuccess('Video summarized successfully!');

        } catch (error) {
            console.error('Summarization error:', error);
            showError('Error: ' + error.message);
        } finally {
            // Re-enable UI
            setLoadingState(false);
        }
    });

    // URL input validation on blur
    youtubeUrl.addEventListener('blur', function() {
        const url = this.value.trim();
        if (url && !isValidYouTubeUrl(url)) {
            showError('Please enter a valid YouTube URL');
        } else {
            hideMessages();
        }
    });

    // Helper functions
    function isValidYouTubeUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/)|youtu\.be\/)[\w-]+/;
        return youtubeRegex.test(url);
    }

    function setLoadingState(isLoading) {
        summarizeBtn.disabled = isLoading;
        spinner.style.display = isLoading ? 'block' : 'none';
        summarizeBtn.textContent = isLoading ? 'Processing...' : 'Summarize';
    }

    function displayResults(summary, keywords) {
        summaryText.innerHTML = summary.replace(/\n/g, '<br>');
        keywordsText.textContent = keywords;
        resultsDiv.style.display = 'block';
        
        // Smooth scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    function hideResults() {
        resultsDiv.style.display = 'none';
    }

    function showError(message) {
        hideMessages();
        const errorDiv = createMessageDiv(message, 'error-message');
        insertMessageAfterForm(errorDiv);
    }

    function showSuccess(message) {
        hideMessages();
        const successDiv = createMessageDiv(message, 'success-message');
        insertMessageAfterForm(successDiv);
        
        // Auto-hide success message after 3 seconds
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 3000);
    }

    function createMessageDiv(message, className) {
        const div = document.createElement('div');
        div.className = className;
        div.textContent = message;
        div.setAttribute('data-message', 'true');
        return div;
    }

    function insertMessageAfterForm(messageDiv) {
        const container = document.querySelector('.container');
        const form = document.getElementById('url-form');
        container.insertBefore(messageDiv, form.nextSibling);
    }

    function hideMessages() {
        const messages = document.querySelectorAll('[data-message="true"]');
        messages.forEach(message => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        });
    }

    // Copy to clipboard functionality for results
    function addCopyButtons() {
        const summaryContent = document.querySelector('.summary-content');
        if (summaryContent && !summaryContent.querySelector('.copy-btn')) {
            const copyBtn = document.createElement('button');
            copyBtn.textContent = 'Copy Summary';
            copyBtn.className = 'copy-btn';
            copyBtn.style.marginTop = '10px';
            copyBtn.style.fontSize = '0.8rem';
            copyBtn.style.padding = '5px 10px';
            
            copyBtn.addEventListener('click', function() {
                const text = summaryText.textContent;
                navigator.clipboard.writeText(text).then(() => {
                    copyBtn.textContent = 'Copied!';
                    setTimeout(() => {
                        copyBtn.textContent = 'Copy Summary';
                    }, 2000);
                }).catch(() => {
                    showError('Failed to copy to clipboard');
                });
            });
            
            summaryContent.appendChild(copyBtn);
        }
    }

    // Add copy buttons when results are displayed
    const originalDisplayResults = displayResults;
    displayResults = function(summary, keywords) {
        originalDisplayResults(summary, keywords);
        setTimeout(addCopyButtons, 100);
    };
});
