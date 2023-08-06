#!/usr/bin/env python3

from wheel.bdist_wheel import bdist_wheel as bdist_wheel_
from setuptools import setup, Extension, Command
from distutils.util import get_platform

#class bdist_wheel(bdist_wheel_):
#    def finalize_options(self):
#        from sys import platform as _platform
#        platform_name = get_platform()
#        if _platform == "linux" or _platform == "linux2":
#            # Linux
#            platform_name = 'manylinux1_x86_64'
#
#        bdist_wheel_.finalize_options(self)
#        self.universal = True
#        self.plat_name_supplied = True
#        self.plat_name = platform_name

libqt_include_path = "/usr/include/x86_64-linux-gnu/qt5/"
liboce_include_path = "/usr/include/oce/"

zenlib = Extension('zenlib',
	include_dirs = [
		"gxx",
		"servoce/src",
		"servoce/include",
		"third_party",
		liboce_include_path,
		libqt_include_path
	],

    sources = [ 
        "src/pywrap.cpp",

		"gxx/gxx/io/file_unix.cpp",
		"gxx/gxx/io/std.cpp",
		"gxx/gxx/impl/panic_abort.cpp",
		"gxx/gxx/util/string.cpp",
		"gxx/gxx/util/base64.cpp",
		"gxx/gxx/util/hexascii.cpp",
		"gxx/gxx/util/numconvert.c",
		"gxx/gxx/osutil/src/posix.cpp",
		"gxx/gxx/path/path.cpp",
		"gxx/gxx/print/src/impl/print_cout.cpp",

		"gxx/gxx/debug/dprint_func_impl.c", 
		"gxx/gxx/debug/dprint_stdout.c", 
		"gxx/gxx/debug/assembler.c", 
		"gxx/gxx/debug/dprintxx.cpp",
	
		"servoce/src/topo.cpp",	
		"servoce/src/wire.cpp",
		"servoce/src/face.cpp",
		"servoce/src/solid.cpp",
		"servoce/src/convert.cpp",
		"servoce/src/boolops.cpp",
		"servoce/src/math3.cpp",
		"servoce/src/display.cpp",
		"servoce/src/display/dispwidget.cpp",
		"servoce/src/display/dispwidget_qt.cpp",
		"servoce/src/display/mainwidget.cpp",
		"servoce/src/display/icons.cpp",
		"servoce/src/display/display.moc.cpp",
		"servoce/src/trans.cpp",
   	],

   	libraries = [
		'TKernel',
		'TKMath',
		'TKG3d',
		'TKBRep',
		'TKGeomBase',
		'TKGeomAlgo',
		'TKTopAlgo',
		'TKPrim',
		'TKBO',
		'TKBool',
		'TKOffset',
		'TKService',
		'TKV3d',
		'TKOpenGl',
		'TKFillet',
		'TKSTL',
		'TKBin',

		'Qt5Core', 
		'Qt5Widgets', 
		'Qt5Test', 
		'Qt5Gui', 
		'Qt5OpenGL',
   	],

	extra_compile_args=['-std=c++14'],
)

setup(
	name = 'zencad',
	packages = ['zencad'],
	version = '0.4.1',
	license='MIT',
	description = 'CAD system for righteous zen programmers ',
	author = 'Sorokin Nikolay',
	author_email = 'mirmikns@yandex.ru',
	url = 'https://mirmik.github.io/zencad/',
	keywords = ['testing', 'cad'],
	classifiers = [],

    install_requires=[
        'evalcache',
    ],

   	include_package_data=True,
    #package_data={'zencad': ['zenlib.so', "libservoce.so"]},

    ext_modules = [zenlib],
#    cmdclass = {"bdist_wheel" : bdist_wheel}
)
