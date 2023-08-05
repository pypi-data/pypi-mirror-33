# (C) British Crown Copyright 2016, Met Office
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
"""Unit tests for the `iris_grib.save_messages` function."""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
import six

# Import iris_grib.tests first so that some things can be initialised before
# importing anything else.
import iris_grib.tests as tests

import gribapi
import mock
import numpy as np

import iris_grib


class TestSaveMessages(tests.IrisGribTest):
    def setUp(self):
        # Create a test object to stand in for a real PPField.
        self.grib_message = gribapi.grib_new_from_samples("GRIB2")

    def test_save(self):
        if six.PY3:
            open_func = 'builtins.open'
        else:
            open_func = '__builtin__.open'
        m = mock.mock_open()
        with mock.patch(open_func, m, create=True):
            # sending a MagicMock object to gribapi raises an AssertionError
            # as the gribapi code does a type check
            # this is deemed acceptable within the scope of this unit test
            with self.assertRaises((AssertionError, TypeError)):
                iris_grib.save_messages([self.grib_message], 'foo.grib2')
        self.assertTrue(mock.call('foo.grib2', 'wb') in m.mock_calls)

    def test_save_append(self):
        if six.PY3:
            open_func = 'builtins.open'
        else:
            open_func = '__builtin__.open'
        m = mock.mock_open()
        with mock.patch(open_func, m, create=True):
            # sending a MagicMock object to gribapi raises an AssertionError
            # as the gribapi code does a type check
            # this is deemed acceptable within the scope of this unit test
            with self.assertRaises((AssertionError, TypeError)):
                iris_grib.save_messages([self.grib_message], 'foo.grib2',
                                        append=True)
        self.assertTrue(mock.call('foo.grib2', 'ab') in m.mock_calls)


if __name__ == "__main__":
    tests.main()
