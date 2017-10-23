# android-backup-tools
Unpack and repack android backups


Install
-------
```
$ pip install android_backup
```

Usage
-----

Unpacking: ./android_backup/unpack.py foo.ab

Results in directory foo.ab_unpacked

Packing: ./android_backup/pack.py foo.ab

Packs foo.ab_unpacked folder to foo.ab_unpacked/foo.ab

Or when installed with: android-backup-{unpack,pack} as above

