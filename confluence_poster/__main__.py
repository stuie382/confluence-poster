"""Main

This file handles receiving the user input and then kicking off the processing of the input file(s) required
by the user.
"""
import argparse
import logging
import os

from confluence_poster import configuration
from confluence_poster import confluence_poster
from confluence_poster import file_converter
from confluence_poster import confluence_session_builder as builder


def main():
    """
    Parse the user input into a Configuration object, then begin processing the files.

    :return: 0 when processing is complete.
    """
    parser = argparse.ArgumentParser(description="Confluence document poster.")
    parser.add_argument('-c', dest='confluence_url', type=str, help="The root Confluence URL.", required=True)
    parser.add_argument('-u', dest='user_name', type=str, help="The service account user name.", default=None)
    parser.add_argument('-p', dest='user_pass', type=str, help="The service account password.", default=None)
    parser.add_argument('-l', dest='ssl_key', type=str, help="The SSL key registered with Confluence", default=None)
    parser.add_argument('-t', dest='ssl_cert', type=str, help="The SSL certificate", default=None)
    parser.add_argument('-f', dest='files', type=str, help="The file or directory to process.", required=True)
    parser.add_argument('-s', dest='space', type=str, help="The Confluence space to use.", required=True)
    parser.add_argument('-k', dest='space_key', type=str, help="The Confluence space key to use.", required=True)
    parser.add_argument('-v', dest='store_true', help="Enable verbose logging")

    args = parser.parse_args()
    setup_logger(args.store_true)
    config = configuration.Configuration(args.confluence_url,
                                         args.user_name,
                                         args.user_pass,
                                         args.ssl_key,
                                         args.ssl_cert,
                                         args.files,
                                         args.space,
                                         args.space_key)
    processed_files = process_the_files(config.files)
    post_the_files(config, processed_files)
    return 0


def post_the_files(config, processed_files: list) -> None:
    """
    Takes the processed files and posts them to the Confluence server.

    :param config: The configuration required to create the connection to Confluence
    :param processed_files: The list of files to post
    """
    confluence_session = builder.ConfluenceSessionBuilder().build(config)
    poster = confluence_poster.ConfluencePoster(config, confluence_session)
    poster.post_to_confluence(processed_files)


def process_the_files(input_files: str) -> list:
    """
    Convert the files from the input formats into Confluence compatible format.

    :param input_files: The file or directory to process
    :return: A list of processed files ready to post
    """
    converter = file_converter.FileConverter()
    return converter.convert(input_files)


def setup_logger(is_debug: bool) -> None:
    """
    Setup the logger to either info mode or debug mode based on the user configuration.

    :param is_debug: Whether to run in debug or info mode
    """
    mode = "INFO"
    if is_debug:
        mode = "DEBUG"
    logging.basicConfig(level=os.environ.get("LOGLEVEL", mode))


if __name__ == '__main__':
    main()
