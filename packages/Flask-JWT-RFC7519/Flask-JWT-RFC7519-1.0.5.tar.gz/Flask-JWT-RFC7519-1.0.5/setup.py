"""
Flask-JWT-RFC7519
------------------
Flask-Login provides jwt endpoint protection for Flask.
"""
import io
import re
from setuptools import setup

with io.open('flask_jwt_rfc7519/__init__.py', encoding='utf-8') as f:
    version = re.search(r"__version__ = '(.+)'", f.read()).group(1)


with open("README.md", "r") as f:
    long_description = f.read()


setup(name='Flask-JWT-RFC7519',
      version=version,
      url='',
      license='MIT',
      author='Magnus Hartvig Groenbech',
      author_email='groenbech96@gmail.com',
      description='FLASK JWT implementing the RFC7519 proposed standard',
      long_description=long_description,
      long_description_content_type="text/markdown",
      keywords=['flask', 'jwt', 'json web token'],
      packages=['flask_jwt_rfc7519'],
      zip_safe=False,
      platforms='any',
      install_requires=[
          'Werkzeug>=0.14',
          'Flask',
          'PyJWT>=1.6.0',
          'cryptography'
      ],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ])
