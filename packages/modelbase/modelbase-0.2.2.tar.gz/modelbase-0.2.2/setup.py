from setuptools import setup

setup(name='modelbase',
      version='0.2.2',
      description='A package to build metabolic models',
      url='https://gitlab.com/ebenhoeh/modelbase',
      author='Oliver Ebenhoeh',
      author_email='oliver.ebenhoeh@hhu.de',
      license='GPL4',
      packages=['modelbase'],
      install_requires=[
          'numpy',
          'scipy',
          'matplotlib'
          #'itertools',
          #'re',
          #'pickle'
      ],
      zip_safe=False)
