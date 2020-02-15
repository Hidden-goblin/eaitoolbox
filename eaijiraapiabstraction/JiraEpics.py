from eaijiraapiabstraction.JiraIssues import JiraIssue


class JiraEpics:
    EPIC = "Epic"

    @staticmethod
    def get_epics(url=None, headers=None, project_id=None):
        """
        Get all epics related to a project
        :return: a list of key-epic name sets
        """
        data = {"jql": "project = {} AND type = Epic".format(project_id),
                "fields": ["key", "customfield_10004"]}
        list_rep = []
        response = JiraIssue.search_issues(url=url, headers=headers, search_request=data)
        issues = response.json()["issues"]
        for item in issues:
            list_rep.append((item["key"], item["fields"]["customfield_10004"]))
        return list_rep

    @staticmethod
    def add_epic(url=None, headers=None, project_id=None, epic_name=None, epic_summary=None):
        data = {"fields": {"project": {"id": str(project_id)},
                           "summary": epic_summary,
                           "issuetype": {"id": str(JiraIssue.get_issue_identifier(issue_type=JiraEpics.EPIC))},  # noqa
                           "customfield_10004": epic_name}}
        return JiraIssue.create_issue(url=url, headers=headers, issue_data=data)
