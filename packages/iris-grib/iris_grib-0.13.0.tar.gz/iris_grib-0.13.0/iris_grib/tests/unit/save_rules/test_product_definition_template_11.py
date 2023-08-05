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
Unit tests for :func:`iris_grib._save_rules.product_definition_template_11`

"""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

# Import iris_grib.tests first so that some things can be initialised before
# importing anything else.
import iris_grib.tests as tests

from cf_units import Unit
import gribapi
import mock

from iris.coords import CellMethod, DimCoord
import iris.tests.stock as stock

from iris_grib._save_rules import product_definition_template_11


class TestRealizationIdentifier(tests.IrisGribTest):
    def setUp(self):
        self.cube = stock.lat_lon_cube()
        # Rename cube to avoid warning about unknown discipline/parameter.
        self.cube.rename('air_temperature')
        coord = DimCoord(23, 'time', bounds=[0, 100],
                         units=Unit('days since epoch', calendar='standard'))
        self.cube.add_aux_coord(coord)
        coord = DimCoord(4, 'realization', units='1')
        self.cube.add_aux_coord(coord)

    @mock.patch.object(gribapi, 'grib_set')
    def test_realization(self, mock_set):
        cube = self.cube
        cell_method = CellMethod(method='sum', coords=['time'])
        cube.add_cell_method(cell_method)

        product_definition_template_11(cube, mock.sentinel.grib)
        mock_set.assert_any_call(mock.sentinel.grib,
                                 "productDefinitionTemplateNumber", 11)
        mock_set.assert_any_call(mock.sentinel.grib,
                                 "perturbationNumber", 4)
        mock_set.assert_any_call(mock.sentinel.grib,
                                 "numberOfForecastsInEnsemble", 255)
        mock_set.assert_any_call(mock.sentinel.grib,
                                 "typeOfEnsembleForecast", 255)


if __name__ == "__main__":
    tests.main()
