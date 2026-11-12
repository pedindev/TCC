"""Teste opcional de navegador: somente paginas locais, sem SIAT ou WhatsApp."""

import os
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import override_settings
from playwright.sync_api import expect, sync_playwright


@override_settings(APP_MODE="preparacao")
class BrowserCheck(StaticLiveServerTestCase):
    host = "127.0.0.1"

    def test_painel_direto_no_chromium(self):
        browser_path = str(Path(settings.BASE_DIR) / ".local" / "browsers")
        with patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": browser_path}):
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                try:
                    page = browser.new_page(viewport={"width": 1280, "height": 900})
                    page.goto(self.live_server_url)
                    expect(page.get_by_role("heading", level=1)).to_contain_text("Atendimento")
                    expect(
                        page.get_by_role("button", name="Consultar", exact=True)
                    ).to_be_disabled()
                    expect(page.get_by_role("link", name="Entrar", exact=True)).to_have_count(0)
                    page.reload()
                    expect(
                        page.get_by_role("heading", name="Atendimento", exact=True)
                    ).to_be_visible()
                    page.set_viewport_size({"width": 390, "height": 844})
                    self.assertTrue(
                        page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                    )
                finally:
                    browser.close()
