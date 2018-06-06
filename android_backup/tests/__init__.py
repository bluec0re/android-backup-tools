import unittest
import base64
import io
import pickle
import tarfile
import time

from android_backup import AndroidBackup, EncryptionType, CompressionType


class UnpackTest(unittest.TestCase):
    # def setUp(self):
    #     self.startTime = time.time()

    # def tearDown(self):
    #     t = time.time() - self.startTime
    #     print("%s: %.3f" % (self.id(), t))

    def test_compressed_stream(self):
        with AndroidBackup(io.BytesIO(TEST_DATA_NONENC)) as ab:
            self.assertEqual(ab.version, 3)
            self.assertEqual(ab.encryption, EncryptionType.NONE)
            self.assertEqual(ab.compression, CompressionType.ZLIB)

            names = list(map(lambda f: f.name, ab.get_files()))
            self.assertListEqual(names, TEST_MEMBERS_NAMES)

            tar = ab.read_data()
            with self.assertRaisesRegex(tarfile.StreamError, 'seeking backwards is not allowed'):
                tar.extractfile(
                    'apps/eu.bluec0re.android-backup/r/settings.cfg').read()

    def test_compressed_nonstream(self):
        with AndroidBackup(io.BytesIO(TEST_DATA_NONENC), stream=False) as ab:
            self.assertEqual(ab.version, 3)
            self.assertEqual(ab.encryption, EncryptionType.NONE)
            self.assertEqual(ab.compression, CompressionType.ZLIB)

            names = list(map(lambda f: f.name, ab.get_files()))
            self.assertListEqual(names, TEST_MEMBERS_NAMES)

            tar = ab.read_data()
            tar.extractfile(
                'apps/eu.bluec0re.android-backup/r/settings.cfg').read()

    def test_encrypted_stream(self):
        with AndroidBackup(io.BytesIO(TEST_DATA_ENC_TEST), password='test') as ab:
            self.assertEqual(ab.version, 3)
            self.assertEqual(ab.encryption, EncryptionType.AES256)
            self.assertEqual(ab.compression, CompressionType.ZLIB)

            names = list(map(lambda f: f.name, ab.get_files()))
            self.assertListEqual(names, TEST_MEMBERS_NAMES)

            tar = ab.read_data()
            with self.assertRaisesRegex(tarfile.StreamError, 'seeking backwards is not allowed'):
                tar.extractfile(
                    'apps/eu.bluec0re.android-backup/r/settings.cfg').read()

    def test_encrypted_nonstream(self):
        with AndroidBackup(io.BytesIO(TEST_DATA_ENC_TEST), password='test', stream=False) as ab:
            self.assertEqual(ab.version, 3)
            self.assertEqual(ab.encryption, EncryptionType.AES256)
            self.assertEqual(ab.compression, CompressionType.ZLIB)

            names = list(map(lambda f: f.name, ab.get_files()))
            self.assertListEqual(names, TEST_MEMBERS_NAMES)

            tar = ab.read_data()
            tar.extractfile(
                'apps/eu.bluec0re.android-backup/r/settings.cfg').read()


TEST_MEMBERS = pickle.loads(base64.b64decode("""
gAJdcQAoY3RhcmZpbGUKVGFySW5mbwpxASmBcQJOfXEDKFgEAAAAbmFtZXEEWCkAAABhcHBzL2V1
LmJsdWVjMHJlLmFuZHJvaWQtYmFja3VwL19tYW5pZmVzdHEFWAQAAABtb2RlcQZNpAFYAwAAAHVp
ZHEHTegDWAMAAABnaWRxCEtkWAQAAABzaXplcQlNuwVYBQAAAG10aW1lcQpKqUjwWVgGAAAAY2hr
c3VtcQtN3SBYBAAAAHR5cGVxDGNfY29kZWNzCmVuY29kZQpxDVgBAAAAMHEOWAYAAABsYXRpbjFx
D4ZxEFJxEVgIAAAAbGlua25hbWVxElgAAAAAcRNYBQAAAHVuYW1lcRRYCAAAAGJsdWVjMHJlcRVY
BQAAAGduYW1lcRZYBQAAAHVzZXJzcRdYCAAAAGRldm1ham9ycRhLAFgIAAAAZGV2bWlub3JxGUsA
WAYAAABvZmZzZXRxGksAWAsAAABvZmZzZXRfZGF0YXEbTQACWAsAAABwYXhfaGVhZGVyc3EcfXEd
WAYAAABzcGFyc2VxHk51hnEfYmgBKYFxIE59cSEoaARYLgAAAGFwcHMvZXUuYmx1ZWMwcmUuYW5k
cm9pZC1iYWNrdXAvci9zZXR0aW5ncy5jZmdxImgGTaQBaAdN6ANoCEtkaAlLCGgKSg9J8FloC02K
ImgMaBFoEmgTaBRYCAAAAGJsdWVjMHJlcSNoFlgFAAAAdXNlcnNxJGgYSwBoGUsAaBpNAAhoG00A
CmgcfXElaB5OdYZxJmJoASmBcSdOfXEoKGgEWCkAAABhcHBzL2V1LmJsdWVjMHJlLmFuZHJvaWQt
YmFja3VwL2RiL2Zvby5kYnEpaAZNpAFoB03oA2gIS2RoCU0AIGgKSrpJ8FloC01LIGgMaBFoEmgT
aBRYCAAAAGJsdWVjMHJlcSpoFlgFAAAAdXNlcnNxK2gYSwBoGUsAaBpNAAxoG00ADmgcfXEsaB5O
dYZxLWJoASmBcS5OfXEvKGgEWCoAAABhcHBzL2V1LmJsdWVjMHJlLmFuZHJvaWQtYmFja3VwL3Nw
L2Zvby54bWxxMGgGTaQBaAdN6ANoCEtkaAlLNmgKSuBJ8FloC035IGgMaBFoEmgTaBRYCAAAAGJs
dWVjMHJlcTFoFlgFAAAAdXNlcnNxMmgYSwBoGUsAaBpNAC5oG00AMGgcfXEzaB5OdYZxNGJlLg==
"""))
TEST_MEMBERS_NAMES = list(map(lambda f: f.name, TEST_MEMBERS))

TEST_DATA_NONENC = base64.b64decode("""
QU5EUk9JRCBCQUNLVVAKMwoxCm5vbmUKeJztml2LXEUQhmdFvBgQhQjeDrlS0N2u7uov2SRGyV1u
1NyKdHVXh8XsB7OzIT/QP+I/8T2bZIlCsrIJkUg9O7Nn+nSf7vp4q88MnHZ2dn6gF/vy5EK72+p+
Oxnb06PxrbT++8XZwW/H7eRo6vludXMcSMzLkXJ0l2163l7wKYcVBcrsmH2klfOUQlxt3Fus+a+5
ON+1LUx5GYDXj9Pt+RvmeeHM1fEDgdavT/46rX1c99Pjl+f3n+rJODp5vHZrWgdXvPPSL4/U2HlX
nWtaZqA2KBap0Y3g3HDJVd9K4lLSzGgT/sRF5wIuCviMURWjQoyOXSKc5hhjIMJHN696guuusE89
xxQ5BJd9isGREmYNFDLeLviAc6FctpcL2yu9hF7+e++7sWGJgfev9ZYWb7EsRmEu93y8a85fHgmX
pZJjSYIaUKckXMfkyBQ6txJqlMiKOgkkqUfm4mvmNJ2vPtEcvrriRFsaXXrL0VOpY3iakedsCAlp
n3kK7A3KFfMN8lFhOXuPRXwZ3FOqEzP6GGDF6LV6r9X3wToIxdlTiVWo1jJbLaV7RSiqJ9en69Rq
TTLLaKm5rm0iurVGH/ro6jnUwmHiisGE6Ufh5EZsLddeC/IykqI/1JalZ19nUT/g/fRecscCNIKf
cLBI1lG5ujokM+UcRWtWTJ4RAGRZRRFwlllVi59ELec8ecDAWGjCKYLZ8IMr4tQVC4eiOdZcIGWn
MWhDpoqWqOqdIpktUBGYVwaaDL+Rggjf0KoaKjJEsxSPU6EOhLp1V3vHUM4aKbKIaIyChEnOI8IB
DUu0EEZHNUMUOfW6iHDRgaM3V8wLDWFkoJQ6c2VBxKcqdYUsvU5JQ1pocD7EXnX4MSJCmCWGmboq
Q64DJudR0yQkqE1mlpgUWROnpSlGVS1LQkPyqWIypCL5CPHVNtJSYBHLZykhppHqyKFB4gF1D5V1
pBd6UobTLNxnChDrqCVoz01qytjzaTSeqRCXGiKJKjLPEDIUlpN6eFAiTahkyCIIaMcnhymDS6IT
wVoS0Cf7HEeDLQ5yGi1zgac8VKZDiLvPPWMf4kE19YF16/QM3aekMSXBjHN2eCxSmRWKmGEIVBZQ
f6kmP0KqSBbxQPZmoSXfivtToymzt4IbmqQMeQolR9Qjor3UXnYcs2dJVaYED8WGRY1Eo7ieZxu5
d+iIYPSEwkKBAaNILKqDB8KtmWrPwWPtoclN7GLSWQvEXFUkaV+/k/2/XXP/3x6c626HPf98v8/H
N1vjmvs/Gu7q/o+iXi17EHm7/78P5unpHWnbdyMm44PjuvofcgCJ7A95izXeXP/+slxe1n/Kfvn+
j+8kVv/vg19+eni008083R633SasPl/t7a2+32zQtYf3R68MXdof/6N9HXur/S/+/HT58NkfK7wM
wzAMwzAMwzAMw7gh3+198uWtW3u/7po8UWlbvD768ecH9x892Dy6/8PDBxuc2Hx1NDZHJzt9rNtv
NiftWDc7fbb7evltjh/9hmEYhmEYhmEYhmH8j7nu+Y/zs8vnP54dP7n5Gtc+/5XS1fMf+Hf5/Hcm
e/7jfXB4D6ndPIVvR6cnd27Tvrt97+76cHt6uru73oBDadu7dHiwHNaHB887/murDcMwDMMwDMMw
DMMwDMMwDMMwDMMwDMN4lb8AzZE8jQ==
""")

TEST_DATA_ENC_TEST = base64.b64decode("""
QU5EUk9JRCBCQUNLVVAKMwoxCkFFUy0yNTYKMDc3MjIzMDk2QkNERjJDQjE3QkIxQzIwM0FCMzY4
NUExMjFCQkI4RTVFOTdFMjgwOERGRDY4MEIzNzlENTJBQzg5Q0M4QjM3QkU5NDBBODZFMDExRTMw
M0Q0RjRCM0ZEMUYyQjEzMjlGRUI5OTE5OEE3ODUzOTM4NDE5RTc5NDAKOTRBREQ2NUIxRTJFQ0Y4
ODU1QkE2NkIwRjcwNzA3ODUzODRENEM1NDJCOTQ2NEUwQTQzMDc1NEM0QjFEMjUwRkQ1Rjk3QzNE
QTU0NUIzMjM3MUY3Q0E4OTBCMUQxNzhFNjg1NEZDMjVBQzQ1MkM0NTREN0NFRTE5OUJDRDM2MzkK
MTAwMDAKNTk5ODMzODFCOENDMTA1Mjg1NkRGMUI0MTI1QUNGRUQKMzg1NkI3QTkzOTU5RjMzMDc4
N0REMzU4MDZFMEM3QzQzOUMwOTRBRThGMDRCMDlDRjBFRTJDMjkxNjQ4MkNDRDU5QTU5NTZEMjQx
N0ExREE4NEMzNTQ3MDYwRTBCRDEyNUMzQzdFRjE2NDA2MTZERkRGRTcwNzhDRjgyRUQ4QTA4RkQ2
NzA3NjQ1MjA5ODgwQkIxNDg4MTdGQTgyQkUyNjMxNUU2QTI5NDBFRTQwNDZDRjQ4MEU5OUI5MEM0
REM5CgLfUFnUHEXrf9rmhgXUU6zMjPNIRuxHuZzH/0UsDZJxmBkh9JhhagcZVDpRBIF52RJY/ZwP
+Akygyv9/AtOcf1wY1sndEyF4E3iWBEnNzmicc9Yncl0RtWdDlF8dEW6QtgEaU67KJ+7Y75fhnhu
/NrvX99Gd445mcJAur18ClJA9B4wMN7rXeiDvlIVe6h72hJ2pYGnLEdj+Y6a3tDB31CFE5J3v3nW
bkqKVYh9kH/nVaDB6yljn2mU8sq62tr84lGiY/KEp7tj12b3BX61B4ZukGJnhUosNzfuPoZlli+d
KiZKUmhxPJsUtcTXQh7o6eoF1i730u7hPOD4K+LKJmIVvExtMqWnZO9GlkVpt/Qj0QBSNNhhzkhc
pYIDIZtA1EVVBuw+VEfBP3Lk9HO8bARM3qVHwEPWrRjOwu033X37mV8WEEPx8LOeWrl1IeiAnMdz
0YcI8rQp9ATsvvHpBdeHMjOAtx1EPwewFShMsKD2pOWSDgDhoI7yithTDIQBZyDc3SHPsW/ZFeFH
Br0a2tQh08XetypZmba0S9ApjhvyPAHO+YYLW674MS72ZrSRM15YP8uH8PqkfdDxbMNEtdd8cpei
e6EX2PhdG56kysbJLTfmi/r2IjmJXLO/hrTex1MOOkZoLTfTcj7msNUFHgfodApntDi6T7/kx0Im
LIqEbH2PDVtY42PWWSbtuVPWhjEwR0xt+SNti8BsnVkxX3c/W5PQiw5pppSVo6xud914DMjdfygl
7doR8TfQqgXBCDO573SSvamwdu8dbnOm+3LwMotvnBvatBihWIi414iTJm+yIDCxu2iy4wfGdQ64
EnhbTXbD7ffK3Z7K8spTVb/opBE3htgrmgbH2TOir0FTAwe1cTDirEbCzz7ed4lTHbMVVRzbqLFM
YjXmJNgEe1km0ThdbGNzyggsDeun3EfhN6WhLfA7Rd+udffgzPtopWIIA1FwyyzFrjg+f3c6jRIf
GtZKmm8VB5KXJEE+pwbluzbliBG+uMSnOd6lN2XpQmh8hiK19D2Ew4tQAKqoxbmHuV3V0RLmYSjF
pADFpsx0mYIem15w1U8iL05itgJmXJmhWol0y5u3+awSAgOrXaXNlOZN8Ypp2DK9hi8bO+cp5xej
BJsi6rmaxnrUG2AE407xrqGwlVVdI/Y+q3xr8iQhgGSB/HUFW+P07110rOc8vCwnUHOHttPzI8hb
6c1fjKeArXDOvgZgpw+3+4YIIIphaOn9lreDE+azMCc7hm2LaiKe14++0A8hNuzaUj9CVZvkibc4
B8bbnA/BlzPodCWdW/vHin4LBhor71waris9xitIb4qVpeJKDLNLEfFjUzjhMXUMOeYUYtGmiUIr
9zCOeLHfUMgNVvBm5CUqaZYdjNAivL3iXtdVIg+uT/DEQvYST2+/n/JDV0G0VaA9X9YytP8TOL2p
IW4vcpowXCIbYxUWShTdRRbbJj9S1oLsi03QRKG/KKo0TtewZmBYhImWS49bbSy+KieCMtsG77dC
tks+7MVeGVykbIfXxxJ5CWbrFikQWNuQf8wndxLs0mDXIgYr6kEtN5sOk1rPLwIhiF96UMBxKH59
2jBLc8YYptcjJpencdKzlNGy0zxtZpNMrahUI8kux/7Aw9pE5lY7LucVV/0eOQ8YgKRNHtPISXqu
PwCt5QihZuuFutNfk+8=
""")
