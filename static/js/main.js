/**
 * GeoPulse Main JavaScript
 * Contains global logic used across multiple pages
 */

// Check Earth Engine status
async function checkEEStatus() {
    try {
        const response = await fetch('/api/ee_status');
        const data = await response.json();
        const statusAlert = document.getElementById('eeStatusAlert');
        const statusText = document.getElementById('eeStatusText');

        if (!statusAlert || !statusText) return;

        if (data.initialized) {
            statusAlert.className = 'alert alert-success mb-0';
            statusText.innerHTML = '<i class="fas fa-check-circle me-2"></i>Earth Engine is ready ✓';
            statusAlert.style.display = 'block';
        } else {
            statusAlert.className = 'alert alert-warning mb-0';
            if (data.status === 'not_configured') {
                statusText.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Earth Engine is not configured.';
            } else {
                statusText.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>Earth Engine initialization failed.';
            }
            statusAlert.style.display = 'block';
        }
    } catch (error) {
        const statusAlert = document.getElementById('eeStatusAlert');
        const statusText = document.getElementById('eeStatusText');

        if (statusAlert && statusText) {
            statusAlert.className = 'alert alert-danger mb-0';
            statusText.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>Status check failed';
            statusAlert.style.display = 'block';
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    // Wait a bit to ensure DOM is fully ready
    setTimeout(() => {
        checkEEStatus();
    }, 100);
});
