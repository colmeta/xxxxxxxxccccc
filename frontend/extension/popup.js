document.getElementById('openDashboard').addEventListener('click', () => {
    chrome.tabs.create({ url: 'http://localhost:5173' }); // Or production URL
});

// Future: Fetch stats from background.js (which syncs with Supabase)
console.log('Pearl Popup Loaded');
