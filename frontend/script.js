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
const apiStatus = document.getElementById('api-status');

// Không khởi tạo Modal toàn cục để tránh lỗi mất tham chiếu
// const loadingModal = ... (Đã xóa dòng này)

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
    
    // Debug info
    console.log('Frontend loaded successfully');
    console.log('API URL:', API_BASE_URL);
});

// ======== EVENT LISTENERS ========
function setupEventListeners() {
    // Form submission
    const form = document.getElementById('classification-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    } else {
        console.error('Classification form not found!');
    }
    
    // Text input changes
    if (textInput) {
        textInput.addEventListener('input', updateCharCount);
    }
    
    // Example button
    if (exampleBtn) {
        exampleBtn.addEventListener('click', showExampleText);
    }
    
    // New analysis button
    if (newAnalysisBtn) {
        newAnalysisBtn.addEventListener('click', resetForm);
    }
}

// ======== API FUNCTIONS ========
async function checkApiStatus() {
    try {
        console.log('Checking API health at:', HEALTH_ENDPOINT);
        const response = await fetch(HEALTH_ENDPOINT);
        const data = await response.json();
        
        if (response.ok && data.status === 'ok') {
            if (apiStatus) {
                apiStatus.textContent = 'Online';
                apiStatus.className = 'badge bg-success';
            }
        } else {
            if (apiStatus) {
                apiStatus.textContent = 'Offline';
                apiStatus.className = 'badge bg-danger';
            }
        }
    } catch (error) {
        console.error('API Health Check Error:', error);
        if (apiStatus) {
            apiStatus.textContent = 'Offline';
            apiStatus.className = 'badge bg-danger';
        }
    }
}

async function classifyText(text) {
    try {
        console.log('Sending classification request to:', API_ENDPOINT);
        
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: text })
        });
        
        console.log('API response status:', response.status);
        
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
    
    if (!textInput) return;
    
    const text = textInput.value.trim();
    
    // Validate input
    if (text.length < 10) {
        showError('Vui lòng nhập ít nhất 10 ký tự.');
        return;
    }
    
    // Disable button to prevent multiple submissions
    if (classifyBtn) {
        classifyBtn.disabled = true;
        classifyBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Đang xử lý...';
    }
    
    // Lấy Modal instance theo cách an toàn nhất
    const modalEl = document.getElementById('loading-modal');
    const loadingModal = bootstrap.Modal.getOrCreateInstance(modalEl);
    
    // Hiển thị modal
    loadingModal.show();
    
    try {
        // Call API
        const result = await classifyText(text);
        
        // --- QUAN TRỌNG: Thêm delay nhỏ để đảm bảo animation mượt mà và tránh lỗi kẹt modal ---
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Ẩn modal
        loadingModal.hide();
        
        // Show results
        displayResults(result);
        
        // Scroll to results
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        // Ẩn modal nếu có lỗi
        loadingModal.hide();
        console.error('Form submission error:', error);
    } finally {
        // Re-enable button
        if (classifyBtn) {
            classifyBtn.disabled = false;
            classifyBtn.innerHTML = '<i class="fas fa-search me-2"></i>Phân loại';
        }

        // --- FIX BỔ SUNG: Dọn dẹp backdrop nếu bị kẹt ---
        // Đôi khi Bootstrap không xóa backdrop kịp thời, ta xóa thủ công để chắc chắn
        setTimeout(() => {
            const backdrops = document.querySelectorAll('.modal-backdrop');
            if (backdrops.length > 0 && !document.body.classList.contains('modal-open')) {
                backdrops.forEach(bd => bd.remove());
            }
        }, 500);
    }
}

function updateCharCount() {
    if (!textInput || !charCount) return;
    
    const count = textInput.value.length;
    charCount.textContent = count;
    
    if (count < 10) {
        charCount.style.color = 'var(--danger-color)';
    } else {
        charCount.style.color = 'var(--success-color)';
    }
}

function showExampleText() {
    if (!textInput) return;
    
    const randomIndex = Math.floor(Math.random() * exampleTexts.length);
    const exampleText = exampleTexts[randomIndex];
    
    textInput.value = exampleText;
    updateCharCount();
    textInput.focus();
}

function displayResults(result) {
    if (!predictedClass || !confidenceScore || !confidenceBar) return;
    
    // Set the results
    predictedClass.textContent = result.label || 'Unknown';
    confidenceScore.textContent = `${(result.score * 100).toFixed(1)}%`;
    confidenceBar.style.width = `${(result.score * 100)}%`;
    
    // Show results section
    if (resultsSection) {
        resultsSection.classList.remove('d-none');
        resultsSection.classList.add('fade-in');
    }
    
    // Set color based on confidence
    confidenceBar.className = 'progress-bar'; // Reset class
    if (result.score >= 0.8) {
        confidenceBar.classList.add('bg-success');
    } else if (result.score >= 0.6) {
        confidenceBar.classList.add('bg-warning');
    } else {
        confidenceBar.classList.add('bg-danger');
    }
}

function resetForm() {
    if (!textInput) return;
    
    textInput.value = '';
    updateCharCount();
    
    if (resultsSection) {
        resultsSection.classList.add('d-none');
    }
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
    textInput.focus();
}

function showError(message) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastHtml = `
        <div class="toast align-items-center text-white bg-danger border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Append temporarily using innerHTML (simple way)
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = toastHtml;
    const toastEl = tempDiv.firstElementChild;
    
    toastContainer.appendChild(toastEl);
    
    if (typeof bootstrap !== 'undefined') {
        const bsToast = new bootstrap.Toast(toastEl);
        bsToast.show();
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    } else {
        setTimeout(() => toastEl.remove(), 5000);
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// ======== PERIODIC API STATUS CHECK ========
setInterval(checkApiStatus, 30000); // Check every 30 seconds