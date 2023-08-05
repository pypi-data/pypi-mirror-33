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
"""
Test function
:func:`iris_grib._load_convert.grid_definition_template_0_and_1`.

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

# Import iris_grib.tests first so that some things can be initialised
# before importing anything else.
import iris_grib.tests as tests

from iris.exceptions import TranslationError

from iris_grib._load_convert import grid_definition_template_0_and_1


class Test(tests.IrisGribTest):

    def test_unsupported_quasi_regular__number_of_octets(self):
        section = {'numberOfOctectsForNumberOfPoints': 1}
        cs = None
        metadata = None
        with self.assertRaisesRegexp(TranslationError, 'quasi-regular'):
            grid_definition_template_0_and_1(section,
                                             metadata,
                                             'latitude',
                                             'longitude',
                                             cs)

    def test_unsupported_quasi_regular__interpretation(self):
        section = {'numberOfOctectsForNumberOfPoints': 1,
                   'interpretationOfNumberOfPoints': 1}
        cs = None
        metadata = None
        with self.assertRaisesRegexp(TranslationError, 'quasi-regular'):
            grid_definition_template_0_and_1(section,
                                             metadata,
                                             'latitude',
                                             'longitude',
                                             cs)


if __name__ == '__main__':
    tests.main()
