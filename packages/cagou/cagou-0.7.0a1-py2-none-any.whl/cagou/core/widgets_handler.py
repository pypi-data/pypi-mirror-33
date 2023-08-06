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
from sat.core import exceptions
from sat_frontends.quick_frontend import quick_widgets
from kivy.graphics import Color, Ellipse
from kivy.uix.layout import Layout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.metrics import dp
from kivy import properties
from cagou import G
from cagou.core.constants import Const as C


REMOVE_WID_LIMIT = dp(10)
MIN_WIDTH = MIN_HEIGHT = dp(50)


class WHWrapper(BoxLayout):
    carousel = properties.ObjectProperty(None)
    split_size = properties.NumericProperty(dp(1))
    split_margin = properties.NumericProperty(dp(2))
    split_color = properties.ListProperty([0.8, 0.8, 0.8, 1])
    split_color_move = C.COLOR_SEC_DARK
    split_color_del = properties.ListProperty([0.8, 0.0, 0.0, 1])
    # sp stands for "split point"
    sp_size = properties.NumericProperty(dp(1))
    sp_space = properties.NumericProperty(dp(4))
    sp_zone = properties.NumericProperty(dp(30))
    _split = properties.OptionProperty('None', options=['None', 'left', 'top'])
    _split_del = properties.BooleanProperty(False)

    def __init__(self, **kwargs):
        idx = kwargs.pop('_wid_idx')
        self._wid_idx = idx
        super(WHWrapper, self).__init__(**kwargs)
        self._former_slide = None
        self.carousel.bind(current_slide=self.onSlideChange)
        self._slides_update_lock = False
        self._left_wids = set()
        self._top_wids = set()
        self._right_wids = set()
        self._bottom_wids = set()

    def __repr__(self):
        return "WHWrapper_{idx}".format(idx=self._wid_idx)

    def _main_wid(self, wid_list):
        """return main widget of a side list

        main widget is either the widget currently splitter
        or any widget if none is split
        @return (WHWrapper, None): main widget or None
            if there is not widget
        """
        if not wid_list:
            return None
        for wid in wid_list:
            if wid._split != 'None':
                return wid
        return next(iter(wid_list))

    @property
    def _left_wid(self):
        return self._main_wid(self._left_wids)

    @property
    def _top_wid(self):
        return self._main_wid(self._top_wids)

    @property
    def _right_wid(self):
        return self._main_wid(self._right_wids)

    @property
    def _bottom_wid(self):
        return self._main_wid(self._bottom_wids)

    @property
    def current_slide(self):
        return self.carousel.current_slide

    def _draw_ellipse(self):
        """draw split ellipse"""
        color = self.split_color_del if self._split_del else self.split_color_move
        try:
            self.canvas.after.remove(self.ellipse)
        except AttributeError:
            pass
        if self._split == "top":
            with self.canvas.after:
                Color(*color)
                self.ellipse = Ellipse(angle_start=90, angle_end=270,
                               pos=(self.x + self.width/2 - self.sp_zone/2,
                                    self.y + self.height - self.sp_zone/2),
                               size=(self.sp_zone, self.sp_zone))
        elif self._split == "left":
            with self.canvas.after:
                Color(*color)
                self.ellipse = Ellipse(angle_end=180,
                               pos=(self.x + -self.sp_zone/2,
                                    self.y + self.height/2 - self.sp_zone/2),
                               size = (self.sp_zone, self.sp_zone))
        else:
            raise exceptions.InternalError('unexpected split value')

    def on_touch_down(self, touch):
        """activate split if touch is on a split zone"""
        if not self.collide_point(*touch.pos):
            return
        log.debug("WIDGET IDX: {} (left: {}, top: {}, right: {}, bottom: {}), pos: {}, size: {}".format(
            self._wid_idx,
            'None' if not self._left_wids else [w._wid_idx for w in self._left_wids],
            'None' if not self._top_wids else [w._wid_idx for w in self._top_wids],
            'None' if not self._right_wids else [w._wid_idx for w in self._right_wids],
            'None' if not self._bottom_wids else [w._wid_idx for w in self._bottom_wids],
            self.pos,
            self.size,
            ))
        touch_rx, touch_ry = self.to_widget(*touch.pos, relative=True)
        if (touch_ry <= self.height and
            touch_ry >= self.height - self.split_size - self.split_margin or
            touch_ry <= self.height and
            touch_ry >= self.height - self.sp_zone and
            touch_rx >= self.width/2 - self.sp_zone/2 and
            touch_rx <= self.width/2 + self.sp_zone/2):
            # split area is touched, we activate top split mode
            self._split = "top"
            self._draw_ellipse()
        elif (touch_rx >= 0 and
              touch_rx <= self.split_size + self.split_margin or
              touch_rx >= 0 and
              touch_rx <= self.sp_zone and
              touch_ry >= self.height/2 - self.sp_zone/2 and
              touch_ry <= self.height/2 + self.sp_zone/2):
            # split area is touched, we activate left split mode
            self._split = "left"
            touch.ud['ori_width'] = self.width
            self._draw_ellipse()
        else:
            if len(self.carousel.slides) == 1:
                # we don't want swipe if there is only one slide
                return StencilView.on_touch_down(self.carousel, touch)
            else:
                return super(WHWrapper, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        """handle size change and widget creation on split"""
        if self._split == 'None':
            return super(WHWrapper, self).on_touch_move(touch)

        elif self._split == 'top':
            new_height = touch.y - self.y

            if new_height < MIN_HEIGHT:
                return

            # we must not pass the top widget/border
            if self._top_wids:
                top = next(iter(self._top_wids))
                y_limit = top.y + top.height

                if top.height <= REMOVE_WID_LIMIT:
                    # we are in remove zone, we add visual hint for that
                    if not self._split_del and self._top_wids:
                        self._split_del = True
                        self._draw_ellipse()
                else:
                    if self._split_del:
                        self._split_del = False
                        self._draw_ellipse()
            else:
                y_limit = self.y + self.height

            if touch.y >= y_limit:
                return

            # all right, we can change size
            self.height = new_height
            self.ellipse.pos = (self.ellipse.pos[0], touch.y - self.sp_zone/2)

            if not self._top_wids:
                # we are the last widget on the top
                # so we create a new widget
                new_wid = self.parent.add_widget()
                self._top_wids.add(new_wid)
                new_wid._bottom_wids.add(self)
                for w in self._right_wids:
                    new_wid._right_wids.add(w)
                    w._left_wids.add(new_wid)
                for w in self._left_wids:
                    new_wid._left_wids.add(w)
                    w._right_wids.add(new_wid)

        elif self._split == 'left':
            ori_width = touch.ud['ori_width']
            new_x = touch.x
            new_width = ori_width - (touch.x - touch.ox)

            if new_width < MIN_WIDTH:
                return

            # we must not pass the left widget/border
            if self._left_wids:
                left = next(iter(self._left_wids))
                x_limit = left.x

                if left.width <= REMOVE_WID_LIMIT:
                    # we are in remove zone, we add visual hint for that
                    if not self._split_del and self._left_wids:
                        self._split_del = True
                        self._draw_ellipse()
                else:
                    if self._split_del:
                        self._split_del = False
                        self._draw_ellipse()
            else:
                x_limit = self.x

            if new_x <= x_limit:
                return

            # all right, we can change position/size
            self.x = new_x
            self.width = new_width
            self.ellipse.pos = (touch.x - self.sp_zone/2, self.ellipse.pos[1])

            if not self._left_wids:
                # we are the last widget on the left
                # so we create a new widget
                new_wid = self.parent.add_widget()
                self._left_wids.add(new_wid)
                new_wid._right_wids.add(self)
                for w in self._top_wids:
                    new_wid._top_wids.add(w)
                    w._bottom_wids.add(new_wid)
                for w in self._bottom_wids:
                    new_wid._bottom_wids.add(w)
                    w._top_wids.add(new_wid)

        else:
            raise Exception.InternalError('invalid _split value')

    def on_touch_up(self, touch):
        if self._split == 'None':
            return super(WHWrapper, self).on_touch_up(touch)
        if self._split == 'top':
            # we remove all top widgets in delete zone,
            # and update there side widgets list
            for top in self._top_wids.copy():
                if top.height <= REMOVE_WID_LIMIT:
                    for w in top._top_wids:
                        w._bottom_wids.remove(top)
                        w._bottom_wids.update(top._bottom_wids)
                    for w in top._bottom_wids:
                        w._top_wids.remove(top)
                        w._top_wids.update(top._top_wids)
                    for w in top._left_wids:
                        w._right_wids.remove(top)
                    for w in top._right_wids:
                        w._left_wids.remove(top)
                    self.parent.remove_widget(top)
        elif self._split == 'left':
            # we remove all left widgets in delete zone,
            # and update there side widgets list
            for left in self._left_wids.copy():
                if left.width <= REMOVE_WID_LIMIT:
                    for w in left._left_wids:
                        w._right_wids.remove(left)
                        w._right_wids.update(left._right_wids)
                    for w in left._right_wids:
                        w._left_wids.remove(left)
                        w._left_wids.update(left._left_wids)
                    for w in left._top_wids:
                        w._bottom_wids.remove(left)
                    for w in left._bottom_wids:
                        w._top_wids.remove(left)
                    self.parent.remove_widget(left)
        self._split = 'None'
        self.canvas.after.remove(self.ellipse)
        del self.ellipse

    def set_widget(self, wid, index=0):
        self.carousel.add_widget(wid, index)

    def changeWidget(self, new_widget):
        """Change currently displayed widget

        slides widgets will be updated
        """
        # slides update need to be blocked to avoid the update in onSlideChange
        # which would mess the removal of current widgets
        self._slides_update_lock = True
        current = self.carousel.current_slide
        for w in self.carousel.slides:
            if w == current or w == new_widget:
                continue
            if isinstance(w, quick_widgets.QuickWidget):
                G.host.widgets.deleteWidget(w)
        self.carousel.clear_widgets()
        self.carousel.add_widget(new_widget)
        self._slides_update_lock = False
        self.updateHiddenSlides()

    def onSlideChange(self, handler, new_slide):
        if isinstance(self._former_slide, quick_widgets.QuickWidget):
            G.host.removeVisibleWidget(self._former_slide)
        self._former_slide = new_slide
        if isinstance(new_slide, quick_widgets.QuickWidget):
            G.host.addVisibleWidget(new_slide)
            self.updateHiddenSlides()

    def hiddenList(self, visible_list):
        """return widgets of same class as holded one which are hidden

        @param visible_list(list[QuickWidget]): widgets visible
        @return (iter[QuickWidget]): widgets hidden
        """
        added = [(w.targets, w.profiles) for w in visible_list]  # we want to avoid recreated widgets
        for w in G.host.widgets.getWidgets(self.current_slide.__class__, profiles=self.current_slide.profiles):
            if w in visible_list or (w.targets, w.profiles) in added:
                continue
            yield w

    def widgets_sort(self, widget):
        """method used as key to sort the widgets

        order of the widgets when changing slide is affected
        @param widget(QuickWidget): widget to sort
        @return: a value which will be used for sorting
        """
        try:
            return unicode(widget.target).lower()
        except AttributeError:
            return unicode(list(widget.targets)[0]).lower()

    def updateHiddenSlides(self):
        """adjust carousel slides according to visible widgets"""
        if self._slides_update_lock:
            return
        if not isinstance(self.carousel.current_slide, quick_widgets.QuickWidget):
            return
        # lock must be used here to avoid recursions
        self._slides_update_lock = True
        visible_list = G.host.getVisibleList(self.current_slide.__class__)
        hidden = list(self.hiddenList(visible_list))
        slides_sorted =  sorted(hidden + [self.carousel.current_slide], key=self.widgets_sort)
        to_remove = set(self.carousel.slides).difference({self.carousel.current_slide})
        for w in to_remove:
            self.carousel.remove_widget(w)
        if hidden:
            # no need to add more than two widgets (next and previous),
            # as the list will be updated on each new visible widget
            current_idx = slides_sorted.index(self.current_slide)
            try:
                next_slide = slides_sorted[current_idx+1]
            except IndexError:
                next_slide = slides_sorted[0]
            self.carousel.add_widget(G.host.getOrClone(next_slide))
            if len(hidden)>1:
                previous_slide = slides_sorted[current_idx-1]
                self.carousel.add_widget(G.host.getOrClone(previous_slide))

        self._slides_update_lock = False


class WidgetsHandlerLayout(Layout):
    count = 0

    def __init__(self, **kwargs):
        super(WidgetsHandlerLayout, self).__init__(**kwargs)
        self._layout_size = None  # size used for the last layout
        fbind = self.fbind
        update = self._trigger_layout
        fbind('children', update)
        fbind('parent', update)
        fbind('size', self.adjust_prop)
        fbind('pos', update)

    @property
    def default_widget(self):
        return G.host.default_wid['factory'](G.host.default_wid, None, None)

    def adjust_prop(self, handler, new_size):
        """Adjust children proportion

        useful when this widget is resized (e.g. when going to fullscreen)
        """
        if len(self.children) > 1:
            old_width, old_height = self._layout_size
            if not old_width or not old_height:
                # we don't want division by zero
                return self._trigger_layout(handler, new_size)
            width_factor = float(self.width) / old_width
            height_factor = float(self.height) / old_height
            for child in self.children:
                child.width *= width_factor
                child.height *= height_factor
                child.x *= width_factor
                child.y *= height_factor
        self._trigger_layout(handler, new_size)

    def do_layout(self, *args):
        self._layout_size = self.size[:]
        for child in self.children:
            # XXX: left must be calculated before right and bottom before top
            #      because they are the pos, and are used to caculate size (right and top)
            # left
            left = child._left_wid
            left_end_x = self.x-1 if left is None else left.right
            if child.x != left_end_x + 1 and child._split == "None":
                child.x = left_end_x + 1
            # right
            right = child._right_wid
            right_x = self.right + 1 if right is None else right.x
            if child.right != right_x - 1:
                child.width = right_x - child.x - 1
            # bottom
            bottom = child._bottom_wid
            if bottom is None:
                if child.y != self.y:
                    child.y = self.y
            else:
                if child.y != bottom.top + 1:
                    child.y = bottom.top + 1
            # top
            top = child._top_wid
            top_y = self.top+1 if top is None else top.y
            if child.top != top_y - 1:
                if child._split == "None":
                    child.height = top_y - child.y - 1

    def remove_widget(self, wid):
        super(WidgetsHandlerLayout, self).remove_widget(wid)
        log.debug("widget deleted ({})".format(wid._wid_idx))

    def add_widget(self, wid=None, index=0):
        WidgetsHandlerLayout.count += 1
        if wid is None:
            wid = self.default_widget
        wrapper = WHWrapper(_wid_idx=WidgetsHandlerLayout.count)
        log.debug("WHWrapper created ({})".format(wrapper._wid_idx))
        wrapper.set_widget(wid)
        super(WidgetsHandlerLayout, self).add_widget(wrapper, index)
        return wrapper


class WidgetsHandler(WidgetsHandlerLayout):

    def __init__(self, **kw):
        super(WidgetsHandler, self).__init__(**kw)
        self.wrapper = self.add_widget()

    @property
    def cagou_widget(self):
        """get holded CagouWidget"""
        return self.wrapper.current_slide
