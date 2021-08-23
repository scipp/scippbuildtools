# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Scipp contributors (https://github.com/scipp)
# @author Neil Vaytet

import os
import argparse
import shutil
import subprocess
import multiprocessing
import sys
import time


def _run_command(cmd, shell):
    """
    Run a command (supplied as a list) using subprocess.check_call
    """
    os.write(1, "{}\n".format(' '.join(cmd)).encode())
    return subprocess.check_call(cmd, stderr=subprocess.STDOUT, shell=shell)


def _get_absolute_paths(*paths):
    abs_paths = [os.path.abspath(p) for p in paths]
    return abs_paths


def make_argument_parser():
    parser = argparse.ArgumentParser(
        description='Build C++ library and run tests')
    parser.add_argument('--prefix', default='install')
    parser.add_argument('--source_dir', default='.')
    parser.add_argument('--build_dir', default='build')
    parser.add_argument('--caching', action='store_true', default=False)
    return parser


class CppBuilder:
    def __init__(self,
                 prefix=None,
                 source_dir=None,
                 build_dir=None,
                 caching=None):

        self._prefix, self._build_dir, self._source_dir = _get_absolute_paths(
            prefix, build_dir, source_dir)
        self._caching = caching

        self._config = {}
        # self._flags_list = None
        # self._build_flags = None
        # self._shell = None
        # self._build_config = None

    # def __init__(self,
    #              flags_list=None,
    #              build_flags=None,
    #              shell=None,
    #              build_config=None):
    #     self.flags_list = flags_list
    #     self.build_flags = build_flags
    #     self.shell = shell
    #     self.build_config = build_config

    def enter_build_dir(self):
        if not os.path.exists(self._build_dir):
            os.makedirs(self._build_dir)
        os.chdir(self._build_dir)

    def cmake_configure(self):
        """
        Platform-independent function to run cmake, build, install and C++ tests.
        """

        # Get the platform name: 'linux', 'darwin' (osx), or 'win32'.
        self._config["platform"] = sys.platform

        # # Set up absolute directory paths
        # source_dir = os.path.abspath(source_dir)
        # prefix = os.path.abspath(prefix)
        # build_dir = os.path.abspath(build_dir)

        # Default options
        self._config["shell"] = False
        parallel_flag = '-j{}'.format(multiprocessing.cpu_count())
        self._config["build_config"] = ''

        # Some flags use a syntax with a space separator instead of '='
        use_space = ['-G', '-A']

        # Default cmake flags
        cmake_flags = {
            # '-G': 'Ninja',
            '-DPython_EXECUTABLE': shutil.which("python"),
            '-DCMAKE_INSTALL_PREFIX': self._prefix,
            '-DWITH_CTEST': 'OFF',
            '-DCMAKE_INTERPROCEDURAL_OPTIMIZATION': 'ON'
        }

        if self._config["platform"] == 'darwin':
            cmake_flags.update({'-DCMAKE_INTERPROCEDURAL_OPTIMIZATION': 'OFF'})
            osxversion = os.environ.get('OSX_VERSION')
            if osxversion is not None:
                cmake_flags.update({
                    '-DCMAKE_OSX_DEPLOYMENT_TARGET':
                    osxversion,
                    '-DCMAKE_OSX_SYSROOT':
                    os.path.join('/Applications', 'Xcode.app', 'Contents',
                                 'Developer', 'Platforms', 'MacOSX.platform',
                                 'Developer', 'SDKs',
                                 'MacOSX{}.sdk'.format(osxversion))
                })

        if self._config["platform"] == 'win32':
            cmake_flags.update({'-G': 'Visual Studio 16 2019', '-A': 'x64'})
            # clcache conda installed to env Scripts dir in env if present
            scripts = os.path.join(os.environ.get('CONDA_PREFIX'), 'Scripts')
            if self._caching and os.path.exists(
                    os.path.join(scripts, 'clcache.exe')):
                cmake_flags.update({'-DCLCACHE_PATH': scripts})
            self._config["shell"] = True
            self._config["build_config"] = 'Release'
            # cmake --build --parallel is detrimental to build performance on
            # windows, see https://github.com/scipp/scipp/issues/2078 for
            # details
            self._config["build_flags"] = []
        else:
            # For other platforms we do want to add the parallel build flag.
            self._config["build_flags"] = [parallel_flag]

        if len(self._config["build_config"]) > 0:
            self._config["build_flags"] += [
                '--config', self._config["build_config"]
            ]

        # Parse cmake flags
        self._config["flags_list"] = []
        for key, value in cmake_flags.items():
            if key in use_space:
                self._config["flags_list"] += [key, value]
            else:
                self._config["flags_list"].append('{}={}'.format(key, value))

    def cmake_run(self):
        # Run cmake
        _run_command(['cmake'] + self._config["flags_list"] +
                     [self._source_dir],
                     shell=self._config["shell"])
        # Show cmake settings
        _run_command(['cmake', '-B', '.', '-S', self._source_dir, '-LA'],
                     shell=self._config["shell"])

    def cmake_build(self, target_list):
        # Compile benchmarks, C++ tests, and python library
        for target in target_list:
            run_command(['cmake', '--build', '.', '--target', target] +
                        self._config["build_flags"],
                        shell=self._config["shell"])

    def run_cpp_tests(test_list):

        for test in test_list:
            run_command(
                [os.path.join('bin', self._config["build_config"], test)],
                shell=self._config["shell"])
        # # Run C++ tests
        # run_command([os.path.join('bin', build_config, 'scippneutron-test')],
        #             shell=shell)

    # if __name__ == '__main__':
    #     args = parser.parse_args()
    #     main(prefix=args.prefix,
    #          build_dir=args.build_dir,
    #          source_dir=args.source_dir,
    #          caching=args.caching)
