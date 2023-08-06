from setuptools import setup
import sys

if sys.version_info[:2] == (2, 7):
    packages = ['smsauth2']
elif sys.version_info[:2] >= (3, 6):
    packages = ['smsauth3']
else:
    raise RuntimeError("Python version 2.7 or >= 3.6 required.")

setup(
    name='smsauth',
    version='0.1.2',
    description='Python API for SMS',
    long_description='An easy-to-use Python API for SMS Authentication',
    url='https://github.com/kwugfighter/sms-auth',
    author='kwugfighter',
    author_email='isaacli430@gmail.com',
    license='MIT',
    keywords=['auth', 'async', 'sms', 'twilio'],
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'

    ],
    packages=packages,
    install_requires=[
        'requests'
    ],
    extras_require={
        ':python_version >= "3.6"': [
            'aiohttp'
        ],
    }
)