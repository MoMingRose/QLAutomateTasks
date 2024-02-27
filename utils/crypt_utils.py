# -*- coding: utf-8 -*-
# crypt_utils.py created by MoMingLog on 13/12/2023.
"""
【作者】MoMingLog
【创建时间】2023-12-13
【功能描述】
"""
import base64
import binascii
from typing import Union

import rsa
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


# md5加密
def md5(s):
    import hashlib
    m = hashlib.md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def rsa_encrypt(
        data: str,
        public_key: str = None
):
    """
    ras加密
    :param data: 待加密数据
    :param public_key: 公钥
    :return: 加密后的数据, hex格式
    """

    if public_key is None:
        raise AttributeError("公钥不能为空")

    public_key_format = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"

    rsa_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key_format.encode())
    crypto = rsa.encrypt(data.encode(), rsa_key)
    return crypto.hex()


def aes_encrypt(data: Union[str, dict], common_key: str):
    """
    aes加密
    :param data: 待加密数据
    :param common_key: 加密密钥（key和iv相同）
    :return:
    """
    key = base64.b64decode(common_key)
    iv = base64.b64decode(common_key)

    # 判断data的类型
    if isinstance(data, dict):
        # 如果是字典类型，则转换为json字符串
        import json
        data = json.dumps(data, separators=(',', ':'))

    plaintext = data.encode('utf-8')

    # 确保数据长度是16字节的整数倍
    padded_plaintext = pad(plaintext, AES.block_size)

    # 创建AES加密器对象
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # 进行加密并返回加密后的hex结果
    ciphertext = cipher.encrypt(padded_plaintext)
    return binascii.hexlify(ciphertext).decode('utf-8').upper()


def aes_decrypt(data: str, common_key: str):
    """
    aes解密
    :param data: 待解密数据
    :param common_key: 解密密钥（key和iv相同）
    :return:
    """
    key = base64.b64decode(common_key)
    iv = base64.b64decode(common_key)

    ciphertext = binascii.unhexlify(data)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    padded_plaintext = cipher.decrypt(ciphertext)

    try:
        plaintext = padded_plaintext.decode("utf-8")[:-6]
        return plaintext
    except UnicodeDecodeError:
        return None
