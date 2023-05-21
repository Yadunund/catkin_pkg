# Software License Agreement (BSD License)
#
# Copyright (c) 2023, Yadunund Vijay.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Yadunund Vijay. nor
#    the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Generate/update ROS changelog files.

The Changelog format is described in REP-0132:

http://ros.org/reps/rep-0132.html
"""

import os
import re

from catkin_pkg.changelog import BAD_CHANGELOG_FILENAME, CHANGELOG_FILENAME
from catkin_pkg.changelog_generator_vcs import Tag

FORTHCOMING_LABEL = 'Forthcoming'

def generate_changelogs(base_path, packages, logger=None):
    for pkg_path, package in packages.items():
        bad_changelog_path = os.path.join(base_path, pkg_path, BAD_CHANGELOG_FILENAME)
        good_changelog_path = os.path.join(base_path, pkg_path, CHANGELOG_FILENAME)
        if os.path.exists(good_changelog_path):
            continue
        # generate package specific changelog file
        if logger:
            logger.info("- creating '%s'" % good_changelog_path)
        data = generate_changelog_file(package.name, bad_changelog_path)
        with open(good_changelog_path, 'wb') as f:
            f.write(data.encode('UTF-8'))


def generate_changelog_file(pkg_name, bad_changelog_path):
    data = ''
    with open(bad_changelog_path, 'rb') as file:
        for line in file:
            line = str(line.decode('UTF-8').rstrip())
            if line[:2] == "##":
                title = line[2:].strip()
                data = data + ''.join(['^' for i in range(len(title))]) + '\n'
                data = data + title + '\n'
                data = data + ''.join(['^' for i in range(len(title))]) + '\n'
            else:
                ## Replace bullets with links
                if line == '\n' or len(line) == 0:
                    data = data + line + '\n'
                    continue
                sline = line.strip()
                if sline[0] != '*':
                    # Add line without changes
                    data = data + line + '\n'
                    continue
                if line.find('[#') < 0:
                    # Line does not have a link
                    data = data + line + '\n'
                    continue
                change = line[:line.find('[#')]
                link = line[line.find("[#"):]
                number = link[1:link.find('](')]
                url = link[link.find('https'):-2]
                new_line = change + '(`' + number + ' <' + url + '>`_)'
                data = data + new_line + '\n'

    return data