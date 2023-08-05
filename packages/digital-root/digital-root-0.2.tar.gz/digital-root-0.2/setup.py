"""
DigitalRoot
-------------

Simple script for calculating digital root of an integer number.

You can get it by downloading it directly or by typing:

    $ pip install digital-root

After it is installed you can check your current temperature by running:

    $ digital_root

"""


from setuptools import setup

setup(name='digital-root',
      version='0.2',
      description='Script for calculating digital root of an integer number.',
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/digital-root",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['digital_root'],
      entry_points={
          "console_scripts": ["digital_root=digital_root.digital_root:main", ],
      },
      )

__author__ = 'Uros Jevremovic'
