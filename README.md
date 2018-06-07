# android-backup-tools

![Build status](https://travis-ci.org/bluec0re/android-backup-tools.svg?branch=master)

Unpack and repack android backups


## Install

```
$ pip install android_backup
```

Optional (for encrypted archives):
```
$ pip install pycrypto
```

## Usage

### CLI

#### Unpacking
```
$ android-backup-unpack foo.ab
```

Results in directory *foo.ab_unpacked*

#### Packing
```
$ android-backup-pack foo.ab
```

Packs *foo.ab_unpacked* folder to *foo.ab*. Requires a previously generated *foo.ab.pickle* file.

### Programmatic

```python
from android_backup import AndroidBackup, CompressionType, EncryptionType

with AndroidBackup('foo.ab') as ab:
  ab.list() # print content to stdout
  
with AndroidBackup('foo.ab') as ab:
  ab.unpack()

ab = AndroidBackup()
ab.version = 3
ab.compression = CompressionType.ZLIB
ab.encryption = EncryptionType.NONE
ab.pack('foo.ab')
```
