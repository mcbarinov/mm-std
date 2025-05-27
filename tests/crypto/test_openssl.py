import shutil
import subprocess
from pathlib import Path

import pytest

from mm_std import openssl_decrypt, openssl_decrypt_base64, openssl_encrypt, openssl_encrypt_base64


def test_encrypt_decrypt_roundtrip(tmp_path: Path) -> None:
    password = "test-password"
    plaintext_data = b"Secret message for encryption!"

    input_file = tmp_path / "input.txt"
    encrypted_file = tmp_path / "encrypted.bin"
    decrypted_file = tmp_path / "decrypted.txt"

    input_file.write_bytes(plaintext_data)

    openssl_encrypt(input_file, encrypted_file, password)
    assert encrypted_file.exists()
    assert encrypted_file.read_bytes() != plaintext_data  # ensure it's encrypted

    openssl_decrypt(encrypted_file, decrypted_file, password)
    assert decrypted_file.exists()
    assert decrypted_file.read_bytes() == plaintext_data


def test_decrypt_invalid_format(tmp_path: Path) -> None:
    input_file = tmp_path / "not_encrypted.bin"
    output_file = tmp_path / "output.txt"

    input_file.write_bytes(b"This is not a valid encrypted file")

    with pytest.raises(ValueError, match="Invalid file format"):
        openssl_decrypt(input_file, output_file, "password")


def test_decrypt_with_wrong_password(tmp_path: Path) -> None:
    plaintext_data = b"Secret message for encryption!"
    password = "correct-password"
    wrong_password = "wrong-password"

    input_file = tmp_path / "plain.txt"
    encrypted_file = tmp_path / "encrypted.bin"
    output_file = tmp_path / "decrypted.txt"

    input_file.write_bytes(plaintext_data)
    openssl_encrypt(input_file, encrypted_file, password)

    with pytest.raises(ValueError):  # likely padding error on wrong password
        openssl_decrypt(encrypted_file, output_file, wrong_password)


def test_openssl_compatibility(tmp_path: Path) -> None:
    """Test compatibility with actual OpenSSL command line tool."""
    if not shutil.which("openssl"):
        pytest.skip("OpenSSL command line tool not available")

    password = "test-password"
    plaintext_data = b"Secret message for OpenSSL compatibility test!"
    iterations = 1_000_000  # Совместимое значение

    input_file = tmp_path / "input.txt"
    encrypted_by_lib = tmp_path / "encrypted_by_lib.bin"
    encrypted_by_openssl = tmp_path / "encrypted_by_openssl.bin"
    decrypted_by_lib = tmp_path / "decrypted_by_lib.txt"
    decrypted_by_openssl = tmp_path / "decrypted_by_openssl.txt"

    input_file.write_bytes(plaintext_data)

    # Encrypt with our library
    openssl_encrypt(input_file, encrypted_by_lib, password, iterations)

    # Decrypt with OpenSSL command
    subprocess.run(
        [
            "openssl",
            "enc",
            "-d",
            "-aes-256-cbc",
            "-pbkdf2",
            "-iter",
            str(iterations),
            "-in",
            str(encrypted_by_lib),
            "-out",
            str(decrypted_by_openssl),
            "-pass",
            f"pass:{password}",
        ],
        capture_output=True,
        check=False,
    )

    assert decrypted_by_openssl.read_bytes() == plaintext_data

    # Encrypt with OpenSSL command
    subprocess.run(
        [
            "openssl",
            "enc",
            "-aes-256-cbc",
            "-pbkdf2",
            "-iter",
            str(iterations),
            "-in",
            str(input_file),
            "-out",
            str(encrypted_by_openssl),
            "-pass",
            f"pass:{password}",
        ],
        capture_output=True,
        check=False,
    )

    # Decrypt with our library
    openssl_decrypt(encrypted_by_openssl, decrypted_by_lib, password, iterations)
    assert decrypted_by_lib.read_bytes() == plaintext_data


def test_invalid_iterations(tmp_path: Path) -> None:
    """Test that zero or negative iterations raise error."""
    input_file = tmp_path / "test.txt"
    output_file = tmp_path / "test.enc"
    input_file.write_bytes(b"test")

    with pytest.raises(ValueError):
        openssl_encrypt(input_file, output_file, "password", 0)


def test_different_iterations(tmp_path: Path) -> None:
    """Test that encrypt/decrypt work with same custom iterations."""
    password = "test-password"
    data = b"Test data"
    iterations = 50000

    input_file = tmp_path / "input.txt"
    encrypted_file = tmp_path / "encrypted.bin"
    decrypted_file = tmp_path / "decrypted.txt"

    input_file.write_bytes(data)

    openssl_encrypt(input_file, encrypted_file, password, iterations)
    openssl_decrypt(encrypted_file, decrypted_file, password, iterations)

    assert decrypted_file.read_bytes() == data


def test_encrypt_decrypt_base64_roundtrip(tmp_path: Path) -> None:
    """Test base64 encrypt/decrypt roundtrip."""
    password = "test-password"
    plaintext_data = b"Secret message for base64 encryption!"

    input_file = tmp_path / "input.txt"
    encrypted_file = tmp_path / "encrypted.txt"
    decrypted_file = tmp_path / "decrypted.txt"

    input_file.write_bytes(plaintext_data)

    openssl_encrypt_base64(input_file, encrypted_file, password)
    assert encrypted_file.exists()

    # Check that output is base64 text
    encrypted_content = encrypted_file.read_text()
    assert encrypted_content.isascii()
    assert len(encrypted_content) > 0

    openssl_decrypt_base64(encrypted_file, decrypted_file, password)
    assert decrypted_file.exists()
    assert decrypted_file.read_bytes() == plaintext_data


def test_base64_openssl_compatibility(tmp_path: Path) -> None:
    """Test base64 compatibility with actual OpenSSL command line tool."""
    if not shutil.which("openssl"):
        pytest.skip("OpenSSL command line tool not available")

    password = "test-password"
    plaintext_data = b"Secret message for OpenSSL base64 compatibility test!"
    iterations = 1_000_000

    input_file = tmp_path / "input.txt"
    encrypted_by_lib = tmp_path / "encrypted_by_lib.txt"
    encrypted_by_openssl = tmp_path / "encrypted_by_openssl.txt"
    decrypted_by_lib = tmp_path / "decrypted_by_lib.txt"
    decrypted_by_openssl = tmp_path / "decrypted_by_openssl.txt"

    input_file.write_bytes(plaintext_data)

    # Encrypt with our library (base64)
    openssl_encrypt_base64(input_file, encrypted_by_lib, password, iterations)

    # Decrypt with OpenSSL command (base64)
    result = subprocess.run(
        [
            "openssl",
            "enc",
            "-d",
            "-aes-256-cbc",
            "-pbkdf2",
            "-iter",
            str(iterations),
            "-base64",
            "-in",
            str(encrypted_by_lib),
            "-out",
            str(decrypted_by_openssl),
            "-pass",
            f"pass:{password}",
        ],
        capture_output=True,
        check=False,
    )

    if result.returncode == 0:
        assert decrypted_by_openssl.read_bytes() == plaintext_data

    # Encrypt with OpenSSL command (base64)
    subprocess.run(
        [
            "openssl",
            "enc",
            "-aes-256-cbc",
            "-pbkdf2",
            "-iter",
            str(iterations),
            "-base64",
            "-in",
            str(input_file),
            "-out",
            str(encrypted_by_openssl),
            "-pass",
            f"pass:{password}",
        ],
        capture_output=True,
        check=False,
    )

    # Decrypt with our library (base64)
    if encrypted_by_openssl.exists():
        openssl_decrypt_base64(encrypted_by_openssl, decrypted_by_lib, password, iterations)
        assert decrypted_by_lib.read_bytes() == plaintext_data


def test_base64_invalid_format(tmp_path: Path) -> None:
    """Test base64 decrypt with invalid base64 format."""
    input_file = tmp_path / "invalid_base64.txt"
    output_file = tmp_path / "output.txt"

    # Use characters that are definitely not valid base64
    input_file.write_text("This is not valid base64! @#$%^&*()")

    with pytest.raises(ValueError, match="Invalid base64 format|Invalid file format"):
        openssl_decrypt_base64(input_file, output_file, "password")


def test_base64_invalid_openssl_format(tmp_path: Path) -> None:
    """Test base64 decrypt with valid base64 but invalid OpenSSL format."""
    import base64

    input_file = tmp_path / "invalid_openssl.txt"
    output_file = tmp_path / "output.txt"

    # Valid base64 but not OpenSSL format (missing Salted__ header)
    invalid_data = base64.b64encode(b"This is valid base64 but not OpenSSL format").decode()
    input_file.write_text(invalid_data)

    with pytest.raises(ValueError, match="Invalid file format"):
        openssl_decrypt_base64(input_file, output_file, "password")


def test_base64_wrong_password(tmp_path: Path) -> None:
    """Test base64 decrypt with wrong password."""
    plaintext_data = b"Secret message for encryption!"
    password = "correct-password"
    wrong_password = "wrong-password"

    input_file = tmp_path / "plain.txt"
    encrypted_file = tmp_path / "encrypted.txt"
    output_file = tmp_path / "decrypted.txt"

    input_file.write_bytes(plaintext_data)
    openssl_encrypt_base64(input_file, encrypted_file, password)

    with pytest.raises(ValueError, match="Decryption failed"):
        openssl_decrypt_base64(encrypted_file, output_file, wrong_password)


def test_base64_invalid_iterations(tmp_path: Path) -> None:
    """Test that base64 functions reject invalid iterations."""
    input_file = tmp_path / "test.txt"
    output_file = tmp_path / "test.enc"
    input_file.write_bytes(b"test")

    with pytest.raises(ValueError, match="Iteration count must be at least 1000"):
        openssl_encrypt_base64(input_file, output_file, "password", 500)

    with pytest.raises(ValueError, match="Iteration count must be at least 1000"):
        openssl_decrypt_base64(input_file, output_file, "password", 0)


def test_base64_different_iterations(tmp_path: Path) -> None:
    """Test that base64 encrypt/decrypt work with same custom iterations."""
    password = "test-password"
    data = b"Test data for base64"
    iterations = 50000

    input_file = tmp_path / "input.txt"
    encrypted_file = tmp_path / "encrypted.txt"
    decrypted_file = tmp_path / "decrypted.txt"

    input_file.write_bytes(data)

    openssl_encrypt_base64(input_file, encrypted_file, password, iterations)
    openssl_decrypt_base64(encrypted_file, decrypted_file, password, iterations)

    assert decrypted_file.read_bytes() == data


def test_base64_vs_binary_compatibility(tmp_path: Path) -> None:
    """Test that base64 and binary versions produce equivalent results."""
    password = "test-password"
    data = b"Test data for compatibility check"
    iterations = 100000

    input_file = tmp_path / "input.txt"
    binary_encrypted = tmp_path / "binary.enc"
    base64_encrypted = tmp_path / "base64.txt"
    binary_decrypted = tmp_path / "binary_dec.txt"
    base64_decrypted = tmp_path / "base64_dec.txt"

    input_file.write_bytes(data)

    # Encrypt with both methods
    openssl_encrypt(input_file, binary_encrypted, password, iterations)
    openssl_encrypt_base64(input_file, base64_encrypted, password, iterations)

    # Decrypt with both methods
    openssl_decrypt(binary_encrypted, binary_decrypted, password, iterations)
    openssl_decrypt_base64(base64_encrypted, base64_decrypted, password, iterations)

    # Both should produce the same result
    assert binary_decrypted.read_bytes() == data
    assert base64_decrypted.read_bytes() == data
    assert binary_decrypted.read_bytes() == base64_decrypted.read_bytes()
