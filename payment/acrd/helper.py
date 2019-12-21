import hashlib
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from framework.settings import ACRD_IV, ACRD_KEY, ACRD_PAYCODE


def encrypt(data):
    data = str.encode(data)
    cipher = AES.new(ACRD_KEY.encode('utf-8'), AES.MODE_CBC, ACRD_IV.encode('utf-8'))
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    ct = b64encode(ct_bytes).decode('utf-8')
    return ct


def decrypt(data):
    data = b64decode(data)
    cipher = AES.new(ACRD_KEY.encode('utf-8'), AES.MODE_CBC, ACRD_IV.encode('utf-8'))
    ct_bytes = cipher.decrypt(data)
    ct_bytes = str(unpad(ct_bytes, AES.block_size), 'utf-8')
    return ct_bytes


def getTransactionPayload(amount, transactionID):
    plaintext = "transactionId=VIDYUT"+str(transactionID)+"|amount="+str(amount)+"|purpose="+str(ACRD_PAYCODE)+"|currency=inr"
    checksum = hashlib.md5(plaintext.encode())
    checksum = checksum.hexdigest()
    pwc = plaintext + "|checkSum=" + checksum
    encodedData = encrypt(pwc)
    return {
        'encdata': encodedData,
        'code': ACRD_PAYCODE
    }


def decryptPayload(data):
    data = decrypt(data)
    # Parse decrypted transaction data from ACRD to JSON
    data = data.replace('=', '" : "')
    data = data.replace('|', '", "')
    return '{ "' + data + '"}'
