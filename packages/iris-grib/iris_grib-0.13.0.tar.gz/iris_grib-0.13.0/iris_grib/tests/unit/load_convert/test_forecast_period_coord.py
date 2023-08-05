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
Test function :func:`iris_grib._load_convert.forecast_period_coord.

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

# import iris_grib.tests first so that some things can be initialised
# before importing anything else.
import iris_grib.tests as tests

from iris.coords import DimCoord

from iris_grib._load_convert import forecast_period_coord


class Test(tests.IrisGribTest):
    def test(self):
        # (indicatorOfUnitOfTimeRange, forecastTime, expected-hours)
        times = [(0, 60, 1),     # minutes
                 (1, 2, 2),      # hours
                 (2, 1, 24),     # days
                 (10, 2, 6),     # 3 hours
                 (11, 3, 18),    # 6 hours
                 (12, 2, 24),    # 12 hours
                 (13, 3600, 1)]  # seconds

        for indicatorOfUnitOfTimeRange, forecastTime, hours in times:
            coord = forecast_period_coord(indicatorOfUnitOfTimeRange,
                                          forecastTime)
            self.assertIsInstance(coord, DimCoord)
            self.assertEqual(coord.standard_name, 'forecast_period')
            self.assertEqual(coord.units, 'hours')
            self.assertEqual(coord.shape, (1,))
            self.assertEqual(coord.points[0], hours)
            self.assertFalse(coord.has_bounds())


if __name__ == '__main__':
    tests.main()
