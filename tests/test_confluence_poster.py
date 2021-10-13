import pytest
import confluence_poster.confluence_poster as poster
from confluence_poster import processed_file


@pytest.fixture()
def mock_config(mocker):
    return mocker.patch("confluence_poster.configuration.Configuration", autospec=True)


@pytest.fixture()
def mock_confluence_connection(mocker):
    return mocker.patch("atlassian.Confluence", autospec=True)


@pytest.fixture()
def uut(mock_config, mock_confluence_connection):
    """
    The unit under test.
    """
    return poster.ConfluencePoster(mock_config, mock_confluence_connection)


def test_can_post_file(uut, mock_config, mock_confluence_connection, mocker):
    """
    Test that a file can be processed.
    """
    # Set up the configuration and connection mocks with appropriate values
    mocker.patch.object(mock_config, 'space_key', "abc")
    mocker.patch.object(mock_config, 'space', "aabbcc")
    mocker.patch.object(mock_confluence_connection, 'get_page_id', return_value="123")
    expected_result = {}
    mocker.patch.dict(expected_result, {'value': '123'})
    mocker.patch.object(mock_confluence_connection, 'update_or_create', return_value=expected_result)

    sample_file = processed_file.ProcessedFile("mytitle", "mycontent")
    files = [sample_file]
    page_id_spy = mocker.spy(uut, '_find_page_id')
    upsert_spy = mocker.spy(uut, '_upsert_page_to_confluence')
    uut.post_to_confluence(files)

    assert page_id_spy.call_count == 1
    assert upsert_spy.call_count == 1
