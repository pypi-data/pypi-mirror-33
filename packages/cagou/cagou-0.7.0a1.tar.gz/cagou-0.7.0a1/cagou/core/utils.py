#!/usr//bin/env python2
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

"""misc utils/behaviors"""


from kivy.animation import Animation


class FilterBehavior(object):
    """class to handle items filtering with animation"""

    def __init__(self, *args, **kwargs):
        super(FilterBehavior, self).__init__(*args, **kwargs)
        self._filter_last = u''
        self._filter_anim = Animation(width = 0,
                                      height = 0,
                                      opacity = 0,
                                      d = 0.5)

    def do_filter(self, children, text, get_child_text, width_cb, height_cb,
                  continue_tests=None):
        """filter the children

        filtered children will have a animation to set width, height and opacity to 0
        @param children(kivy.uix.widget.Widget): widgets to filter
        @param text(unicode): filter text (if this text is not present in a child,
            the child is filtered out)
        @param get_child_text(callable): must retrieve child text
            child is used as sole argument
        @param width_cb(callable, int, None): method to retrieve width when opened
            child is used as sole argument, int can be used instead of callable
        @param height_cb(callable, int, None): method to retrieve height when opened
            child is used as sole argument, int can be used instead of callable
        @param continue_tests(list[callable]): list of test to skip the item
            all callables take child as sole argument.
            if any of the callable return True, the child is skipped (i.e. not filtered)
        """
        text = text.strip().lower()
        filtering = len(text)>len(self._filter_last)
        self._filter_last = text
        for child in self.layout.children:
            if continue_tests is not None and any([t(child) for t in continue_tests]):
                continue
            if text in get_child_text(child).lower():
                self._filter_anim.cancel(child)
                for key, method in (('width', width_cb),
                                    ('height', height_cb),
                                    ('opacity', lambda c: 1)):
                    try:
                        setattr(child, key, method(child))
                    except TypeError:
                        # method is not a callable, must be an int
                        setattr(child, key, method)
            elif (filtering
                  and child.opacity > 0
                  and not self._filter_anim.have_properties_to_animate(child)):
                self._filter_anim.start(child)
