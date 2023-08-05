from setuptools import setup

with open('readme.md') as f:
    long_description = f.read()

setup(name='dativatools',
      version='2.9.8',
      description='A selection of tools for easier processing of data using Pandas and AWS',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://bitbucket.org/dativa4data/dativatools/',
      author='Dativa',
      author_email='hello@dativa.com',
      license='MIT',
      zip_safe=False,
      packages=['dativatools',
                'dativa.tools',
                'dativa.tools.pandas',
                'dativa.tools.aws',
                'dativa.tools.logging',
                'dativa.tools.db'],
      setup_requires=['setuptools>=38.6.0'],
      install_requires=[
          'boto>=2.48.0',
          'boto3>=1.4.4',
          'botocore>=1.5.80',
          'chardet>=3.0.4',
          'pandas>=0.18.0',
          'paramiko>=2.2.1',
          'patool>=1.12',
          'psycopg2>=2.7.3.1',
          'pexpect>=4.2.1',
          's3fs>=0.1.5'
      ],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Libraries',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.6'],
      keywords='dativa',)
