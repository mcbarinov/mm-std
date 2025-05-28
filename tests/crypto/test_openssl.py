import base64

import pytest

from mm_std.crypto.openssl import OpensslAes256Cbc


class TestOpensslAes256Cbc:
    """Test cases for the OpensslAes256Cbc class."""

    def test_basic_encrypt_decrypt_base64(self) -> None:
        """Test basic base64 encryption and decryption roundtrip."""
        cipher = OpensslAes256Cbc("test_password")
        original_data = "Hello, World!"

        encrypted = cipher.encrypt_base64(original_data)
        decrypted = cipher.decrypt_base64(encrypted)

        assert decrypted == original_data

    def test_basic_encrypt_decrypt_bytes(self) -> None:
        """Test basic bytes encryption and decryption roundtrip."""
        cipher = OpensslAes256Cbc("test_password")
        original_data = b"Hello, World!"

        encrypted = cipher.encrypt_bytes(original_data)
        decrypted = cipher.decrypt_bytes(encrypted)

        assert decrypted == original_data

    def test_cross_compatibility_bytes_base64(self) -> None:
        """Test that bytes and base64 methods are compatible."""
        cipher = OpensslAes256Cbc("test_password")
        original_text = "Test message"
        original_bytes = original_text.encode("utf-8")

        # Encrypt as bytes, decode via base64
        encrypted_bytes = cipher.encrypt_bytes(original_bytes)
        encrypted_base64 = base64.b64encode(encrypted_bytes).decode("ascii")
        decrypted_text = cipher.decrypt_base64(encrypted_base64)
        assert decrypted_text == original_text

        # Encrypt as base64, decode via bytes
        encrypted_base64 = cipher.encrypt_base64(original_text)
        encrypted_bytes = base64.b64decode(encrypted_base64)
        decrypted_bytes = cipher.decrypt_bytes(encrypted_bytes)
        assert decrypted_bytes == original_bytes

    def test_initialization_simple(self) -> None:
        """Test simple initialization without custom parameters."""
        cipher = OpensslAes256Cbc("test_password")

        # Test that it works
        data = "Test data"
        encrypted = cipher.encrypt_base64(data)
        decrypted = cipher.decrypt_base64(encrypted)
        assert decrypted == data

    def test_reuse_cipher_object(self) -> None:
        """Test that the same cipher object can be used multiple times."""
        cipher = OpensslAes256Cbc("test_password")

        data1 = "First message"
        data2 = "Second message"

        encrypted1 = cipher.encrypt_base64(data1)
        encrypted2 = cipher.encrypt_base64(data2)

        # Should be different due to random salt
        assert encrypted1 != encrypted2

        # But both should decrypt correctly
        assert cipher.decrypt_base64(encrypted1) == data1
        assert cipher.decrypt_base64(encrypted2) == data2

    def test_different_cipher_objects_same_password(self) -> None:
        """Test that different cipher objects with same password can decrypt each other's data."""
        cipher1 = OpensslAes256Cbc("same_password")
        cipher2 = OpensslAes256Cbc("same_password")

        data = "Shared secret"
        encrypted = cipher1.encrypt_base64(data)
        decrypted = cipher2.decrypt_base64(encrypted)

        assert decrypted == data

    def test_different_passwords_fail(self) -> None:
        """Test that different passwords cannot decrypt each other's data."""
        cipher1 = OpensslAes256Cbc("password1")
        cipher2 = OpensslAes256Cbc("password2")

        data = "Secret data"
        encrypted = cipher1.encrypt_base64(data)

        with pytest.raises(ValueError, match="Decryption failed: wrong password or corrupted data"):
            cipher2.decrypt_base64(encrypted)

    def test_unicode_data(self) -> None:
        """Test encryption and decryption of Unicode data."""
        cipher = OpensslAes256Cbc("unicode_password_тест")
        original_data = "Привет, мир! 🌍 こんにちは世界"

        encrypted = cipher.encrypt_base64(original_data)
        decrypted = cipher.decrypt_base64(encrypted)

        assert decrypted == original_data

    def test_empty_string(self) -> None:
        """Test encryption and decryption of empty string."""
        cipher = OpensslAes256Cbc("test_password")
        original_data = ""

        encrypted = cipher.encrypt_base64(original_data)
        decrypted = cipher.decrypt_base64(encrypted)

        assert decrypted == original_data

    def test_empty_bytes(self) -> None:
        """Test encryption and decryption of empty bytes."""
        cipher = OpensslAes256Cbc("test_password")
        original_data = b""

        encrypted = cipher.encrypt_bytes(original_data)
        decrypted = cipher.decrypt_bytes(encrypted)

        assert decrypted == original_data

    def test_long_data_string(self) -> None:
        """Test encryption and decryption of long string data."""
        cipher = OpensslAes256Cbc("long_data_password")
        original_data = "A" * 10000  # 10KB of data

        encrypted = cipher.encrypt_base64(original_data)
        decrypted = cipher.decrypt_base64(encrypted)

        assert decrypted == original_data

    def test_long_data_bytes(self) -> None:
        """Test encryption and decryption of long bytes data."""
        cipher = OpensslAes256Cbc("long_data_password")
        original_data = b"B" * 10000  # 10KB of data

        encrypted = cipher.encrypt_bytes(original_data)
        decrypted = cipher.decrypt_bytes(encrypted)

        assert decrypted == original_data

    def test_multiline_data(self) -> None:
        """Test encryption and decryption of multiline data."""
        cipher = OpensslAes256Cbc("multiline_password")
        original_data = """Line 1
Line 2 with special chars: !@#$%^&*()
Line 3 with unicode: 测试
Line 4"""

        encrypted = cipher.encrypt_base64(original_data)
        decrypted = cipher.decrypt_base64(encrypted)

        assert decrypted == original_data

    def test_binary_data(self) -> None:
        """Test encryption and decryption of binary data."""
        cipher = OpensslAes256Cbc("binary_password")
        # Create some binary data
        original_data = bytes(range(256))  # All possible byte values

        encrypted = cipher.encrypt_bytes(original_data)
        decrypted = cipher.decrypt_bytes(encrypted)

        assert decrypted == original_data

    def test_encrypted_format_structure_bytes(self) -> None:
        """Test that encrypted bytes have correct OpenSSL format structure."""
        cipher = OpensslAes256Cbc("test_password")
        data = b"Test message"

        encrypted = cipher.encrypt_bytes(data)

        # Should start with "Salted__" magic
        assert encrypted[:8] == b"Salted__"

        # Should have salt (8 bytes) + ciphertext
        assert len(encrypted) >= 16  # At least magic + salt

    def test_encrypted_format_structure_base64(self) -> None:
        """Test that base64 encrypted data has correct OpenSSL format structure."""
        cipher = OpensslAes256Cbc("test_password")
        data = "Test message"

        encrypted_base64 = cipher.encrypt_base64(data)

        # Decode base64 to check binary structure
        binary_data = base64.b64decode(encrypted_base64)

        # Should start with "Salted__" magic
        assert binary_data[:8] == b"Salted__"

        # Should have salt (8 bytes) + ciphertext
        assert len(binary_data) >= 16  # At least magic + salt

    def test_invalid_base64_error(self) -> None:
        """Test that invalid base64 data raises appropriate error."""
        cipher = OpensslAes256Cbc("test_password")
        invalid_base64 = "Invalid base64 with spaces and @@@ symbols"

        with pytest.raises(ValueError, match="Invalid base64 format"):
            cipher.decrypt_base64(invalid_base64)

    def test_invalid_format_error_bytes(self) -> None:
        """Test that bytes without OpenSSL magic header raise appropriate error."""
        cipher = OpensslAes256Cbc("test_password")
        invalid_data = b"This is not OpenSSL format"

        with pytest.raises(ValueError, match="Invalid format: missing OpenSSL salt header"):
            cipher.decrypt_bytes(invalid_data)

    def test_invalid_format_error_base64(self) -> None:
        """Test that base64 data without OpenSSL magic header raises appropriate error."""
        cipher = OpensslAes256Cbc("test_password")
        # Valid base64 but wrong format
        invalid_data = "VGhpcyBpcyBub3QgT3BlblNTTCBmb3JtYXQ="  # "This is not OpenSSL format"

        with pytest.raises(ValueError, match="Invalid format: missing OpenSSL salt header"):
            cipher.decrypt_base64(invalid_data)

    def test_whitespace_handling_base64(self) -> None:
        """Test that whitespace in base64 encrypted data is handled correctly."""
        cipher = OpensslAes256Cbc("test_password")
        data = "Test data"

        encrypted = cipher.encrypt_base64(data)

        # Add whitespace and test decryption
        encrypted_with_whitespace = f"  {encrypted}  \n\t"
        decrypted = cipher.decrypt_base64(encrypted_with_whitespace)

        assert decrypted == data

    def test_same_data_different_salt(self) -> None:
        """Test that same data with same password produces different encrypted results due to random salt."""
        cipher = OpensslAes256Cbc("same_password")
        data = "Secret message"

        encrypted1 = cipher.encrypt_base64(data)
        encrypted2 = cipher.encrypt_base64(data)

        # Should be different due to random salt
        assert encrypted1 != encrypted2

        # But both should decrypt to the same original data
        decrypted1 = cipher.decrypt_base64(encrypted1)
        decrypted2 = cipher.decrypt_base64(encrypted2)

        assert decrypted1 == data
        assert decrypted2 == data

    def test_corrupted_data_error(self) -> None:
        """Test that corrupted encrypted data raises appropriate error."""
        cipher = OpensslAes256Cbc("test_password")
        data = "Test data"

        encrypted = cipher.encrypt_base64(data)

        # Corrupt the encrypted data by changing a character
        corrupted = encrypted[:-1] + ("A" if encrypted[-1] != "A" else "B")

        with pytest.raises(ValueError, match="Decryption failed: wrong password or corrupted data"):
            cipher.decrypt_base64(corrupted)

    def test_short_encrypted_data_error(self) -> None:
        """Test that too short encrypted data raises appropriate error."""
        cipher = OpensslAes256Cbc("test_password")

        # Create data that's too short (less than header + salt)
        short_data = b"Salted__"  # Only magic header, no salt

        with pytest.raises(ValueError):  # Should raise some error due to insufficient data
            cipher.decrypt_bytes(short_data)

    @pytest.mark.parametrize(
        "test_data",
        [
            "Simple text",
            "Text with numbers 123456",
            "Special chars: !@#$%^&*()",
            "Unicode: 你好世界 🌍",
            "Mixed: Hello мир 123 🎉",
            'JSON-like: {"key": "value", "number": 42}',
            "XML-like: <root><item>value</item></root>",
            "Newlines\nand\ttabs",
            "Quotes: 'single' and \"double\"",
        ],
    )
    def test_various_data_types_base64(self, test_data: str) -> None:
        """Test base64 encryption and decryption with various data types."""
        cipher = OpensslAes256Cbc("test_password")

        encrypted = cipher.encrypt_base64(test_data)
        decrypted = cipher.decrypt_base64(encrypted)

        assert decrypted == test_data

    @pytest.mark.parametrize(
        "test_data",
        [
            b"Simple bytes",
            b"Binary data: \x00\x01\x02\xff",
            bytes(range(256)),  # All possible byte values
            b"Unicode encoded: " + "тест 🌍".encode(),
            b"",  # Empty bytes
            b"A" * 1000,  # Long data
        ],
    )
    def test_various_data_types_bytes(self, test_data: bytes) -> None:
        """Test bytes encryption and decryption with various data types."""
        cipher = OpensslAes256Cbc("test_password")

        encrypted = cipher.encrypt_bytes(test_data)
        decrypted = cipher.decrypt_bytes(encrypted)

        assert decrypted == test_data

    @pytest.mark.parametrize(
        "password",
        [
            "simple",
            "complex_P@ssw0rd!",
            "unicode_пароль",
            "very_long_password_" * 10,
            "123456",
            "!@#$%^&*()",
            "",  # Empty password
            "🔐🗝️",  # Emoji password
        ],
    )
    def test_various_passwords(self, password: str) -> None:
        """Test encryption and decryption with various password types."""
        cipher = OpensslAes256Cbc(password)
        data = "Test data for password variations"

        encrypted = cipher.encrypt_base64(data)
        decrypted = cipher.decrypt_base64(encrypted)

        assert decrypted == data

    def test_large_data_performance(self) -> None:
        """Test encryption and decryption of large data (performance test)."""
        cipher = OpensslAes256Cbc("performance_test")

        # 1MB of data
        large_data = "X" * (1024 * 1024)

        encrypted = cipher.encrypt_base64(large_data)
        decrypted = cipher.decrypt_base64(encrypted)

        assert decrypted == large_data
        assert len(encrypted) > len(large_data)  # Should be larger due to base64 encoding

    def test_constants_and_attributes(self) -> None:
        """Test that class constants are set correctly."""
        cipher = OpensslAes256Cbc("test")

        assert cipher.MAGIC_HEADER == b"Salted__"
        assert cipher.SALT_SIZE == 8
        assert cipher.KEY_SIZE == 32
        assert cipher.IV_SIZE == 16
        assert cipher.ITERATIONS == 1_000_000
        assert cipher.HEADER_LEN == 8
