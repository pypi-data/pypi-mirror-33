import unittest
from unittest.mock import patch

from apodeflags import features, errors, utils

class TestFeatures(unittest.TestCase):
    def setUp(self):
        self.f = features.Features()

    def test_available_flags(self):
        self.assertIsInstance(self.f.available_flags, dict)

    def test_new_feature_is_not_enabled(self):
        self.assertFalse(self.f.is_enabled('new_feature'))

    def test_new_feature_is_disabled(self):
        self.assertTrue(self.f.is_disabled('new_feature'))

    def test_is_enabled_with_missing_flag(self):
        with self.assertRaises(errors.FeatureDoesNotExist):
            self.f.is_enabled('missing_feature')

    @patch.object(features.Features, 'validate')
    def test_calls_validate(self, mock_validate):
        self.f.is_enabled('new_feature')
        mock_validate.assert_called_once

    def test_validate_with_invalid_flag(self):
        self.f._flags = dict(invalid_flag=True)
        with self.assertRaises(errors.FeatureDoesNotExist) as e:
            self.f.validate()
        self.assertEqual(e.exception.args[0], "Invalid feature flags: {'invalid_flag'}")

    def test_validate_with_invalid_flag_value(self):
        self.f._flags = dict(new_feature='INVALID')
        with self.assertRaises(errors.FeatureValueMustBeBoolean) as e:
            self.f.validate()
        self.assertEqual(e.exception.args[0], "Invalid feature flag values: {'INVALID'}")

    @utils.with_features(something=True)
    def test_with_features_decorator(self):
        self.assertTrue(self.f.get('something'))

    @utils.with_features()
    def test_with_features_decorator_when_empty(self):
        self.assertEqual(self.f.available_flags, dict())
