"""
Unit tests for TypeMaster Registration UI validation logic.
Tests validation checks for form inputs (username, passwords, mismatching inputs).
"""
import unittest
import tkinter as tk
from ui.register import RegisterView

class TestRegistrationUIValidation(unittest.TestCase):
    def setUp(self):
        # Initialize a hidden Tk instance context for test run
        self.root = tk.Tk()
        self.root.withdraw() # Do not open visual window
        self.view = RegisterView(self.root, controller=None)

    def tearDown(self):
        self.root.destroy()

    def test_validation_empty_username(self):
        """Verify empty username fails validation."""
        self.view.username_var.set("")
        self.view.password_var.set("securepass123")
        self.view.confirm_password_var.set("securepass123")
        
        self.assertFalse(self.view.validate_inputs())
        self.assertEqual(self.view.error_label.cget("text"), "Foydalanuvchi nomi kiritilishi shart!")

    def test_validation_empty_password(self):
        """Verify empty password fails validation."""
        self.view.username_var.set("user_xyz")
        self.view.password_var.set("")
        self.view.confirm_password_var.set("")
        
        self.assertFalse(self.view.validate_inputs())
        self.assertEqual(self.view.error_label.cget("text"), "Parol kiritilishi shart!")

    def test_validation_password_length(self):
        """Verify password shorter than 6 characters fails validation."""
        self.view.username_var.set("user_xyz")
        self.view.password_var.set("12345")
        self.view.confirm_password_var.set("12345")
        
        self.assertFalse(self.view.validate_inputs())
        self.assertEqual(self.view.error_label.cget("text"), "Parol kamida 6 ta belgidan iborat bo'lishi kerak!")

    def test_validation_password_mismatch(self):
        """Verify mismatched passwords fail validation."""
        self.view.username_var.set("user_xyz")
        self.view.password_var.set("securepass123")
        self.view.confirm_password_var.set("securepass999")
        
        self.assertFalse(self.view.validate_inputs())
        self.assertEqual(self.view.error_label.cget("text"), "Parollar o'zaro mos kelmadi!")

    def test_validation_success(self):
        """Verify valid details pass validations."""
        self.view.username_var.set("user_xyz")
        self.view.password_var.set("securepass123")
        self.view.confirm_password_var.set("securepass123")
        
        self.assertTrue(self.view.validate_inputs())
        self.assertEqual(self.view.error_label.cget("text"), "")

if __name__ == '__main__':
    unittest.main()
