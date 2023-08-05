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
"""Unit tests for the `iris_grib._load_generate` function."""

from __future__ import (absolute_import, division, print_function)
from six.moves import (filter, input, map, range, zip)  # noqa

import iris_grib.tests as tests

import mock

import iris
from iris.exceptions import TranslationError
from iris.fileformats.rules import Loader

import iris_grib
from iris_grib import GribWrapper
from iris_grib import _load_generate
from iris_grib.message import GribMessage


class Test(tests.IrisGribTest):
    def setUp(self):
        self.fname = mock.sentinel.fname
        self.message_id = mock.sentinel.message_id
        self.grib_fh = mock.sentinel.grib_fh

    def _make_test_message(self, sections):
        raw_message = mock.Mock(sections=sections, _message_id=self.message_id)
        file_ref = mock.Mock(open_file=self.grib_fh)
        return GribMessage(raw_message, None, file_ref=file_ref)

    def test_grib1(self):
        sections = [{'editionNumber': 1}]
        message = self._make_test_message(sections)
        mfunc = 'iris_grib.GribMessage.messages_from_filename'
        mclass = 'iris_grib.GribWrapper'
        with mock.patch(mfunc, return_value=[message]) as mock_func:
            with mock.patch(mclass, spec=GribWrapper) as mock_wrapper:
                field = next(_load_generate(self.fname))
                mock_func.assert_called_once_with(self.fname)
                self.assertIsInstance(field, GribWrapper)
                mock_wrapper.assert_called_once_with(self.message_id,
                                                     grib_fh=self.grib_fh)

    def test_grib2(self):
        sections = [{'editionNumber': 2}]
        message = self._make_test_message(sections)
        mfunc = 'iris_grib.GribMessage.messages_from_filename'
        with mock.patch(mfunc, return_value=[message]) as mock_func:
            field = next(_load_generate(self.fname))
            mock_func.assert_called_once_with(self.fname)
            self.assertEqual(field, message)

    def test_grib_unknown(self):
        sections = [{'editionNumber': 0}]
        message = self._make_test_message(sections)
        mfunc = 'iris_grib.GribMessage.messages_from_filename'
        emsg = 'GRIB edition 0 is not supported'
        with mock.patch(mfunc, return_value=[message]):
            with self.assertRaisesRegexp(TranslationError, emsg):
                next(_load_generate(self.fname))


if __name__ == '__main__':
    tests.main()
