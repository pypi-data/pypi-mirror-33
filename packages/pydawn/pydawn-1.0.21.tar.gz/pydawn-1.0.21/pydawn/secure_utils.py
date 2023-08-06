# coding=utf-8
import rsa
from Crypto.Cipher import AES
from Crypto import Random
import binascii

buffer_size = 1024 * 1024 * 16


class RsaUtil:

    def __init__(self, public_key_file=None, private_key_file=None):
        self.max_buffer_room = 245
        self.rsa_block_size = 256
        if public_key_file is not None:
            self.load_rsa_pub_key(public_key_file)
        else:
            self.pub_key = None

        if private_key_file is not None:
            self.load_rsa_pri_key(private_key_file)
        else:
            self.pri_key = None

    def gen_rsa_key_pair(self, public_key_file, private_key_file):
        (self.pub_key, self.pri_key) = rsa.newkeys(2048)
        with open(public_key_file, 'w+') as f:
            f.write(self.pub_key.save_pkcs1().decode())

        with open(private_key_file, 'w+') as f:
            f.write(self.pri_key.save_pkcs1().decode())

    def load_rsa_pub_key(self, public_key_file):
        with open(public_key_file, 'r') as f:
            self.pub_key = rsa.PublicKey.load_pkcs1(f.read().encode())

    def load_rsa_pri_key(self, private_key_file):
        with open(private_key_file, 'r') as f:
            self.pri_key = rsa.PrivateKey.load_pkcs1(f.read().encode())

    def rsa_encrypt_string(self, msg):
        return rsa.encrypt(msg, self.pub_key)

    def rsa_decrypt_string(self, msg):
        return rsa.decrypt(msg, self.pri_key)

    def rsa_encrypt_file(self, input_file_path, output_file_path):
        output_file = open(output_file_path, "wb+")
        with open(input_file_path, "rb") as f:
            file_buffer = f.read(self.max_buffer_room)
            while file_buffer != "":
                content = self.rsa_encrypt_string(file_buffer)
                output_file.write(content)
                file_buffer = f.read(self.max_buffer_room)

        output_file.close()

    def rsa_decrypt_file(self, input_file_path, output_file_path):
        output_file = open(output_file_path, "wb+")
        with open(input_file_path, "rb") as f:
            file_buffer = f.read(self.rsa_block_size)
            while file_buffer != "":
                content = self.rsa_decrypt_string(file_buffer)
                output_file.write(content)
                file_buffer = f.read(self.rsa_block_size)

        output_file.close()


class AesUtil:

    def __init__(self, aes_key_path=None):
        if aes_key_path is not None:
            self.load_aes_key_iv(aes_key_path)
        else:
            self.key = None
            self.iv = None

    def gen_aes_key_iv(self, aes_key_path):
        self.key = Random.new().read(AES.block_size)
        self.iv = Random.new().read(AES.block_size)
        ase_file = open(aes_key_path, "wb+")
        ase_file.write(self.key)
        ase_file.write(self.iv)
        ase_file.close()

    def load_aes_key_iv(self, aes_key_path):
        ase_file = open(aes_key_path, "rb")
        self.key = ase_file.read(AES.block_size)
        self.iv = ase_file.read(AES.block_size)
        ase_file.close()

    def aes_encrypt_string(self, msg):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        mode = len(msg) % AES.block_size
        msg = msg + " " * (AES.block_size - mode)
        return cipher.encrypt(msg)

    def aes_decrypt_string(self, msg):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return cipher.decrypt(msg).strip()

    def aes_encrypt_file(self, input_path, out_path):
        encrypt_file = open(out_path, "wb+")
        with open(input_path, "rb") as f:
            file_buffer = f.read(buffer_size)
            while file_buffer != "":
                buffer_enc = self.aes_encrypt_string(file_buffer)
                encrypt_file.write(buffer_enc)
                file_buffer = f.read(buffer_size)

        encrypt_file.close()

    def aes_decrypt_file(self, input_path, out_path):
        decrypt_file = open(out_path, "wb+")
        with open(input_path, "rb") as f:
            file_buffer = f.read(buffer_size)
            while file_buffer != "":
                buffer_dec = self.aes_decrypt_string(file_buffer)
                decrypt_file.write(buffer_dec)
                file_buffer = f.read(buffer_size)

        decrypt_file.close()


if __name__ == '__main__':
    # gen_rsa_key_pair("zc.pub", "zc.pri")
    # aes_file_path = "zc.aes"
    # aes_util = AesUtil(aes_file_path)
    # aes_util.aes_encrypt_file("zc.rar", "zc.rar.enc")
    # aes_util.aes_decrypt_file("zc.rar.enc", "zc.rar.enc.rar")

    pub_key_file = "test.pub"
    pri_key_file = "test.pri"
    rsa_util = RsaUtil(pub_key_file, pri_key_file)

    ori_str = "zhangchao"
    str_encrypt = rsa_util.rsa_encrypt_string(ori_str)
    str_decrypt = rsa_util.rsa_decrypt_string(str_encrypt)
    print str_decrypt

    rsa_util.rsa_encrypt_file("pydawn.zip", "pydawn.zip.rsa.enc")
    rsa_util.rsa_decrypt_file("pydawn.zip.rsa.enc", "pydawn.rar.rsa.dec.zip")
