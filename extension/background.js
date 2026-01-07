// THE INVISIBLE HAND - BACKGROUND WORKER

// Initialize Context Menu
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "scout_selection",
        title: "Scout '%s' in Clarity Pearl",
        contexts: ["selection"]
    });
});

// Handle Context Menu Clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "scout_selection") {
        const query = info.selectionText;

        // In a real build, we'd fetch the user's API Key from storage
        // For now, we'll log it or assume a dev setup
        console.log(`🕊️ The Invisible Hand: Intercepted query '${query}'`);

        // Send to local API (for dev demonstration)
        fetch("http://localhost:8000/api/v1/scout", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-KEY": "dev_key_verified" // Mock key for demo
            },
            body: JSON.stringify({
                query: query,
                platform: "generic"
            })
        }).then(res => {
            if (res.ok) {
                chrome.action.setBadgeText({ text: "OK" });
                chrome.action.setBadgeBackgroundColor({ color: "#00FF9D" });
            } else {
                chrome.action.setBadgeText({ text: "ERR" });
                chrome.action.setBadgeBackgroundColor({ color: "#FF0055" });
            }
        }).catch(err => {
            console.error("Transmission failed", err);
            chrome.action.setBadgeText({ text: "FAIL" });
        });
    }
});
