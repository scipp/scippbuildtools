# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Scipp contributors (https://github.com/scipp)
import os
import shutil
import glob


class FileMover():
    def __init__(self, source_root, destination_root):
        self.source_root = source_root
        self.destination_root = destination_root

    def move_file(self, src, dst):
        os.write(1, "move {} {}\n".format(src, dst).encode())
        shutil.move(src, dst)

    def move(self, src, dst):
        src = os.path.join(self.source_root, *src)
        dst = os.path.join(self.destination_root, *dst)
        if '*' in dst:
            dst = glob.glob(dst)[-1]
        if '*' in src:
            for f in glob.glob(src):
                self.move_file(f, dst)
        else:
            self.move_file(src, dst)
