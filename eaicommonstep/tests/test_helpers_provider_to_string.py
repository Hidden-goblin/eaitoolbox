from eaicommonstep.helpers import provider_to_string


class TestHelpersProviderToString:

    def test_boolean(self):
        response = provider_to_string(True)
        assert isinstance(response, str), "Not a string"
        assert response == "true", f"Expecting 'true' get '{response}"

        response = provider_to_string(False)
        assert isinstance(response, str), "Not a string"
        assert response == "false", f"Expecting 'false' get '{response}"

        response = provider_to_string(0)
        assert isinstance(response, str), "Not a string"
        assert response == "0", f"Expecting '0' get '{response}"

    def test_none(self):
        response = provider_to_string()
        assert isinstance(response, str), "Not a string"
        assert response == "", f"Expecting '' get '{response}"

    def test_string(self):
        response = provider_to_string("True")
        assert isinstance(response, str), "Not a string"
        assert response == "True", f"Expecting 'true' get '{response}"

    def test_list(self):
        response = provider_to_string([1, 'blue', True])
        assert isinstance(response, str), "Not a string"
        assert response == "[1, 'blue', True]", f"Expecting 'true' get '{response}"
