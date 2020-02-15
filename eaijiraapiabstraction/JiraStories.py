from eaijiraapiabstraction.JiraIssues import JiraIssue


class JiraStories:
    ROLE_JIRA_KEY = "customfield_10503"
    ACTION_JIRA_KEY = "customfield_10504"
    BENEFIT_JIRA_KEY = "customfield_10505"
    STORY = "Story"

    @staticmethod
    def create_story(url=None, headers=None, project_id=None, title=None, description=None,
                     epic_key=None, actor=None, action=None, benefit=None):
        """
        Request the creation of a story
        :param project_id:
        :param headers:
        :param url:
        :param action:
        :param benefit:
        :param actor:
        :param epic_key:
        :param title:
        :param description:
        :return: request response
        """
        data = {"fields": {"project": {"id": str(project_id)},
                           "summary": title,
                           "issuetype": {"id": str(
                               JiraIssue.get_issue_identifier(url=url, headers=headers,
                                                              issue_type=JiraStories.STORY))},
                           "description": description,
                           "customfield_10002": epic_key,
                           JiraStories.ROLE_JIRA_KEY: actor,
                           JiraStories.ACTION_JIRA_KEY: action,
                           JiraStories.BENEFIT_JIRA_KEY: benefit}}
        return JiraIssue.create_issue(url=url, headers=headers, issue_data=data)

    @staticmethod
    def update_story(url=None, headers=None, issue_key=None, title=None, description=None,
                     epic_key=None, actor=None, action=None, benefit=None):
        data = {"fields": {"summary": title,
                           "description": description,
                           "customfield_10002": epic_key,
                           JiraStories.ROLE_JIRA_KEY: actor,
                           JiraStories.ACTION_JIRA_KEY: action,
                           JiraStories.BENEFIT_JIRA_KEY: benefit}}
        return JiraIssue.update_issue(url=url, headers=headers, issue_key=issue_key, issue_data=data)  # noqa
