from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()


setup(
   name='pyquran',
   version='1.0.0',
   description='PyQuran: The Python package for Quranic Analysis',
   url='https://github.com/hci-lab/PyQuran',
   author='Waleed A. Yousef and Taha M. Madbouly and Omar M. Ibrahime and Ali H. El-Kassas and Ali O. Hassan and Abdallah R. Albohy',
   author_email='tahamagdy@fci.helwan.edu.eg',
   packages=find_packages(),
   long_description=long_description,
   long_description_content_type='text/markdown', # !!
   install_requires=['numpy', 'pyarabic'],
   include_package_data=True
)

"""
Delete the build, dist, and <package name>.egg-info folders in your root directory.
Change version number in your setup.py file.
Create distribution again. e.g:  $ python setup.py sdist bdist_wheel
Upload distribution again. e.g:  $ twine upload dist/*
enjoy! :-)
"""
