import os
import pathlib
import distutils
from setuptools import setup, find_packages
from miyadaiku.common import setuputils

DIR = pathlib.Path(__file__).resolve().parent
os.chdir(DIR)

requires = [
    "miyadaiku",
    "miyadaiku.themes.jquery"
]

srcdir = 'node_modules/fullpage.js/dist/'
destdir = 'miyadaiku/themes/fullpagejs/files/static/fullpage_js/'
copy_files = [[srcdir, ['fullpage.*'], destdir]]

setup(
    name="miyadaiku.themes.fullpagejs",
    version="0.0.2",
    author="Atsuo Ishimoto",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    description='fullPage.js files for miyadaiku static site generator',
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
