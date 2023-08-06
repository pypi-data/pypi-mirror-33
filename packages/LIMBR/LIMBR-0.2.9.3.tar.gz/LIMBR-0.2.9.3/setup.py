from setuptools import setup

setup(name='LIMBR',
      version='0.2.9.3',
      packages=['LIMBR'],
      py_modules=['batch_fx','imputation','old_fashioned'],
      description='Learning and Imputation for Mass-spec Bias Reduction',
      url='https://github.com/aleccrowell/LIMBR',
      download_url='https://github.com/aleccrowell/LIMBR/releases/tag/v0.2.9.3',
      author='Alec Crowell',
      author_email='alexander.m.crowell@gmail.com',
      license='BSD-3',
      keywords=['SVA','SVD','mass-spec','bioinformatics'],
      install_requires=['numpy','pandas','scipy','sklearn','statsmodels','tqdm','multiprocess','matplotlib'],
      zip_safe=False,long_description=open('README.md').read())
