# Pearl Chrome Extension

## Installation (Developer Mode)

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer Mode** (toggle in top-right)
3. Click **Load Unpacked**
4. Select the `frontend/extension` folder
5. The Pearl icon should appear in your extensions bar

## Features

### Popup Dashboard
- Click the Pearl icon to see:
  - High-intent leads count
  - Active missions count
  - Recently discovered profiles
  - Quick "Open Dashboard" button

### LinkedIn Overlay
- Navigate to any LinkedIn profile (e.g., `linkedin.com/in/someone`)
- Pearl will auto-inject a floating badge showing:
  - Intent score (mock data for now)
  - "Add to Pearl" button
  - "View Graph" button

## Future Enhancements
- Connect to live Supabase for real intent scores
- Sync with Pearl backend for "Add to Pearl" functionality
- Badge notifications for new high-intent leads
- Support for Product Hunt, Shopify, and other platforms

## Files
- `manifest.json` - Extension config (Manifest V3)
- `popup.html` / `popup.js` - Mini dashboard
- `content.js` - Profile detection & overlay injection
- `overlay.css` - Styling for injected UI
- `background.js` - Service worker (future: Supabase sync)

---

**Note**: This extension is built but not published to Chrome Web Store (requires $5 payment). Load it locally to test the concept.
