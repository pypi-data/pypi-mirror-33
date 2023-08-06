import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open(os.path.join(os.path.dirname(__file__), 'LICENSE.txt')) as license:
    LICENSE = license.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='dplus-api',
    version='3.1.2',
    packages=['dplus'],
	install_requires=['numpy>=1.10', 'psutil==5.2.2', 'requests==2.10.0'],
    include_package_data=True,
    license=LICENSE,  # example license
    description='Call the DPlus Calculation Backend',
    long_description=README,
    url='https://scholars.huji.ac.il/uriraviv',
    author='Devora Witty',
    author_email='devorawitty@chelem.co.il',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
)
