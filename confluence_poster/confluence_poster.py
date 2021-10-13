"""Confluence Poster

This file organises the sorting and ensuring that the input files are in the correct format to be consider acceptable
to Confluence, and then does the posting to the Confluence server.
"""
import logging


log = logging.getLogger(__name__)


class ConfluencePoster:
    """
    Class that provides the functionality to process incoming Markdown or HTML files, putting them into a format
    that Confluence understands, and then posting the set of files to the specified Confluence space.
    """

    def __init__(self, config, confluence_session):
        """
        Store the user provided configuration and the Confluence session with custom SSL context.

        :param config: The user provided configuration
        """
        self._config = config
        self._confluence = confluence_session

    def post_to_confluence(self, processed_files):
        """
        Take a list of files and upsert them into Confluence.

        :param processed_files: The files to post to Confluence
        """
        for file in processed_files:
            if file is None:
                continue
            log.info("Posting file: {0}".format(file.title))
            root_page_id = self._find_page_id()
            self._upsert_page_to_confluence(file, root_page_id)

    def _upsert_page_to_confluence(self, file, root_page_id):
        """
        Attempt to perform the post to Confluence. This will log any individual errors found in the process and
        continue on to the next file rather than failing and stopping.

        :param file: The processed file to try and post to Confluence
        :param root_page_id: The root page ID to use to upsert pages under
        """
        # The result returned from the Confluence module is not an HTTP result when successful, so we can't just
        # get the status code.
        result = self._confluence.update_or_create(parent_id=root_page_id,
                                                   title=file.title,
                                                   body=file.content,
                                                   representation="storage")
        status = result.get('statusCode', 200)
        if status != 200:
            self._log_error_information(result, status, file.content)

    def _find_page_id(self):
        """
        Find the page ID in Confluence for the given space and space key

        :return: The page ID from Confluence
        """
        log.debug("Attempting to get page ID for space {0} and space key {1}".format(self._config.space,
                                                                                     self._config.space_key))
        root_page_id = self._confluence.get_page_id(space=self._config.space_key,
                                                    title=self._config.space)
        log.debug("Page ID found {0}".format(root_page_id))
        return root_page_id

    @staticmethod
    def _log_error_information(result, status, content):
        """
        Log out the required information when a non-200 error code is returned from the server.
        This includes the fully processed file contents.

        :param result: The result object from the Confluence server
        :param status: The status code of the communication attempt
        :param content: The fully processed contents of the file
        """
        log.error(
            "Status code {0} received for reason '{1}' with message\n{2}.\n"
            "Processed content is: {3}".format(status,
                                               result.get('reason'),
                                               result.get('message'),
                                               content))
