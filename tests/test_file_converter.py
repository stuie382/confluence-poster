import codecs

import pytest
import confluence_poster.file_converter as file_converter


@pytest.fixture()
def uut():
    """
    The unit under test.
    """
    return file_converter.FileConverter()


def test_empty_empty_md_file_returns_correct_title(uut):
    """
    Check that when given a path to a markdown file, the path and extension are correctly removed for the title.
    """
    result = uut.convert("data/empty/empty_md.md")
    assert len(result) == 1
    assert result[0].title == "empty_md"


def test_convert_empty_html_file_returns_correct_title(uut):
    """
    Check that when given a path to an HTML file, the path and extension are correctly removed for the title.
    """
    result = uut.convert("data/empty/empty_html.html")
    assert len(result) == 1
    assert result[0].title == "empty_html"


def test_convert_multiple_empty_files(uut):
    """
    Check that when given a directory of valid files, the correct set is processed and converted.
    """
    result = uut.convert("data/empty")
    assert len(result) == 3
    assert result[0].title == "empty_html"
    """
    This file exists in the directory but is ignored by the system
    """
    assert result[1] is None
    assert result[2].title == "empty_md"


def test_convert_code_block(uut):
    """
    Test that different types of code blocks can be properly converted. The sample
    includes blocks with and without languages for syntax highlighting
    """
    result = uut.convert("data/code_block.md")
    expected = '<h2>Code</h2>\n' \
               '<p>Inline <code>code</code></p>\n' \
               '<p>Indented code</p>\n' \
               '<ac:structured-macro ac:name="code"><ac:parameter ac:name="theme">Midnight</ac:parameter>' \
               '<ac:parameter ac:name="linenumbers">true</ac:parameter>' \
               '<ac:parameter ac:name="language">none</ac:parameter>' \
               '<ac:plain-text-body><![CDATA[// Some comments\n' \
               'line 1 of code\n' \
               'line 2 of code\n' \
               'line 3 of code\n' \
               ']]></ac:plain-text-body></ac:structured-macro>\n' \
               '<p>Block code “fences”</p>\n' \
               '<ac:structured-macro ac:name="code"><ac:parameter ac:name="theme">Midnight</ac:parameter>' \
               '<ac:parameter ac:name="linenumbers">true</ac:parameter><ac:parameter ac:name="language">none' \
               '</ac:parameter>' \
               '<ac:plain-text-body><![CDATA[Sample text here...\n' \
               ']]></ac:plain-text-body></ac:structured-macro>\n' \
               '<p>Syntax highlighting</p>\n' \
               '<ac:structured-macro ac:name="code"><ac:parameter ac:name="theme">Midnight</ac:parameter>' \
               '<ac:parameter ac:name="linenumbers">true</ac:parameter>' \
               '<ac:parameter ac:name="language">python' \
               '</ac:parameter><ac:plain-text-body><![CDATA[def my_func():\n' \
               '    return 1\n' \
               ']]></ac:plain-text-body></ac:structured-macro>'
    assert len(result) == 1
    assert result[0].title == "code_block"
    assert result[0].content == expected


def test_convert_blockquote(uut):
    """
    Test that blockquotes are properly converted and nested.
    """
    result = uut.convert("data/blockquote.md")
    expected = '<h2>Blockquotes</h2>\n' \
               '<p><ac:structured-macro ac:name="info"><ac:rich-text-body><p>Blockquotes can also be nested… > …by ' \
               'using additional greater-than\n' \
               'signs right next to each other… > > …or with spaces between arrows.</p>' \
               '</ac:rich-text-body></ac:structured-macro></p>'
    assert len(result) == 1
    assert result[0].title == "blockquote"
    assert result[0].content == expected


def test_convert_full_document_short(uut):
    """
    Test that a full document is properly converted.
    """
    result = uut.convert("data/test-short.md")
    with open("data/test-short-converted.html", 'r') as expected_output:
        expected = expected_output.read()
        assert len(result) == 1
        assert result[0].title == "test-short"
        assert result[0].content == expected
