"""
Unit tests for Developer Profile localization and UI cards in SettingsView and ResultsView.
"""
import unittest
import tkinter as tk
from services.i18n_service import t, set_locale, get_locale
from ui.settings import SettingsView
from ui.results import ResultsView
from app.event_bus import EventBus

class MockApplicationController:
    """Mock application controller for view testing."""
    def __init__(self):
        self.shown_view = None
        self.current_theme = "dark"
        self.current_font_family = "Consolas"
        self.current_font_size = 14
        self.current_ui_language = "uz"
        self.event_bus = EventBus()

    def show_view(self, view_name: str):
        self.shown_view = view_name

    def apply_theme(self, theme_name: str, font_family: str, font_size: int):
        self.current_theme = theme_name
        self.current_font_family = font_family
        self.current_font_size = font_size

    def retranslate_ui(self):
        pass


class TestDeveloperInfoLocalizationAndUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = MockApplicationController()
        set_locale("uz")

    def tearDown(self):
        self.root.destroy()
        set_locale("uz")

    def test_i18n_developer_keys_exist_in_all_languages(self):
        """Verify developer info translation keys exist in uz, en, and ru."""
        keys = [
            "dev_info_title",
            "dev_info_name",
            "dev_info_phone",
            "dev_info_services",
            "dev_info_contact",
            "dev_info_badge_title"
        ]
        for lang in ["uz", "en", "ru"]:
            set_locale(lang)
            for k in keys:
                translated = t(k)
                self.assertIsNotNone(translated)
                self.assertNotEqual(translated, k, f"Key '{k}' not found in '{lang}' dictionary!")

    def test_settings_view_developer_card_initialization_and_retranslate(self):
        """Verify developer card exists in SettingsView and updates on locale change."""
        view = SettingsView(self.root, self.app)
        
        # Check elements exist
        self.assertTrue(hasattr(view, "dev_frame"))
        self.assertTrue(hasattr(view, "dev_title"))
        self.assertTrue(hasattr(view, "dev_name_lbl"))
        self.assertTrue(hasattr(view, "dev_phone_lbl"))
        self.assertTrue(hasattr(view, "dev_services_lbl"))
        self.assertTrue(hasattr(view, "dev_contact_btn"))

        # Verify Uzbek initial text
        self.assertIn("Valijon Ergashev", view.dev_name_lbl.cget("text"))
        self.assertIn("998 (77) 342-33-21", view.dev_phone_lbl.cget("text"))

        # Test language switch to English
        set_locale("en")
        view.retranslate_ui()
        self.assertEqual(view.dev_title.cget("text"), "👨‍💻  About Developer")
        self.assertIn("Developer: Valijon Ergashev", view.dev_name_lbl.cget("text"))

        # Test language switch to Russian
        set_locale("ru")
        view.retranslate_ui()
        self.assertEqual(view.dev_title.cget("text"), "👨‍💻  О разработчике")
        self.assertIn("Разработчик: Валижон Эргашев", view.dev_name_lbl.cget("text"))

        view.destroy()

    def test_results_view_developer_card_initialization_and_retranslate(self):
        """Verify developer footer card exists in ResultsView and updates on locale change."""
        view = ResultsView(self.root, self.app)

        # Check elements exist
        self.assertTrue(hasattr(view, "dev_info_card"))
        self.assertTrue(hasattr(view, "dev_info_text"))
        self.assertTrue(hasattr(view, "dev_contact_btn"))

        # Verify Uzbek initial text
        self.assertIn("Valijon Ergashev", view.dev_info_text.cget("text"))
        self.assertIn("998 (77) 342-33-21", view.dev_info_text.cget("text"))

        # Test language switch to English
        set_locale("en")
        view.retranslate_ui()
        self.assertIn("Developer: Valijon Ergashev", view.dev_info_text.cget("text"))

        # Test language switch to Russian
        set_locale("ru")
        view.retranslate_ui()
        self.assertIn("Разработчик: Валижон Эргашев", view.dev_info_text.cget("text"))

        view.destroy()


if __name__ == "__main__":
    unittest.main()
