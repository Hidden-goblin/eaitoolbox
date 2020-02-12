# -*- coding: utf-8 -*-
import base64
import logging

import requests

from jiraapiabstraction.JiraAttachments import JiraAttachments
from jiraapiabstraction.JiraEpics import JiraEpics
from jiraapiabstraction.JiraIssues import JiraIssue
from jiraapiabstraction.JiraReporter import JiraReporter
from jiraapiabstraction.JiraStories import JiraStories
from jiraapiabstraction.JiraTests import JiraTests
from jiraapiabstraction.XRayIssues import XRayIssues

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class JiraConnection:
    """Abstraction of the Jira Rest API in order to perform specific operations.

        This class provides a simple mechanism to connect to Jira and perform restricted operations
        on several issues.
        You can use specific issues creation or use the more generic create_issue.

        All requests response will be encapsulated in a dictionary providing the status_code and
        the content.
    """
    IMPROVEMENT = "Improvement"
    TEST_EXECUTION = "Test Execution"
    IMPROVEMENT_FIELD_KEY = "customfield_10506"

    def __init__(self, url: str = None, username: str = None, password: str = None):
        assert url is not None, "The jira endpoint is mandatory"
        assert username is not None, "The username is mandatory"
        assert password is not None, "The password is mandatory"

        self.url = url.rstrip(" /.")
        self.token = base64.b64encode(str.encode("{}:{}".format(username, password))).decode()
        self.project_id = None

    def __del__(self):
        self.url = None
        self.token = None
        self.project_id = None

    def header(self):
        """
        The default request's header.
        :return: a default header dictionary
        """
        return {'Authorization': "Basic {}".format(self.token), 'content-type': 'application/json'}

    ###############################
    # PROJECT
    ###############################
    def get_project(self):
        """
        Get all the Project issues held in Jira.
        :raise Exception: Response status code is not 200 ok
        :return: a Request response.
        """
        response = requests.get("{}/rest/api/2/project".format(self.url), headers=self.header())
        if response.status_code != 200:
            log.error("Getting project cast an error {}".format(response.text))
            raise Exception("Getting project cast an error {}".format(response.text))
        else:
            return {"status_code": response.status_code,
                    "content": JiraIssue.sanitize(content=response.content)}

    def get_project_id(self, project_name: str = None, project_key: str = None):
        """
        Retrieve the project id from his name or key. If already set in the object instance it will
        return it.
        :param project_name: a string
        :param project_key: a string
        :return: a string as the project id.
        """
        if self.project_id:
            return self.project_id
        else:
            return self.set_project_id(project_name=project_name, project_key=project_key)

    def set_project_id(self, project_id=None, project_name=None, project_key=None):
        """
        Set the project giving either the project id, name or key.
        The object instance will store the project id.
        :param project_id: a string
        :param project_name: a string
        :param project_key: a string
        :raise Exception:
        :return: the project id
        """
        if project_id:
            self.project_id = project_id
            return self.project_id
        else:
            try:
                project_list = self.get_project()["content"]
            except Exception as exception:
                log.error("Retrieving project list fail; {}".format(repr(exception)))
                raise Exception("Retrieving project list fail; {}".format(repr(exception)))(None)

            if (project_name and isinstance(project_name, str)) or \
                    (project_key and isinstance(project_key, str)):
                for project_dict in project_list:
                    if project_key and project_dict['key'] == project_key:
                        self.project_id = project_dict['id']
                        return self.project_id
                    elif project_name and project_dict['name'] == project_name:
                        self.project_id = project_dict['id']
                        return self.project_id
                    else:
                        pass
                raise Exception("Project not found")
            log.error("No data to search")
            raise Exception("No data to search")

    #########################################
    # ISSUES
    #########################################

    def get_issue_meta(self):
        """
        Get the issues' project meta data
        :return:
        """
        return JiraIssue.get_issue_meta(url=self.url, headers=self.header(),
                                        project_id=self.project_id)

    def get_issue(self, issue_key: str = None):
        """
        Retrieve a Jira issue by its key.
        :param issue_key: a string as a Jira Key
        :return: a requests response
        """
        assert isinstance(issue_key, str), "issue_key must be a string"

        return JiraIssue.get_issue(url=self.url, headers=self.header(), issue_key=issue_key)

    def get_issue_identifier(self, issue_type: str = None):
        """
        Retrieve the issue id of a specific issue type.

        :param issue_type: the issue name
        :return: a string as a Jira id
        """
        assert isinstance(issue_type, str), "issue_type must be a string"

        return JiraIssue.get_issue_identifier(url=self.url, headers=self.header(),
                                              issue_type=issue_type)

    def update_issue_description(self, issue_key: str = None, description: str = None):
        """
        Update the given issue with the new description
        :param issue_key: a jira issue key
        :param description: the new description
        :return: a requests response
        """
        assert isinstance(issue_key, str), "issue_key must be a string"
        assert isinstance(description, str), "description must be a string"

        return JiraIssue.update_issue_description(url=self.url, headers=self.header(),
                                                  issue_key=issue_key, description=description)

    def get_issue_status(self, issue_key: str = None):
        """
        Retrieve the issue status
        :param issue_key: a jira issue key
        :return: a string as the status
        """
        assert isinstance(issue_key, str), "issue_key must be a string"

        return JiraIssue.get_issue_status(url=self.url, headers=self.header(), issue_key=issue_key)

    def create_issue(self, issue_data: dict = None):
        """
        Create a new issue in the project.
        :param issue_data:
        :return: a request response
        """
        return JiraIssue.create_issue(url=self.url, headers=self.header(), issue_data=issue_data)

    def update_issue(self, issue_key: str = None, issue_data: dict = None):
        """
        Update the issue with the given data
        :param issue_key: the jira issue key
        :param issue_data: the issue update
        :return: a request Response
        """
        return JiraIssue.update_issue(url=self.url,
                                      headers=self.header(),
                                      issue_key=issue_key,
                                      issue_data=issue_data)

    def create_link(self, from_key=None, to_key=None, link_type=None):
        return JiraIssue.create_link(url=self.url, headers=self.header(), from_key=from_key,
                                     to_key=to_key, link_type=link_type)

    def search(self, jql_query: str = None, field_list: list = None, paginated: bool = True):
        assert isinstance(jql_query, str), "jql_query must be a string"
        assert isinstance(field_list, list), "field_list must be a list"
        assert all([isinstance(field, str) for field in field_list]), \
            "all fields in the field_list must be a string"
        assert isinstance(paginated, bool), "paginated is a boolean True or False"

        if paginated:
            return JiraIssue.search(url=self.url, headers=self.header(),
                                    search_request={'jql': jql_query, 'fields': field_list})
        else:
            return JiraIssue.search_issues(url=self.url, headers=self.header(),
                                           search_request={'jql': jql_query, 'fields': field_list})

    #########################################
    # Attachments
    #########################################

    def get_issue_attachments_id(self, issue_key=None):
        assert isinstance(issue_key, str), "issue_key must be a string"

        return JiraIssue.get_issue_attachments_id(url=self.url, headers=self.header(),
                                                  issue_key=issue_key)

    def retrieve_attachments(self, issue_key=None, attachment_id=None, folder=None):
        assert isinstance(issue_key, str), "issue_key must be a string"

        return JiraAttachments.retrieve_attachments(url=self.url, headers=self.header(),
                                                    issue_key=issue_key,
                                                    attachment_id=attachment_id, folder=folder)

    def add_attachments_to_issue(self, issue_key=None, file_name=None):
        """

        :param issue_key:
        :param file_name:
        :return:
        """
        assert isinstance(issue_key, str), "issue_key must be a string"

        return JiraIssue.add_attachments_to_issue(url=self.url, headers=self.header(),
                                                  issue_key=issue_key, file_name=file_name)

    def delete_attachments(self, issue_key=None, attachment_id=None):
        assert isinstance(issue_key, str), "issue_key must be a string"

        return JiraAttachments.delete_attachments(url=self.url, headers=self.header(),
                                                  issue_key=issue_key, attachment_id=attachment_id)

    ############################################
    # STORY
    ############################################

    def create_story(self, title=None, description=None, epic_key=None, actor=None, action=None,
                     benefit=None):
        return JiraStories.create_story(url=self.url, headers=self.header(),
                                        project_id=self.project_id, title=title,
                                        description=description, epic_key=epic_key, actor=actor,
                                        action=action, benefit=benefit)

    def update_story(self, issue_key=None, title=None, description=None, epic_key=None, actor=None,
                     action=None, benefit=None):
        return JiraStories.update_story(url=self.url, headers=self.header(), title=title,
                                        description=description, epic_key=epic_key, actor=actor,
                                        action=action, benefit=benefit, issue_key=issue_key)

    ###########################################
    # EPIC
    ###########################################

    def get_epics(self):
        """
        Get all epics related to a project
        :return: a list of key-epic name sets
        """
        return JiraEpics.get_epics(url=self.url, headers=self.header(), project_id=self.project_id)

    def add_epic(self, epic_name=None, epic_summary=None):
        return JiraEpics.add_epic(url=self.url, headers=self.header(), project_id=self.project_id,
                                  epic_name=epic_name, epic_summary=epic_summary)

    ###########################################
    # TEST
    ###########################################

    def add_test(self, story_key=None, test_description=None, test_name=None, test_type=None):
        data = {"fields": {
            "project": {
                "id": str(self.project_id)
            },
            "summary": test_name,
            "description": "",
            "issuetype": {
                "id": str(self.get_issue_identifier(issue_type=JiraTests.TEST))
            },
            "customfield_10202": {"value": "Cucumber"},
            "customfield_10203": {"value": str(test_type)},
            "customfield_10204": test_description
        }
        }
        log.debug("data: \n{}".format(data))
        response = self.create_issue(issue_data=data)
        log.debug("response: {}".format(response.text))
        key = response.json()["key"]

        response = self.create_link(from_key=key, to_key=story_key, link_type="Tests")
        return response, key

    def update_test(self, test_key=None, test_description=None, test_name=None, test_type=None):
        data = {"fields": {
            "summary": test_name,
            "description": "",
            "customfield_10202": {"value": "Cucumber"},
            "customfield_10203": {"value": str(test_type)},
            "customfield_10204": test_description
        }
        }
        return self.update_issue(issue_key=test_key, issue_data=data)

    def get_link_type(self):
        return requests.get("{}/rest/api/2/issueLinkType".format(self.url), headers=self.header())

    def download_execution_evidences(self, test_execution_key=None, folder=None):
        return XRayIssues.download_evidence(url=self.url, headers=self.header(),
                                            test_execution_key=test_execution_key,
                                            folder=folder)

    def download_plan_evidences(self, test_plan_key=None, folder=None):
        return XRayIssues.download_test_plan_evidences(url=self.url, headers=self.header(),
                                                       test_plan_key=test_plan_key,
                                                       folder=folder)

    def download_release_evidences(self, release_name=None, folder=None):
        return XRayIssues.download_release_evidence(url=self.url, headers=self.header(),
                                                    release_name=release_name,
                                                    folder=folder)

    def import_execution_to_test_plan(self, test_plan_key=None,
                                      cucumber_report_path=None, summary=None):
        response = XRayIssues.create_test_execution(url=self.url, headers=self.header(),
                                                    result_file=cucumber_report_path)
        if response.ok:
            test_execution_key = response.json()["testExecIssue"]["key"]
            data = {"update": {},
                    "fields": {
                        "customfield_10228": [test_plan_key],
                        "summary": summary
                    }}
            return self.update_issue(issue_key=test_execution_key, issue_data=data)

    def test_execution_load_attachments(self, execution_key=None, evidence_files=None):
        return XRayIssues.load_attachments(url=self.url,
                                           headers=self.header(),
                                           execution_key=execution_key,
                                           evidence_files=evidence_files)

    #########################################
    # Reports
    #########################################

    def release_report(self, release_name: str = None, destination_folder: str = None,
                       test_plan_key: str = None, test_execution_key: str = None):

        assert isinstance(release_name, str) or isinstance(test_plan_key, str) or \
               isinstance(test_execution_key,
                          str), "release_name or test_plan_key or test execution_key must be a string"  # noqa
        assert isinstance(destination_folder, str), "destination_folder must be a string"

        # check folder and prepare it
        destination_folder = JiraReporter.check_folder(folder=destination_folder)

        # catch many values for test_executions
        if (test_execution_key is not None) and (',' in test_execution_key):
            test_execution_key = test_execution_key.replace(' ', '')  # remove spaces
            test_execution_list = test_execution_key.split(',')  # separator ,
            for test_exec in test_execution_list:
                log.info("test execution: {}".format(test_exec))
                result = JiraReporter.create_release_report(url=self.url, headers=self.header(),
                                                            release_name=release_name,
                                                            test_plan_key=test_plan_key,
                                                            test_execution_key=test_exec,
                                                            folder=destination_folder)
                log.debug("result: {}".format(result))
                if result:
                    log.warning("Error for report {}".format(test_exec))

        else:
            return JiraReporter.create_release_report(url=self.url, headers=self.header(),
                                                      release_name=release_name,
                                                      test_plan_key=test_plan_key,
                                                      test_execution_key=test_execution_key,
                                                      folder=destination_folder)
