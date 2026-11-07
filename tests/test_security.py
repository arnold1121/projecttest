import unittest
from app.services.auth_service import hash_password, verify_password


class PasswordHashTests(unittest.TestCase):
    def test_password_hash_is_not_plaintext(self):
        password = "SeaFishPick-demo-password"
        encoded = hash_password(password)
        self.assertNotEqual(encoded, password)
        self.assertTrue(encoded.startswith("pbkdf2_sha256$"))

    def test_correct_password_verifies(self):
        encoded = hash_password("correct horse battery staple")
        self.assertTrue(verify_password("correct horse battery staple", encoded))

    def test_wrong_password_does_not_verify(self):
        encoded = hash_password("correct horse battery staple")
        self.assertFalse(verify_password("not the same password", encoded))

    def test_invalid_hash_is_rejected(self):
        self.assertFalse(verify_password("password", "not-a-valid-hash"))


if __name__ == "__main__":
    unittest.main()
