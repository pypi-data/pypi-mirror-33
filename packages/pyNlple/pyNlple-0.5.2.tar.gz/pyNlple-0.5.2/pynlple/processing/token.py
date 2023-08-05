# -*- coding: utf-8 -*-
import re
from operator import itemgetter

from .dictionary import FileFolderTokenMapping
from .emojis import UnicodeEmojiProvider

PUNCTUATION = list(map(itemgetter(0), (map(itemgetter(0), FileFolderTokenMapping(['punctuation.txt'])))))
SPECIAL_SYMBOLS = list(map(itemgetter(0), (map(itemgetter(0), FileFolderTokenMapping(['special_symbols.txt'])))))
CURRENCY = list(map(itemgetter(0),map(itemgetter(0), FileFolderTokenMapping(['currency.txt']))))
EMOJIS = list(map(itemgetter(0), UnicodeEmojiProvider()))
TOKEN_TYPES = [
            r'(' + '|'.join(map(re.escape, EMOJIS)) + r')',
            r'([^\W\d_]+([\'\-][^\W\d_]+)*[^\W\d_]*)',  # tokens, also with - and ' in middle
            r'([^\W_]+([\'\-][^\W\d_]+)+)',  # tokens, starting with number and ' - in middle ("7-fold", etc.)
            r'(\d+([,:.]\d+)*\d*)',  # digital sequences, also with , : . in middle
            # r'[^\W\d_]+',  # all other alpha tokens, excluding underscore
            # r'[\d\W]+',  # all other numeric sequences
            r'\.+',
            r'[^\w\d\s]',  # all individual symbols that are not alphanum or whitespaces
            r'_',  # underscore as being exluded by \w and previously by [^\W\d_]+
            r'\r\n?',
        ]


def has_capital_letter(token):
    return any(l.isupper() for l in token)


def first_capital_letter(token):
    return len(token) > 0 and token[0].isupper()


def only_first_capital_letter(token):
    return first_capital_letter(token) and not has_capital_letter(token[1:])


def has_not_first_capital_letter(token):
    return not first_capital_letter(token) and has_capital_letter(token[1:])


def one_capital_letter(token):
    return sum(l.isupper() for l in token) == 1


def more_than_one_capital_letter(token):
    return sum(l.isupper() for l in token) > 1


def all_capital(token):
    return token.isupper()


def all_lower(token):
    return token.islower()


newline_pattern = re.compile(r'\r\n?')
def is_newline(token):
    return newline_pattern.fullmatch(token) is not None


multidot_pattern = re.compile(r'\.\.+')
def is_multiple_dot(token):
    return multidot_pattern.fullmatch(token) is not None


digital_sequence_pattern = re.compile(r'^[\.]?[\d][\d\.,\-:]*$')
def is_a_digital_sequence(token):
    return digital_sequence_pattern.fullmatch(token) is not None