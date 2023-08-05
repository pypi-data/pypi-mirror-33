#!/usr/bin/env python
from pathlib import Path
from setuptools import setup, find_packages

install_requires = ['python-dateutil', 'pytz', 'pandas', 'h5py', 'scikit-image', 'imageio',
                    'histutils', 'morecvutils']
tests_require = ['pytest', 'coveralls', 'flake8', 'mypy']


scripts = [s.name for s in Path(__file__).parent.glob(
    '*.py') if not s.name == 'setup.py']

setup(name='dmcutils',
      packages=find_packages(),
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/dmcutils',
      description='Utilities to read and plot DMC Experiment data',
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      version='0.9.2',
      classifiers=[
          'Intended Audience :: Science/Research',
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
          'Programming Language :: Python :: 3.6',
      ],
      install_requires=install_requires,
      tests_require=tests_require,
      python_requires='>=3.6',
      extras_require={'web': ['flask', 'flask-limiter'],
                      'plot': ['matplotlib'],
                      'io': ['astrometry_azel'],
                      'tests': tests_require},
      )
