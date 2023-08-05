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
Test function :func:`iris_grib._load_convert.ellipsoid_geometry.

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

# import iris_grib.tests first so that some things can be initialised
# before importing anything else.
import iris_grib.tests as tests

from iris_grib._load_convert import ellipsoid_geometry


class Test(tests.IrisGribTest):
    def setUp(self):
        self.section = {'scaledValueOfEarthMajorAxis': 10,
                        'scaleFactorOfEarthMajorAxis': 1,
                        'scaledValueOfEarthMinorAxis': 100,
                        'scaleFactorOfEarthMinorAxis': 2,
                        'scaledValueOfRadiusOfSphericalEarth': 1000,
                        'scaleFactorOfRadiusOfSphericalEarth': 3}

    def test_geometry(self):
        result = ellipsoid_geometry(self.section)
        self.assertEqual(result, (1.0, 1.0, 1.0))


if __name__ == '__main__':
    tests.main()
