// PEARL CONTENT SCRIPT
console.log('Pearl Content Script Loaded');

// Helper to create the overlay
function createOverlay(name, score) {
    // Remove existing
    const existing = document.querySelector('.pearl-overlay-badge');
    if (existing) existing.remove();

    const badge = document.createElement('div');
    badge.className = 'pearl-overlay-badge';

    badge.innerHTML = `
    <div class="pearl-header">
      <div class="pearl-title">PEARL INTEL</div>
      <div style="cursor:pointer" onclick="this.parentElement.parentElement.remove()">✕</div>
    </div>
    
    <div style="display:flex; justify-content:space-between; align-items:flex-end">
      <div>
        <div class="pearl-label">Intent Score</div>
        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.5)">Based on signals</div>
      </div>
      <div class="pearl-score">${score}</div>
    </div>

    <div class="pearl-actions">
      <button class="pearl-btn pearl-btn-primary">Add to Pearl</button>
      <button class="pearl-btn pearl-btn-secondary">View Graph</button>
    </div>
  `;

    document.body.appendChild(badge);
}

// Simple detection for LinkedIn profiles (URL change listener)
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        checkUrl();
    }
}).observe(document, { subtree: true, childList: true });

function checkUrl() {
    if (window.location.href.includes('linkedin.com/in/')) {
        // Simulate detecting a lead
        // In production, this would send the URL to background.js -> Supabase to check if in vault

        // Mock delay
        setTimeout(() => {
            // Random mock score for demo
            const mockScore = Math.floor(Math.random() * (99 - 70) + 70);
            createOverlay('Detected Profile', mockScore);
        }, 1500);
    } else {
        const existing = document.querySelector('.pearl-overlay-badge');
        if (existing) existing.remove();
    }
}

// Initial check
checkUrl();
