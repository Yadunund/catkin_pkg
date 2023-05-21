"""This script generates REP-0132 CHANGELOG.rst files for git or hg repositories."""

from __future__ import print_function

import argparse
import logging
import os
import sys

from catkin_pkg.changelog import BAD_CHANGELOG_FILENAME, CHANGELOG_FILENAME
from catkin_pkg.changelog_generator_vcs import get_vcs_client
from catkin_pkg.md2rst_changelog_generator import generate_changelogs
from catkin_pkg.packages import find_packages

try:
    raw_input
except NameError:
    raw_input = input  # noqa: A001


def prompt_continue(msg, default):
    """Prompt the user for continuation."""
    if default:
        msg += ' [Y/n]?'
    else:
        msg += ' [y/N]?'

    while True:
        response = raw_input(msg)
        if not response:
            response = 'y' if default else 'n'
        else:
            response = response.lower()

        if response in ['y', 'n']:
            return response == 'y'

        print("Response '%s' was not recognized, please use one of the following options: y, Y, n, N" % response, file=sys.stderr)


def main(sysargs=None):
    parser = argparse.ArgumentParser(description='Generate a REP-0132 %s' % CHANGELOG_FILENAME)
    group_merge = parser.add_mutually_exclusive_group()
    parser.add_argument(
        '-a', '--all', action='store_true', default=True,
        help='Generate changelog for all versions instead of only the forthcoming one (only supported when no changelog file exists yet)')
    group_merge.add_argument(
        '--only-merges', action='store_true', default=False,
        help='Only add merge commits to the changelog')
    parser.add_argument(
        '--print-root', action='store_true', default=False,
        help='Output changelog content to the console as if there would be only one package in the root of the repository')
    parser.add_argument(
        '--skip-contributors', action='store_true', default=False,
        help='Skip adding the list of contributors to the changelog')
    group_merge.add_argument(
        '--skip-merges', action='store_true', default=False,
        help='Skip adding merge commits to the changelog')
    parser.add_argument(
        '-y', '--non-interactive', action='store_true', default=False,
        help="Run without user interaction, confirming all questions with 'yes'")
    args = parser.parse_args(sysargs)

    base_path = '.'
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)


    # find packages
    packages = find_packages(base_path)
    if not packages:
        raise RuntimeError('No packages found')
    print('Found packages: %s' % ', '.join(sorted(p.name for p in packages.values())))

    # check for missing changelogs
    missing_changelogs = []
    for pkg_path, package in packages.items():
        bad_changelog_path = os.path.join(base_path, pkg_path, BAD_CHANGELOG_FILENAME)
        changelog_path = os.path.join(base_path, pkg_path, CHANGELOG_FILENAME)
        if not os.path.exists(changelog_path) and os.path.exists(bad_changelog_path):
            missing_changelogs.append(package.name)
    print('Packages with missing CHANGELOG.md files: %s' % ', '.join(sorted(missing_changelogs)))

    if args.all and not missing_changelogs:
        raise RuntimeError('All packages already have a changelog. Either remove (some of) them before using --all or invoke the script without --all.')

    if args.all and len(missing_changelogs) != len(packages):
        ignored = set([p.name for p in packages.values()]) - set(missing_changelogs)
        print('The following packages already have a changelog file and will be ignored: %s' % ', '.join(sorted(ignored)), file=sys.stderr)

    # prompt to switch to --all
    if not args.all and missing_changelogs:
        print('Some of the packages have no changelog file: %s' % ', '.join(sorted(missing_changelogs)))
        print('You might consider to use --all to generate the changelogs for all versions (not only for the forthcoming version).')
        if not args.non_interactive and not prompt_continue('Continue without --all option', default=False):
            raise RuntimeError('Skipping generation, rerun the script with --all.')

    generate_changelogs(base_path, packages, logger=logging)
    print('Done.')
    print('Please review the extracted commit messages and consolidate the changelog entries before committing the files!')


def main_catching_runtime_error(*args, **kwargs):
    try:
        main(*args, **kwargs)
    except RuntimeError as e:
        print('ERROR: ' + str(e), file=sys.stderr)
        sys.exit(1)
