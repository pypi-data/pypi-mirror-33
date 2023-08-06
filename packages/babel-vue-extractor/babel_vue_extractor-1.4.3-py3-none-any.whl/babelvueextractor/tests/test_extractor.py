# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from babel.messages.extract import DEFAULT_KEYWORDS, extract

from babelvueextractor.extract import extract_vue
from six import BytesIO as FileMock

TEST_OPTIONS = {}


class TestMessagesExtractor(unittest.TestCase):
    def test_empty_template(self):
        template = FileMock(b"")
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertEqual(list(), list(result))

    def test_no_messages(self):
        template = FileMock(b"""
        <div>
            <h1>Foo</h1>
            <p>Lore ipsum delore gettext() ...</p>
        </div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertEqual(list(), list(result))

    def test_gettext(self):
        template = FileMock(b"""
        <div>
            {{ gettext('Foo') }}
        </div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertEqual(list(result), [
            (3, u'gettext', u"Foo", [])
        ])

    def test_ngettext(self):
        template = FileMock(b"""
        <div>
            {{ ngettext('Foo', 'Foos', 1) }}
        </div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertEqual(list(result), [
            (3, u'ngettext', (u"Foo", u"Foos"), []),
        ])

    def test_underscore(self):
        template = FileMock(b"""
        <div>
            {{ _("Bar") }}
        </div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertEqual(list(result), [
            (3, '_', u'Bar', [])
        ])

    def test_token_without_content(self):
        template = FileMock(b"""
            {{  }}
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertEqual(list(result), [])

    def test_commas(self):
        template = FileMock(b"""
            {{ gettext('Hello, User') }}
            {{ gettext("You're") }}
            {{ gettext("You\\"re") }}
        """)

        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertEqual(list(result), [
            (2, u'gettext', u'Hello, User', []),
            (3, u'gettext', u"You're", []),
            (4, u'gettext', u"You\"re", []),
        ])

    def test_babel(self):
        method = 'babelvueextractor.extract.extract_vue'
        fileobj = open('babelvueextractor/tests/templates/for_babel.vhtml', 'rb')
        result = extract(method, fileobj)

        self.assertListEqual(list(result), [
            (1, u'Привет, User', [], None),
            (2, (u'Здравствуй, друг', u'Здравствуйте, друзья'), [], None)
        ])
        fileobj.close()

    def test_gettext_with_parameter(self):
        template = FileMock(b"""
        <li>
            {{ gettext('{number} season').replace("{number}", season) }}
            {{ gettext('Processed by filter')|somefilter }}
            {{ somefunc(gettext('Processed by function')) }}
            {{ gettext('Foo') + gettext('bar') }}
        </li>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertEqual(list(result), [
            (3, u'gettext', u'{number} season', []),
            (4, u'gettext', u'Processed by filter', []),
            (5, u'gettext', u'Processed by function', []),
            (6, u'gettext', u'Foo', []),
            (6, u'gettext', u'bar', []),
        ])

    def test_text_directives(self):
        template = FileMock(b"""
        <div v-text="gettext('Sometext')"></div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertListEqual(list(result), [(2, u'gettext', u'Sometext', [])])

    def test_directives_with_inner_tag(self):
        template = FileMock(b"""
        <div v-text="gettext('Sometext')">
        {{ gettext('Hello') }}
        </div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertListEqual(list(result), [
            (2, u'gettext', u'Sometext', []),
            (3, u'gettext', u'Hello', [])
        ])

    def test_directives_with_inner_colon_tag(self):
        template = FileMock(b"""
        <div :text="gettext('Sometext')">
        {{ gettext('Hello') }}
        </div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertListEqual(list(result), [
            (2, u'gettext', u'Sometext', []),
            (3, u'gettext', u'Hello', [])
        ])

    def test_html_directives(self):
        template = FileMock(b"""
        <div v-html="gettext('Sometext')"></div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertListEqual(list(result), [(2, u'gettext', u'Sometext', [])])

    def test_colon_directives(self):
        template = FileMock(b"""
        <div :html="gettext('Sometext')"></div>
        """)
        result = extract_vue(template, DEFAULT_KEYWORDS.keys(), [], TEST_OPTIONS)
        self.assertListEqual(list(result), [(2, u'gettext', u'Sometext', [])])

    def test_vue_file(self):
        method = 'babelvueextractor.extract.extract_vue'
        with open('babelvueextractor/tests/templates/for_babel.vue', 'rb') as f:
            result = extract(method, f)

            self.assertListEqual(list(result), [
                (2, u'Xin chào, Babel', [], None),
                (9, u'Tôi là một chú hươu nhỏ', [], None)
            ])
