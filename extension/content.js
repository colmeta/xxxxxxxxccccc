// Clarity Pearl: Sovereign Extension - LinkedIn Scraper

function scrapeLinkedInProfile() {
    console.log("💎 Clarity Pearl: Extracting Intelligence...");

    const getName = () => document.querySelector('.text-heading-xlarge')?.innerText ||
        document.querySelector('.pv-top-card--list li')?.innerText;

    const getTitle = () => document.querySelector('.text-body-medium.break-words')?.innerText ||
        document.querySelector('div.ph5.pb5 > div.display-flex.mt2 > div > div.text-body-medium.break-words')?.innerText;

    const getCompany = () => document.querySelector('[data-field="experience_company_logo"] img')?.alt ||
        document.querySelector('.pv-text-details__right-panel li button span')?.innerText ||
        document.querySelector('.experience-item .company-name')?.innerText;

    const getLocation = () => document.querySelector('.text-body-small.inline.t-black--light.break-words')?.innerText;

    const getAvatar = () => document.querySelector('.pv-top-card-profile-picture__image--show')?.src;

    const profileData = {
        name: getName()?.trim(),
        title: getTitle()?.trim(),
        company: getCompany()?.trim(),
        location: getLocation()?.trim(),
        avatar_url: getAvatar(),
        linkedin_url: window.location.href,
        source_url: window.location.href,
        platform: 'linkedin'
    };

    console.log("✅ Intelligence Captured:", profileData);
    return profileData;
}

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "GET_PROFILE_DATA") {
        const data = scrapeLinkedInProfile();
        sendResponse({ data: data });
    }
});
