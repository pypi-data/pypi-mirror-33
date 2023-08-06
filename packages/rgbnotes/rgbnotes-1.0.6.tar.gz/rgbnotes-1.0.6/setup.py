from setuptools import setup, find_packages


with open("LONG_DESCRIPTION.rst", "r") as fh:
    long_description = fh.read()


setup(name='rgbnotes',
      version='1.0.6',
      description='Python bindings for the RGB Notes API',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='rgbnotes',
      author_email='support@rgbnotes.com',
      url='https://github.com/rgbnotes/rgb-api-python',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'requests >= 0.8.8',
          'simplejson >= 1.0.0'
      ])
