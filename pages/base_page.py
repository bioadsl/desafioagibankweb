class BasePage:
    def __init__(self, page):
        self.page = page

    def navigate(self, url):
        self.page.goto(url, wait_until="domcontentloaded")

    def click_element(self, locator):
        self.page.locator(locator).wait_for(state="visible")
        self.page.locator(locator).click()

    def fill_input(self, locator, value):
        self.page.locator(locator).wait_for(state="visible")
        self.page.locator(locator).fill(value)

    def select_dropdown(self, locator, value):
        self.page.locator(locator).wait_for(state="visible")
        self.page.locator(locator).select_option(value)

    def get_text(self, locator):
        self.page.locator(locator).wait_for(state="visible")
        return self.page.locator(locator).inner_text().strip()

    def is_element_visible(self, locator, timeout=10000):
        try:
            self.page.locator(locator).wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def wait_for_element(self, locator, timeout=30000):
        self.page.locator(locator).wait_for(state="visible", timeout=timeout)

    def wait_for_load(self):
        self.page.wait_for_load_state("networkidle")
