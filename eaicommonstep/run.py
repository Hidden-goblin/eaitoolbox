# -*- coding: utf-8 -*-
from behave.__main__ import main as behave_main
import getopt
import sys
import os
import time
import logging
from eaireporter.FeatureReporter import ExportUtilities


def main():
    # Keeping the last execution log.
    if os.path.exists("test_log.log"):
        if os.path.exists("test_log_back.log"):
            os.remove("test_log_back.log")
        os.rename("test_log.log", "test_log_back.log")
    # Logger definition
    logging.basicConfig(level=logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s -- %(filename)s.%(funcName)s-- %(levelname)s -- %("
        "message)s")
    handler = logging.FileHandler("test_log.log", mode="a", encoding="utf-8")
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logging.getLogger("parse").setLevel(level=logging.WARNING)
    logging.getLogger("resourceprovider").setLevel(level=logging.WARNING)
    logging.getLogger("automatontools").setLevel(level=logging.WARNING)
    logging.getLogger("PIL").setLevel(level=logging.WARNING)
    logging.getLogger("drivers_tools").setLevel(level=logging.WARNING)
    logging.getLogger("behave").setLevel(level=logging.WARNING)
    logging.getLogger("resquests").setLevel(level=logging.WARNING)
    logging.getLogger("selenium").setLevel(level=logging.WARNING)
    logging.getLogger("urllib3").setLevel(level=logging.WARNING)
    logging.getLogger("reporter").setLevel(level=logging.WARNING)
    logging.getLogger("commonstep").setLevel(level=logging.WARNING)
    logging.getLogger("applicationmodels").setLevel(level=logging.WARNING)
    logging.getLogger(__name__).debug("Main started")
    # Setting a start timestamp. Used for tagging all result files
    timestamp = str(int(time.time()))
    # Get options from command line input
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "lhc:t:e:a:b:v:i:",
                                   ["configuration=", "tags=", "browser=",
                                    "version="])
        # No options cast an error as this is the purpose of doing CLI
        if len(sys.argv[1:]) == 0:
            print('Please run "python run.py -h" in order to display the help')
            sys.exit(2)

    except getopt.GetoptError:
        print("run.py -c <configuration>")
        sys.exit(2)
    # Runner variables
    behave_arguments = ["./features"]  # List of  behave arguments
    open_allure_report = False  # If true launch the allure report
    generate_report = False  # If true create a docx report
    default_environment = True  # Use the default environment
    is_api_run = False  # Use the UI run as a default
    browser = "chrome"  # Use Chrome as default
    version = "32"  # Use the 32 version
    legacy = False  # Run on migration as default
    is_intellihub_run = False  # Run intellihub check
    intellihub_credential = None  # Intellihub ftp&ssh credentials

    # Behaviour of the various options
    for opt, arg in opts:
        if opt == "-h":
            print("""Runner usage is: python run.py [Options]

            [Options]
                -h print this help section
                -c<configuration>, --configuration=<configuration>
                -t<tags>, --tags=<tags>
                -e<environment>
                -a api run
                -b<browser name>, --browser=<browser name>
                -v<browser version>, --version=<browser version>
                -l legacy run
                -i intellihub run

            Available configurations:
                * json: export results to a simple json output
                * allure: export results to allure report (need allure to be
                installed on computer)
                * cucumber: export results to json output (XRay reporter)
                * plain: export results to simple text file""")
            sys.exit(0)
        elif opt in ("-c", "--configuration"):
            if arg == "json":
                behave_arguments.append("-fjson")
                behave_arguments.append(
                    "-ojson/{}-output.json".format(timestamp))
            elif arg == "allure":
                behave_arguments.append(
                    "-f allure_behave.formatter:AllureFormatter")
                behave_arguments.append("-oallure_results")
                open_allure_report = True
            elif arg == 'cucumber':
                behave_arguments.append(
                    "-f  "
                    "reporter.CucumberJson:PrettyCucumberJSONFormatter")
                behave_arguments.append(
                    "-ocucumber_json/{}-output.json".format(timestamp))
            elif arg == 'plain':
                behave_arguments.append("-fplain")
                behave_arguments.append(
                    "-oplain/{}-output.txt".format(timestamp))
                generate_report = True
        elif opt in ("-t", "--tags"):
            behave_arguments.append("-t {}".format(arg))
        elif default_environment and opt in ("-e",
                                             "--environment"):  # Avoid
            # using two environment at a time, we should not have set an
            # environment (i.e. default to True) and get the option to set
            # an environement
            behave_arguments.append("-D env={}".format(arg))
            default_environment = False
        elif opt in ("-a",):
            is_api_run = True
        elif opt in ("-b", "--browser"):
            browser = arg
        elif opt in ("-v", "--version"):
            version = arg
        elif opt in ("-l",):
            legacy = True
        elif opt in ("-i",):
            is_intellihub_run = True
            intellihub_credential = arg
        else:
            print("Unknown option! Stopping the execution")
            sys.exit(1)

    behave_arguments.append("-D browsername={}".format(browser))
    behave_arguments.append("-D browserversion={}".format(version))
    behave_arguments.append("--no-logcapture")
    behave_arguments.append("-D is_api={}".format(is_api_run))
    behave_arguments.append("-D is_legacy_run={}".format(legacy))
    behave_arguments.append("-D is_intellihub_run={}".format(is_intellihub_run))
    behave_arguments.append("-D intellihub_credential={}".format(intellihub_credential))
    # Set the environment if not set
    if default_environment:
        behave_arguments.append("-D env=dev_air")
    behave_main(behave_arguments)  # Run behave with the CLI arguments

    if generate_report:
        ExportUtilities.create_application_documentation(
            report_file="plain/{}-output.txt".format(timestamp))

    if open_allure_report:
        os.system('allure serve ./allure_results')

    # push test execution to Jira (need Project, user token, test plan key


if __name__ == "__main__":
    main()
