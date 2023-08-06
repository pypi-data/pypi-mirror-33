# Copyright (C) 2015 Jonathan Laperle. All Rights Reserved.
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================

from __future__ import absolute_import, division, print_function

import sys
import unittest

from error import ValidationError, MultiValidationError


class ValidationErrorTest(unittest.TestCase):
    def test_message(self):
        err_msg = "test"
        try:
            raise ValidationError(err_msg)
        except ValidationError as e:
            self.assertEqual(str(e), err_msg)

    def test_raise(self):
        with self.assertRaises(ValidationError):
            raise ValidationError("test")

class MultiValidationErrorTest(unittest.TestCase):
    def test_message(self):
        err_msg = "\ntest"
        try:
            try:
                raise ValidationError("test")
            except ValidationError as e:
                raise MultiValidationError([e])
        except MultiValidationError as e:
            self.assertEqual(str(e), err_msg)

    def test_raise(self):
        with self.assertRaises(MultiValidationError):
            try:
                raise ValidationError("test")
            except ValidationError as e:
                raise MultiValidationError([e])

if __name__ == "__main__":
    unittest.main()
