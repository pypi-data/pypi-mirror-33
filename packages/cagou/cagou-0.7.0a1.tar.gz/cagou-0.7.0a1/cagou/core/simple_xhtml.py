#!/usr/bin/python
# -*- coding: utf-8 -*-

# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2018 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from sat.core import log as logging
log = logging.getLogger(__name__)
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.utils import escape_markup
from kivy.metrics import sp
from kivy import properties
from xml.etree import ElementTree as ET
from sat_frontends.tools import css_color, strings as sat_strings
from cagou.core.image import AsyncImage
import webbrowser


class Escape(unicode):
    """Class used to mark that a message need to be escaped"""

    def __init__(self, text):
        super(Escape, self).__init__(text)


class SimpleXHTMLWidgetEscapedText(Label):

    def on_parent(self, instance, parent):
        self.font_size = parent.font_size

    def _addUrlMarkup(self, text):
        text_elts = []
        idx = 0
        links = 0
        while True:
            m = sat_strings.RE_URL.search(text[idx:])
            if m is not None:
                text_elts.append(escape_markup(m.string[0:m.start()]))
                link_key = u'link_' + unicode(links)
                url = m.group()
                text_elts.append(u'[color=5500ff][ref={link}]{url}[/ref][/color]'.format(
                    link = link_key,
                    url = url
                    ))
                if not links:
                    self.ref_urls = {link_key: url}
                else:
                    self.ref_urls[link_key] = url
                links += 1
                idx += m.end()
            else:
                if links:
                    text_elts.append(escape_markup(text[idx:]))
                    self.markup = True
                    self.text = u''.join(text_elts)
                break

    def on_text(self, instance, text):
        # do NOT call the method if self.markup is set
        # this would result in infinite loop (because self.text
        # is changed if an URL is found, and in this case markup too)
        if text and not self.markup:
            self._addUrlMarkup(text)

    def on_ref_press(self, ref):
        url = self.ref_urls[ref]
        webbrowser.open(url)


class SimpleXHTMLWidgetText(Label):

    def on_parent(self, instance, parent):
        self.font_size = parent.font_size


class SimpleXHTMLWidgetImage(AsyncImage):
    # following properties are desired height/width
    # i.e. the ones specified in height/width attributes of <img>
    # (or wanted for whatever reason)
    # set to 0 to ignore them
    target_height = properties.NumericProperty()
    target_width = properties.NumericProperty()

    def _get_parent_container(self):
        """get parent SimpleXHTMLWidget instance

        @param warning(bool): if True display a log.error if nothing found
        @return (SimpleXHTMLWidget, None): found SimpleXHTMLWidget instance
        """
        parent = self.parent
        while parent and not isinstance(parent, SimpleXHTMLWidget):
            parent = parent.parent
        if parent is None:
            log.error(u"no SimpleXHTMLWidget parent found")
        return parent

    def _on_source_load(self, value):
        # this method is called when image is loaded
        super(SimpleXHTMLWidgetImage, self)._on_source_load(value)
        if self.parent is not None:
            container = self._get_parent_container()
            # image is loaded, we need to recalculate size
            self.on_container_width(container, container.width)

    def on_container_width(self, container, container_width):
        """adapt size according to container width

        called when parent container (SimpleXHTMLWidget) width change
        """
        target_size = (self.target_width or self.texture.width, self.target_height or self.texture.height)
        padding = container.padding
        padding_h = (padding[0] + padding[2]) if len(padding) == 4 else padding[0]
        width = container_width - padding_h
        if target_size[0] < width:
            self.size = target_size
        else:
            height = width / self.image_ratio
            self.size = (width, height)

    def on_parent(self, instance, parent):
        if parent is not None:
            container = self._get_parent_container()
            container.bind(width=self.on_container_width)


class SimpleXHTMLWidget(StackLayout):
    """widget handling simple XHTML parsing"""
    xhtml = properties.StringProperty()
    color = properties.ListProperty([1, 1, 1, 1])
    # XXX: bold is only used for escaped text
    bold = properties.BooleanProperty(False)
    content_width = properties.NumericProperty(0)
    font_size = properties.NumericProperty(sp(14))

    # text/XHTML input

    def on_xhtml(self, instance, xhtml):
        """parse xhtml and set content accordingly

        if xhtml is an instance of Escape, a Label with not markup
        will be used
        """
        self.clear_widgets()
        if isinstance(xhtml, Escape):
            label = SimpleXHTMLWidgetEscapedText(text=xhtml, color=self.color)
            self.bind(color=label.setter('color'))
            self.bind(bold=label.setter('bold'))
            self.add_widget(label)
        else:
            xhtml = ET.fromstring(xhtml.encode('utf-8'))
            self.current_wid = None
            self.styles = []
            self._callParseMethod(xhtml)

    def escape(self, text):
        """mark that a text need to be escaped (i.e. no markup)"""
        return Escape(text)

    # sizing

    def on_width(self, instance, width):
        if len(self.children) == 1:
            wid = self.children[0]
            if isinstance(wid, Label):
                # we have simple text
                try:
                    full_width = wid._full_width
                except AttributeError:
                    # on first time, we need the required size
                    # for the full text, without width limit
                    wid.size_hint = (None, None)
                    wid.texture_update()
                    full_width = wid._full_width = wid.texture_size[0]

                if full_width > width:
                    wid.text_size = width, None
                    wid.width = width
                else:
                    wid.text_size = None, None
                    wid.texture_update()
                    wid.width = wid.texture_size[0]
                self.content_width = wid.width + self.padding[0] + self.padding[2]
            else:
                wid.size_hint = (1, None)
                wid.height = 100
                self.content_width = self.width
        else:
            self._do_complexe_sizing(width)

    def _do_complexe_sizing(self, width):
        try:
            self.splitted
        except AttributeError:
            # XXX: to make things easier, we split labels in words
            log.debug(u"split start")
            children = self.children[::-1]
            self.clear_widgets()
            for child in children:
                if isinstance(child, Label):
                    log.debug(u"label before split: {}".format(child.text))
                    styles = []
                    tag = False
                    new_text = []
                    current_tag = []
                    current_value = []
                    current_wid = self._createText()
                    value = False
                    close = False
                    # we will parse the text and create a new widget
                    # on each new word (actually each space)
                    # FIXME: handle '\n' and other white chars
                    for c in child.text:
                        if tag:
                            # we are parsing a markup tag
                            if c == u']':
                                current_tag_s = u''.join(current_tag)
                                current_style = (current_tag_s, u''.join(current_value))
                                if close:
                                    for idx, s in enumerate(reversed(styles)):
                                        if s[0] == current_tag_s:
                                            del styles[len(styles) - idx - 1]
                                            break
                                else:
                                    styles.append(current_style)
                                current_tag = []
                                current_value = []
                                tag = False
                                value = False
                                close = False
                            elif c == u'/':
                                close = True
                            elif c == u'=':
                                value = True
                            elif value:
                                current_value.append(c)
                            else:
                                current_tag.append(c)
                            new_text.append(c)
                        else:
                            # we are parsing regular text
                            if c == u'[':
                                new_text.append(c)
                                tag = True
                            elif c == u' ':
                                # new word, we do a new widget
                                new_text.append(u' ')
                                for t, v in reversed(styles):
                                    new_text.append(u'[/{}]'.format(t))
                                current_wid.text = u''.join(new_text)
                                new_text = []
                                self.add_widget(current_wid)
                                log.debug(u"new widget: {}".format(current_wid.text))
                                current_wid = self._createText()
                                for t, v in styles:
                                    new_text.append(u'[{tag}{value}]'.format(
                                        tag = t,
                                        value = u'={}'.format(v) if v else u''))
                            else:
                                new_text.append(c)
                    if current_wid.text:
                        # we may have a remaining widget after the parsing
                        close_styles = []
                        for t, v in reversed(styles):
                            close_styles.append(u'[/{}]'.format(t))
                        current_wid.text = u''.join(close_styles)
                        self.add_widget(current_wid)
                        log.debug(u"new widget: {}".format(current_wid.text))
                else:
                    # non Label widgets, we just add them
                    self.add_widget(child)
            self.splitted = True
            log.debug(u"split OK")

        # we now set the content width
        # FIXME: for now we just use the full width
        self.content_width = width

    # XHTML parsing methods

    def _callParseMethod(self, e):
        """call the suitable method to parse the element

        self.xhtml_[tag] will be called if it exists, else
        self.xhtml_generic will be used
        @param e(ET.Element): element to parse
        """
        try:
            method = getattr(self, "xhtml_{}".format(e.tag))
        except AttributeError:
            log.warning(u"Unhandled XHTML tag: {}".format(e.tag))
            method = self.xhtml_generic
        method(e)

    def _addStyle(self, tag, value=None, append_to_list=True):
        """add a markup style to label

        @param tag(unicode): markup tag
        @param value(unicode): markup value if suitable
        @param append_to_list(bool): if True style we be added to self.styles
            self.styles is needed to keep track of styles to remove
            should most probably be set to True
        """
        label = self._getLabel()
        label.text += u'[{tag}{value}]'.format(
            tag = tag,
            value = u'={}'.format(value) if value else ''
            )
        if append_to_list:
            self.styles.append((tag, value))

    def _removeStyle(self, tag, remove_from_list=True):
        """remove a markup style from the label

        @param tag(unicode): markup tag to remove
        @param remove_from_list(bool): if True, remove from self.styles too
            should most probably be set to True
        """
        label = self._getLabel()
        label.text += u'[/{tag}]'.format(
            tag = tag
            )
        if remove_from_list:
            for rev_idx, style in enumerate(reversed(self.styles)):
                if style[0] == tag:
                    tag_idx = len(self.styles) - 1 - rev_idx
                    del self.styles[tag_idx]
                    break

    def _getLabel(self):
        """get current Label if it exists, or create a new one"""
        if not isinstance(self.current_wid, Label):
            self._addLabel()
        return self.current_wid

    def _addLabel(self):
        """add a new Label

        current styles will be closed and reopened if needed
        """
        self._closeLabel()
        self.current_wid = self._createText()
        for tag, value in self.styles:
            self._addStyle(tag, value, append_to_list=False)
        self.add_widget(self.current_wid)

    def _createText(self):
        label = SimpleXHTMLWidgetText(color=self.color, markup=True)
        self.bind(color=label.setter('color'))
        label.bind(texture_size=label.setter('size'))
        return label

    def _closeLabel(self):
        """close current style tags in current label

        needed when you change label to keep style between
        different widgets
        """
        if isinstance(self.current_wid, Label):
            for tag, value in reversed(self.styles):
                self._removeStyle(tag, remove_from_list=False)

    def _parseCSS(self, e):
        """parse CSS found in "style" attribute of element

        self._css_styles will be created and contained markup styles added by this method
        @param e(ET.Element): element which may have a "style" attribute
        """
        styles_limit = len(self.styles)
        styles = e.attrib['style'].split(u';')
        for style in styles:
            try:
                prop, value = style.split(u':')
            except ValueError:
                log.warning(u"can't parse style: {}".format(style))
                continue
            prop = prop.strip().replace(u'-', '_')
            value = value.strip()
            try:
                method = getattr(self, "css_{}".format(prop))
            except AttributeError:
                log.warning(u"Unhandled CSS: {}".format(prop))
            else:
                method(e, value)
        self._css_styles = self.styles[styles_limit:]

    def _closeCSS(self):
        """removed CSS styles

        styles in self._css_styles will be removed
        and the attribute will be deleted
        """
        for tag, dummy in reversed(self._css_styles):
            self._removeStyle(tag)
        del self._css_styles

    def xhtml_generic(self, elem, style=True, markup=None):
        """generic method for adding HTML elements

        this method handle content, style and children parsing
        @param elem(ET.Element): element to add
        @param style(bool): if True handle style attribute (CSS)
        @param markup(tuple[unicode, (unicode, None)], None): kivy markup to use
        """
        # we first add markup and CSS style
        if markup is not None:
            if isinstance(markup, basestring):
                tag, value = markup, None
            else:
                tag, value = markup
            self._addStyle(tag, value)
        style_ = 'style' in elem.attrib and style
        if style_:
            self._parseCSS(elem)

        # then content
        if elem.text:
            self._getLabel().text += escape_markup(elem.text)

        # we parse the children
        for child in elem:
            self._callParseMethod(child)

        # closing CSS style and markup
        if style_:
            self._closeCSS()
        if markup is not None:
            self._removeStyle(tag)

        # and the tail, which is regular text
        if elem.tail:
            self._getLabel().text += escape_markup(elem.tail)

    # method handling XHTML elements

    def xhtml_br(self, elem):
        label = self._getLabel()
        label.text+='\n'
        self.xhtml_generic(style=False)

    def xhtml_em(self, elem):
        self.xhtml_generic(elem, markup='i')

    def xhtml_img(self, elem):
        try:
            src = elem.attrib['src']
        except KeyError:
            log.warning(u"<img> element without src: {}".format(ET.tostring(elem)))
            return
        try:
            target_height = int(elem.get(u'height', 0))
        except ValueError:
            log.warning(u"Can't parse image height: {}".format(elem.get(u'height')))
            target_height = 0
        try:
            target_width = int(elem.get(u'width', 0))
        except ValueError:
            log.warning(u"Can't parse image width: {}".format(elem.get(u'width')))
            target_width = 0

        img = SimpleXHTMLWidgetImage(source=src, target_height=target_height, target_width=target_width)
        self.current_wid = img
        self.add_widget(img)

    def xhtml_p(self, elem):
        if isinstance(self.current_wid, Label):
            self.current_wid.text+="\n\n"
        self.xhtml_generic(elem)

    def xhtml_span(self, elem):
        self.xhtml_generic(elem)

    def xhtml_strong(self, elem):
        self.xhtml_generic(elem, markup='b')

    # methods handling CSS properties

    def css_color(self, elem, value):
        self._addStyle(u"color", css_color.parse(value))

    def css_text_decoration(self, elem, value):
        if value == u'underline':
            log.warning(u"{} not handled yet, it needs Kivy 1.9.2 to be released".format(value))
            # FIXME: activate when 1.9.2 is out
            # self._addStyle('u')
        elif value == u'line-through':
            log.warning(u"{} not handled yet, it needs Kivy 1.9.2 to be released".format(value))
            # FIXME: activate when 1.9.2 is out
            # self._addStyle('s')
        else:
            log.warning(u"unhandled text decoration: {}".format(value))
