import base64
from Crypto.Cipher import AES

AES_TYPES = [128, 192, 256]
BLOCK_SIZE = {128:16, 192:24, 256:32}

class AESCipher:
    '''
    PyCrypto AES using ECB mode implementation in Python 3.3.  
    This uses very basic 0x00 padding, I would recommend PKCS5/7.
    '''

    def __init__(self, key):
        '''
        The constructor takes in a PLAINTEXT string as the key and converts it
        to a byte string to work with throughout the class.
        '''
        self.key = bytes(key, 'utf-8')
        self.iv = bytes(key[0:16], 'utf-8')
        
    def __pad(self, text):
        '''
        This right pads the raw text with 0x00 to force the text to be a
        multiple of 16.  This is how the CFX_ENCRYPT_AES tag does the padding.
        
        @param raw: String of clear text to pad
        @return: byte string of clear text with padding
        '''
        text_length = len(text)
        amount_to_pad = 16 - (text_length % 16)
        if amount_to_pad == 0:
            amount_to_pad = 16
        pad = chr(amount_to_pad)
        return text + pad * amount_to_pad
    
    def __unpad(self, text):
        '''
        This strips all of the 0x00 from the string passed in. 
        
        @param s: the byte string to unpad
        @return: unpadded byte string
        '''
        pad = ord(text[-1])
        return text[:-pad]
    
    def encrypt(self, raw):
        '''
        Takes in a string of clear text and encrypts it.
        
        @param raw: a string of clear text
        @return: a string of encrypted ciphertext
        '''
        raw = bytes(self.__pad(raw), 'utf-8')
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(cipher.encrypt(raw)) 
    
    def decrypt(self, enc):
        '''
        Takes in a string of ciphertext and decrypts it.
        
        @param enc: encrypted string of ciphertext
        @return: decrypted string of clear text
        '''
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv )
        return self.__unpad(cipher.decrypt(enc).decode("utf-8"))
        