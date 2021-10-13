# Confluence Poster

## Overview

Project to automate the posting of documentation to Confluence pages. The tool will accept an input file or directory containing Markdown files, process them into a suitable Confluence format (making use of Confluence macros), and will then post the documents into the specified Confluence space.

## Requirements

- Python 3.9+
- Poetry
- Account with access to Confluence and permissions to add/edit/delete pages

## Installation

Once the codebase is checked out, you should use poetry to create the virtual environment, install all the depednencies from the ```pyproject.toml``` file, and activate the venv. Run the following command from the checkout root directory. 

```poetry install```

There are no external dependencies other than Python dependencies as specified in the ```pyproject.toml```.

Once the venv has been created, change into the ```tests``` directory and then run the following to check everything is working correctly.

```poetry run pytest```

## Building for deployment

In order to build the sdist and wheel archives for deployment to a repository, use the following command

```poetry build```

## Usage

The project has the following command line arguments:

| Flag | Description |
| :--: |:----------: |
| '-c' | The root URL of the Confluence instance to which the documents will be posted. |
| '-u' | The username of the account that will be used to do the posting. |
| '-p' | The password of the account that will be used to do the posting. |
| '-l' | The SSL key registered with Confluence. |
| '-t' | The certificate to use with Confluence. |
| '-f' | The file/directory containing the files to be posted. |
| '-s' | The title of the parent page you want to post under. This can either be the project homepage, or an existing page in the Confluence space. |
| '-k' | The space key for the project. |
| '-v' | Verbose logging mode, can be omitted if not required. |

*Note - You will need to provide either the username/password pair __or__ the SSL key/certificate pair.*

*Note - You will need to ensure that you have the virtual environment activated. The command ```poetry shell``` will do this.*

When the tool runs it will use the file name of the input file (Without the file extension) as the title of the Confluence page.

When running the tool on the command line, it should be in the root of the project. When running the tests, you should change to the `tests` directory.

### Examples

If you wanted to post the file `meeting-minutes.md` to the Confluence project homepage:

````commandline
python -m confluence_poster -c https://url.com -f meeting-minutes.md -s homepage -k PY123 -v true -u USER -p PASSWORD
```` 

If you wanted to post the file `meeting-minutes-2.md` under the `meeting-minutes` page:

````commandline
python -m confluence_poster -c https://url.com -f meeting-minutes-2.md -s meeting-minutes -k PY123 -v true -u USER -p PASSWORD
````

## Project Structure

```Configuration``` and ```ProcessedFile``` are named tuples that encapsulate the configuration provided on the command line, and the processed files that will be posted to the Confluence server.

```Confluence Session Builder``` takes the configuration and uses that to create an instance of the Confluence API based on what configuration is provided.

```Confluence Poster``` is where all the logic relating to the actual posting of files is located.

```File Converter``` is where all the logic relating to translating the input Markdown into HTML, which is then modified with Confluence macros. 

```SSL Context Adapter``` allows the manipulation of the SSL context that is used when building the Confluence session.

## Utilities

In the ```docs``` directory, there are two configuration files to allow easy running of the tool and the unit tests when using Pycharm as an IDE. The ```confluence_poster.run.xml``` will need to be configured with the correct parameters for your Confluence space/user/files.

## Things TODO

- Correct external document links
- Improve test coverage.
- Consider allowing the tool to delete pages
- Consider adding relevant labels when posting or updating pages
