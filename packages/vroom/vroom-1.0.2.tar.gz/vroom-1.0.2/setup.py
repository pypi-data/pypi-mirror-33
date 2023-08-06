from setuptools import setup

with open('README.rst') as readme:
    LONG_DESCRIPTION = readme.read()
    
setup(name='vroom',
      license='MIT',
      version='1.0.2',
      description='License Plate Parser',
      long_description=LONG_DESCRIPTION,
      author='Magdalena Nowak',
      author_email='magdanowak0804@gmail.com',
      url='https://github.com/magdanowak/vroom',
      install_requires=['pyyaml'],
      packages=['vroom'],
      package_data={'vroom': ['*.yml']}
     )