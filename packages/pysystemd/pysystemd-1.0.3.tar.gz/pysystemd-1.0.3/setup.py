from distutils.core import setup
with open("README", "r") as fh:
    long_description = fh.read()
setup(
  name = 'pysystemd',
  packages = ['pysystemd'],
  version = '1.0.3',
  description = 'a systemd binding Library in python',
    long_description=long_description,
  author = 'alimiracle',
  author_email = 'alimiracle@riseup.net',
  url="https://notabug.org/alimiracle/pysystemd",
  license='GPL v3',
  keywords = ['services', 'init', 'systemd'],
  classifiers = [],
)