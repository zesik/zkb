# -*- coding: utf-8 -*-
"""
zkb.readers
~~~~~~~~~~~

Readers for reading article sources.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

import codecs

from zkb.configparsers import YamlConfigParser
from zkb.utils import DEFAULT_ENCODING
from zkb.utils import UnknownEncodingError


class HeaderedContentReader(object):
    """Base class of reader for reading and parsing a headered file.

    :param encoding: default encoding when read the stream for the first time.
    :type encoding: str
    """

    def __init__(self, encoding=DEFAULT_ENCODING):
        super(HeaderedContentReader, self).__init__()
        self._default_encoding = encoding

    @classmethod
    def from_extension(cls, extension, **kwargs):
        """Create a HeaderedContentReader based on file extension.

        :param extension: file extension.
        :type extension: str
        :return: a instance of one child class of HeaderedContentReader, or
            None if the extension cannot be recognized.
        :rtype: HeaderedContentReader
        """
        extension = extension.lower()
        if extension in _READER_EXTENSIONS:
            return HeaderedContentReader.from_type(
                _READER_EXTENSIONS[extension], **kwargs)
        return None

    @classmethod
    def from_type(cls, file_format, **kwargs):
        """Create a HeaderedContentReader based on its type.

        :param file_format: file format.
        :type file_format: str
        :return: a instance of one child class of HeaderedContentReader, or
            None if the file format cannot be recognized.
        :rtype: HeaderedContentReader
        """
        file_format = file_format.lower()
        if file_format in _CONFIG_READERS:
            constructor = globals()[_CONFIG_READERS[file_format]]
            return constructor(**kwargs)
        return None

    def _get_encoding(self, header):
        """Gets the encoding of the file specified in header of the file.

        This method is called by :func:`read` when parsing header. Do not call
        this method manually.

        Having different header format, this class does not actually parse the
        header, but define an interface so that subclasses can override this
        method to extract correct encoding information.

        :param header: a list contains header lines.
        :type header: list
        :return: a string representing encoding judged from header lines; None
            if encoding cannot be determined.
        :rtype: str
        """
        pass

    def _parse_header(self, header, base=None):
        """Parses header lines to dictionary.

        This method is called by :func:`read` after all content is properly
        read. Do not call this method manually.

        Having different header format, this class does not actually parse the
        header, but define an interface so that subclasses can override this
        method to parse the header correctly.

        :param header: a list containing header lines.
        :type header: list
        :param base: a copy of *base* will be used as base dictionary that will
            be updated with key/value read from header, with exiting key/value
            overwritten.
        :type base: dict or None
        :return: a new dict based on base dict and header value.
        :rtype: dict
        """
        pass

    def read(self, stream, read_payload=True, base=None):
        """Reads a headered file and parse its header.

        A headered file contains a header and its payload, separated by a blank
        line. Since a blank line is used to identify end of header, header
        cannot contain any blank line. Payload can contain as many blank lines
        as it needs.

        Header comes with different formats. This class does not understand
        actual format of a header, so parsing a header will always return None.
        Subclasses can override :func:`_parse_header` method to parse the
        header correctly.

        When reading the header, :func:`_get_encoding` will be called several
        times to check whether encoding of the file is specified in the header.
        And when the encoding specified is different from the encoding that is
        currently being used, reading will be restarted from the beginning of
        the stream using encoding specified. Having different format of header,
        this class will not parse the header but always consider encoding is
        correct. Subclasses can override :func:`_get_encoding` method to
        extract correct encoding information.

        :param stream: a stream to read.
        :type stream: stream
        :param read_payload: True if payload of the file should be read; False
            if only header should be read.
        :type read_payload: bool
        :param base: if provided, a copy of *base* will be returned with
            key/value updated with data read from file header.
        :type base: dict or None
        :return: a tuple containing two objects; respectively these are a dict
            parsed from header and the payload of the file. Payload will be
            None if *read_payload* is False.
        :rtype: tuple
        :raises UnknownEncodingError: if encoding specified in header is not
            supported.
        """
        encoding = self._default_encoding
        encoding_determined = False
        file_loaded = False
        header = []
        payload = []
        while not file_loaded:
            del header[:]
            del payload[:]
            reading_payload = False
            try:
                reader = codecs.getreader(encoding)(stream, 'replace')
            except LookupError:
                raise UnknownEncodingError(encoding)
            stream.seek(0)
            while True:
                # Read a new line
                line = reader.readline()
                if not line:
                    # All content has been read
                    file_loaded = True
                    break
                line = line.strip('\r\n')

                # Check for separator of header and payload
                if not reading_payload and len(line) == 0:
                    # Found separator of header and payload
                    if not read_payload:
                        file_loaded = True
                        break
                    # Switch state and ignore the separator line
                    reading_payload = True
                    continue

                # Add line to the list
                if reading_payload:
                    payload.append(line)
                else:
                    header.append(line)
                    if not encoding_determined:
                        specified = self._get_encoding(header)
                        if specified is not None:
                            encoding_determined = True
                            if specified != encoding:
                                # Restart reading the entire file with new
                                # encoding
                                encoding = specified
                                break
        header_result = self._parse_header(header, base)
        payload_result = None if not read_payload else u'\n'.join(payload)
        return header_result, payload_result


class YamlHeaderedContentReader(HeaderedContentReader):
    """Reader for headered file with header of YAML format.

    :param encoding: default encoding when read the stream for the first time.
    :type encoding: str
    """

    def __init__(self, encoding=DEFAULT_ENCODING):
        super(YamlHeaderedContentReader, self).__init__(encoding)
        self._yaml_parser = YamlConfigParser()

    def _get_encoding(self, header):
        """Override to extract the encoding of YAML format header.

        :param header: a list contains header lines.
        :type header: list
        :return: a string representing encoding judged from header lines; None
            if encoding cannot be determined.
        :rtype: str
        """
        parsed = self._yaml_parser.parse('\n'.join(header))
        if parsed is not None and 'encoding' in parsed:
            return parsed['encoding']

    def _parse_header(self, header, base=None):
        """Override to parses header lines in YAML format to dictionary.

        :param header: a list containing header lines.
        :type header: list
        :param base: a copy of *base* will be used as base dictionary that will
            be updated with key/value read from header, with exiting key/value
            overwritten.
        :type base: dict or None
        :return: a new dict based on base dict and header value.
        :rtype: dict
        """
        parsed = self._yaml_parser.parse('\n'.join(header))
        result = {} if base is None else base.copy()
        result.update(parsed if parsed is not None else {})
        return result


_READER_EXTENSIONS = {
    '.yml': 'yaml',
    '.yaml': 'yaml'
}

_CONFIG_READERS = {
    'yaml': YamlHeaderedContentReader.__name__
}
