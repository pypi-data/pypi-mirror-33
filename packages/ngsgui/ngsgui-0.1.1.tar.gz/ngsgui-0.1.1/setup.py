#! /usr/bin/python3

from skbuild import setup
import subprocess, pathlib, os

icons = [ "src/icons/" + filename for filename in os.listdir("src/icons")]
shaders = [ "src/shader/" + filename for filename in os.listdir("src/shader")]

setup(name="ngsgui",
      version="0.1.1",
      description="New graphical interface for NGSolve",
      packages=['ngsgui', 'ngsgui.code_editor'],
      package_dir={'ngsgui' : 'src',
                   'ngsgui.code_editor' : 'src/code_editor'},
      data_files=[('ngsgui/icons', icons),
                  ('ngsgui/shader', shaders)],
      cmake_args=['-DUSE_OCC=ON', '-DUSE_CCACHE=ON'],
      classifiers=("Programming Language :: Python :: 3",
                   "Operating System :: OS Independent",
                   "Development Status :: 2 - Pre-Alpha",
                   "Environment :: X11 Applications :: Qt",
                   "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)"),
      entry_points={ "gui_scripts" : "ngsolve = ngsgui.start:main" })

