from commonstep.helpers import my_path
import pytest


class TestHelperMyPath:

    def test_my_path(self):

        existing_list = {"value": {"test": ["1", "2"]}}
        non_existing_list = {"value": {"test": ""}}
        empty_list = {"value": {"test": [], "summary": ""}}
        path = "value/test/3"

        expected_existing_list = {'value': {'test': ['1', '2', None, 'existing_list']}}
        expected_non_existing_list = "The following entry can not be added: {'test': ''}." \
                                     " This is not a list"
        expected_empty_list = {'value': {'test': [None, None, None, 'empty_list'], 'summary': ''}}

        assert my_path(existing_list, path, "existing_list") == expected_existing_list
        assert my_path(empty_list, path, "empty_list") == expected_empty_list

        with pytest.raises(ValueError, match=expected_non_existing_list):
            my_path(non_existing_list, path, "non_existing_list")

    def test_my_path_not_dictionary(self):
        existing_data = {
            "contact": {
                "name": "Test1",
                "phone": "0123456790",
                "fax": "01234567890",
                "email": "nsh.r&d.bl.uk.pfw.qc@neopost.com"
            },
            "address": {
                "address line 1": "Address1",
                "address line 2": "Address2",
                "address line 3": "Address3",
                "town": "ROMFORD",
                "postcode": "RM1 2AR",
                "country_code": "GB"
            }
        }
        path1 = "contact/name"
        path2 = "contact/test"
        path3 = "address/address line 1"

        expected_data1 = {
            "contact": {
                "name": "Test2",
                "phone": "0123456790",
                "fax": "01234567890",
                "email": "nsh.r&d.bl.uk.pfw.qc@neopost.com"
            },
            "address": {
                "address line 1": "Address1",
                "address line 2": "Address2",
                "address line 3": "Address3",
                "town": "ROMFORD",
                "postcode": "RM1 2AR",
                "country_code": "GB"
            }}
        expected_data2 = {
            "contact": {
                "name": "Test2",
                "phone": "0123456790",
                "fax": "01234567890",
                "email": "nsh.r&d.bl.uk.pfw.qc@neopost.com",
                "test": "123"
            },
            "address": {
                "address line 1": "Address1",
                "address line 2": "Address2",
                "address line 3": "Address3",
                "town": "ROMFORD",
                "postcode": "RM1 2AR",
                "country_code": "GB"
            }}
        expected_data3 = {
            "contact": {
                "name": "Test2",
                "phone": "0123456790",
                "fax": "01234567890",
                "email": "nsh.r&d.bl.uk.pfw.qc@neopost.com",
                "test": "123"
            },
            "address": {
                "address line 1": "AddressTest",
                "address line 2": "Address2",
                "address line 3": "Address3",
                "town": "ROMFORD",
                "postcode": "RM1 2AR",
                "country_code": "GB"
            }}
        assert my_path(existing_data, path1, "Test2") == expected_data1
        assert my_path(existing_data, path2, "123") == expected_data2
        assert my_path(existing_data, path3, "AddressTest") == expected_data3

