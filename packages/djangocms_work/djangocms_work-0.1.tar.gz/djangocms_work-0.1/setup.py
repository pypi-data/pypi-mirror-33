import os
from setuptools import setup, find_packages

def read(fname):
    # read the contents of a text file
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djangocms_work',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='GNU General Public License',
    description='Companies works small app',
    long_description=read('README.md'),
    url='https://github.com/dmodules/djangocms_work',
    author='D-Modules',
    #install_requires=["django-taggit==0.22.1"],
    author_email='support@d-modules.com',
)