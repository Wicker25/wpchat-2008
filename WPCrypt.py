#!/usr/bin/python
# -*- coding: UTF-8 -*-
#=================================================================================
#        Name: WPCHAT - Crypto Library
#        Author:   wicker25 (http://hackerforum.devil.it/  -  wicker25@gmail.com)
#        Description: Crypto Library
#        Licence: GPL
#        Version: 0.1
#=================================================================================

from Crypto.Cipher import ARC4, DES3

def DataEncrypt(key, data, mode):
    try:
        if mode == "ARC4":
            EncryptRC4 = ARC4.new(key)
            CData = EncryptRC4.encrypt(data)
            return CData
        if mode == "DES3":
            EncryptDES3 = DES3.new(key, DES3.MODE_ECB)
            if len(data)%8 > 0:
                data = data+' '*(DES3.block_size-len(data)%DES3.block_size)
            CData = EncryptDES3.encrypt(data)
            return CData
    except:
        return "Error"


def DataDecrypt(key, data, mode):
    try:
        if mode == "ARC4":
            DecryptRC4 = ARC4.new(key)
            WData = DecryptRC4.decrypt(data)
            return WData
        if mode == "DES3":
            DecryptDES3 = DES3.new(key, DES3.MODE_ECB)
            WData = DecryptDES3.decrypt(data)
            return WData
    except:
        return "Error"


if __name__ == '__main__':
    data = DataEncrypt("chiave", "evviva!", "ARC4")
    print "Encrypt ARC4:", data
    data = DataDecrypt("chiave", data, "ARC4")
    print "Decrypt ARC4:", data
    data = DataEncrypt("1122334455667788", "0"*128, "DES3")
    print "Encrypt DES3:", data
    data = DataDecrypt("1122334455667788", data, "DES3")
    print "Decrypt DES3:", data
