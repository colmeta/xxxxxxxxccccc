// Pearl Background Worker
chrome.runtime.onInstalled.addListener(() => {
    console.log('Pearl Extension Installed');
});

// Future: Listen for messages from content.js to check Supabase
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'CHECK_PROFILE') {
        // TODO: Call Supabase Edge Function to check vault
        sendResponse({ status: 'mock_data', score: 85 });
    }
});
