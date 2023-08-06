import os
import pathlib
from setuptools import setup, find_packages
from miyadaiku.common import setuputils

DIR = pathlib.Path(__file__).resolve().parent
os.chdir(DIR)


requires = [
    "miyadaiku"
]

srcdir = 'node_modules/@fortawesome/fontawesome-free/'
destdir = 'miyadaiku/themes/fontawesome/externals'
filesdir = 'miyadaiku/themes/fontawesome/files'
copy_files = [
    [srcdir+'/css/', ['*.css'], destdir+'/css/'],
    [srcdir+'/fonts/', ['*', ], filesdir+'/static/fontawesome/fonts/']
]

setup(
    name="miyadaiku.themes.fontawesome",
    version="0.0.6",
    author="Atsuo Ishimoto",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    description='Font Awesome files for miyadaiku static site generator',
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
