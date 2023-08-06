.. -*- coding: utf-8 -*-
.. :Project:   metapensiero.markup.semtext -- a Simple Enough Markup
.. :Created:   Wed 23 Nov 2016 09:14:23 CET
.. :Author:    Lele Gaifax <lele@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
.. :Copyright: © 2016, 2017 Arstecnica s.r.l.
.. :Copyright: © 2018 Lele Gaifax
..

=============================
 metapensiero.markup.semtext
=============================

a Simple Enough Markup
======================

 :author: Lele Gaifax
 :contact: lele@metapensiero.it
 :license: GNU General Public License version 3 or later

Implement a minimalistic markup usable in the various descriptions, with just the needed
elements: headings and paragraphs containing plain, **bold** or *italic* text, `hyper
<link>` and unordered lists.

The internal representation is a tree of nodes, and a set of functions to transpose it to/from
a textual format, HTML and `Quill Delta`__ are included.

__ https://quilljs.com/docs/delta/
