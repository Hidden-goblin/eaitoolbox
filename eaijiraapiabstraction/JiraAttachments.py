import requests
import logging
from os.path import join
from eaijiraapiabstraction.JiraIssues import JiraIssue


class JiraAttachments:
    @staticmethod
    def delete_attachments(url=None, headers=None, issue_key=None, attachment_id=None):
        """"
        Delete all issue attachments or only one attachment depending on the input
        """
        if issue_key is not None and attachment_id is None:
            attachments_id_list = JiraIssue.get_issue_attachments_id(url=url, headers=headers,
                                                                     issue_key=issue_key)
            for attachment_id in attachments_id_list:
                JiraAttachments.delete_attachments(url=url, headers=headers,
                                                   attachment_id=attachment_id)
        elif issue_key is None and attachment_id is not None:
            return requests.delete("{}/rest/api/2/attachment/{}".format(url, attachment_id),
                                   headers=headers)
        else:
            print("Error")

    @staticmethod
    def retrieve_attachments(url=None, headers=None, issue_key=None,
                             attachment_id=None, folder=None):
        logging.info("Retrieve attachment with issue_key='{}',"
                     " attachment_id='{}' and folder='{}'".format(issue_key,
                                                                  attachment_id,
                                                                  folder))
        attachments = JiraIssue.get_issue_attachments_links(url=url, headers=headers,
                                                            issue_key=issue_key)
        logging.info("attachments are '{}'".format(repr(attachments)))
        if attachment_id is not None and attachment_id in attachments.keys():
            JiraAttachments.download_file(url=attachments[attachment_id]["url"], headers=headers,
                                          file_absolute_path=join(folder,attachments[attachment_id]["filename"]))  # noqa
        else:
            for key in attachments.keys():
                JiraAttachments.download_file(url=attachments[key]["url"], headers=headers,
                                              file_absolute_path=join(folder, attachments[key]["filename"]))  # noqa

    @staticmethod
    def download_file(url=None, headers=None, file_absolute_path=None):
        attachment = requests.get(url=url, headers=headers, stream=True)
        with open(file_absolute_path, "wb") as download_file:
            download_file.write(attachment.content)
        download_file.close()
