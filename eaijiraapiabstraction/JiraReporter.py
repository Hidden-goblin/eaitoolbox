import logging
import os.path
from pathlib import Path
from shutil import rmtree

import xlsxwriter

from jiraapiabstraction.JiraAttachments import JiraAttachments
from jiraapiabstraction.JiraIssues import JiraIssue
from jiraapiabstraction.JiraTests import JiraTests
from jiraapiabstraction.XRayIssues import XRayIssues

log = logging.getLogger(__name__)


class JiraReporter:

    @staticmethod
    def create_release_report(url=None, headers=None, release_name=None, folder=None,
                              test_plan_key=None, test_execution_key=None):
        tested_folder = folder
        if release_name is not None:
            JiraReporter.__from_release_report(url=url, headers=headers, release_name=release_name,
                                               folder=tested_folder)
        elif test_plan_key is not None:
            JiraReporter.__from_test_plan_report(url=url,
                                                 headers=headers,
                                                 test_plan_key=test_plan_key, folder=tested_folder)
        elif test_execution_key is not None:
            JiraReporter.__from_test_execution_report(url=url, headers=headers,
                                                      test_execution_key=test_execution_key,
                                                      folder=tested_folder,
                                                      relative_folder='{}/'.format(test_execution_key))  # noqa
        else:
            logging.error("Can't process report")
            return 1

    @staticmethod
    def check_folder(folder=None):
        # check if folder exists or is empty
        tested_folder = folder
        if not os.path.isabs(tested_folder):
            logging.debug("'{}' is not an absolute path.".format(tested_folder))
            # noinspection PyTypeChecker
            tested_folder = os.path.join(Path.home(), folder)

        if not os.path.exists(tested_folder):
            logging.debug("'{}' doesn't exist. Create it.".format(tested_folder))
            os.makedirs(tested_folder)
        else:
            logging.debug("'{}' exists. Clear it.".format(tested_folder))
            rmtree(tested_folder)
            os.makedirs(tested_folder)
        return tested_folder

    @staticmethod
    def __create_xlsx_file(folder=None, name=None):
        report = xlsxwriter.Workbook(os.path.join(folder, "{}-report.xlsx".format(name)))
        main_title_format = report.add_format({'bg_color': '0DA917', 'font_size': 18, 'bold': True})
        header_format = report.add_format({'bg_color': '0DA917', 'bold': True})
        fail_format = report.add_format({'bg_color': 'red'})
        wrap_format = report.add_format()
        wrap_format.set_text_wrap(True)
        wrap_format.set_align('top')
        return {"workbook": report, "format": {"main_title": main_title_format,
                                               "header": header_format,
                                               "wrap": wrap_format,
                                               "fail": fail_format}, "sheets": {}}

    @staticmethod
    def __format_test_report_sheet(report=None, sheet_key=None):
        report["sheets"][sheet_key].set_column(1, 10, None, report["format"]["wrap"])
        report["sheets"][sheet_key].set_column(0, 0, 10, report["format"]["wrap"])
        report["sheets"][sheet_key].set_column(2, 2, 30)
        report["sheets"][sheet_key].set_column(4, 4, 35)
        report["sheets"][sheet_key].set_column(6, 6, 90)
        report["sheets"][sheet_key].set_column(7, 7, 45)
        report["sheets"][sheet_key].conditional_format('F5:F200', {'type': 'text',
                                                                  'criteria': 'containing',
                                                                  'value': 'FAIL',
                                                                  'format': report["format"][
                                                                      "fail"]})  # noqa
        # sheet's header
        report["sheets"][sheet_key].write_url(2, 0, "internal:Summary!A1", string="To summary")
        report["sheets"][sheet_key].write_string('B4', "US ID", report["format"]["header"])
        report["sheets"][sheet_key].write_string('C4', "US title", report["format"]["header"])
        report["sheets"][sheet_key].write_string('D4', "Test ID", report["format"]["header"])
        report["sheets"][sheet_key].write_string('E4', "Test title", report["format"]["header"])
        report["sheets"][sheet_key].write_string('F4', "Status", report["format"]["header"])
        report["sheets"][sheet_key].write_string('G4', "Description", report["format"]["header"])
        report["sheets"][sheet_key].write_string('H4', "Evidence", report["format"]["header"])

    @staticmethod
    def __from_release_report(url=None, headers=None, release_name=None, folder=None):
        test_plans = JiraTests.get_test_plan_in_release(url=url, headers=headers,
                                                        release_name=release_name)

        for test_plan_dict in test_plans["issues"]:
            JiraReporter.__from_test_plan_report(url=url,
                                                 headers=headers,
                                                 test_plan_key=test_plan_dict["key"], folder=folder)

    @staticmethod
    def __from_test_plan_report(url=None, headers=None, test_plan_key=None, folder=None):
        # Retrieve the summary and description
        test_plan = JiraIssue.search(url=url, headers=headers,
                                     search_request={"jql": 'issuekey="{}"'.format(test_plan_key),
                                                     "fields": ["key", "summary", "description"]})

        #  Create a xlsx file per test plan
        report = JiraReporter.__create_xlsx_file(folder=folder, name=test_plan_key)

        #  Prepare the summary page and fill with Test plan data
        report["sheets"]["summary"] = report["workbook"].add_worksheet("Summary")
        report["sheets"]["summary"].write_string('A1', "This page is a summary of the test"
                                                       " execution(s) for test"
                                                       " plan {}".format(test_plan_key))
        report["sheets"]["summary"].set_column(3, 5, 15)
        report["sheets"]["summary"].merge_range(1, 1, 1, 5,
                                                test_plan.json()["issues"][0]["fields"]["summary"],
                                                report["format"]["main_title"])
        report["sheets"]["summary"].merge_range(3, 3, 3, 5, "Description",
                                                report["format"]["header"])
        report["sheets"]["summary"].write_string(3, 1, "Key", report["format"]["header"])
        report["sheets"]["summary"].write_string(3, 3, "Description", report["format"]["header"])

        test_executions = XRayIssues.get_tests_execution_of_test_plan(url=url,
                                                                      headers=headers,
                                                                      test_plan_key=test_plan_key)
        log.info("test_plan_key: {}".format(test_plan_key))

        for index, test_execution in enumerate(test_executions.json()):
            log.debug("Line: {}".format(4 + index))
            #  Creating the sheet for the execution
            report["sheets"][test_execution["key"]] = report["workbook"].add_worksheet(test_execution["key"])  # noqa

            #  Updating the summary's sheet
            #  TODO: check the wrap format as it seems not to work
            report["sheets"]["summary"].merge_range(4 + index, 3, 4 + index, 5,
                                                    test_execution["summary"],
                                                    report["format"]["wrap"])
            report["sheets"]["summary"].write_url(4 + index, 1,
                                                  "internal:'{}'!A1".format(test_execution["key"]))
            report["sheets"]["summary"].write_string(4 + index, 1, test_execution["key"],
                                                     report["format"]["wrap"])

            # data
            JiraReporter.__from_test_execution_report(url=url,
                                                      headers=headers,
                                                      test_execution_key=test_execution["key"],
                                                      new_report_sheet=report["sheets"][test_execution["key"]],  # noqa
                                                      folder=os.path.join(folder, test_plan_key,
                                                                          test_execution["key"]),
                                                      relative_folder='{}/{}/'.format(test_plan_key,
                                                                                      test_execution["key"]))  # noqa
            # set format
            JiraReporter.__format_test_report_sheet(report=report, sheet_key=test_execution["key"])

        report["workbook"].close()

    @staticmethod
    def __from_test_execution_report(url=None, headers=None, test_execution_key=None,
                                     new_report_sheet=None, folder=None, relative_folder=None):
        if new_report_sheet is None:
            log.debug("Only one test execution")
            report = JiraReporter.__create_xlsx_file(folder=folder, name=test_execution_key)
            report["sheets"][test_execution_key] = report["workbook"].add_worksheet(test_execution_key)  # noqa
            JiraReporter.__format_test_report_sheet(report=report, sheet_key=test_execution_key)
            JiraReporter.__add_execution_to_report(url=url,
                                                   headers=headers,
                                                   test_execution_key=test_execution_key,
                                                   new_report_sheet=report["sheets"][test_execution_key],  # noqa
                                                   folder=os.path.join(folder, test_execution_key),
                                                   relative_folder=relative_folder)
            JiraReporter.__format_test_report_sheet(report=report, sheet_key=test_execution_key)
            report["workbook"].close()
        else:
            JiraReporter.__add_execution_to_report(url=url,
                                                   headers=headers,
                                                   test_execution_key=test_execution_key,
                                                   new_report_sheet=new_report_sheet,
                                                   folder=folder,
                                                   relative_folder=relative_folder)

    @staticmethod
    def __add_execution_to_report(url=None, headers=None, test_execution_key=None,
                                  new_report_sheet=None, folder=None,
                                  relative_folder=None):
        # this function add lines in test execution's sheet

        test_execution = JiraIssue.search(url=url, headers=headers,
                                          search_request={"jql": 'issuekey="{}"'.format(test_execution_key),  # noqa
                                                          "fields": ["key", "summary", "description"]})  # noqa

        # header definition
        new_report_sheet.merge_range(1, 1, 1, 5,
                                     test_execution.json()["issues"][0]["fields"]["summary"])
        new_report_sheet.write_string('A2', 'Test execution:')

        # get test data
        tests = XRayIssues.get_tests_in_execution(url=url, headers=headers,
                                                  test_execution_key=test_execution_key)
        evidences = JiraIssue.sanitize(content=tests.content)
        evidences = {item["key"]: item for item in evidences}

        current_row = 4
        log.debug("{} data: \n{}".format(test_execution_key, tests.json()))
        log.debug("Evidences {} data: \n{}".format(test_execution_key, evidences))

        for index, test in enumerate(tests.json()):
            #  Create the download folder
            os.makedirs(os.path.join(folder, test["key"]))
            #  Get steps or scenarios
            steps = JiraIssue.search(url=url,
                                     headers=headers,
                                     search_request={"jql": 'issuekey="{}"'.format(test["key"]),
                                                     "fields": ["key",
                                                                "customfield_10204",
                                                                "customfield_10206",
                                                                "summary", "issuelinks"]})
            steps = JiraIssue.sanitize(content=steps.content)
            # log.info("step {} data:\n[{}".format(test["key"], steps))

            story_key = ''
            story_name = ''
            # try to catch story attached to the test
            try:
                # these fields doesn't exist for Release level, only for test plan / exec level
                short_link = steps["issues"][0]["fields"]["issuelinks"][0]  # to ease readability
                story_key = short_link["inwardIssue"]["key"]
                story_name = short_link["inwardIssue"]["fields"]["summary"]
            except (KeyError, IndexError):
                try:
                    # on old version, field use outward instead of inward
                    short_link = steps["issues"][0]["fields"]["issuelinks"][0]  # ease readability

                    log.debug("step {} data:\n{}".format(test["key"],
                                                         short_link["outwardIssue"]["key"]))
                    story_key = short_link["outwardIssue"]["key"]
                    story_name = short_link["outwardIssue"]["fields"]["summary"]
                except (KeyError, IndexError):
                    log.warning("There is no story / improvement attached to"
                                " test {}".format(test["key"]))

            if steps["issues"][0]["fields"]["customfield_10204"] is not None:
                steps_list = [steps["issues"][0]["fields"]["customfield_10204"]]
            else:
                steps_list = [item["step"] for item in
                              steps["issues"][0]["fields"]["customfield_10206"]["steps"]]

            file_list = evidences[test["key"]]["evidences"]
            defect_list = evidences[test["key"]]["defects"]

            lines_to_write = max((len(steps_list), len(file_list), len(defect_list)))
            for step_index, step in enumerate(steps_list):
                new_report_sheet.write_string(current_row + step_index, 6, step)
            for evidence_index, evidence in enumerate(file_list):
                file_name = evidence["fileName"]
                JiraAttachments.download_file(url=evidence["fileURL"],
                                              headers=headers,
                                              file_absolute_path=os.path.join(folder,
                                                                              test["key"],
                                                                              file_name))
                new_report_sheet.write_url(current_row + evidence_index, 7,
                                           os.path.join(relative_folder, test["key"], file_name),
                                           string=file_name)
            # set jira's ID url
            new_report_sheet.write_url(current_row, 3,
                                       "{}/browse/{}".format(url, test["key"]),
                                       string=test["key"])  # Test ID
            if story_key != '':
                new_report_sheet.write_url(current_row, 1,
                                           "{}/browse/{}".format(url, story_key),
                                           string=story_key)  # US ID
            new_report_sheet.write_string(current_row, 2, story_name)  # US name

            # merge rows when result is on multi lines
            if lines_to_write > 1:
                # set values and merge rows
                new_report_sheet.merge_range(current_row, 4,
                                             current_row + lines_to_write - 1, 4,
                                             steps["issues"][0]["fields"]["summary"])
                new_report_sheet.merge_range(current_row, 5, current_row + lines_to_write - 1, 5,
                                             test["status"])
                # value already set, only merge rows
                new_report_sheet.merge_range(current_row, 1, current_row + lines_to_write - 1, 1,
                                             story_key)  # US ID field  # todo improve format
                new_report_sheet.merge_range(current_row, 2, current_row + lines_to_write - 1, 2,
                                             None)  # US title field
                new_report_sheet.merge_range(current_row, 3, current_row + lines_to_write - 1, 3,
                                             test["key"])  # Test ID   # todo improve format
                new_report_sheet.merge_range(current_row, 6, current_row + lines_to_write - 1, 6,
                                             None)  # Step field
            else:
                new_report_sheet.write_string(current_row, 1, story_key)  # todo improve format
                new_report_sheet.write_string(current_row, 3, test["key"])  # todo improve format
                new_report_sheet.write_string(current_row, 4,
                                              steps["issues"][0]["fields"]["summary"])
                new_report_sheet.write_string(current_row, 5, test["status"])

            current_row = current_row + lines_to_write
