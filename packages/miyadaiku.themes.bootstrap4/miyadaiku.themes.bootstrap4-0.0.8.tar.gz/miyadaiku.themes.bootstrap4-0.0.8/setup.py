import os
import pathlib
from setuptools import setup, find_packages
from miyadaiku.common import setuputils

DIR = pathlib.Path(__file__).resolve().parent
os.chdir(DIR)


requires = [
    "miyadaiku",
    "miyadaiku.themes.jquery",
    "miyadaiku.themes.tether",
]

srcdir = 'node_modules/bootstrap/dist'
destdir = 'miyadaiku/themes/bootstrap4/externals'
copy_files = [
    [srcdir+'/css/', ['bootstrap.css', 'bootstrap.min.css', ], destdir+'/css/'],
    [srcdir+'/js/', ['bootstrap.css', '*.js', ], destdir+'/js/']
]

setup(
    name="miyadaiku.themes.bootstrap4",
    version="0.0.8",
    author="Atsuo Ishimoto",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    description='Bootstrap 4 files for miyadaiku static site generator',
    long_description=setuputils.read_file(DIR, 'README.rst'),
    packages=list(setuputils.list_packages(DIR, 'miyadaiku')),
    package_data={
        '': setuputils.SETUP_FILE_EXTS,
    },
    install_requires=requires,
    include_package_data=True,
    zip_safe=False,
    cmdclass={'copy_files': setuputils.copy_files},
    copy_files=copy_files
)
