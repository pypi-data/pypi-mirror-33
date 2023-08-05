#!/usr/bin/env python3

"""Python 3 ready and reusable version of a script found online.

Original source: https://gist.github.com/mahmoudimus/1654254

with help and inspiration from
* ASN1_generate_nconf(3) (specifically the SubjectPublicKeyInfo structure)
* http://www.sysmic.org/dotclear/index.php?post/2010/03/24/Convert-keys-betweens-GnuPG%2C-OpenSsh-and-OpenSSL
* http://blog.oddbit.com/2011/05/converting-openssh-public-keys.html

# the unix way of doing it:
# Convert ssh-rsa key to pem
# ssh-keygen -f infile.pub -e -m PKCS8 > outfile.pem
# Encrypt a file using public key pem
# openssl rsautl -encrypt -inkey public.pem -pubin -in file.txt -out file.ssl
# Decrypt using private key
# openssl rsautl -decrypt -inkey private.pem -in file.ssl -out decrypted.txt
"""

import ast
# import sys
import base64
import struct
from pyasn1.type import univ
from pyasn1.codec.der import encoder as der_encoder
# , decoder as der_decoder

PEM_TEMPLATE = '''-----BEGIN PUBLIC KEY-----
{}{}
-----END PUBLIC KEY-----
'''


'''
def openssh_public_key_to_pem(public_key: str) -> str:
    openssh_intro = 'ssh-rsa '
    intro = '-----BEGIN RSA PUBLIC KEY-----\n'
    outro = '\n-----END RSA PUBLIC KEY-----'
    public_key = public_key.replace(openssh_intro, intro)
    public_key = public_key[:public_key.rindex(' ')] + outro
    return public_key
'''


def convert(public_key: str) -> str:
    """Convert given """

    if not isinstance(public_key, str):
        raise TypeError()

    keyfields = public_key.split(None)
    if len(keyfields) < 3:
        # there might not be a comment, so pad it
        keyfields.append("")
    keytype, keydata, keycomment = keyfields

    if keytype != 'ssh-rsa':
        raise ValueError("key type does not appear to be ssh-rsa")

    keydata = base64.b64decode(keydata)

    parts = []
    while keydata:
        # read the length of the data
        dlen = struct.unpack('>I', keydata[:4])[0]

        # read in <length> bytes
        data, keydata = keydata[4:dlen+4], keydata[4+dlen:]

        parts.append(data)

    # parts[1]
    # [bytes([x]) for x in parts[1]]
    # [struct.unpack('B', bytes(x)) for x in parts[1]]

    # ast.literal_eval
    unpack_byte = lambda x: '%02X' % struct.unpack('B', bytes([x]))[0]
    unpack = lambda part: '0x' + ''.join([unpack_byte(x) for x in part])

    e_val = ast.literal_eval(unpack(parts[1]))
    n_val = ast.literal_eval(unpack(parts[2]))

    bitstring = univ.Sequence()
    bitstring.setComponentByPosition(0, univ.Integer(n_val))
    bitstring.setComponentByPosition(1, univ.Integer(e_val))

    bitstring = der_encoder.encode(bitstring)

    bitstring = ''.join([('00000000'+bin(ord(x))[2:])[-8:] for x in list(bitstring)])

    bitstring = univ.BitString("'%s'B" % bitstring)

    pubkeyid = univ.Sequence()
    pubkeyid.setComponentByPosition(0, univ.ObjectIdentifier('1.2.840.113549.1.1.1'))
    # == OID for rsaEncryption
    pubkeyid.setComponentByPosition(1, univ.Null(''))

    pubkey_seq = univ.Sequence()
    pubkey_seq.setComponentByPosition(0, pubkeyid)
    pubkey_seq.setComponentByPosition(1, bitstring)

    base64.MAXBINSIZE = (64//4)*3
    # this actually doesn't matter, but it helped with comparing to openssl's output

    output = PEM_TEMPLATE.format(
        'X-Comment: {}\n\n'.format(keycomment) if keycomment else '',
        base64.encodestring(der_encoder.encode(pubkey_seq)))

    # print "-----BEGIN PUBLIC KEY-----"
    # if keycomment:
    #    print "X-Comment: " + keycomment
    #    print
    # base64.MAXBINSIZE = (64//4)*3
    # # this actually doesn't matter, but it helped with comparing to openssl's output
    # print base64.encodestring(der_encoder.encode(pubkey_seq)),
    # print '-----END PUBLIC KEY-----'

    return output

public_key = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCuGIo6Ge/sbpT+N1N6JWTxBtCq6kv+16DrXOfOePUjKyBgGPt7y8Ihnt/xTXy1WNocUBo77TdVMbvQoBOsx3RLcOAtZNn7ZaieVoZpLlfftUxbObvhu/u0loDJLV9LVFVuNBfAQRwX3dj7kgD8tgGBkFoVTA1N6XTzy38yqVVWxeUkA4wsaoYgiU9noYQc9wWa2tN3qr+WwMb4+1ZzEoWoEEeMbcH3mxRIA2VxkpJwfeQ6W8ESWyf1ur5BU/RpkxghClAlsgoTGP76Sq/zulezLc1Er6pJS2IKMRO8cF2YOiojYCITfAggVnfWNcO+pBpiYpnkgSuMbjRpKSZ0kQZTv++p+/DrCvx+BLieHBtmHzRwf10GwDixbvFZeyIrYlv0Q4zMtYv5AyussuG8Q8XcWGb+/NUXFQepdrUrsnChyQIkb116gwO57LTDXsL1AAKsR8wyyTXjddrVEQbrMKvf+09awUZonf8kuNgnxoZj7p2mh4v3QIrP/m+vpGILNyHuGXtuUG0F9+lDNaEtTQduvVkymodz/kqYyfp1vu8u9SUSFUJ3Mqwp1L0fju8Zv71cJZMKPYpoOptaJbRtTqxiY2ltYkH4+kSmszXaoXYGrCOxGEgcb4SzbFR9s+7VqDVz3waxGpvScWe4tjyHMzt8m26AXurHjMAqlFPQe3LtqQ== mbLab-mb@mbdev.pl'

convert(public_key)
