"""Hashing, symmetric encryption, and public/private key encryption functions.

Example:
    >>> # hashing
    >>> from easyencrypt import hashText
    >>> message = "Hello, World!"
    >>> hashText(message)
    b'\xdf\xfd`!\xbb+\xd5\xb0\xafgb\x90\x80\x9e\xc3\xa51\x91\xdd\x81\xc7\xf7\nK(h\x8a6!\x82\x98o'
    >>> # symmetric encryption/decryption
    >>> from easyencrypt import newKey, passwordToKey, symmetricEncrypt, symmetricDecrypt
    >>> newKey()
    b'1h8_Z3LcL55r3ljklF_1fhKWy122zqDYWAJyQEZaKlA='
    >>> password = "password123"
    >>> key = passwordToKey(password)
    >>> key
    b'75K3eLr-dx6JJFuJ7LwIpEpOFmwGZZkRiB84PURz6U8='
    >>> ciphertext = symmetricEncrypt(message, key)
    >>> ciphertext
    b"\x80\x00\x00\x00\x00[B?\xe7\xbb\x825s\xff\xf3\x92AX|$\xf5\x19\x16\xe7f\x98\x8cgND\xf8\xdf\xd4Q\x00Y\xe5v\xb9\x0e\xa0\xa0\xb8\x05\x87N\xe6\x19h\x93K\xa9\xdb\x11\xef%V\xc2\xb1'\xa4;\xb8\xaf\xd2[\xdc\xb2\xae\xea\xca\xa4z"
    >>> symmetricDecrypt(ciphertext, key)
    b'Hello, World!'
    >>> # public/private key encryption/decryption
    >>> from easyencrypt import newKeyPair, encrypt, decrypt
    >>> pub, priv = newKeyPair()
    >>> ciphertext = encrypt(message, pub)
    >>> ciphertext
    b"\x01@H\x16\xe5\x01\xc0\x02)\x13\x8e\xba\xbb{p_5t\xf1\x81\x18y2\x12=t\xfe\xeb(\xcf\xce\xdd\xbd'\xb2\xddS\xbd\x0e\xc3\xf5\x0b-\xd8{\xe3W\xd5\xe8)_\xa8\xfb\x11\x8d\xb2\xb0l\x04\xf2>\xd9`\x0cS\xb9"
    >>> decrypt(ciphertext, priv)
    b'Hello, World!'
"""

import base64
import hashlib
import rsa
from rsa.bigfile import encrypt_bigfile, decrypt_bigfile
from cryptography.fernet import Fernet
from io import BytesIO

def hashText(text, algorithm="sha256"):
    """Hash some text."""
    try:
        text = text.encode()
    except:
        pass
    thehash = hashlib.new(algorithm, text).digest()
    return thehash

def newKey():
    """Generate a new symmetric key."""
    key = Fernet.generate_key()
    return key

def passwordToKey(password):
    """Convert a password into a useable encryption/decryption key."""
    try:
        password = password.encode()
    except:
        pass
    key = hashlib.sha256(password).digest()
    key = base64.urlsafe_b64encode(key)
    return key

def symmetricEncrypt(plaintext, key):
    """Encrypt text symmetrically with a key. Use passwordToKey if
    using a password instead of a generated key.
    """
    try:
        plaintext = plaintext.encode()
    except:
        pass
    cipher = Fernet(key)
    ciphertext = cipher.encrypt(plaintext)
    ciphertext = base64.urlsafe_b64decode(ciphertext)
    return ciphertext

def symmetricDecrypt(ciphertext, key):
    """Decrypt text symmetrically with a key. Use passwordToKey if
    using a password instead of a generated key.
    """
    try:
        ciphertext = ciphertext.encode()
    except:
        pass
    cipher = Fernet(key)
    ciphertext = base64.urlsafe_b64encode(ciphertext)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext

def newKeyPair(keysize=512):
    """Generate a new public/private key pair."""
    pub, priv = rsa.newkeys(keysize)
    return pub, priv

def encrypt(plaintext, pubKey):
    """Encrypt text with a public key."""
    try:
        plaintext = plaintext.encode()
    except:
        pass
    b = BytesIO()
    encrypt_bigfile(BytesIO(plaintext), b, pubKey)
    ciphertext = b.getvalue()
    return ciphertext

def decrypt(ciphertext, privKey):
    """Decrypt text with a private key."""
    try:
        ciphertext = ciphertext.encode()
    except:
        pass
    b = BytesIO()
    decrypt_bigfile(BytesIO(ciphertext), b, privKey)
    plaintext = b.getvalue()
    return plaintext
