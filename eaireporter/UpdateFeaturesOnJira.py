# coding=utf8
import logging
import os
import re
import argparse
import dpath.util
from behave.parser import parse_file
from jiraapiabstraction.JiraConnection import JiraConnection
from jiraapiabstraction.JiraIssues import JiraIssue

my_format = "%(asctime)s -- %(filename)s.%(funcName)s-- %(levelname)s -- %(message)s"
# my_format = "%(levelname)s -- %(message)s"  # use for debug

logging.basicConfig(level=logging.INFO, format=my_format)
log = logging.getLogger(__name__)

# mapping dictionary between feature & jira
mapping_feature_jira = {
    "description": "/fields/description",
    "story_tags": "/fields/issuelinks",
    # "precondition": "/fields/customfield_10210",  # Not supported yet
    "scenario_id": "key",
    "labels": "/fields/labels",
    "type": "/fields/customfield_10203",  # Jira's field: "Scenario type"
    "title": "/fields/summary",
    "scenario": "/fields/customfield_10204"
}


class UpdateFeatureOnJira:
    def __init__(self, url: str = None, username: str = None, password: str = None):
        """
        :param username: jira's login
        :param password: jira's password
        :param url: jira's URL
        """
        self.__connection = JiraConnection(url=url, username=username, password=password)
        self.feature = None  # feature file parsed via behave.parser

    def update_feature_on_jira(self, feature_repository: str = None, check=False):
        """
        get all features from a directory
        https://jira.neopost-id.com/confluence/display/PFWES/Synchronise+feature+files+with+Jira+tests  # noqa
        :param check: check option to not change on JIRA
        :param feature_repository: folder with features in it
        :return:
        """
        assert feature_repository is not None, "Missing 'feature_repository' argument"
        feature_files_list = UpdateFeatureOnJira.check_repository(feature_repository)
        error_files_list = list()
        for feature_file in feature_files_list:
            # get all project's features files and manage each individually
            # only if get_feature get correct value do something
            log.info('\n\t## Feature file: {}'.format(feature_file))
            error_file = self.get_feature(feature_file=feature_file)
            if error_file == 0:
                for i in range(0, len(self.feature["scenarios"])):  # for each scenario
                    jira_id = self.feature["scenarios"][i]["scenario_id"]
                    jira_test = UpdateFeatureOnJira.get_jira_test(self, jira_id)  # get jira data
                    jira_change = dict(UpdateFeatureOnJira.compare_feature_vs_jira(self, i,
                                                                                   jira_test))
                    if len(jira_change):  # if there are no change, send message
                        log.debug("{} changes to do: {}".format(jira_id, jira_change.keys()))
                        if check is False:  # if check option, do not change on JIRA
                            # todo add gitlab ci on dev --check
                            results = UpdateFeatureOnJira.update_jira_test(self, jira_id,
                                                                           jira_change)
                            log.debug("Results: \n\t{}".format(results))
            else:  # if get_feature can't get feature
                log.warning("No feature in file: {}".format(feature_file))
                error_files_list.append(feature_file)
        # if there are some files in error, write it in the logs
        if len(error_files_list) != 0:
            error_files = "\n\t".join(error_files_list)
            log.error('\n#################\n## Run summary ##\nThese files were in error, '
                      'please check them:\n\t{}'.format(error_files))
        return 0

    def get_jira_test(self, jira_id=None):
        # get the test case from JIRA from a jira_id (ex: PFWES-5336)
        assert jira_id is not None, "Impossible to get jira issue: {}".format(jira_id)
        log.debug("## Get jira: {}".format(jira_id))
        jira_test_json = self.__connection.get_issue(jira_id)
        jira_test = 0
        if jira_test_json.status_code != 200:  # if we can't get the test
            log.error("Connection to JIRA impossible. Check url, login/password - HTTP: {}".format(
                jira_test_json.status_code))
            log.debug(jira_test_json.content)
            quit(1)
        else:
            jira_test = JiraIssue.sanitize(jira_test_json.content)
            log.debug('jira {}\n{}'.format(jira_id, jira_test))
            # check if jira's ID is a test case
            if jira_test["fields"]["issuetype"]['name'] != 'Test':
                log.error("{} is not a test case!".format(jira_id))
                quit(2)
        return jira_test

    def get_feature(self, feature_file=None):
        # Parse a feature file and convert it in a dictionary (self.feature)
        assert feature_file is not None, "Get feature - Missing file {}".format(feature_file)
        feature = parse_file(feature_file)  # parse feature file into a feature object
        # get all feature's story / improvement
        try:
            story_tags = UpdateFeatureOnJira.return_jira_id_from_list(feature.tags)
        except AttributeError:
            log.warning("Error in feature file: {}".format(feature_file))
            return feature_file
        self.feature = {"description": UpdateFeatureOnJira.add_description(feature),
                        "story_tags": ', '.join(story_tags),  # could get multiple jira ids
                        "scenarios": []}
        # manage case where background/precondition is empty
        if feature.background is not None:  # when background / precondition exist
            self.feature["precondition"] = feature.background.name[1:]  # remove @ at the beginning
        else:
            self.feature["precondition"] = None
        # TODO check background VS jira precondition
        for scenario in feature.scenarios:  # get scenario data
            # get the scenario jira id
            scenario_id = UpdateFeatureOnJira.return_jira_id_from_list(scenario.tags)
            # get all labels without jira ids
            tags = scenario.effective_tags
            jira_ids = UpdateFeatureOnJira.return_jira_id_from_list(scenario.effective_tags)
            if len(jira_ids) < 2:
                log.debug("There is no jira's id in feature in file: {}".format(feature_file))
                return 1
            for item in jira_ids:  # remove jira ids from tags
                tags.remove(item)
            my_scenario = {"scenario_id": str(scenario_id[0]),  # could only get 1 jira id
                           "labels": tags,
                           "type": scenario.keyword,
                           "title": "{} - {}".format(feature.name, scenario.name),
                           "scenario": UpdateFeatureOnJira.add_scenario(scenario.steps)
                           }
            if scenario.keyword == 'Scenario Outline':
                # When Scenario Outline --> there are examples to add
                examples = "\n".join(UpdateFeatureOnJira.add_examples(scenario.examples))
                my_scenario["scenario"] += "\n\n{}".format(examples)
            self.feature["scenarios"].append(my_scenario)
        return 0

    @staticmethod
    def return_jira_id_from_list(tag_list=None):
        # return all jira tags (ex: PFWES-12, NIZP-5487 ...) from a list
        # jira ID should have 3 to 6 letters, a "-" and numbers
        # ex: ETP-1, TESTSS-99999991, PFWES-12 ....
        assert tag_list is not None, "return_jira_id_from_list: Missing Tag_list"
        jira_tags = []
        for tag in tag_list:
            if re.search("^[A-Z]{3,6}-[0-9]*", tag):  # match jiraID (ex: PFWES-12, ETP-31 ...)
                log.debug("tag: {}".format(tag))
                jira_tags.append(tag)
        return jira_tags

    @staticmethod
    def add_description(feature=None):
        # format description part
        assert feature is not None, "add_description: Missing feature"
        # construct description part from a behave feature object
        description = "{}: {}\n\n".format(feature.keyword, feature.name)
        description += '\n'.join(feature.description)
        # add blank line before "Business Rules:" line
        description = re.sub('[Bb]usiness [Rr]ules', '\nBusiness rules', description)
        return description

    @staticmethod
    def add_examples(examples=None):
        # format example and table to be printable
        assert examples is not None, "add_example: Missing examples"
        my_examples = []
        for example in examples:
            my_table = UpdateFeatureOnJira.add_table(example.table)
            my_examples.append('{}: {}\n{}'.format(example.keyword,
                                                   example.name,
                                                   my_table))
        return my_examples

    @staticmethod
    def add_table(table=None):
        # get tables and format them to be printable
        assert table is not None, "add_table: Missing table"
        my_table = ''
        columns_size = UpdateFeatureOnJira.get_max_columns_size(table)
        column = 0
        for heading in table.headings:  # build heading table line
            # add space to make sure all columns have same size
            space_nb = columns_size[column] - len(heading)
            value = '{}'.format(heading)
            value += " " * space_nb
            my_table = '{} | {}'.format(my_table, value)
            column += 1
        my_table = '{} |\n'.format(my_table)
        for row in table.rows:
            column = 0
            for cell in row.cells:
                # add space to make sure all columns have same size
                space_nb = columns_size[column] - len(cell)
                value = '{}'.format(cell)
                value += " " * space_nb

                my_table = '{} | {}'.format(my_table, value)
                column += 1
            my_table = '{} |\n'.format(my_table)
        return my_table

    @staticmethod
    def get_max_columns_size(table=None):
        # Use to format table columns to the same size
        max_column_size = []
        heading_size = len(table.headings)
        row_size = len(table.rows)
        for column_nb in range(heading_size):  # go through columns
            size = len(table.headings[column_nb])
            for row_nb in range(row_size):
                cell_size = len(table.rows[row_nb].cells[column_nb])
                if size < cell_size:
                    size = cell_size
            max_column_size.append(size)
        return max_column_size

    @staticmethod
    def add_scenario(scenario_steps=None):
        # build scenario from behave feature.scenarios[X].steps
        assert scenario_steps is not None, "add_scenario: Missing scenario_steps"
        scenario = ''
        step_done = []
        for step in scenario_steps:
            if step.keyword in step_done:
                keyword = 'And'
            else:
                step_done.append(step.keyword)
                keyword = step.keyword
            if scenario == '':  # for first line, remove first \n
                scenario = '{} {}'.format(keyword, step.name)
            else:
                scenario = '{}\n{} {}'.format(scenario, keyword, step.name)
        return scenario

    @staticmethod
    def check_repository(path):
        """
        Check if the path specified exists and is in a correct format.
        :param path:
        :return:
        """
        if not os.path.isabs(path):  # convert relative path in absolute path
            path = os.path.abspath(path)
        if not os.path.exists(path):  # if path doesn't exist, quit
            log.error("feature_repository's value: {} doesn't exist".format(path))
            quit(3)
        if os.path.isdir(path):  # if it's a directory
            feature_files_list = UpdateFeatureOnJira.get_list_of_feature_files(path)
        else:  # if it's a file
            feature_files_list = [path]
        if len(feature_files_list) == 0:  # if there is no feature file
            log.warning("No feature files found in the repository.  Repo: {}".format(path))
        return feature_files_list

    @staticmethod
    def get_list_of_feature_files(path):
        # create a list of file and sub directories
        # names in the given directory
        list_of_files = os.listdir(path)
        all_files = list()
        # Iterate over all the entries
        for entry in list_of_files:
            # Create full path
            full_path = os.path.join(path, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                all_files = all_files + UpdateFeatureOnJira.get_list_of_feature_files(full_path)
            elif '.feature' in entry:
                log.debug('Feature file found: {}'.format(full_path))
                all_files.append(full_path)
        return all_files

    def compare_feature_vs_jira(self, scenario_nb=None, jira_test=None):
        # compare jira test data VS feature data
        # jira_test VS self.feature
        assert scenario_nb is not None, "Missing parameter: scenario_nb"
        assert jira_test is not None, "Missing parameter: jira_test"
        change = {}  # Dictionary with {jira field id: new value}
        scenario = self.feature["scenarios"][scenario_nb]
        fields_change = []  # list with all the fields name to change

        # Compare data from feature (parent level of scenario)
        # data from feature, field by field
        # for feature_field in ["description", "story_tags" , "precondition"]: to enable for precondition # noqa
        for feature_field in ["description", "story_tags"]:
            log.debug("feature_field: {}".format(feature_field))
            jira_json_path = mapping_feature_jira[feature_field]
            feature_value = self.feature[feature_field]
            log.debug("{} - feature_field: {}".format(type(feature_value), feature_value))
            jira_value = dpath.util.get(jira_test, jira_json_path)
            if feature_field != "description":
                log.debug("{} jira_value: {}".format(type(jira_value), jira_value))
                if len(jira_value) != 0:
                    for field in jira_value:
                        # check precondition, if jira VS feature are different, change it
                        if type(field) == dict:  # if field is a json
                            if field["type"]['name'] == 'Tests':  # check story_tags
                                if field["outwardIssue"]["key"] != feature_value:  # if != values
                                    log.debug("field: {} - value: {}".format(field["outwardIssue"]
                                                                             ["key"],
                                                                             feature_value))
                                    log.debug("Story_tags are different")
                                    fields_change.append(feature_field)
                                    change[jira_json_path] = feature_value  # the changes payload
                        elif (field != feature_value) and \
                                (re.search("^[A-Z]{4,6}-[0-9]*",
                                           field)):  # precondition ex: PFWES-5335
                            log.debug("precondition are different")
                            fields_change.append(feature_field)
                            change[jira_json_path] = feature_value  # create changes payload
                else:  # when jira_value is empty
                    log.debug("No story_tags in Jira")
                    change[jira_json_path] = feature_value
            else:  # when feature_field is "description"
                if jira_value != self.feature[feature_field]:
                    log.debug('description are different')
                    fields_change.append(feature_field)
                    change[jira_json_path] = feature_value  # create payload request of changes

        # Compare data for scenario
        for key in scenario:
            log.debug("key: {}".format(key))
            value = scenario[key]
            if key in mapping_feature_jira.keys():
                jira_json_path = mapping_feature_jira[key]
                try:
                    jira_value = dpath.util.get(jira_test, jira_json_path)
                except KeyError:  # this case happen when a field is set to None (ex: ScenarioType)
                    log.info("This field {} is not set on the test.".format(jira_json_path))
                    log.debug("jira_value: {}".format(jira_value))
                if type(value) == list:  # if value to check is a list
                    if sorted(value) != sorted(jira_value):  # reorder list to have same order
                        log.debug("{} keys are different".format(key))
                        fields_change.append(key)
                        if key == 'labels':
                            # get 2 list for labels, 1 to delete, 1 to add
                            add = list(set(value) - set(jira_value))  # get tags to add
                            remove = list(set(jira_value) - set(value))  # tags to delete
                            value = {"add": add,
                                     "remove": remove}
                            log.debug("list of labels to add and remove: ".format(value))

                        log.debug('#feature {}: {}\n\t#jira {}: {}'.format(type(value), value,
                                                                           type(jira_value),
                                                                           jira_value))
                        change[jira_json_path] = value  # create payload request of changes
                elif value != jira_value:
                    log.debug("{} keys are different".format(key))
                    log.debug('#feature {}: {}\n\t#jira {}: {}'.format(type(value), value,
                                                                       type(jira_value),
                                                                       jira_value))
                    fields_change.append(key)
                    change[jira_json_path] = value  # create payload request of changes
            else:  # when key is not in mapping_feature_jira.keys()
                log.warning("{} not in the dictionary".format(key))

        if len(fields_change) > 0:  # if there are changes, write it
            log.info("{} - Changes to do:\t{}".format(scenario['scenario_id'],
                                                      ', '.join(fields_change)))
        else:
            log.info("No change for {}".format(scenario['scenario_id']))
        return change

    def update_jira_test(self, jira_id=None, jira_changes=None):
        # Update the test case from Jira with feature file data
        # jira_id = jira's id who will be updated
        # jira_changes = list of all changes
        assert jira_id is not None, "There is no jira_id to change"
        assert jira_changes is not None, "There is no change for jira_id{}".format(jira_id)

        results = {jira_id: {}}  # build a json for results = { jira_id: {"field1": "204 OK"}}

        # Split jira_changes to manage each field individually
        for field in jira_changes:
            log.debug("{} - jira_change[field]: {}".format(type(jira_changes[field]),
                                                           jira_changes[field]))
            value = str(jira_changes[field])
            if field == mapping_feature_jira['story_tags']:
                # manage linked issue field
                my_result = self.__connection.create_link(from_key=jira_id, to_key=value,
                                                          link_type='Tests')
            else:
                log.debug("field ---> {}".format(field))
                if field == mapping_feature_jira['labels']:
                    # Manage labels field
                    change = []
                    # update labels and remove unexpected labels
                    for action, data in jira_changes[field].items():
                        for tag in data:
                            change.append({action: tag})
                        value = change
                elif field == mapping_feature_jira['type']:
                    # manage case for field = type (scenario type)
                    value = [{"set": {"value": value}}]
                else:
                    # manage other fields than "label" "type" & "story tags"
                    value = [{"set": value}]

                field = field.replace('fields/', 'update/')
                log.debug('field: {} - value: \n\t{}\n'.format(field, value))
                json_data = {}
                dpath.util.new(json_data, field, value)
                log.debug("json_data: {}".format(json_data))
                # Update jira issue change by change
                my_result = self.__connection.update_issue(jira_id, json_data)

            # Manage return message of the issue's update
            if not (my_result.status_code == 204 or my_result.status_code == 201):
                # when error return ERROR messages
                log.warning("HTTP:{} - Error to update field: {}\n\t{}".format(my_result.status_code, field,  # noqa
                                                                               JiraIssue.sanitize(my_result.content)))  # noqa
            else:
                # when not error return INFO messages
                log.info("HTTP:{} - Field: {} updated successfully".format(my_result.status_code,
                                                                           field))

            results[jira_id][field] = my_result  # save result for this field
        # loop end
        return results


if __name__ == "__main__":
    # manage arguments
    parser = argparse.ArgumentParser(description="Synchronise feature files to jira")
    # add arguments
    parser.add_argument('--url', type=str, help="Jira's url",
                        default='https://jira.neopost-id.com/jira')
    parser.add_argument('-u', '--username', help="Jira's Login", required=True)
    parser.add_argument('-p', '--password', help="Jira's password", required=True)
    parser.add_argument('-dir', '--feature_repository', help="Repository with the feature files",
                        required=True)
    parser.add_argument('--check', help="Only check issues, no update", action="store_true")
    parser.add_argument('--verbose', '-v', help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    # run
    if args.verbose:  # when option verbose enable
        log.setLevel(logging.DEBUG)
        log.debug("Verbose enabled")
    my_test = UpdateFeatureOnJira(url=args.url, username=args.username, password=args.password)
    my_test.update_feature_on_jira(feature_repository=args.feature_repository, check=args.check)
