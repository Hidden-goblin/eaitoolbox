# -*- coding: utf-8 -*-
from eaijiraapiabstraction.JiraConnection import JiraConnection


class ReleaseReporter:

    def __init__(self, url: str = None, username: str = None, password: str = None):
        self.__connection = JiraConnection(url=url, username=username, password=password)
        self.__destination_folder = None
        self.__project_key = None

    @property
    def project_key(self):
        return self.__project_key

    @project_key.setter
    def project_key(self, project_key: str = None):
        assert isinstance(project_key, str), "Can't set an empty project key"
        # Check the project id is returned
        if self.__connection.set_project_id(project_key=project_key):
            self.__project_key = project_key

    @property
    def destination_folder(self):
        return self.__destination_folder

    @destination_folder.setter
    def destination_folder(self, destination_folder: str = None):
        assert isinstance(destination_folder, str), "Can't set an empty folder name"

        self.__destination_folder = destination_folder

    def release_report(self, release_name: str = None):
        assert self.project_key is not None, "Project identification is mandatory"
        assert isinstance(release_name, str), "Release name is mandatory"

        self.__connection.release_report(destination_folder=self.destination_folder,
                                         release_name=release_name)

    def test_plan_report(self, test_plan_key: str = None):
        assert self.project_key is not None, "Project identification is mandatory"
        assert isinstance(test_plan_key, str), "Test plan key is mandatory"

        self.__connection.release_report(destination_folder=self.destination_folder,
                                         test_plan_key=test_plan_key)

    def test_execution_report(self, test_execution_key: str = None):
        assert self.project_key is not None, "Project identification is mandatory"
        assert isinstance(test_execution_key, str), "Test execution key is mandatory"

        self.__connection.release_report(destination_folder=self.destination_folder,
                                         test_execution_key=test_execution_key)
