from setuptools import setup
import sys

deps = []
if sys.version_info[:2] < (3,4):
    deps.append('enum34')

setup(
    name='android_backup',
    version='0.2.0',
    description='Unpack and repack android backups',
    url='https://github.com/bluec0re/android-backup-tools',
    author='BlueC0re',
    author_email='bluec0re@users.noreply.github.com',
    license='Apache-2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    packages=['android_backup'],
    keywords='android backup pack unpack development',
    entry_points={
        'console_scripts': [
            'android-backup-unpack=android_backup.unpack:main',
            'android-backup-pack=android_backup.pack:main',
        ],
    },
    install_requires=deps,
)
