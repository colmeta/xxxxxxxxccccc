import random

class StealthContext:
    @staticmethod
    async def apply_stealth(page):
        """
        Injects a series of JavaScript patches to hide Playwright/Headless signatures.
        """
        
        # 1. Mask navigator.webdriver
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # 2. Mock chrome object
        await page.add_init_script("""
            window.chrome = {
                runtime: {},
                app: {
                    InstallState: {
                        DISABLED: 'disabled',
                        INSTALLED: 'installed',
                        NOT_INSTALLED: 'not_installed'
                    },
                    RunningState: {
                        CANNOT_RUN: 'cannot_run',
                        READY_TO_RUN: 'ready_to_run',
                        RUNNING: 'running'
                    },
                    getDetails: () => {},
                    getIsInstalled: () => {},
                    installState: () => {},
                    isInstalled: false,
                    runningState: () => {}
                },
                csi: () => {},
                loadTimes: () => {}
            };
        """)

        # 3. Mock Plugins (Standard Chrome plugins)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    },
                    {
                        0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable", enabledPlugin: Plugin},
                        description: "",
                        filename: "internal-nacl-plugin",
                        length: 2,
                        name: "Native Client"
                    }
                ]
            });
        """)

        # 4. Mock Languages
        await page.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

        # 5. Pass Permissions Test
        await page.add_init_script("""
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: 'denied', onchange: null }) :
                    originalQuery(parameters)
            );
        """)

        # 6. WebGL/Hardware Concurrency Randomizer
        concurrency = random.choice([4, 8, 12, 16])
        memory = random.choice([4, 8, 16])
        await page.add_init_script(f"""
            Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {concurrency} }});
            Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {memory} }});
        """)
        
        # 7. WebGL Vendor Override (Masking Headless renderer)
        await page.add_init_script("""
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // 37446 = UNMASKED_VENDOR_WEBGL
                // 37445 = UNMASKED_RENDERER_WEBGL
                if (parameter === 37445) {
                    return 'Intel Iris OpenGL Engine';
                }
                if (parameter === 37446) {
                    return 'Intel Inc.';
                }
                return getParameter(parameter);
            };
        """)
