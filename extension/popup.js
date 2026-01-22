// Clarity Pearl: Sovereign Extension - Popup Logic

document.addEventListener('DOMContentLoaded', async () => {
    const nameEl = document.getElementById('lead-name');
    const titleEl = document.getElementById('lead-title');
    const captureBtn = document.getElementById('capture-btn');
    const statusEl = document.getElementById('status');

    let currentLead = null;

    // 1. Ask content script for profile data
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (tab.url.includes("linkedin.com/in/") || tab.url.includes("linkedin.com/company/")) {
        try {
            const response = await chrome.tabs.sendMessage(tab.id, { action: "GET_PROFILE_DATA" });
            if (response && response.data) {
                currentLead = response.data;
                nameEl.innerText = currentLead.name || "Lead Detected";
                titleEl.innerText = `${currentLead.title} @ ${currentLead.company}`;
                captureBtn.disabled = false;
                statusEl.innerText = "Ready to sync with Vault.";
            }
        } catch (e) {
            statusEl.innerText = "Error communicating with page. Please refresh.";
            console.error(e);
        }
    } else {
        statusEl.innerText = "Navigating to a LinkedIn profile...";
    }

    // 2. Handle Capture Click
    captureBtn.addEventListener('click', async () => {
        captureBtn.disabled = true;
        statusEl.innerText = "Syncing with Sales Intelligence Vault...";

        chrome.runtime.sendMessage({ action: "CAPTURE_LEAD", data: currentLead }, (response) => {
            if (response && response.success) {
                statusEl.innerText = "✅ Synchronized Successfully.";
                captureBtn.innerText = "Lead Vaulted";
            } else {
                statusEl.innerText = "❌ Sync Failed. Check Connection.";
                captureBtn.disabled = false;
            }
        });
    });
});
