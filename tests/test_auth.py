"""
Unit tests for TypeMaster authentication services and cryptographic password helper logic.
Verifies hashing formatting, unique salting, matching logic, and invalid format handling.
"""
import unittest
from services.auth_service import hash_password, verify_password

class TestPasswordHashing(unittest.TestCase):
    def test_hash_password_generates_correct_format(self):
        """Verify generated hash string structure match pbkdf2 prefix."""
        passwd = "my_super_secret_password_123"
        hashed = hash_password(passwd)
        
        self.assertIsInstance(hashed, str)
        parts = hashed.split('$')
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "pbkdf2_sha256")
        
        # Iterations should be integer
        self.assertEqual(parts[1], "100000")
        
        # Salt and hash parts should be valid hex digits
        # 16 bytes salt represented as 32 hex chars
        self.assertEqual(len(parts[2]), 32)
        int(parts[2], 16) # Should not raise ValueError
        int(parts[3], 16) # Should not raise ValueError

    def test_hash_password_is_salted(self):
        """Verify hashing same password twice yields distinct strings due to random salts."""
        passwd = "same_password"
        hash1 = hash_password(passwd)
        hash2 = hash_password(passwd)
        
        self.assertNotEqual(hash1, hash2)

    def test_verify_password_correct(self):
        """Verify matching passwords validate to True."""
        passwd = "secret_password"
        hashed = hash_password(passwd)
        
        self.assertTrue(verify_password(passwd, hashed))

    def test_verify_password_incorrect(self):
        """Verify non-matching passwords fail validations."""
        passwd = "secret_password"
        hashed = hash_password(passwd)
        
        self.assertFalse(verify_password("wrong_password", hashed))

    def test_verify_password_invalid_format(self):
        """Verify invalid/corrupted hash formats are handled gracefully returning False."""
        self.assertFalse(verify_password("pwd", ""))
        self.assertFalse(verify_password("pwd", None))
        self.assertFalse(verify_password("pwd", "invalid_hash_value"))
        self.assertFalse(verify_password("pwd", "pbkdf2_sha256$100$nothex$nothex"))

if __name__ == '__main__':
    unittest.main()
