from playwright.sync_api import Page, expect
from .base_page import BasePage

class DashboardPage(BasePage):
    def assert_loaded(self):
        expect(self.page).to_have_url(lambda u: '/dashboard' in u)
        expect(self.page.locator('.welcome-message')).to_be_visible()
