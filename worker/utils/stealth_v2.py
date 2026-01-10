import random
import json

class StealthContextV2:
    """
    THE GHOST LAYER - SUPREME STEALTH (v2026)
    Bypassing Cloudflare, Datadome, and Akamai.
    """
    
    @staticmethod
    async def apply_advanced_stealth(page):
        # 1. Inject Canvas Fingerprint Noise
        # This makes every Hydra Head unique to graphics hardware detectors.
        await page.add_init_script("""
            const toBlob = HTMLCanvasElement.prototype.toBlob;
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            const getImageData = CanvasRenderingContext2D.prototype.getImageData;

            const noise = () => {
                const s = Math.random() * 0.1;
                return s - 0.05;
            };

            CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {
                const res = getImageData.apply(this, arguments);
                for (let i = 0; i < res.data.length; i += 4) {
                    res.data[i] = res.data[i] + noise();
                }
                return res;
            };
        """)

        # 2. Modern WebGL Vendor Selection
        vendors = [
            ("Intel Inc.", "Intel Iris OpenGL Engine"),
            ("Google Inc.", "ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)"),
            ("Apple Inc.", "Apple GPU")
        ]
        vendor, renderer = random.choice(vendors)
        
        await page.add_init_script(f"""
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) return '{renderer}';
                if (parameter === 37446) return '{vendor}';
                return getParameter(parameter);
            }};
        """)

        # 3. Human-like User Agent and Platform Sync
        # We ensure navigator.platform matches the UA to prevent "Inconsistency Flags"
        await page.add_init_script("""
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'productSub', { get: () => '20030107' });
            Object.defineProperty(navigator, 'vendor', { get: () => 'Google Inc.' });
        """)

        # 4. CRITICAL: Mask Navigator.webdriver (The #1 Bot Tell)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # 5. Mock Chrome Runtime (To look like a real headed Chrome)
        await page.add_init_script("""
            window.chrome = {
                runtime: {}
            };
        """)

        # 6. Permissions API Mock
        await page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
        """)

        # 7. Plugin Entropy
        await page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)

    @staticmethod
    async def enact_human_behavior(page):
        """
        Performs non-linear mouse movements and variable scrolling.
        """
        # random viewport jitter
        width = 1280 + random.randint(-50, 50)
        height = 720 + random.randint(-50, 50)
        await page.set_viewport_size({"width": width, "height": height})
        
        # Natural scroll
        for _ in range(random.randint(2, 5)):
            await page.mouse.wheel(0, random.randint(300, 700))
            await page.wait_for_timeout(random.randint(500, 1500))

stealth_v2 = StealthContextV2()
