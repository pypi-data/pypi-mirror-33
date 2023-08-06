from setuptools import setup
from pathlib import Path

base_dir = Path(__file__).absolute().parent
read_me = base_dir / 'README.md'
long_description = read_me.read_text(encoding='utf-8')
version = '0.1.6'

setup(name='PinPoint',
      version=version,
      description='A fast geo toolkit for academic affiliation strings',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://pinpoint.eckert.science',
      download_url=f'https://bitbucket.org/nathan-diodan/pinpoint/get/{version}.zip',
      author='Hagen Eckert',
      author_email='pinpoint@eckert.science',
      license='MIT',
      packages=['pinpoint'],
      include_package_data=True,
      install_requires=['appdirs', 'geopy', 'numpy', 'nvector', 'scipy', 'ujson', 'unidecode'],
      zip_safe=True,
      keywords=['collaboration metrics', 'weighted distance', 'cooperation distance',
                'apparent location', 'affiliation strings', 'bibliometrics'],
      python_requires='~=3.6',
      classifiers=[
          'Development Status :: 4 - Beta',

          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Information Analysis',

          'License :: OSI Approved :: MIT License',

          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3 :: Only'
      ],
      )
