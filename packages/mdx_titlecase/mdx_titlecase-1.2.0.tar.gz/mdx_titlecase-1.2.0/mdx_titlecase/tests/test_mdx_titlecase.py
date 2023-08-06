# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Kevin Deldycke <kevin@deldycke.com>
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals
)

import textwrap
import unittest

import markdown
from mdx_titlecase.mdx_titlecase import TitlecaseExtension


class MDXTitlecase(unittest.TestCase):

    def test_load_extension_as_string(self):
        markdown.markdown(
            '', extensions=['mdx_titlecase.mdx_titlecase:TitlecaseExtension'])

    def test_load_extension_as_object(self):
        markdown.markdown('', extensions=[TitlecaseExtension()])

    def test_custom_config(self):
        md = markdown.Markdown()
        md.registerExtension(TitlecaseExtension(metadata=['foo', 'bar']))
        ext = md.registeredExtensions[0]
        self.assertEqual(ext.config['metadata'][0], ['foo', 'bar'])

    def test_subtitle_casing(self):
        text = textwrap.dedent("""
            un-cased article title of the year
            ==================================

            This is a stupid sentence.

            sub-title of the day
            --------------------

            Lorem ipsum.
            """)
        html = textwrap.dedent("""\
            <h1>Un-Cased Article Title of the Year</h1>
            <p>This is a stupid sentence.</p>
            <h2>Sub-Title of the Day</h2>
            <p>Lorem ipsum.</p>""")
        output = markdown.markdown(text, extensions=[TitlecaseExtension()])
        self.assertEqual(output, html)

    def test_default_metadata_casing(self):
        text = textwrap.dedent("""\
            Title: un-cased article title of the year
            Foo: secondary item in the metadata section

            sub-title of the day
            --------------------

            Lorem ipsum.
            """)
        html = textwrap.dedent("""\
            <h2>Sub-Title of the Day</h2>
            <p>Lorem ipsum.</p>""")
        md = markdown.Markdown(extensions=[
            TitlecaseExtension(), 'markdown.extensions.meta'])
        output = md.convert(text)
        self.assertEqual(output, html)
        self.assertEqual(md.Meta, {
            'title': ['Un-Cased Article Title of the Year'],
            'foo': ['secondary item in the metadata section'],
        })

    def test_custom_metadata_casing(self):
        text = textwrap.dedent("""\
            Title: un-cased article title of the year
            Foo: secondary item in the metadata section

            sub-title of the day
            --------------------

            Lorem ipsum.
            """)
        html = textwrap.dedent("""\
            <h2>Sub-Title of the Day</h2>
            <p>Lorem ipsum.</p>""")
        md = markdown.Markdown(extensions=[
            TitlecaseExtension(metadata=['foo', 'bar']),
            'markdown.extensions.meta'])
        output = md.convert(text)
        self.assertEqual(output, html)
        self.assertEqual(md.Meta, {
            'title': ['un-cased article title of the year'],
            'foo': ['Secondary Item in the Metadata Section'],
        })
