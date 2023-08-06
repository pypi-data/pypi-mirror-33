"""Python setup script for dvible"""

from setuptools.command.build_py import build_py
from setuptools import setup
import subprocess
import shlex
import sys
import os


def pre_install():
    """Do the custom compiling of the dvible-helper executable from the makefile"""
    try:
        print("Working dir is " + os.getcwd())
        for cmd in [ "make -C ./dvible clean", "make -C dvible -j1" ]:
            print("execute " + cmd)
            msgs = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("Failed to compile dvible-helper. Exiting install.")
        print("Command was " + repr(cmd) + " in " + os.getcwd())
        print("Return code was %d" % e.returncode)
        print("Output was:\n%s" % e.output)
        sys.exit(1)

class my_build_py(build_py):
    def run(self):
        pre_install()
        build_py.run(self)

setup_cmdclass = {
    'build_py' : my_build_py,
}

# Force package to be *not* pure Python
# Discusssed at issue #158

try:
    from wheel.bdist_wheel import bdist_wheel

    class BluepyBdistWheel(bdist_wheel):
        def finalize_options(self):
            bdist_wheel.finalize_options(self)
            self.root_is_pure = False

    setup_cmdclass['bdist_wheel'] = BluepyBdistWheel
except ImportError:
    pass


setup (
    name='dvible',
    version='1.0.5',
    description='Python module for interfacing with BLE devices through Bluez',
    author='Davi Orzechowski',
    author_email='daviorze@gmail.com',
    url='https://daviorze.com.br',
    keywords=[ 'Bluetooth', 'Bluetooth Smart', 'BLE', 'Bluetooth Low Energy' ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    packages=['dvible'],
    
    package_data={
        'dvible': ['dvible-helper', '*.json', 'bluez-src.tgz', 'dvible-helper.c', 'Makefile']
    },
    cmdclass=setup_cmdclass,
    entry_points={
        'console_scripts': [
            'thingy52=dvible.thingy52:main',
            'sensortag=dvible.sensortag:main',
            'blescan=dvible.blescan:main',
        ]
    }
)

