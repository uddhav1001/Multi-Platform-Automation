from playwright.sync_api import Page, expect
from .base_page import BasePage

class LoginPage(BasePage):
    def login(self, email, password, base_url):
        self.page.goto(f'{base_url}/login')
        self.page.get_by_label('Email').fill(email)
        self.page.get_by_label('Password').fill(password)
        self.page.get_by_role('button', name='Log in').click()
        self.page.wait_for_url(f'{base_url}/dashboard')
        expect(self.page.locator('.welcome-message')).to_be_visible()
