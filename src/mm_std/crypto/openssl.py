from base64 import b64decode, b64encode
from hashlib import pbkdf2_hmac
from os import urandom
from pathlib import Path

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

MAGIC = b"Salted__"
SALT_SIZE = 8
KEY_SIZE = 32  # for AES-256
IV_SIZE = 16


def openssl_encrypt(input_path: Path, output_path: Path, password: str, iterations: int = 1_000_000) -> None:
    """
    Encrypt a file using OpenSSL-compatible AES-256-CBC with PBKDF2 and output in binary format.

    This function creates encrypted files that are fully compatible with OpenSSL command:
    openssl enc -aes-256-cbc -pbkdf2 -iter 1000000 -salt -in message.txt -out message.enc

    Args:
        input_path: Path to the input file to encrypt
        output_path: Path where the encrypted binary file will be saved
        password: Password for encryption
        iterations: Number of PBKDF2 iterations (minimum 1000, default 1,000,000)

    Raises:
        ValueError: If iterations < 1000

    Example:
        >>> from pathlib import Path
        >>> openssl_encrypt(Path("secret.txt"), Path("secret.enc"), "mypassword")

        # Decrypt with OpenSSL:
        # openssl enc -d -aes-256-cbc -pbkdf2 -iter 1000000 -in secret.enc -out secret_decrypted.txt -pass pass:mypassword
    """
    if iterations < 1000:
        raise ValueError("Iteration count must be at least 1000 for security")

    data: bytes = input_path.read_bytes()
    salt: bytes = urandom(SALT_SIZE)

    key_iv: bytes = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, KEY_SIZE + IV_SIZE)
    key: bytes = key_iv[:KEY_SIZE]
    iv: bytes = key_iv[KEY_SIZE:]

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data: bytes = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext: bytes = encryptor.update(padded_data) + encryptor.finalize()

    output_path.write_bytes(MAGIC + salt + ciphertext)


def openssl_decrypt(input_path: Path, output_path: Path, password: str, iterations: int = 1_000_000) -> None:
    """
    Decrypt a binary file created by OpenSSL-compatible AES-256-CBC with PBKDF2.

    This function decrypts files that were encrypted with OpenSSL command:
    openssl enc -aes-256-cbc -pbkdf2 -iter 1000000 -salt -in message.txt -out message.enc

    Args:
        input_path: Path to the encrypted binary file
        output_path: Path where the decrypted file will be saved
        password: Password for decryption
        iterations: Number of PBKDF2 iterations (minimum 1000, default 1,000,000)

    Raises:
        ValueError: If iterations < 1000, invalid file format, or wrong password

    Example:
        >>> from pathlib import Path
        >>> openssl_decrypt(Path("secret.enc"), Path("secret_decrypted.txt"), "mypassword")

        # Encrypt with OpenSSL:
        # openssl enc -aes-256-cbc -pbkdf2 -iter 1000000 -salt -in secret.txt -out secret.enc -pass pass:mypassword
    """
    if iterations < 1000:
        raise ValueError("Iteration count must be at least 1000 for security")

    raw: bytes = input_path.read_bytes()
    if not raw.startswith(MAGIC):
        raise ValueError("Invalid file format: missing OpenSSL Salted header")

    salt: bytes = raw[8:16]
    ciphertext: bytes = raw[16:]

    key_iv: bytes = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, KEY_SIZE + IV_SIZE)
    key: bytes = key_iv[:KEY_SIZE]
    iv: bytes = key_iv[KEY_SIZE:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_plaintext: bytes = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    try:
        plaintext: bytes = unpadder.update(padded_plaintext) + unpadder.finalize()
    except ValueError as e:
        raise ValueError("Decryption failed: invalid padding or wrong password") from e

    output_path.write_bytes(plaintext)


def openssl_encrypt_base64(input_path: Path, output_path: Path, password: str, iterations: int = 1_000_000) -> None:
    """
    Encrypt a file using OpenSSL-compatible AES-256-CBC with PBKDF2 and output in base64 format.

    This function creates encrypted files that are fully compatible with OpenSSL command:
    openssl enc -aes-256-cbc -pbkdf2 -iter 1000000 -salt -base64 -in message.txt -out message.enc

    Args:
        input_path: Path to the input file to encrypt
        output_path: Path where the encrypted base64 file will be saved
        password: Password for encryption
        iterations: Number of PBKDF2 iterations (minimum 1000, default 1,000,000)

    Raises:
        ValueError: If iterations < 1000

    Example:
        >>> from pathlib import Path
        >>> openssl_encrypt_base64(Path("secret.txt"), Path("secret.enc"), "mypassword")

        # Decrypt with OpenSSL:
        # openssl enc -d -aes-256-cbc -pbkdf2 -iter 1000000 -base64 -in secret.enc -out secret_decrypted.txt -pass pass:mypassword
    """
    if iterations < 1000:
        raise ValueError("Iteration count must be at least 1000 for security")

    data: bytes = input_path.read_bytes()
    salt: bytes = urandom(SALT_SIZE)

    key_iv: bytes = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, KEY_SIZE + IV_SIZE)
    key: bytes = key_iv[:KEY_SIZE]
    iv: bytes = key_iv[KEY_SIZE:]

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data: bytes = padder.update(data) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext: bytes = encryptor.update(padded_data) + encryptor.finalize()

    # Encode binary data to base64
    binary_data: bytes = MAGIC + salt + ciphertext
    base64_data: str = b64encode(binary_data).decode("ascii")
    output_path.write_text(base64_data)


def openssl_decrypt_base64(input_path: Path, output_path: Path, password: str, iterations: int = 1_000_000) -> None:
    """
    Decrypt a base64-encoded file created by OpenSSL-compatible AES-256-CBC with PBKDF2.

    This function decrypts files that were encrypted with OpenSSL command:
    openssl enc -aes-256-cbc -pbkdf2 -iter 1000000 -salt -base64 -in message.txt -out message.enc

    Args:
        input_path: Path to the encrypted base64 file
        output_path: Path where the decrypted file will be saved
        password: Password for decryption
        iterations: Number of PBKDF2 iterations (minimum 1000, default 1,000,000)

    Raises:
        ValueError: If iterations < 1000, invalid file format, or wrong password

    Example:
        >>> from pathlib import Path
        >>> openssl_decrypt_base64(Path("secret.enc"), Path("secret_decrypted.txt"), "mypassword")

        # Encrypt with OpenSSL:
        # openssl enc -aes-256-cbc -pbkdf2 -iter 1000000 -salt -base64 -in secret.txt -out secret.enc -pass pass:mypassword
    """
    if iterations < 1000:
        raise ValueError("Iteration count must be at least 1000 for security")

    # Decode base64 to binary data
    try:
        base64_data: str = input_path.read_text().strip()
        raw: bytes = b64decode(base64_data)
    except Exception as e:
        raise ValueError("Invalid base64 format") from e

    if not raw.startswith(MAGIC):
        raise ValueError("Invalid file format: missing OpenSSL Salted header")

    salt: bytes = raw[8:16]
    ciphertext: bytes = raw[16:]

    key_iv: bytes = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, KEY_SIZE + IV_SIZE)
    key: bytes = key_iv[:KEY_SIZE]
    iv: bytes = key_iv[KEY_SIZE:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_plaintext: bytes = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    try:
        plaintext: bytes = unpadder.update(padded_plaintext) + unpadder.finalize()
    except ValueError as e:
        raise ValueError("Decryption failed: invalid padding or wrong password") from e

    output_path.write_bytes(plaintext)
