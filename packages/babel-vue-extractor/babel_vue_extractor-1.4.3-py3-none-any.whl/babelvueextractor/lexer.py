from __future__ import unicode_literals
import re

TOKEN_TEXT = 0
TOKEN_VAR = 1
TOKEN_CONST = 2
TOKEN_COMMENT = 3
TOKEN_RAW_HTML = 4
TOKEN_DOUBLE_WAY_BINDING = 5
TOKEN_DIRECTIVE = 6

TOKEN_MAPPING = {
    TOKEN_TEXT: 'Text',
    TOKEN_VAR: 'Var',
    TOKEN_CONST: 'Const',
    TOKEN_DOUBLE_WAY_BINDING: 'Binding',
    TOKEN_COMMENT: 'Comment',
    TOKEN_RAW_HTML: 'Raw',
    TOKEN_DIRECTIVE: 'Directive',
}

# template syntax constants
FILTER_SEPARATOR = '|'
FILTER_ARGUMENT_SEPARATOR = ':'
VARIABLE_ATTRIBUTE_SEPARATOR = '.'

VARIABLE_TAG_START = '{{'
VARIABLE_TAG_END = '}}'
CONST_START = '{{*'
CONST_END = '}}'
RAW_HTML_TAG_START = '{{{'
RAW_HTML_TAG_END = '}}}'
DOUBLE_WAY_BINDING_START = '{{@'
DOUBLE_WAY_BINDING_END = '}}'
COMMENT_START = '<!--'
COMMENT_END = '-->'
V_DIRECTIVE_PREFIX = 'v-'
COLON_DIRECTIVE_PREFIX = '\x3a'  # 0x3a = ":"

tag_re = re.compile('(%s.*?%s|%s.*?%s|%s.*?%s|%s.*?%s|%s.*?%s|(?:%s|%s).+?=(?:".*?"|\'.*?\'))' % (
    re.escape(CONST_START), re.escape(CONST_END),
    re.escape(RAW_HTML_TAG_START), re.escape(RAW_HTML_TAG_END),
    re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END),
    re.escape(COMMENT_START), re.escape(COMMENT_END),
    re.escape(DOUBLE_WAY_BINDING_START), re.escape(DOUBLE_WAY_BINDING_END),

    V_DIRECTIVE_PREFIX,
    COLON_DIRECTIVE_PREFIX,
))


class Token(object):
    def __init__(self, token_type, contents):
        self.token_type, self.contents = token_type, contents
        self.lineno = None

    def __str__(self):
        token_name = TOKEN_MAPPING[self.token_type]
        return ('<{0} token: "{1}...">'.format(
            token_name, self.contents[:20].replace('\n', '')))

    def __repr__(self):
        return 'Token(token_type={token_type}, contents="{contents}")'.format(
            token_type=self.token_type,
            contents=self.contents
        )

    def __eq__(self, other):
        return all([self.token_type == other.token_type, self.contents == other.contents])

    @property
    def token_name(self):
        return TOKEN_MAPPING[self.token_type]


class Lexer(object):
    def __init__(self, template_string, origin=None):
        self.template_string = template_string
        self.origin = origin
        self.lineno = 1
        self.verbatim = False

    def tokenize(self):
        """
        Return a list of tokens from a given template_string.
        """
        in_tag = False
        result = []
        for bit in tag_re.split(self.template_string):
            if bit:
                result.append(
                    self.create_token(bit, in_tag)
                )
            in_tag = not in_tag
        return result

    def create_token(self, token_string, in_tag):
        """
        Convert the given token string into a new Token object and return it.
        If in_tag is True, we are processing something that matched a tag,
        otherwise it should be treated as a literal string.
        """
        token_type = TOKEN_TEXT
        content = token_string

        if in_tag:
            _start, _end = None, 0

            if token_string.startswith(DOUBLE_WAY_BINDING_START):
                _start = len(DOUBLE_WAY_BINDING_START)
                _end = len(DOUBLE_WAY_BINDING_END)
                token_type = TOKEN_DOUBLE_WAY_BINDING

            elif token_string.startswith(CONST_START):
                _start = len(CONST_START)
                _end = len(CONST_END)
                token_type = TOKEN_CONST

            elif token_string.startswith(RAW_HTML_TAG_START):
                _start = len(RAW_HTML_TAG_START)
                _end = len(RAW_HTML_TAG_END)
                token_type = TOKEN_RAW_HTML

            elif token_string.startswith(COMMENT_START):
                _start = len(COMMENT_START)
                _end = len(COMMENT_END)
                token_type = TOKEN_COMMENT

            elif token_string.startswith(VARIABLE_TAG_START):
                _start = len(VARIABLE_TAG_START)
                _end = len(VARIABLE_TAG_END)
                token_type = TOKEN_VAR

            elif token_string.endswith(('"', "'")):
                token_type = TOKEN_DIRECTIVE
                # eg. v-text="attr" => ['v-text=', 'attr', '']
                content = token_string.split(token_string[-1])[1]

            if _start is not None:
                content = token_string[_start:-_end].strip()

        token = Token(token_type, content)
        token.lineno = self.lineno
        self.lineno += token_string.count('\n')
        return token
