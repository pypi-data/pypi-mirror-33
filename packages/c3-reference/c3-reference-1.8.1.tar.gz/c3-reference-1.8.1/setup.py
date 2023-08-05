from setuptools import find_packages, setup
setup(
    name='c3-reference',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.8.1',
    description='Reference implementations for C3 Wireless security beacons',
    url='https://github.com/C3Wireless/c3-reference',
    author='C3 Wireless',
    author_email='support@c3wireless.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='c3 c3wireless btle beacon ibeacon cmac aead eax',
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    install_requires=[# 'pycryptodome==3.4.3',
                      # 'aiokafka==0.2.2',
                      'python-lzo==1.11',
                      'protobuf==3.6.0'
                      ],
    extras_require={
        'test': ['tox']
    },
    entry_points={
        'console_scripts': [
            # 'authserver=c3reference.authserver:main',
            'listener=c3reference.listener:main',
            # 'kafka=c3reference.kafka:main'
        ],
    },
)
