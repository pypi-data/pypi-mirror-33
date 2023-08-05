# (C) British Crown Copyright 2014 - 2016, Met Office
#
# This file is part of iris-grib.
#
# iris-grib is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iris-grib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with iris-grib.  If not, see <http://www.gnu.org/licenses/>.
"""
Unit tests for iris-grib license header conformance.

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

from datetime import datetime
from fnmatch import fnmatch
import os
import re
import subprocess
import unittest

import iris_grib


LICENSE_TEMPLATE = """
# (C) British Crown Copyright {YEARS}, Met Office
#
# This file is part of iris-grib.
#
# iris-grib is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# iris-grib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with iris-grib.  If not, see <http://www.gnu.org/licenses/>.""".strip()

LICENSE_RE_PATTERN = re.escape(LICENSE_TEMPLATE).replace('\{YEARS\}', '(.*?)')
# Add shebang possibility to the LICENSE_RE_PATTERN
LICENSE_RE_PATTERN = r'(\#\!.*\n)?' + LICENSE_RE_PATTERN
LICENSE_RE = re.compile(LICENSE_RE_PATTERN, re.MULTILINE)

# Guess iris repo directory of Iris - realpath is used to mitigate against
# Python finding the iris package via a symlink.
IRIS_GRIB_DIR = os.path.realpath(os.path.dirname(iris_grib.__file__))
REPO_DIR = os.path.dirname(IRIS_GRIB_DIR)


class TestLicenseHeaders(unittest.TestCase):
    @staticmethod
    def years_of_license_in_file(fh):
        """
        Using :data:`LICENSE_RE` look for the years defined in the license
        header of the given file handle.

        If the license cannot be found in the given fh, None will be returned,
        else a tuple of (start_year, end_year) will be returned.

        """
        license_matches = LICENSE_RE.match(fh.read())
        if not license_matches:
            # no license found in file.
            return None

        years = license_matches.groups()[-1]
        if len(years) == 4:
            start_year = end_year = int(years)
        elif len(years) == 11:
            start_year, end_year = int(years[:4]), int(years[7:])
        else:
            fname = getattr(fh, 'name', 'unknown filename')
            raise ValueError("Unexpected year(s) string in {}'s copyright "
                             "notice: {!r}".format(fname, years))
        return (start_year, end_year)

    @staticmethod
    def whatchanged_parse(whatchanged_output):
        """
        Returns a generator of tuples of data parsed from
        "git whatchanged --pretty='TIME:%at". The tuples are of the form
        ``(filename, last_commit_datetime)``

        Sample input::

            ['TIME:1366884020', '',
             ':000000 100644 0000000... 5862ced... A\tlib/iris/cube.py']

        """
        dt = None
        for line in whatchanged_output:
            if not line.strip():
                continue
            elif line.startswith('TIME:'):
                dt = datetime.fromtimestamp(int(line[5:]))
            else:
                # Non blank, non date, line -> must be the lines
                # containing the file info.
                fname = ' '.join(line.split('\t')[1:])
                yield fname, dt

    @staticmethod
    def last_change_by_fname():
        """
        Return a dictionary of all the files under git which maps to
        the datetime of their last modification in the git history.

        .. note::

            This function raises a ValueError if the repo root does
            not have a ".git" folder. If git is not installed on the system,
            or cannot be found by subprocess, an IOError may also be raised.

        """
        # Check the ".git" folder exists at the repo dir.
        if not os.path.isdir(os.path.join(REPO_DIR, '.git')):
            raise ValueError('{} is not a git repository.'.format(REPO_DIR))

        # Call "git whatchanged" to get the details of all the files and when
        # they were last changed.
        output = subprocess.check_output(['git', 'whatchanged',
                                          "--pretty=TIME:%ct"],
                                         cwd=REPO_DIR)
        output = output.decode().split('\n')
        res = {}
        for fname, dt in TestLicenseHeaders.whatchanged_parse(output):
            if fname not in res or dt > res[fname]:
                res[fname] = dt

        return res

    def test_license_headers(self):
        exclude_patterns = ('setup.py',
                            'build/*',
                            'dist/*',
                            'docs/*',
                            'iris_grib/tests/unit/results/*',
                            'iris_grib.egg-info/*')

        try:
            last_change_by_fname = self.last_change_by_fname()
        except ValueError:
            # Caught the case where this is not a git repo.
            return self.skipTest('Iris-grib installation did not look like a '
                                 'git repo.')

        failed = False
        for fname, last_change in sorted(last_change_by_fname.items()):
            full_fname = os.path.join(REPO_DIR, fname)
            if full_fname.endswith('.py') and os.path.isfile(full_fname) and \
                    not any(fnmatch(fname, pat) for pat in exclude_patterns):
                with open(full_fname) as fh:
                    years = TestLicenseHeaders.years_of_license_in_file(fh)
                    if years is None:
                        print('The file {} has no valid header license and '
                              'has not been excluded from the license header '
                              'test.'.format(fname))
                        failed = True
                    elif last_change.year > years[1]:
                        print('The file header at {} is out of date. The last'
                              ' commit was in {}, but the copyright states it'
                              ' was {}.'.format(fname, last_change.year,
                                                years[1]))
                        failed = True

        if failed:
            raise ValueError('There were license header failures. See stdout.')


if __name__ == '__main__':
    unittest.main()
