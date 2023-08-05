from setuptools import setup

setup(name='food_trucks_boston',
      version='0.2',
      description='Know where the food trucks are in Boston, from the command line.',
      url='https://github.com/DennisMelamed/food_trucks_boston.git',
      author='dennis.melamed',
      author_email='dennis@dennismelamed.me',
      packages=['food_trucks_boston'],
      scripts=['food_trucks_boston/test.py'],
      install_requires=[
          'jsonpath_ng', 'click', 'esridump', 'fuzzywuzzy', 'numpy', 'prettytable',
          ],
      zip_safe=False)
