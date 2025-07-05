import os

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def generate_key(password: str, key_length: int = 64) -> bytes:
    """
    将密码转换为固定长度的十六进制密钥

    :param password: 原始密码字符串
    :param key_length: 密钥长度（字符数，默认为64）
    :return: 字节类型的密钥
    """
    hex_key = ""
    for char in password:
        hex_char = hex(ord(char))[2:]
        hex_key += hex_char.zfill(2)

    if len(hex_key) > key_length:
        hex_key = hex_key[:key_length]
    else:
        hex_key = hex_key.ljust(key_length, "0")

    return bytes.fromhex(hex_key)


def encrypt_password(password: str) -> str:
    """
    加密密码（使用AES-CBC模式）

    :param password: 原始密码字符串
    :return: IV + 密文的十六进制字符串
    """
    key = generate_key(password)
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(password.encode("utf-8"), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return iv.hex() + encrypted_data.hex()


def decrypt_password(encrypted_str: str, password: str) -> str:
    """
    解密密码

    :param encrypted_str: IV + 密文的十六进制字符串
    :param password: 原始密码（用于生成密钥）
    :return: 解密后的原始密码
    """
    iv_hex = encrypted_str[:32]
    ciphertext_hex = encrypted_str[32:]
    iv = bytes.fromhex(iv_hex)
    ciphertext = bytes.fromhex(ciphertext_hex)
    key = generate_key(password)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(ciphertext)
    return decrypted_data.rstrip(b"\x00").decode("utf-8")
