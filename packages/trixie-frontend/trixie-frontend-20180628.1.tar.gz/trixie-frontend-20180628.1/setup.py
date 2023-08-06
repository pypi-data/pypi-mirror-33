from setuptools import setup, find_packages

setup(name='trixie-frontend',
      version='20180628.1',
      description='The Trixie frontend',
      url='https://github.com/charbelsarkis/trixie-frontend',
      author='Trixie Home Assistant Authors',
      author_email='hello@trixie.io',
      license='Apache License 2.0',
      packages=find_packages(include=[
          'hass_frontend',
          'hass_frontend_es5',
          'hass_frontend.*',
          'hass_frontend_es5.*'
      ]),
      install_requires=[
          'user-agents==1.1.0',
      ],
      include_package_data=True,
      zip_safe=False)
