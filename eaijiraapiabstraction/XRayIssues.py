import base64
import logging
import os
import os.path
import requests
from json import load

from eaijiraapiabstraction.JiraAttachments import JiraAttachments
from eaijiraapiabstraction.JiraTests import JiraTests

log = logging.getLogger(__name__)


class XRayIssues:
    @staticmethod
    def get_tests_in_test_plan(url=None, headers=None, test_plan_key=None):
        #  May be paginated
        #  TODO get rid of pagination
        return requests.get(url="{}/rest/raven/1.0/api/testplan/{}/test".format(url, test_plan_key),
                            headers=headers)

    @staticmethod
    def get_tests_execution_of_test_plan(url=None, headers=None, test_plan_key=None):
        #  The return is not paginated
        return requests.get(
            url="{}/rest/raven/1.0/api/testplan/{}/testexecution".format(url, test_plan_key),
            # noqa
            headers=headers)

    @staticmethod
    def get_tests_in_execution(url=None, headers=None, test_execution_key=None):
        #  The return may be paginated
        #  TODO get rid of pagination
        return requests.get(url="{}/rest/raven/1.0/api/testexec/{}/test".format(url,
                                                                                test_execution_key),
                            headers=headers,
                            params={"detailed": True})

    @staticmethod
    def download_evidence(url=None, headers=None, test_execution_key=None, folder=None):
        # TODO maybe check folder
        execution = XRayIssues.get_tests_in_execution(url=url, headers=headers,
                                                      test_execution_key=test_execution_key)
        for test in execution.json():
            destination_folder = os.path.join(folder, test['key'])
            if not os.path.isdir(destination_folder):
                os.mkdir(destination_folder)
            for evidence in test["evidences"]:
                JiraAttachments.download_file(url=evidence["fileURL"], headers=headers,
                                              file_absolute_path=os.path.join(destination_folder,
                                                                              evidence["fileName"]))
            del destination_folder
        del execution

    @staticmethod
    def download_test_plan_evidences(url=None, headers=None, test_plan_key=None, folder=None):
        test_executions = XRayIssues.get_tests_execution_of_test_plan(url=url,
                                                                      headers=headers,
                                                                      test_plan_key=test_plan_key)
        for execution in test_executions.json():
            destination_folder = os.path.join(folder, execution["key"])
            if not os.path.isdir(destination_folder):
                os.mkdir(destination_folder)
            XRayIssues.download_evidence(url=url,
                                         headers=headers,
                                         test_execution_key=execution["key"],
                                         folder=destination_folder)

    @staticmethod
    def download_release_evidence(url=None, headers=None, release_name=None, folder=None):
        test_plans = JiraTests.get_test_plan_in_release(url=url, headers=headers,
                                                        release_name=release_name)
        for test_plan in test_plans.json()["issues"]:
            destination_folder = os.path.join(folder, test_plan['key'])
            if not os.path.isdir(destination_folder):
                os.mkdir(destination_folder)
            XRayIssues.download_test_plan_evidences(url=url,
                                                    headers=headers,
                                                    test_plan_key=test_plan["key"],
                                                    folder=destination_folder)
            del destination_folder
        del test_plans

    @staticmethod
    def test_plan_report(url=None, headers=None, test_plan_key=None, folder=None):
        pass

    @staticmethod
    def create_test_execution(url=None, headers=None, result_file=None):
        with open(result_file) as my_results:
            result = load(my_results)

            response = requests.post(
                url="{}/rest/raven/1.0/import/execution/cucumber".format(url),
                headers=headers,
                json=result
            )
        return response

    @staticmethod
    def load_attachments(url=None, headers=None, execution_key=None, evidence_files=None):
        with open(evidence_files) as evidences:
            evidences_list = load(evidences)

        for key in evidences_list:
            response = requests.get("{}/rest/raven/1.0/api/testrun".format(url),
                                    headers=headers,
                                    params={"testExecIssueKey": execution_key, "testIssueKey": key})
            if response.status_code == 200:
                test_run_id = response.json()["id"]

            for file_name in evidences_list[key]:
                with open(file_name, 'rb') as file:
                    b64_file = base64.b64encode(file.read())
                    payload = {"data": b64_file.decode("utf-8"),
                               "filename": file_name.split("/")[-1],
                               "contentType": "application/msword"
                               }
                    response = requests.post(
                        url="{}/rest/raven/1.0/api/testrun/{}/attachment".format(url, test_run_id),
                        # noqa
                        headers=headers,
                        json=payload)
                    log.debug(response)
