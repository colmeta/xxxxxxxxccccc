chrome.runtime.onInstalled.addListener(() => {
    console.log("💎 Clarity Pearl: Sovereign Extension Installed & Licensed.");
});

// Future: Handle message passing from content scripts to side-panel
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "VAULT_IDENTITY_FOUND") {
        console.log("🔒 Vault Identity Confirmed in Background:", request.id);
    }
});
