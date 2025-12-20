// ======== CONFIGURATION ========
const API_BASE_URL = 'https://llm-vhhs.onrender.com';
const API_ENDPOINT = `${API_BASE_URL}/predict`;
const HEALTH_ENDPOINT = `${API_BASE_URL}/health`;

// DOM Elements
const textInput = document.getElementById('text-input');
const charCount = document.getElementById('char-count');
const classifyBtn = document.getElementById('classify-btn');
const exampleBtn = document.getElementById('example-btn');
const resultsSection = document.getElementById('results-section');
const predictedClass = document.getElementById('predicted-class');
const confidenceScore = document.getElementById('confidence-score');
const confidenceBar = document.getElementById('confidence-bar');
const newAnalysisBtn = document.getElementById('new-analysis-btn');
const loadingModal = new bootstrap.Modal(document.getElementById('loading-modal'));
const apiStatus = document.getElementById('api-status');

// Example texts for demonstration
const exampleTexts = [
    'Thẻ của tôi bị lỗi không thể thanh toán được',
    'Tôi không thể đăng nhập vào ứng dụng',
    'Giao dịch chuyển tiền thất bại',
    'Tôi muốn vay tiền mua nhà',
    'Tài khoản của tôi có dấu hiệu bị xâm nhập',
    'Làm sao để đổi mật khẩu?'
];

// ======== INITIALIZATION ========
document.addEventListener('DOMContentLoaded', function() {
    // Check API status on page load
    checkApiStatus();
    
    // Set up event listeners
    setupEventListeners();
    
    // Update character count
    updateCharCount();
});

// ======== EVENT LISTENERS ========
function setupEventListeners() {
    // Form submission
    document.getElementById('classification-form').addEventListener('submit', handleFormSubmit);
    
    // Text input changes
    textInput.addEventListener('input', updateCharCount);
    
    // Example button
    exampleBtn.addEventListener('click', showExampleText);
    
    // New analysis button
    newAnalysisBtn.addEventListener('click', resetForm);
}

// ======== API FUNCTIONS ========
async function checkApiStatus() {
    try {
        const response = await fetch(HEALTH_ENDPOINT);
        const data = await response.json();
        
        if (response.ok && data.status === 'ok') {
            apiStatus.textContent = 'Online';
            apiStatus.className = 'badge bg-success';
        } else {
            apiStatus.textContent = 'Offline';
            apiStatus.className = 'badge bg-danger';
        }
    } catch (error) {
        apiStatus.textContent = 'Offline';
        apiStatus.className = 'badge bg-danger';
        console.error('API Health Check Error:', error);
    }
}

async function classifyText(text) {
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Classification Error:', error);
        showError('Không thể phân loại văn bản. Vui lòng thử lại sau.');
        throw error;
    }
}

// ======== UI FUNCTIONS ========
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const text = textInput.value.trim();
    
    // Validate input
    if (text.length < 10) {
        showError('Vui lòng nhập ít nhất 10 ký tự.');
        return;
    }
    
    // Show loading modal
    loadingModal.show();
    
    try {
        // Call API
        const result = await classifyText(text);
        
        // Hide loading modal
        loadingModal.hide();
        
        // Show results
        displayResults(result);
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        // Hide loading modal
        loadingModal.hide();
    }
}

function updateCharCount() {
    const count = textInput.value.length;
    charCount.textContent = count;
    
    // Update char count color based on length
    if (count < 10) {
        charCount.style.color = 'var(--danger-color)';
    } else {
        charCount.style.color = 'var(--success-color)';
    }
}

function showExampleText() {
    // Get random example
    const randomIndex = Math.floor(Math.random() * exampleTexts.length);
    const exampleText = exampleTexts[randomIndex];
    
    // Set the text
    textInput.value = exampleText;
    updateCharCount();
    
    // Focus on input
    textInput.focus();
}

function displayResults(result) {
    // Set the results
    predictedClass.textContent = result.label || 'Unknown';
    confidenceScore.textContent = `${(result.score * 100).toFixed(1)}%`;
    confidenceBar.style.width = `${(result.score * 100)}%`;
    
    // Show results section with animation
    resultsSection.classList.remove('d-none');
    resultsSection.classList.add('fade-in');
    
    // Set color based on confidence
    if (result.score >= 0.8) {
        confidenceBar.className = 'progress-bar bg-success';
    } else if (result.score >= 0.6) {
        confidenceBar.className = 'progress-bar bg-warning';
    } else {
        confidenceBar.className = 'progress-bar bg-danger';
    }
}

function resetForm() {
    // Clear input
    textInput.value = '';
    updateCharCount();
    
    // Hide results section
    resultsSection.classList.add('d-none');
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Focus on input
    textInput.focus();
}

function showError(message) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-danger border-0';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Show toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast when hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// ======== CREATE TOAST CONTAINER STYLES ========
const style = document.createElement('style');
style.textContent = `
    .toast-container {
        z-index: 1055;
    }
    
    .toast {
        opacity: 0.9;
    }
`;
document.head.appendChild(style);

// ======== ERROR HANDLING ========
window.addEventListener('error', (event) => {
    console.error('JavaScript Error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
});

// ======== PERIODIC API STATUS CHECK ========
setInterval(checkApiStatus, 30000); // Check every 30 seconds
