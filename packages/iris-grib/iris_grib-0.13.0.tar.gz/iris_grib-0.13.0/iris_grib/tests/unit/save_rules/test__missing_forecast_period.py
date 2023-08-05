# (C) British Crown Copyright 2013 - 2016, Met Office
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
Unit tests for :func:`iris_grib._save_rules._missing_forecast_period.`

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

# Import iris_grib.tests first so that some things can be initialised before
# importing anything else.
import iris_grib.tests as tests

import datetime
import numpy as np

from iris.cube import Cube
from iris.coords import DimCoord

from iris_grib._save_rules import _missing_forecast_period


class TestNoForecastReferenceTime(tests.IrisGribTest):
    def test_no_bounds(self):
        t_coord = DimCoord(15, 'time', units='hours since epoch')
        cube = Cube(23)
        cube.add_aux_coord(t_coord)

        res = _missing_forecast_period(cube)
        expected_rt = t_coord.units.num2date(15)
        expected_rt_type = 3
        expected_fp = 0
        expected_fp_type = 1
        expected = (expected_rt,
                    expected_rt_type,
                    expected_fp,
                    expected_fp_type)
        self.assertEqual(res, expected)

    def test_with_bounds(self):
        t_coord = DimCoord(15, 'time', bounds=[14, 16],
                           units='hours since epoch')
        cube = Cube(23)
        cube.add_aux_coord(t_coord)

        res = _missing_forecast_period(cube)
        expected_rt = t_coord.units.num2date(14)
        expected_rt_type = 3
        expected_fp = 0
        expected_fp_type = 1
        expected = (expected_rt,
                    expected_rt_type,
                    expected_fp,
                    expected_fp_type)
        self.assertEqual(res, expected)


class TestWithForecastReferenceTime(tests.IrisGribTest):
    def test_no_bounds(self):
        t_coord = DimCoord(3, 'time', units='days since epoch')
        frt_coord = DimCoord(8, 'forecast_reference_time',
                             units='hours since epoch')
        cube = Cube(23)
        cube.add_aux_coord(t_coord)
        cube.add_aux_coord(frt_coord)

        res = _missing_forecast_period(cube)
        expected_rt = frt_coord.units.num2date(8)
        expected_rt_type = 1
        expected_fp = 3 * 24 - 8
        expected_fp_type = 1
        expected = (expected_rt,
                    expected_rt_type,
                    expected_fp,
                    expected_fp_type)
        self.assertEqual(res, expected)

    def test_with_bounds(self):
        t_coord = DimCoord(3, 'time', bounds=[2, 4], units='days since epoch')
        frt_coord = DimCoord(8, 'forecast_reference_time',
                             units='hours since epoch')
        cube = Cube(23)
        cube.add_aux_coord(t_coord)
        cube.add_aux_coord(frt_coord)

        res = _missing_forecast_period(cube)
        expected_rt = frt_coord.units.num2date(8)
        expected_rt_type = 1
        expected_fp = 2 * 24 - 8
        expected_fp_type = 1
        expected = (expected_rt,
                    expected_rt_type,
                    expected_fp,
                    expected_fp_type)
        self.assertEqual(res, expected)


if __name__ == "__main__":
    tests.main()
