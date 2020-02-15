# -*- coding: utf-8 -*-
from eaireporter.FeatureReporter import ExportUtilities


class TestFeatureReporter:

    def test_feature_reporter(self):
        test = ExportUtilities()
        test.create_application_documentation()
        assert True
