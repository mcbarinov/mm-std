from mm_std import fernet_decrypt, fernet_encrypt, fernet_generate_key


def test_fernet_generate_key():
    assert len(fernet_generate_key()) == 44
    assert fernet_generate_key() != fernet_generate_key()


def test_fernet_encrypt():
    key = "vI_keS83qo0zCD1T5gltNT7aj4O-IAggD_rd7LmUeDg="
    encoded_data = fernet_encrypt(data="hello world", key=key)
    assert fernet_decrypt(encoded_data=encoded_data, key=key) == "hello world"


def test_fernet_decrypt():
    key = "vI_keS83qo0zCD1T5gltNT7aj4O-IAggD_rd7LmUeDg="
    encoded_data = "gAAAAABl9UFKXsY7dcUFpyJuev7_AeBitLnySq7amsFdrlSjMZJreeoTpBtAOJFVSY_OLgouxymX8Qt7kIuhygZLVihaQ68y3A=="
    assert fernet_decrypt(encoded_data=encoded_data, key=key) == "hello world"
