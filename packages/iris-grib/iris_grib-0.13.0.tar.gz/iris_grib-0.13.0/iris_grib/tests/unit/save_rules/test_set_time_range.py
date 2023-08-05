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
Unit tests for :func:`iris_grib._save_rules.set_time_range`

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa
import six

# Import iris_grib.tests first so that some things can be initialised before
# importing anything else.
import iris_grib.tests as tests

import warnings

from cf_units import Unit
import gribapi
import mock

from iris.coords import DimCoord

from iris_grib._save_rules import set_time_range


class Test(tests.IrisGribTest):
    def setUp(self):
        self.coord = DimCoord(0, 'time',
                              units=Unit('hours since epoch',
                                         calendar='standard'))

    def test_no_bounds(self):
        with self.assertRaisesRegexp(ValueError, 'Expected time coordinate '
                                     'with two bounds, got 0 bounds'):
            set_time_range(self.coord, mock.sentinel.grib)

    def test_three_bounds(self):
        self.coord.bounds = [0, 1, 2]
        with self.assertRaisesRegexp(ValueError, 'Expected time coordinate '
                                     'with two bounds, got 3 bounds'):
            set_time_range(self.coord, mock.sentinel.grib)

    def test_non_scalar(self):
        coord = DimCoord([0, 1], 'time', bounds=[[0, 1], [1, 2]],
                         units=Unit('hours since epoch', calendar='standard'))
        with self.assertRaisesRegexp(ValueError, 'Expected length one time '
                                     'coordinate, got 2 points'):
            set_time_range(coord, mock.sentinel.grib)

    @mock.patch.object(gribapi, 'grib_set')
    def test_hours(self, mock_set):
        lower = 10
        upper = 20
        self.coord.bounds = [lower, upper]
        set_time_range(self.coord, mock.sentinel.grib)
        mock_set.assert_any_call(mock.sentinel.grib,
                                 'indicatorOfUnitForTimeRange', 1)
        mock_set.assert_any_call(mock.sentinel.grib,
                                 'lengthOfTimeRange', upper - lower)

    @mock.patch.object(gribapi, 'grib_set')
    def test_days(self, mock_set):
        lower = 4
        upper = 6
        self.coord.bounds = [lower, upper]
        self.coord.units = Unit('days since epoch', calendar='standard')
        set_time_range(self.coord, mock.sentinel.grib)
        mock_set.assert_any_call(mock.sentinel.grib,
                                 'indicatorOfUnitForTimeRange', 1)
        mock_set.assert_any_call(mock.sentinel.grib,
                                 'lengthOfTimeRange',
                                 (upper - lower) * 24)

    @mock.patch.object(gribapi, 'grib_set')
    def test_fractional_hours(self, mock_set_long):
        lower = 10.0
        upper = 20.9
        self.coord.bounds = [lower, upper]
        with warnings.catch_warnings(record=True) as warn:
            warnings.simplefilter("always")
            set_time_range(self.coord, mock.sentinel.grib)
        self.assertEqual(len(warn), 1)
        msg = 'Truncating floating point lengthOfTimeRange 10\.8?9+ ' \
              'to integer value 10'
        six.assertRegex(self, str(warn[0].message), msg)
        mock_set_long.assert_any_call(mock.sentinel.grib,
                                      'indicatorOfUnitForTimeRange', 1)
        mock_set_long.assert_any_call(mock.sentinel.grib,
                                      'lengthOfTimeRange', int(upper - lower))


if __name__ == "__main__":
    tests.main()
