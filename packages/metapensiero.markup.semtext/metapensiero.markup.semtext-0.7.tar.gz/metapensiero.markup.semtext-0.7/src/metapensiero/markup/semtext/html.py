# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- HTML parser
# :Created:   sab 01 apr 2017 14:00:33 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Arstecnica s.r.l.
# :Copyright: © 2018 Lele Gaifax
#

from io import StringIO
from itertools import chain
from re import compile

from lxml.html import fragment_fromstring

from .ast import Heading, Item, Link, List, ListStyle, Paragraph, Span, SpanStyle, Text
from .text import parse_text
from .visitor import HTMLPrinter, SEMPrinter


def squash_ws(text, empty=None, ws_rx=compile(r'\s+')):
    "Squash consecutive whitespaces to a single space."

    if not text:
        return None
    elif text.isspace():
        return empty
    else:
        return ws_rx.sub(" ", text)


class Parser:
    "HTML parser based on ``lxml``."

    def __init__(self, top_element, **options):
        self.top_element = top_element
        self.options = options
        self.lists_style_stack = []

    def __call__(self, children):
        handle = self.handle
        elts = []
        for c in children:
            elts.extend(handle(c))
        return self.top_element(elts, **self.options)

    def handle(self, element):
        handler = getattr(self, 'handle_' + element.tag)
        return handler(element)

    def make_heading(self, level, element):
        elts = []

        spans = []
        handle = self.handle

        text = squash_ws(element.text)
        if text:
            spans.append(Span(text))

        partial = False

        children = element.iterchildren()
        for elt in children:
            if elt.tag not in ('a', 'b', 'em', 'i', 'strong'):
                partial = True
                break

            spans.extend(handle(elt))

        tail = squash_ws(element.tail, " ")
        if spans and tail:
            spans.append(Span(tail))

        if spans:
            elts.append(Heading(level, spans))

        remaining = chain((elt,), children) if partial else None

        return elts, remaining

    def handle_h1(self, element):
        elts, remaining = self.make_heading(1, element)
        assert remaining is None
        return elts

    def handle_h2(self, element):
        elts, remaining = self.make_heading(2, element)
        assert remaining is None
        return elts

    def handle_h3(self, element):
        elts, remaining = self.make_heading(3, element)
        assert remaining is None
        return elts

    def handle_h4(self, element):
        elts, remaining = self.make_heading(4, element)
        assert remaining is None
        return elts

    def handle_h5(self, element):
        elts, remaining = self.make_heading(5, element)
        assert remaining is None
        return elts

    def handle_h6(self, element):
        elts, remaining = self.make_heading(6, element)
        assert remaining is None
        return elts

    def make_paragraph(self, element):
        elts = []

        spans = []
        handle = self.handle

        text = squash_ws(element.text)
        if text:
            spans.append(Span(text))

        partial = False

        children = element.iterchildren()
        for elt in children:
            if elt.tag == 'br':
                tail = squash_ws(elt.tail, " ")
                if tail:
                    if spans:
                        elts.append(Paragraph(spans))
                        ss = spans[-1].style
                        spans = [Span(tail, ss)]
                    else:
                        spans = [Span(tail)]
            else:
                if elt.tag not in ('a', 'b', 'em', 'i', 'span', 'strong'):
                    partial = True
                    break

                spans.extend(handle(elt))

        tail = squash_ws(element.tail, " ")
        if spans and tail:
            spans.append(Span(tail))

        if spans:
            elts.append(Paragraph(spans))

        remaining = chain((elt,), children) if partial else None

        return elts, remaining

    def handle_div(self, element):
        children = element.getchildren()
        if not children:
            yield from self.handle_p(element)
        else:
            for elt in children:
                yield from self.handle(elt)

    def handle_p(self, element):
        elts, remaining = self.make_paragraph(element)
        assert remaining is None, [e.text for e in element.iterchildren()]
        return elts

    def handle_strong(self, element):
        elts = []
        text = squash_ws(element.text)
        if text:
            elts.append(Span(text, SpanStyle.BOLD))
        tail = squash_ws(element.tail, " ")
        if tail:
            elts.append(Span(tail))
        return elts

    handle_b = handle_strong

    def handle_em(self, element):
        elts = []
        text = squash_ws(element.text)
        if text:
            elts.append(Span(text, SpanStyle.ITALIC))
        tail = squash_ws(element.tail, " ")
        if tail:
            elts.append(Span(tail))
        return elts

    handle_i = handle_em

    def handle_span(self, element):
        elts = []
        text = squash_ws(element.text)
        if text:
            elts.append(Span(text))
        tail = squash_ws(element.tail, " ")
        if tail:
            elts.append(Span(tail))
        return elts

    def handle_ul(self, element):
        self.lists_style_stack.append(ListStyle.DOTTED)
        items = []
        handle = self.handle
        for elt in element.iterchildren():
            items.extend(handle(elt))
        self.lists_style_stack.pop()
        return [List(items)]

    def handle_ol(self, element):
        self.lists_style_stack.append(ListStyle.NUMERIC)
        items = []
        handle = self.handle
        for elt in element.iterchildren():
            items.extend(handle(elt))
        self.lists_style_stack.pop()
        index = 0
        for item in items:
            if item.index is None:
                index += 1
                item.index = index
            else:
                index = item.index
        return [List(items, ListStyle.NUMERIC)]

    def handle_li(self, element):
        elts, remaining = self.make_paragraph(element)
        if remaining is not None:
            handle = self.handle
            for r in remaining:
                elts.extend(handle(r))
        index = None
        if self.lists_style_stack[-1] == ListStyle.NUMERIC:
            values = element.values()
            if values:
                try:
                    index = int(values[0])
                except ValueError:
                    pass
        return [Item(elts, index=index)]

    def handle_a(self, element):
        elts = []
        text = squash_ws(element.text)
        if 'href' in element.attrib:
            elts.append(Link(text, element.attrib['href']))
        else:
            elts.append(Span(text))
        tail = squash_ws(element.tail, " ")
        if tail:
            elts.append(Span(tail))
        return elts


def parse_html(html):
    "Parse `html` and return a :class:`.ast.Text` with the equivalent *AST*."

    fragment = fragment_fromstring(html, 'text')
    parser = Parser(Text)
    return parser(fragment.iterchildren())


def html_to_text(html):
    """Parse `html` and return an equivalent *semtext*."""

    if squash_ws(html):
        parsed = parse_html(html)
        stream = StringIO()
        SEMPrinter(where=stream).visit(parsed)
        return stream.getvalue() or html


def text_to_html(text):
    """Parse `text` and return an equivalent ``HTML`` representation."""

    if squash_ws(text):
        parsed = parse_text(text)
        stream = StringIO()
        HTMLPrinter(where=stream).visit(parsed)
        return stream.getvalue() or text
