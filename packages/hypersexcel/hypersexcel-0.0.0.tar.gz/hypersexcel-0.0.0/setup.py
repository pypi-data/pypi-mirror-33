from Cython.Build import cythonize
import sys
import subprocess

from distutils.core import setup
from distutils.extension import Extension


def lib():
    command = 'cd lib && make && make install'
    command_sudo = 'cd lib && make && make install'
    subprocess.call(command, shell=True)
    subprocess.call(command_sudo, shell=True)
    subprocess.call('python setup.py build_ext --inplace', shell=True)


if 'build_ext' not in sys.argv:
    lib()
ext_modules = cythonize(
    [Extension("cpexcel", ["src/cpexcel.pyx"], libraries=["xlsxwriter"])])

setup(name="hypersexcel", ext_modules=cythonize(ext_modules))
