from setuptools import setup

package = "tranx"
version = "0.0.1"

setup(name = package,
      version = version,
      description="Translating XLIFF tool",
      url='https://github.com/dicaso/tranx',
      author = 'Christophe Van Neste',
      author_email = 'beukueb@gmail.com',
      license = 'GNU GENERAL PUBLIC LICENSE',
      packages = ['tranx'],
      install_requires = [
      ],
      extras_require = {
      },
      package_data = {
      },
      include_package_data = True,
      zip_safe = False,
      entry_points = {
          'console_scripts': [
              'tranx=tranx:merge'
          ],
      },
      test_suite = 'nose.collector',
      tests_require = ['nose']
)

#To install with symlink, so that changes are immediately available:
#pip install -e .
