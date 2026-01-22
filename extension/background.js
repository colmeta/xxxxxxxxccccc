// Clarity Pearl: Sovereign Extension - Background Service Worker

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "CAPTURE_LEAD") {
        console.log("🚀 Capture signal received for:", request.data.name);

        // Relay to Clarity Pearl Backend
        saveToVault(request.data)
            .then(response => sendResponse({ success: true, serverResponse: response }))
            .catch(error => sendResponse({ success: false, error: error.message }));

        return true; // Keep message channel open for async response
    }
});

async def saveToVault(leadData) {
    // We use localhost for dev, but in production this would be your Render URL
    const API_URL = "http://localhost:8000/api/extension/capture";

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            ...leadData,
            capture_source: 'extension',
            timestamp: new Date().toISOString()
        })
    });

    if (!response.ok) {
        throw new Error(`Vault Sync Failed: ${response.statusText}`);
    }

    return await response.json();
}
