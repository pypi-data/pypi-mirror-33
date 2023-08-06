from setuptools import setup, find_packages

v = '0.2.2'

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context

setup(
    name='lp_api_wrapper',
    version=v,
    description='LivePerson API Python Wrapper',
    author='Liveperson',
    author_email='analytics@liveperson.com',
    url='https://lpgithub.dev.lprnd.net/Analytics/lp-api-wrapper',
    download_url='https://github.com/danielkerwin/lp-api-wrapper/archive/{}.tar.gz'.format(v),
    packages=find_packages(),
    install_requires=['requests', 'requests_oauthlib'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)
