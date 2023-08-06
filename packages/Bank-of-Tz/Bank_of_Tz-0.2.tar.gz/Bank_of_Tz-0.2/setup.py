from setuptools import setup

setup(name='Bank_of_Tz',
      version='0.2',
      description='Gets data from  the Bank of Tanzania',
      long_description='Helpful in fetching alot of data',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
      ],
      keywords='Bonds',
      url='https://github.com/Mbonea-Mjema/Bank-of-Tanzania-Tbill-Tbond-',
      author='Mbonea Mjema',
      author_email='mjema86@gmail.com',
      license='MIT',
      packages=['Bank_of_Tz'],
      install_requires=[
          'bs4','requests'
      ],
      include_package_data=True,
      zip_safe=False)