"""JavaScript rendering handler using Playwright"""
import asyncio
import threading


class JavaScriptRenderer:
    """Handles JavaScript rendering for dynamic content using Playwright"""

    def __init__(self, config):
        self.config = config
        self.playwright = None
        self.browser = None
        self.page_pool = []
        self.pool_lock = threading.Lock()

    async def initialize(self):
        """Initialize Playwright browser and page pool"""
        try:
            from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
            self.PlaywrightTimeoutError = PlaywrightTimeoutError
            browser_type = self.config.get('js_browser', 'chromium').lower()
            headless = self.config.get('js_headless', True)
            self.playwright = await async_playwright().start()
            if browser_type == 'firefox':
                self.browser = await self.playwright.firefox.launch(headless=headless)
            elif browser_type == 'webkit':
                self.browser = await self.playwright.webkit.launch(headless=headless)
            else:
                args = ['--no-sandbox', '--disable-dev-shm-usage'] if headless else []
                self.browser = await self.playwright.chromium.launch(headless=headless, args=args)
            max_pages = self.config.get('js_max_concurrent_pages', 3)
            for _ in range(max_pages):
                context = await self.browser.new_context(
                    user_agent=self.config.get('js_user_agent', 'seocli/1.0'),
                    viewport={'width': self.config.get('js_viewport_width', 1920), 'height': self.config.get('js_viewport_height', 1080)}
                )
                page = await context.new_page()
                page.set_default_timeout(self.config.get('js_timeout', 30) * 1000)
                self.page_pool.append(page)
        except ImportError:
            raise RuntimeError("playwright not installed. Install: pip install playwright && playwright install chromium")
        except Exception as e:
            await self.cleanup()
            raise RuntimeError(f"Failed to initialize Playwright: {e}")

    async def cleanup(self):
        if self.page_pool:
            for page in self.page_pool:
                try:
                    await page.context.close()
                except Exception:
                    pass
            self.page_pool.clear()
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
            self.browser = None
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception:
                pass
            self.playwright = None

    async def get_page(self):
        with self.pool_lock:
            if self.page_pool:
                return self.page_pool.pop()
        return None

    async def return_page(self, page):
        with self.pool_lock:
            self.page_pool.append(page)

    async def render_page(self, url):
        """Render a page with JavaScript and return (html_content, status_code, error_message)."""
        page = None
        try:
            page = await self.get_page()
            if not page:
                return None, 0, "No JavaScript page available"
            response = await page.goto(url, wait_until='domcontentloaded', timeout=self.config.get('js_timeout', 30) * 1000)
            await asyncio.sleep(self.config.get('js_wait_time', 3))
            html_content = await page.content()
            status_code = response.status if response else 200
            return html_content, status_code, None
        except Exception as e:
            msg = str(e)
            if 'Timeout' in msg:
                return None, 0, "JavaScript rendering timeout"
            return None, 0, f"JS rendering error: {msg}"
        finally:
            if page:
                await self.return_page(page)
