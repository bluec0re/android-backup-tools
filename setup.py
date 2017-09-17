from setuptools import setup

setup(
    name='android_backup',
    version='0.0.1',
    description='Unpack and repack android backups',
    url='https://github.com/bluec0re/android-backup-tools',

    author='The Python Packaging Authority',
    author_email='pypa-dev@googlegroups.com',

    license='GPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    keywords='android backup pack unpack development',

    entry_points={
        'console_scripts': [
            'android-backup-unpack=android_backup.unpack:main',
            'android-backup-pack=android_backup.pack:main',
        ],
    },
)
