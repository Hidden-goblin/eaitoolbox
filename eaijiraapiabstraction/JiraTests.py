from eaijiraapiabstraction.JiraIssues import JiraIssue


class JiraTests:
    TEST = "Test"

    @staticmethod
    def add_test(url: str = None, headers: dict = None, project_id: str = None,
                 story_key: str = None, test_description: str = None, test_name: str = None,
                 test_type: str = None):
        """
        Create a Jira "test" entry related to a project and story
        TODO work on the customfield as it may vary with the jira setting
        :param url: the jira server url without endpoint
        :param headers: the request headers
        :param project_id: the project id not the project key
        :param story_key: the story key the test is related to
        :param test_description: the test description
        :param test_name: the test name
        :param test_type: the test type (Manual, Cucumber, Generic)
        :return: the create link response and the test key
        """
        data = {"fields": {
            "project": {
                "id": str(project_id)
            },
            "summary": test_name,
            "description": "",
            "issuetype": {
                "id": str(JiraIssue.get_issue_identifier(url=url, headers=headers,
                                                         issue_type=JiraTests.TEST))
            },
            "customfield_10202": {"value": "Cucumber"},
            "customfield_10203": {"value": str(test_type)},
            "customfield_10204": test_description
        }
        }

        response = JiraIssue.create_issue(url=url, headers=headers, issue_data=data)
        key = response.json()["key"]

        response = JiraIssue.create_link(url=url, headers=headers, from_key=key, to_key=story_key,
                                         link_type="Tests")
        return response, key

    @staticmethod
    def update_test(url=None, headers=None, test_key=None, test_description=None, test_name=None,
                    test_type=None):
        data = {"fields": {
            "summary": test_name,
            "description": "",
            "customfield_10202": {"value": "Cucumber"},
            "customfield_10203": {"value": str(test_type)},
            "customfield_10204": test_description
        }
        }
        return JiraIssue.update_issue(url=url, headers=headers, issue_key=test_key, issue_data=data)

    @staticmethod
    def get_test_plan_in_release(url: str = None, headers: dict = None, release_name: str = None):
        """

        :param url: the jira server url without endpoint
        :param headers: the request headers
        :param release_name: the release name
        :return: a dictionary containing the key "issues" which value is a list of test plan key
        in a dictionary i.e.
        can be acceded with return_var["issues"][position]["key"]
        """
        data = {"jql": 'fixVersion="{}" AND issueType = "Test Plan"'.format(release_name),
                "fields": ["key", ]}

        return JiraIssue.search_issues(url=url, headers=headers, search_request=data)
