import re
import codecs
from os import path


def find_uploads(content):
    return re.findall('upload\([\'|"](.*?)[\'|"]\)', content.decode("utf-8"))


def find_reads(content):
    return re.findall('read\([\'|"](.*?)[\'|"]\)', content.decode("utf-8"))


def read_files(names, file_path):
    return [__resolve_file(name, file_path) for name in names]


def __resolve_file(file, folder):
    if path.isabs(file):
        abs_file_path = path.abspath(file)
        return __check_non_existing_path(abs_file_path)

    folder_prefixed_file_path = path.abspath(path.join(folder, file))
    return __check_non_existing_path(folder_prefixed_file_path)


def __check_non_existing_path(file_path):
    if path.exists(file_path):
        return file_path
    raise Exception(
        '{0} could not be found in {1}'.format(path.basename(file_path), path.dirname(file_path)))


ESCAPE_SEQUENCE_RE = re.compile(r'''
    ( \\[\\'"abfnrtv]  # Single-character escapes
    )''', re.UNICODE | re.VERBOSE)


def decode_escapes(s):
    def decode_match(match):
        return codecs.decode(match.group(0), 'unicode-escape')

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)
