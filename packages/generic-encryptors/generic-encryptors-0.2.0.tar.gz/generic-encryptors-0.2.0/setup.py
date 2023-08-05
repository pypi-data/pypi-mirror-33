import os
from setuptools import setup, find_packages

dir_path = os.path.dirname(os.path.realpath(__file__))

VERSION = open(os.path.join(dir_path, 'VERSION')).read()

setup(
  name = 'generic-encryptors',
  packages = find_packages(),
  version = VERSION,
  description = '''
  A set of encryptors which provide an interface compatible with https://github.com/mmontagna/generic-encoders
  ''',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  author = 'Marco Montagna',
  author_email = 'marcojoemontagna@gmail.com',
  url = 'https://github.com/mmontagna/generic-encryptors',
  keywords = ['encryptors', 'encryption', 'aes', 'decryption'],
  classifiers=(
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'Natural Language :: English',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.6',
  ),
  data_files = [('', ['LICENSE', 'VERSION'])],
  include_package_data=True,
  python_requires=">=2.7",
  license=open(os.path.join(dir_path, 'LICENSE')).read(),
  install_requires=[
    "cryptography~=2.2.0",
    "generic-encoders==0.3.2"
  ],
  entry_points = {

  },
)