# -*- coding: utf-8 -*-

from setuptools import setup
from fresh._version import __version__


setup(name="fresh",
      version=__version__,
      author="Miles Granger",
      maintainer='Miles Granger',
      author_email='miles59923@gmail.com',
      maintainer_email='miles59923@gmail.com',
      keywords='automated machine learning',
      description='Automated, end-to-end machine learning',
      long_description='',
      packages=['fresh'],
      license='BSD',
      url='https://github.com/milesgranger/fresh',
      zip_safe=False,
      setup_requires=['pytest-runner'],
      install_requires=[],
      tests_require=['pytest'],
      test_suite='tests',
      include_package_data=True,
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Intended Audience :: Financial and Insurance Industry',
            'Intended Audience :: Information Technology',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Rust',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS :: MacOS X',
      ],
)
