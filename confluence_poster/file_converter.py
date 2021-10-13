"""File Converter

This file handles the conversion of files from several input formats (currently Markdown and HTML),
and processes them into Confluence compatible XHTML, making use of appropriate Confluence marcos to produce a visually
pleasing output.
"""
import codecs
from pathlib import Path
import os
import re
import markdown

from confluence_poster import processed_file


class FileConverter:
    """
    The class that processes the specified file/s and gets them into the correct format for Confluence.
    """

    def convert(self, input_file_or_directory) -> list:
        """
        Process the file(s) into an appropriate state for posting to Confluence.

        :param input_file_or_directory: The file or directory to process
        :return: The processed files ready to be posted to Confluence
        """
        processed_files = []
        if os.path.isdir(input_file_or_directory):
            for child_file in os.listdir(input_file_or_directory):
                processed_files.append(self._process_a_file((os.path.join(input_file_or_directory, child_file))))
        else:
            processed_files.append(self._process_a_file(input_file_or_directory))
        return processed_files

    def _process_a_file(self, input_file: str) -> processed_file.ProcessedFile:
        """
        Take a Markdown or HTML file and process it into something that Confluence understands.

        :param input_file: The file to process
        :return: The fully processed file
        """
        converted_file = None
        if input_file.endswith(".md"):
            converted_file = self._convert_markdown_to_confluence(input_file)
        elif input_file.endswith(".html"):
            converted_file = self._convert_html_to_confluence(input_file)
        return converted_file

    def _convert_markdown_to_confluence(self, input_file_path: str) -> processed_file.ProcessedFile:
        """
        Take the input markdown file and convert it into Confluence compatible format.

        :param input_file_path: The file to convert
        :return: The fully converted file ready to be posted to Confluence
        """
        with codecs.open(input_file_path, 'r', 'utf-8') as markdown_file:
            converted_markdown = markdown.markdown(markdown_file.read(),
                                                   extensions=['markdown.extensions.tables',
                                                               'markdown.extensions.fenced_code'])
        confluence_output = self._convert_to_confluence(converted_markdown)
        title = self._process_title(input_file_path)
        return processed_file.ProcessedFile(title, confluence_output)

    def _convert_html_to_confluence(self, input_html: str) -> processed_file.ProcessedFile:
        """
        Take the input HTML file and convert it into markdown (to strip out elements that Confluence does not like),
        then convert it into standard HTML with embedded Confluence macros for code blocks.

        :param input_html: The HTML file to process
        :return: The fully converted file ready to be posted to Confluence
        """
        confluence_output = self._convert_to_confluence(input_html)
        title = self._process_title(input_html)
        return processed_file.ProcessedFile(title, confluence_output)

    def _convert_to_confluence(self, converted_markdown: str) -> str:
        """
        Convert the input markdown file into HTML, and convert and code blocks into Confluence macros.

        :param converted_markdown: The data to convert
        :return: The fully processed data
        """
        converted_markdown = self._convert_info_macros(converted_markdown)
        converted_markdown = self._convert_links(converted_markdown)
        converted_markdown = self._convert_code_block(converted_markdown)
        converted_markdown = self._convert_references(converted_markdown)
        return converted_markdown

    @staticmethod
    def _convert_code_block(html: str) -> str:
        """
        Convert HTML code blocks into Confluence macros. This will look for any <pre><code> tags in the HTML,
        and convert them into Confluence structured code macros. This will also provide syntax highlighting, line
        numbers, and a colour theme for the block on the Confluence page.

        :param html: The HTML source to check for code tags
        :return: The processed HTML with Confluence code macros embedded within
        """

        def _process_language(lang):
            if lang is None:
                lang = 'none'
            else:
                lang = lang.rsplit('-', 1)[1]
            return lang

        def _replace(match):
            """
            This regex will match any <pre><code> tags within the HTML, extracting the language and the data contained
            within the tags. It will then construct a Confluence code macro using the specified programming language,
            the midnight colour scheme, and will display line numbers on the final Confluence page.
            """
            confluence_macro = '<ac:structured-macro ac:name="code">' \
                               '<ac:parameter ac:name="theme">Midnight</ac:parameter>' \
                               '<ac:parameter ac:name="linenumbers">true</ac:parameter>'
            lang = match.group('class')
            lang = _process_language(lang)

            confluence_macro += '<ac:parameter ac:name="language">' + lang + '</ac:parameter>'
            content = '<ac:plain-text-body><![CDATA[' + match.group('content') + ']]></ac:plain-text-body>'

            # This is in a CDATA block, so un-escape any characters that may have been escaped.
            content = content.replace('&amp;', '&').replace('&quot;', '"')
            content = content.replace('&lt;', '<').replace('&gt;', '>')
            confluence_macro += content + '</ac:structured-macro>'
            return confluence_macro

        return re.sub(
            r'<pre><code[^>]*?(?: class="(?P<class>[^"]*)")?[^>]*?>(?P<content>.*?)</code></pre>',
            _replace,
            html,
            flags=re.DOTALL)

    @staticmethod
    def _convert_links(content: str) -> str:
        """
        Remove and file extension (as these do not exist once in Confluence), and remove any underscores from any
        href elements within 'a' tags.

        :param content: The content to process
        :return: The processed data
        """
        content = content.replace(".md\"", "\"").replace(".html#", "#")

        def _replace_underscores(match):
            """
            This regex creates three match groups:

            * Start will match any a tag that contains at least an href attribute (allowing others)
            * Link will match a string of text, an underscore, and a closing string of text
            * End will match a double quote and closing > symbol

            This will replace the underscore with a single whitespace character, then rebuild the rest of the a
            tag either side of the link.
            """
            link = match.group('link')
            link = link.replace("_", " ")
            return match.group('start') + link + match.group('end')

        return re.sub(
            r'(?P<start>\<a[^>]* href=\")(?P<link>[a-zA-Z]+[\_][a-zA-Z]+)(?P<end>\"[^>]*\>)',
            _replace_underscores,
            content
        )

    @staticmethod
    def _convert_references(content: str) -> str:
        """
        Process references
        :param content: The content to process
        :return: The processed data
        """
        refs = re.findall('\n(\[\^(\d)\].*)|<p>(\[\^(\d)\].*)', content)
        if refs:
            for ref in refs:
                if ref[0]:
                    full_ref = ref[0].replace('</p>', '').replace('<p>', '')
                    ref_id = ref[1]
                else:
                    full_ref = ref[2]
                    ref_id = ref[3]

                full_ref = full_ref.replace('</p>', '').replace('<p>', '')
                content = content.replace(full_ref, '')
                href = re.search('href="(.*?)"', full_ref).group(1)
                superscript = '<a id="test" href="%s"><sup>%s</sup></a>' % (href, ref_id)
                content = content.replace('[^%s]' % ref_id, superscript)

        return content

    @staticmethod
    def _convert_comment_block(content: str) -> str:
        """
        Convert markdown code bloc to Confluence hidden comment
        :param content: The content to process
        :return: The processed data
        """
        open_tag = '<ac:placeholder>'
        close_tag = '</ac:placeholder>'
        content = content.replace('<!--', open_tag).replace('-->', close_tag)
        return content

    def _convert_info_macros(self, content: str) -> str:
        """
        Converts html for info, note or warning macros
        :param content: html string
        :return: modified html string
        """
        info_tag = '<p><ac:structured-macro ac:name="info"><ac:rich-text-body><p>'
        note_tag = info_tag.replace('info', 'note')
        warning_tag = info_tag.replace('info', 'warning')
        close_tag = '</p></ac:rich-text-body></ac:structured-macro></p>'

        # Custom tags converted into macros
        content = content.replace('<p>~?', info_tag).replace('?~</p>', close_tag)
        content = content.replace('<p>~!', note_tag).replace('!~</p>', close_tag)
        content = content.replace('<p>~%', warning_tag).replace('%~</p>', close_tag)

        # Convert block quotes into macros
        quotes = re.findall('<blockquote>(.*?)</blockquote>', content, re.DOTALL)
        if quotes:
            for quote in quotes:
                note = re.search('^<.*>Note', quote.strip(), re.IGNORECASE)
                warning = re.search('^<.*>Warning', quote.strip(), re.IGNORECASE)

                if note:
                    clean_tag = self._strip_type(quote, 'Note')
                    macro_tag = clean_tag.replace('<p>', note_tag).replace('</p>', close_tag).strip()
                elif warning:
                    clean_tag = self._strip_type(quote, 'Warning')
                    macro_tag = clean_tag.replace('<p>', warning_tag).replace('</p>', close_tag).strip()
                else:
                    macro_tag = quote.replace('<p>', info_tag).replace('</p>', close_tag).strip()

                content = content.replace('<blockquote>%s</blockquote>' % quote, macro_tag)

        # Convert doctoc to toc confluence macro
        content = self._convert_doctoc(content)
        return content

    @staticmethod
    def _convert_doctoc(content: str) -> str:
        """
        Convert doctoc to confluence macro
        :param content: html string
        :return: modified html string
        """

        toc_tag = '''<p>
        <ac:structured-macro ac:name="toc">
          <ac:parameter ac:name="printable">true</ac:parameter>
          <ac:parameter ac:name="style">disc</ac:parameter>
          <ac:parameter ac:name="maxLevel">7</ac:parameter>
          <ac:parameter ac:name="minLevel">1</ac:parameter>
          <ac:parameter ac:name="type">list</ac:parameter>
          <ac:parameter ac:name="outline">clear</ac:parameter>
          <ac:parameter ac:name="include">.*</ac:parameter>
        </ac:structured-macro>
        </p>'''

        content = re.sub('\<\!\-\- START doctoc.*END doctoc \-\-\>', toc_tag, content, flags=re.DOTALL)
        return content

    def _strip_type(self, tag: str, tagtype: str) -> str:
        """
        Strips Note or Warning tags from html in various formats
        :param tag: tag name
        :param tagtype: tag type
        :return: modified tag
        """
        tag = re.sub('%s:\s' % tagtype, '', tag.strip(), re.IGNORECASE)
        tag = re.sub('%s\s:\s' % tagtype, '', tag.strip(), re.IGNORECASE)
        tag = re.sub('<.*?>%s:\s<.*?>' % tagtype, '', tag, re.IGNORECASE)
        tag = re.sub('<.*?>%s\s:\s<.*?>' % tagtype, '', tag, re.IGNORECASE)
        tag = re.sub('<(em|strong)>%s:<.*?>\s' % tagtype, '', tag, re.IGNORECASE)
        tag = re.sub('<(em|strong)>%s\s:<.*?>\s' % tagtype, '', tag, re.IGNORECASE)
        tag = re.sub('<(em|strong)>%s<.*?>:\s' % tagtype, '', tag, re.IGNORECASE)
        tag = re.sub('<(em|strong)>%s\s<.*?>:\s' % tagtype, '', tag, re.IGNORECASE)
        string_start = re.search('<.*?>', tag)
        tag = self._upper_chars(tag, [string_start.end()])
        return tag

    @staticmethod
    def _upper_chars(tag: str, indices: str) -> str:
        """
        Make characters uppercase in string
        :param tag: string to modify
        :param indices: character index to change to uppercase
        :return: uppercased string
        """
        upper_string = "".join(c.upper() if i in indices else c for i, c in enumerate(tag))
        return upper_string

    @staticmethod
    def _process_title(input_file: str) -> str:
        """
        Trim the extension and path from the file name to give the page a suitable title.
        :param input_file: The file to trim
        :return: The file name without an extension or path
        """
        return Path(input_file).stem
