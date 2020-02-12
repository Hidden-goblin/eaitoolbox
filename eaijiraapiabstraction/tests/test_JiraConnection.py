import pytest
from unittest.mock import MagicMock, patch
from jiraapiabstraction.JiraConnection import JiraConnection


class TestJiraConnection:
    @pytest.fixture
    def jira_connection(self):
        jira_connection = JiraConnection(username="toto", password="titi",
                                         url="http://my.domain.com")
        jira_connection.project_id = 10051
        return jira_connection

    @pytest.fixture
    def jira_connection_no_project(self):
        return JiraConnection(username="toto", password="titi", url="http://my.domain.com")

    def test_jiraconnection_valid(self):
        assert JiraConnection(username="toto", password="titi", url="http://my.domain.com")

    def test_jiraconnection_missing_username(self):
        with pytest.raises(AssertionError):
            JiraConnection(password="titi", url="http://my.domain.com")
            pytest.fail('Expecting username is a mandatory field')

    def test_jiraconnection_missing_password(self):
        with pytest.raises(AssertionError):
            JiraConnection(username="toto", url="http://my.domain.com")
            pytest.fail('Expecting password is a mandatory field')

    def test_jiraconnection_missing_url(self):
        with pytest.raises(AssertionError):
            JiraConnection(username="toto", password="titi")
            pytest.fail('Expecting jira endpoint is a mandatory field')

    def test_header(self, jira_connection):
        assert isinstance(jira_connection.header(), dict)
        assert all([element in ["Authorization", "content-type"]
                    for element in jira_connection.header().keys()])

    @patch('requests.get')
    @patch('jiraapiabstraction.JiraIssues.JiraIssue.sanitize')
    def test_get_project_valid(self, mock_sanitize, mock_get, jira_connection):
        instance = mock_get.return_value
        instance.status_code = 200
        mock_sanitize.return_value = {"toto": "titi"}
        assert all([element in ["status_code", "content"]
                    for element in jira_connection.get_project()])

    @patch('requests.get')
    def test_get_project_error(self, mock_get, jira_connection):
        instance = mock_get.return_value
        instance.status_code = 201
        with pytest.raises(Exception):
            jira_connection.get_project()
            pytest.fail("Error when retrieving the projects")

    def test_get_project_id(self, jira_connection):
        assert jira_connection.get_project_id() == 10051

    def test_get_project_id_none(self, jira_connection_no_project):
        test = jira_connection_no_project
        test.set_project_id = MagicMock(return_value=11111)
        assert test.get_project_id() == 11111

    def test_get_project_id_not_set(self, jira_connection_no_project):
        test = jira_connection_no_project
        test.set_project_id = MagicMock(side_effect=Exception("Retrieve project list fail"))
        with pytest.raises(Exception):
            test.get_project_id()
            pytest.fail("Retrieve project list fail")

    def test_get_project_id_no_parameter(self, jira_connection_no_project):
        test = jira_connection_no_project
        test.get_project = MagicMock(return_value={"content": [{"key": "TST", "id": "147",
                                                                "name": "Test Project"}]})
        with pytest.raises(Exception):
            test.get_project_id()
            pytest.fail("Missing arguments")

    def test_get_project_id_name_parameter(self, jira_connection_no_project):
        test = jira_connection_no_project
        test.get_project = MagicMock(return_value={"content": [{"key": "TST", "id": "147",
                                                                "name": "Test Project"}]})
        assert test.get_project_id(project_name="Test Project") == "147"

    def test_get_project_id_name_parameter_not_found(self, jira_connection_no_project):
        test = jira_connection_no_project
        test.get_project = MagicMock(return_value={"content": [{"key": "TST", "id": "147",
                                                                "name": "Test Project"}]})
        with pytest.raises(Exception):
            test.get_project_id(project_name="Test")
            pytest.fail("Project not found")

    def test_get_project_id_key_parameter(self, jira_connection_no_project):
        test = jira_connection_no_project
        test.get_project = MagicMock(return_value={"content": [{"key": "TST", "id": "147",
                                                                "name": "Test Project"}]})
        assert test.get_project_id(project_name="Test Project") == "147"

    def test_get_project_id_key_parameter_not_found(self, jira_connection_no_project):
        test = jira_connection_no_project
        test.get_project = MagicMock(return_value={"content": [{"key": "TST",
                                                                "id": "147",
                                                                "name": "Test Project"}]})
        with pytest.raises(Exception):
            test.get_project_id(project_key="Test")
            pytest.fail("Project not found")

    #######################################################
    # Test get_issue
    #######################################################
    @patch('jiraapiabstraction.JiraIssues.JiraIssue.get_issue', return_value="An issue")
    def test_get_issue_string_key(self, get_issue, jira_connection):
        test = jira_connection
        assert test.get_issue(issue_key="toto") == "An issue"

    @patch('jiraapiabstraction.JiraIssues.JiraIssue.get_issue', return_value="An issue")
    def test_get_issue_non_string_key(self, get_issue, jira_connection):
        test = jira_connection
        with pytest.raises(AssertionError):
            test.get_issue(issue_key=127)
            pytest.fail("Key must be a string")

    #######################################################
    # Test get_issue_identifier
    #######################################################
    @patch('jiraapiabstraction.JiraIssues.JiraIssue.get_issue_identifier', return_value="An issue")
    def test_get_issue_identifier_string_key(self, get_issue, jira_connection):
        test = jira_connection
        assert test.get_issue_identifier(issue_type="toto") == "An issue"

    @patch('jiraapiabstraction.JiraIssues.JiraIssue.get_issue_identifier', return_value="An issue")
    def test_get_issue_identifier_non_string_key(self, get_issue, jira_connection):
        test = jira_connection
        with pytest.raises(AssertionError):
            test.get_issue_identifier(issue_type=["127", ])
            pytest.fail("Key must be a string")

    #######################################################
    # Test update_issue_description
    #######################################################
    @patch('jiraapiabstraction.JiraIssues.JiraIssue.update_issue_description',
           return_value="Updated")
    def test_update_issue_description(self, mock_update, jira_connection):
        assert jira_connection.update_issue_description(issue_key="Key",
                                                        description="new desc") == "Updated"

    @patch('jiraapiabstraction.JiraIssues.JiraIssue.update_issue_description',
           return_value="Updated")
    def test_update_issue_description_non_string_key(self, mock_update, jira_connection):
        with pytest.raises(AssertionError):
            jira_connection.update_issue_description(issue_key=127, description="new desc")
            pytest.fail("Key must be a string")

    @patch('jiraapiabstraction.JiraIssues.JiraIssue.update_issue_description',
           return_value="Updated")
    def test_update_issue_description_non_string_description(self, mock_update, jira_connection):
        with pytest.raises(AssertionError):
            jira_connection.update_issue_description(issue_key="Key", description=127)
            pytest.fail("Description must be a string")

    #######################################################
    # Test get_issue_status
    #######################################################
    @patch('jiraapiabstraction.JiraIssues.JiraIssue.get_issue_status', return_value="An issue")
    def test_get_issue_status_string_key(self, get_issue, jira_connection):
        test = jira_connection
        assert test.get_issue_status(issue_key="toto") == "An issue"

    @patch('jiraapiabstraction.JiraIssues.JiraIssue.get_issue_status', return_value="An issue")
    def test_get_issue_status_non_string_key(self, get_issue, jira_connection):
        test = jira_connection
        with pytest.raises(AssertionError):
            test.get_issue_status(issue_key=["127", ])
            pytest.fail("Key must be a string")

    #######################################################
    # Test create_issue not tested as it just calls another method without any check
    #######################################################
    #######################################################
    # Test update_issue
    #######################################################
