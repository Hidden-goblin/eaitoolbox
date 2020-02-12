import requests
import json
import logging
from copy import deepcopy


# TODO: update exception handling and raising
# TODO: implement a paranoid development
class JiraIssue:
    @staticmethod
    def get_issue_meta(url: str = None, headers: dict = None, project_id: str = None):
        """
        Get the issues' project meta data
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param project_id: the project identifier as a string
        :type project_id str
        :return: a requests response.
        """
        return requests.get("{}/rest/api/2/issue/createmeta".format(url), headers=headers,
                            params={'projectIds': str(project_id)})

    @staticmethod
    def get_issue(url: str = None, headers: dict = None, issue_key: str = None):
        """
        Retrieve a Jira issue by its key.
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_key: a string as a Jira Key
        :type issue_key str
        :return: a requests response
        """
        return requests.get("{}/rest/api/2/issue/{}".format(url, issue_key),
                            headers=headers)

    @staticmethod
    def get_issue_identifier(url: str = None, headers: dict = None, issue_type: str = None):
        """
        Retrieve the issue id of a specific issue type.
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_type: the issue name
        :return: a string as a Jira id
        """
        assert issue_type is not None, "Issue type is mandatory"
        assert isinstance(issue_type, str), "Issue type is a string"

        response = JiraIssue.get_issue_meta(url=url, headers=headers)
        # Response JSON is projects/<list>/issuetypes
        for response_issue_type in response.json()["projects"][0]["issuetypes"]:
            if response_issue_type['name'].casefold() == issue_type.casefold():
                return str(response_issue_type["id"])

        logging.error("Issue {} not found".format(issue_type))
        raise Exception("Issue {} not found".format(issue_type))

    @staticmethod
    def update_issue_description(url: str = None, headers: dict = None, issue_key: str = None,
                                 description: str = None):
        """
        Update the issue's description with the new description
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_key: the issue key to update
        :type issue_key str
        :param description: the new description
        :return: a requests response
        """
        data = {"update": {"description": [{'set': description}]}}
        return requests.put("{}/rest/api/2/issue/{}".format(url, issue_key),
                            data=json.dumps(data),
                            headers=headers)

    @staticmethod
    def get_issue_attachments_id(url: str = None, headers: dict = None, issue_key: str = None):
        """

        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_key:
        :return:
        """
        response = JiraIssue.get_issue(url=url, headers=headers, issue_key=issue_key)
        assert response.status_code == 200, "Can't get the issue {}".format(issue_key)

        attachments = response.json()["fields"]["attachment"]
        return [attachment["id"] for attachment in attachments]

    @staticmethod
    def get_issue_status(url: str = None, headers: dict = None, issue_key=None):
        """

        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_key:
        :return: a string as the status
        """
        response = requests.get("{}/rest/api/2/issue/{}".format(url, issue_key),
                                headers=headers)
        if response.status_code == 200:
            return response.json()['fields']['status']['name']
        else:
            raise Exception(
                "Get issue status return\n response code: '{}'\n response text: '{}'".format(response.status_code, response.text))  # noqa

    @staticmethod
    def create_issue(url: str = None, headers: dict = None, issue_data: dict = None):
        """
        Create an issue with the given payload
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_data:
        :type issue_data dict
        :return: a request Response
        """
        assert isinstance(issue_data, dict), "The payload must be a dictionary"
        assert issue_data != {}, "The payload can't be empty"

        return requests.post("{}/rest/api/2/issue".format(url), data=json.dumps(issue_data),
                             headers=headers)

    @staticmethod
    def update_issue(url: str = None, headers: dict = None, issue_key: str = None,
                     issue_data: dict = None):
        """

        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_key:
        :param issue_data:
        :return: a request Response
        """
        assert isinstance(issue_key, str), "The issue key is mandatory and must be a string"
        assert isinstance(issue_data, dict), "The payload must be a dictionary"
        assert "update" in issue_data, "The payload must contains the 'update' key"

        return requests.put("{}/rest/api/2/issue/{}".format(url, issue_key),
                            data=json.dumps(issue_data),
                            headers=headers)

    @staticmethod
    def create_link(url: str = None, headers: dict = None, from_key=None, to_key=None,
                    link_type=None):
        """

        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param from_key:
        :param to_key:
        :param link_type:
        :return:
        """
        data = {
            "type": {
                "name": str(link_type)
            },
            "inwardIssue": {
                "key": str(from_key)
            },
            "outwardIssue": {
                "key": str(to_key)
            }
        }
        return requests.post("{}/rest/api/2/issueLink".format(url), data=json.dumps(data),
                             headers=headers)

    @staticmethod
    def add_attachments_to_issue(url: str = None, headers: dict = None, issue_key=None,
                                 file_name=None):
        """
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_key:
        :param file_name:
        :return:
        """
        temp_header = deepcopy(headers)
        temp_header["X-Atlassian-Token"] = "no-check"

        with open(file_name, "rb") as file:
            return requests.post("{}/rest/api/2/issue/{}/attachments".format(url, issue_key),
                                 files={'file': file},
                                 headers=temp_header)

    @staticmethod
    def get_issue_attachments_links(url: str = None, headers: dict = None, issue_key=None):
        """
        Provide the list of issue's attachments.
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param issue_key: the jira issue key
        :return: a dictionary of dictionaries.
        """
        response = JiraIssue.get_issue(url=url, headers=headers, issue_key=issue_key)
        assert response.status_code == 200, "Can't get the issue {}".format(issue_key)

        attachments = response.json()["fields"]["attachment"]
        result = {}
        for attachment in attachments:
            result[attachment["id"]] = {"url": attachment["content"],
                                        "filename": attachment["filename"]}
        return result

    @staticmethod
    def search_issues(url: str = None, headers: dict = None, search_request=None):
        """
        Search all issues recursively i.e. try to get all issues matching the request without
         pagination
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param search_request:
        :return: a dictionary with "issues" key and value a list of requested fields as a dictionary
        """
        new_search = deepcopy(search_request)
        new_search["startAt"] = 0
        end_point = "{}/rest/api/2/search".format(url)
        post = requests.post
        dump = json.dumps
        response = post(url=end_point, headers=headers, data=dump(new_search))
        max_results = response.json()["maxResults"]
        search_return = {"issues": []}
        while max_results == len(response.json()["issues"]):
            search_return["issues"].extend(response.json()["issues"])
            new_search["startAt"] = new_search["startAt"] + response.json()["maxResults"]
            response = post(url=end_point, headers=headers, data=dump(new_search))

        search_return["issues"].extend(response.json()["issues"])
        return search_return

    @staticmethod
    def search(url: str = None, headers: dict = None, search_request=None):
        """
        Search issues bound to the search request. If there is a pagination the response will
         be limited to
        this pagination.
        The output differs from the search_issues method.
        :param url: the jira server url without endpoint
        :type url str
        :param headers: the request headers
        :type headers dict
        :param search_request:
        :return:
        """
        return requests.post(url="{}/rest/api/2/search".format(url), headers=headers,
                             data=json.dumps(search_request))

    @staticmethod
    def sanitize(content: bytes = None):
        """
        Sanitize a request content so that the value is a valid json
        :param content: an encoded string i.e. bytes
        :return: python json representation i.e. a dictionary
        """
        content = content.decode()  # Convert the bytes to string
        content.replace('\\"', '\\\"')  # Replace the faulty characters
        content = json.loads(content)  # Convert the string to a json representation
        return content
