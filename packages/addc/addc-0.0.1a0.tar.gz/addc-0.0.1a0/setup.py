from setuptools import setup, Extension, find_packages
import numpy.distutils.misc_util

ext_modules = [
    Extension("addc.c._array_info", ["./src/pyc/_array_info.c"]),
    Extension("addc.c._add", [
        "./src/pyc/_add.c",
        "./src/c/add.c"]),
    Extension("addc.c._array_add", [
        "./src/pyc/_array_add.c",
        "./src/c/array_add.c"]),
]

setup(
    name='addc',
    version='0.0.1a0',
    description='Test C ext',
    author='sahn',
    author_email='jam31118@gmail.com',
    url='https://github.com/jam31118/pycext',
    packages=find_packages(),
    install_requires=['numpy'],
    ext_modules=ext_modules,
    include_dirs=["./src/include"]+numpy.distutils.misc_util.get_numpy_include_dirs(),
    license='GPLv3'
)

