"""Setup script for encrypted_config package."""

import setup_boilerplate


class Package(setup_boilerplate.Package):

    """Package metadata."""

    name = 'encrypted-config'
    description = 'Partially encrypted configuration library/tool.'
    download_url = 'https://github.com/mbdevpl/encrypted-config'
    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Communications :: File Sharing',
        'Topic :: Security :: Cryptography',
        'Topic :: Utilities']
    keywords = ['config', 'encryption', 'rsa', 'security']


if __name__ == '__main__':
    Package.setup()
