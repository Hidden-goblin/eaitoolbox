import argparse
import glob
import os
import datetime
import subprocess
from jiraapiabstraction.JiraConnection import JiraConnection
from reporter.CucumberJson import CucumberCleaner
import logging
import json


def main():
    # Keeping the last execution log.
    if os.path.exists("export_log.log"):
        if os.path.exists("export_log_back.log"):
            os.remove("export_log_back.log")
        os.rename("export_log.log", "export_log_back.log")
    # Logger definition
    logging.basicConfig(level=logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s -- %(filename)s.%(funcName)s-- %(levelname)s -- %("
        "message)s")
    handler = logging.FileHandler("export_log.log", mode="a", encoding="utf-8")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    log = logging.getLogger(__name__)

    log.info("Start the export")
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Jira username")
    parser.add_argument("password", help="Jira password")
    parser.add_argument("test_plan", help="Jira test plan issue key")
    parser.add_argument("-b", "--binary", type=str,
                        help="The CURL binary path", default="curl")
    parser.add_argument("-s", "--summary", type=str,
                        help="Specifies the system used during the tests (browser, os..)",
                        default="")

    args = parser.parse_args()
    try:
        log.info("Create a clean report from last execution")
        list_of_files = glob.glob('cucumber_json/*json')
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
        else:
            log.error("No cucumber report in the cucumber output folder")

        CucumberCleaner.cleaner(latest_file, "clean_report.json")

        log.info("Create a test execution for the project")

        current_date = datetime.datetime.today()
        summary = "{} execution. Ended at {}. System information: {}".format(
            current_date.strftime("%d-%B-%Y"),
            current_date.strftime("%H:%M"),
            args.summary
        )

        test_execution = {'fields': {
                            'customfield_10228': [args.test_plan],
                            'summary': summary,
                            'customfield_10302': '9',
                            'project': {'key': 'PFWES'},
                            'issuetype': {'id': '10206'}}}

        with open("test_execution.json", "w") as execution_file:
            json.dump(test_execution, execution_file)

        command = [args.binary,
                   "-u",
                   "{}:{}".format(args.username, args.password),
                   "-F",
                   "info=@test_execution.json",
                   "-F", "result=@clean_report.json",
                   "https://jira.neopost-id.com/jira/rest/raven/1.0/import/execution/cucumber/multipart"]  # noqa
        output = subprocess.run(command,
                                capture_output=True)

        log.info("Output:'{}'\nError: '{}'".format(output.stdout, output.stderr))
        response = json.loads(output.stdout)
        log.debug("Get response".format(response))
        test_execution_key = response["testExecIssue"]["key"]

        my_jira = JiraConnection(username=args.username,
                                 password=args.password,
                                 url="https://jira.neopost-id.com/jira")
        my_jira.set_project_id(project_key="PFWES")

        my_jira.test_execution_load_attachments(execution_key=test_execution_key,
                                                evidence_files="evidences.json")

    except json.decoder.JSONDecodeError as json_error:
        log.error("Json decoder send: '{}'\n line '{}' column '{}'".format(
            json_error.args[0],
            json_error.lineno,
            json_error.colno))
        log.debug("File is '{}'".format(json_error.doc))

    except Exception as exception:
        log.error(exception)

    log.info("End of export")


if __name__ == "__main__":
    main()
