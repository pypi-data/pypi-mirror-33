import os
import pathlib
import distutils
from setuptools import setup, find_packages
from miyadaiku.common import setuputils

DIR = pathlib.Path(__file__).resolve().parent
os.chdir(DIR)

requires = [
    "miyadaiku"
]

srcdir = 'node_modules/jquery/dist/'
destdir = 'miyadaiku/themes/jquery/externals/'
copy_files = [[srcdir, ['jquery*.js'], destdir]]

setup(
    name="miyadaiku.themes.jquery",
    version="0.0.10",
    author="Atsuo Ishimoto",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    description='jQuery files for miyadaiku static site generator',
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
