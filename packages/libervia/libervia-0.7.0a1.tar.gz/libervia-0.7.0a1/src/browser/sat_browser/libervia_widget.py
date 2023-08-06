#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libervia: a Salut à Toi frontend
# Copyright (C) 2011-2018 Jérôme Poisson <goffi@goffi.org>

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
"""Libervia base widget"""

import pyjd  # this is dummy in pyjs
from sat.core.log import getLogger
log = getLogger(__name__)

from sat.core.i18n import _
from sat.core import exceptions
from sat_frontends.quick_frontend import quick_widgets

from pyjamas.ui.FlexTable import FlexTable
from pyjamas.ui.TabPanel import TabPanel
from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.ui.AbsolutePanel import AbsolutePanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.HTMLPanel import HTMLPanel
from pyjamas.ui.Label import Label
from pyjamas.ui.HTML import HTML
from pyjamas.ui.Button import Button
from pyjamas.ui.Widget import Widget
from pyjamas.ui.ClickListener import ClickHandler
from pyjamas.ui import HasAlignment
from pyjamas.ui.DragWidget import DragWidget
from pyjamas.ui.DropWidget import DropWidget
from pyjamas import DOM
from pyjamas import Window

import dialog
import base_menu
import base_widget
import base_panel


unicode = str  # FIXME: pyjamas workaround


# FIXME: we need to group several unrelated panels/widgets in this module because of isinstance tests and other references to classes (e.g. if we separate Drag n Drop classes in a separate module, we'll have cyclic import because of the references to LiberviaWidget in DropCell).
# TODO: use a more generic method (either use duck typing, or register classes in a generic way, without hard references), then split classes in separate modules


### Drag n Drop ###


class DragLabel(DragWidget):

    def __init__(self, text, type_, host=None):
        """Base of Drag n Drop mecanism in Libervia

        @param text: data embedded with in drag n drop operation
        @param type_: type of data that we are dragging
        @param host: if not None, the host will be use to highlight BorderWidgets
        """
        DragWidget.__init__(self)
        self.host = host
        self._text = text
        self.type_ = type_

    def onDragStart(self, event):
        dt = event.dataTransfer
        dt.setData('text/plain', "%s\n%s" % (self._text, self.type_))
        dt.setDragImage(self.getElement(), 15, 15)
        if self.host is not None:
            current_panel = self.host.tab_panel.getCurrentPanel()
            for widget in current_panel.widgets:
                if isinstance(widget, BorderWidget):
                    widget.addStyleName('borderWidgetOnDrag')

    def onDragEnd(self, event):
        if self.host is not None:
            current_panel = self.host.tab_panel.getCurrentPanel()
            for widget in current_panel.widgets:
                if isinstance(widget, BorderWidget):
                    widget.removeStyleName('borderWidgetOnDrag')


class LiberviaDragWidget(DragLabel):
    """ A DragLabel which keep the widget being dragged as class value """
    current = None  # widget currently dragged

    def __init__(self, text, type_, widget):
        DragLabel.__init__(self, text, type_, widget.host)
        self.widget = widget

    def onDragStart(self, event):
        LiberviaDragWidget.current = self.widget
        DragLabel.onDragStart(self, event)

    def onDragEnd(self, event):
        DragLabel.onDragEnd(self, event)
        LiberviaDragWidget.current = None


class DropCell(DropWidget):
    """Cell in the middle grid which replace itself with the dropped widget on DnD"""
    drop_keys = {}

    def __init__(self, host):
        DropWidget.__init__(self)
        self.host = host
        self.setStyleName('dropCell')

    @classmethod
    def addDropKey(cls, key, cb):
        """Add a association between a key and a class to create on drop.

        @param key: key to be associated (e.g. "CONTACT", "CHAT")
        @param cb: a callable (either a class or method) returning a
            LiberviaWidget instance
        """
        DropCell.drop_keys[key] = cb

    def onDragEnter(self, event):
        if self == LiberviaDragWidget.current:
            return
        self.addStyleName('dragover')
        DOM.eventPreventDefault(event)

    def onDragLeave(self, event):
        if event.clientX <= self.getAbsoluteLeft() or event.clientY <= self.getAbsoluteTop() or\
            event.clientX >= self.getAbsoluteLeft() + self.getOffsetWidth() - 1 or event.clientY >= self.getAbsoluteTop() + self.getOffsetHeight() - 1:
            # We check that we are inside widget's box, and we don't remove the style in this case because
            # if the mouse is over a widget inside the DropWidget, if will leave the DropWidget, and we
            # don't want that
            self.removeStyleName('dragover')

    def onDragOver(self, event):
        DOM.eventPreventDefault(event)

    def _getCellAndRow(self, grid, event):
        """Return cell and row index where the event is occuring"""
        cell = grid.getEventTargetCell(event)
        row = DOM.getParent(cell)
        return (row.rowIndex, cell.cellIndex)

    def onDrop(self, event):
        """
        @raise NoLiberviaWidgetException: something else than a LiberviaWidget
            has been returned by the callback.
        """
        self.removeStyleName('dragover')
        DOM.eventPreventDefault(event)
        item, item_type = eventGetData(event)
        if item_type == "WIDGET":
            if not LiberviaDragWidget.current:
                log.error("No widget registered in LiberviaDragWidget !")
                return
            _new_panel = LiberviaDragWidget.current
            if self == _new_panel:  # We can't drop on ourself
                return
            # we need to remove the widget from the panel as it will be inserted elsewhere
            widgets_panel = _new_panel.getParent(WidgetsPanel, expect=True)
            wid_row = widgets_panel.getWidgetCoords(_new_panel)[0]
            row_wids = widgets_panel.getLiberviaRowWidgets(wid_row)
            if len(row_wids) == 1 and wid_row == widgets_panel.getWidgetCoords(self)[0]:
                # the dropped widget is the only one in the same row
                # as the target widget (self), we don't do anything
                return
            widgets_panel.removeWidget(_new_panel)
        elif item_type in self.drop_keys:
            _new_panel = self.drop_keys[item_type](self.host, item)
            if not isinstance(_new_panel, LiberviaWidget):
                raise base_widget.NoLiberviaWidgetException
        else:
            log.warning("unmanaged item type")
            return
        if isinstance(self, LiberviaWidget):
            # self.host.unregisterWidget(self) # FIXME
            self.onQuit()
            if not isinstance(_new_panel, LiberviaWidget):
                log.warning("droping an object which is not a class of LiberviaWidget")
        _flextable = self.getParent()
        _widgetspanel = _flextable.getParent().getParent()
        row_idx, cell_idx = self._getCellAndRow(_flextable, event)
        if self.host.getSelected() == self:
            self.host.setSelected(None)
        _widgetspanel.changeWidget(row_idx, cell_idx, _new_panel)
        """_unempty_panels = filter(lambda wid:not isinstance(wid,EmptyWidget),list(_flextable))
        _width = 90/float(len(_unempty_panels) or 1)
        #now we resize all the cell of the column
        for panel in _unempty_panels:
            td_elt = panel.getElement().parentNode
            DOM.setStyleAttribute(td_elt, "width", "%s%%" % _width)"""
        if isinstance(self, quick_widgets.QuickWidget):
            self.host.widgets.deleteWidget(self)


class EmptyWidget(DropCell, SimplePanel):
    """Empty dropable panel"""

    def __init__(self, host):
        SimplePanel.__init__(self)
        DropCell.__init__(self, host)
        #self.setWidget(HTML(''))
        self.setSize('100%', '100%')


class BorderWidget(EmptyWidget):
    def __init__(self, host):
        EmptyWidget.__init__(self, host)
        self.addStyleName('borderPanel')


class LeftBorderWidget(BorderWidget):
    def __init__(self, host):
        BorderWidget.__init__(self, host)
        self.addStyleName('leftBorderWidget')


class RightBorderWidget(BorderWidget):
    def __init__(self, host):
        BorderWidget.__init__(self, host)
        self.addStyleName('rightBorderWidget')


class BottomBorderWidget(BorderWidget):
    def __init__(self, host):
        BorderWidget.__init__(self, host)
        self.addStyleName('bottomBorderWidget')


class DropTab(Label, DropWidget):

    def __init__(self, tab_panel, text):
        Label.__init__(self, text)
        DropWidget.__init__(self, tab_panel)
        self.tab_panel = tab_panel
        self.setStyleName('dropCell')
        self.setWordWrap(False)

    def _getIndex(self):
        """ get current index of the DropTab """
        # XXX: awful hack, but seems the only way to get index
        return self.tab_panel.tabBar.panel.getWidgetIndex(self.getParent().getParent()) - 1

    def onDragEnter(self, event):
        #if self == LiberviaDragWidget.current:
        #    return
        self.parent.addStyleName('dragover')
        DOM.eventPreventDefault(event)

    def onDragLeave(self, event):
        self.parent.removeStyleName('dragover')

    def onDragOver(self, event):
        DOM.eventPreventDefault(event)

    def onDrop(self, event):
        DOM.eventPreventDefault(event)
        self.parent.removeStyleName('dragover')
        if self._getIndex() == self.tab_panel.tabBar.getSelectedTab():
            # the widget comes from the same tab, so nothing to do, we let it there
            return

        item, item_type = eventGetData(event)
        if item_type == "WIDGET":
            if not LiberviaDragWidget.current:
                log.error("No widget registered in LiberviaDragWidget !")
                return
            _new_panel = LiberviaDragWidget.current
        elif item_type in DropCell.drop_keys:
            pass  # create the widget when we are sure there's a tab for it
        else:
            log.warning("unmanaged item type")
            return

        # XXX: when needed, new tab creation must be done exactly here to not mess up with LiberviaDragWidget.onDragEnd
        try:
            widgets_panel = self.tab_panel.getWidget(self._getIndex())
        except IndexError:  # widgets panel doesn't exist, e.g. user dropped in "+" tab
            widgets_panel = self.tab_panel.addWidgetsTab(None)
            if widgets_panel is None:  # user cancelled
                return

        if item_type == "WIDGET":
            _new_panel.getParent(WidgetsPanel, expect=True).removeWidget(_new_panel)
        else:
            _new_panel = DropCell.drop_keys[item_type](self.tab_panel.host, item)

        widgets_panel.addWidget(_new_panel)


### Libervia Widget ###


class WidgetHeader(AbsolutePanel, LiberviaDragWidget):

    def __init__(self, parent, host, title, info=None):
        """
        @param parent (LiberviaWidget): LiberWidget instance
        @param host (SatWebFrontend): SatWebFrontend instance
        @param title (Label, HTML): text widget instance
        @param info (Widget): text widget instance
        """
        AbsolutePanel.__init__(self)
        self.add(title)
        if info:
            # FIXME: temporary design to display the info near the menu
            button_group_wrapper = HorizontalPanel()
            button_group_wrapper.add(info)
        else:
            button_group_wrapper = SimplePanel()
        button_group_wrapper.setStyleName('widgetHeader_buttonsWrapper')
        button_group = base_widget.WidgetMenuBar(parent, host)
        button_group.addItem('<img src="media/icons/misc/settings.png"/>', True, base_menu.SimpleCmd(parent.onSetting))
        button_group.addItem('<img src="media/icons/misc/close.png"/>', True, base_menu.SimpleCmd(parent.onClose))
        button_group_wrapper.add(button_group)
        self.add(button_group_wrapper)
        self.addStyleName('widgetHeader')
        LiberviaDragWidget.__init__(self, "", "WIDGET", parent)


class LiberviaWidget(DropCell, VerticalPanel, ClickHandler):
    """Libervia's widget which can replace itself with a dropped widget on DnD"""

    def __init__(self, host, title='', info=None, selectable=False, plugin_menu_context=None):
        """Init the widget

        @param host (SatWebFrontend): SatWebFrontend instance
        @param title (unicode): title shown in the header of the widget
        @param info (unicode): info shown in the header of the widget
        @param selectable (bool): True is widget can be selected by user
        @param plugin_menu_context (iterable): contexts of menus to have (list of C.MENU_* constant)
        """
        VerticalPanel.__init__(self)
        DropCell.__init__(self, host)
        ClickHandler.__init__(self)
        self._selectable = selectable
        self._plugin_menu_context = [] if plugin_menu_context is None else plugin_menu_context
        self._title_id = HTMLPanel.createUniqueId()
        self._setting_button_id = HTMLPanel.createUniqueId()
        self._close_button_id = HTMLPanel.createUniqueId()
        self._title = Label(title)
        self._title.setStyleName('widgetHeader_title')
        if info is not None:
            self._info = HTML(info)
            self._info.setStyleName('widgetHeader_info')
        else:
            self._info = None
        header = WidgetHeader(self, host, self._title, self._info)
        self.add(header)
        self.setSize('100%', '100%')
        self.addStyleName('widget')
        if self._selectable:
            self.addClickListener(self)

    @property
    def plugin_menu_context(self):
        return self._plugin_menu_context

    def getDebugName(self):
        return "%s (%s)" % (self, self._title.getText())

    def getParent(self, class_=None, expect=True):
        """Return the closest ancestor of the specified class.

        Note: this method overrides pyjamas.ui.Widget.getParent

        @param class_: class of the ancestor to look for or None to return the first parent
        @param expect: set to True if the parent is expected (raise an error if not found)
        @return: the parent/ancestor or None if it has not been found
        @raise exceptions.InternalError: expect is True and no parent is found
        """
        current = Widget.getParent(self)
        if class_ is None:
            return current  # this is the default behavior
        while current is not None and not isinstance(current, class_):
            current = Widget.getParent(current)
        if current is None and expect:
            raise exceptions.InternalError("Can't find parent %s for %s" % (class_, self))
        return current

    def onClick(self, sender):
        self.host.setSelected(self)

    def onClose(self, sender):
        """ Called when the close button is pushed """
        widgets_panel = self.getParent(WidgetsPanel, expect=True)
        widgets_panel.removeWidget(self)
        self.onQuit()
        self.host.widgets.deleteWidget(self)

    def onQuit(self):
        """ Called when the widget is actually ending """
        pass

    def refresh(self):
        """This can be overwritten by a child class to refresh the display when,
        instead of creating a new one, an existing widget is found and reused.
        """
        pass

    def onSetting(self, sender):
        widpanel = self.getParent(WidgetsPanel, expect=True)
        row, col = widpanel.getIndex(self)
        body = VerticalPanel()

        # colspan & rowspan
        colspan = widpanel.getColSpan(row, col)
        rowspan = widpanel.getRowSpan(row, col)

        def onColSpanChange(value):
            widpanel.setColSpan(row, col, value)

        def onRowSpanChange(value):
            widpanel.setRowSpan(row, col, value)
        colspan_setter = dialog.IntSetter("Columns span", colspan)
        colspan_setter.addValueChangeListener(onColSpanChange)
        colspan_setter.setWidth('100%')
        rowspan_setter = dialog.IntSetter("Rows span", rowspan)
        rowspan_setter.addValueChangeListener(onRowSpanChange)
        rowspan_setter.setWidth('100%')
        body.add(colspan_setter)
        body.add(rowspan_setter)

        # size
        width_str = self.getWidth()
        if width_str.endswith('px'):
            width = int(width_str[:-2])
        else:
            width = 0
        height_str = self.getHeight()
        if height_str.endswith('px'):
            height = int(height_str[:-2])
        else:
            height = 0

        def onWidthChange(value):
            if not value:
                self.setWidth('100%')
            else:
                self.setWidth('%dpx' % value)

        def onHeightChange(value):
            if not value:
                self.setHeight('100%')
            else:
                self.setHeight('%dpx' % value)
        width_setter = dialog.IntSetter("width (0=auto)", width)
        width_setter.addValueChangeListener(onWidthChange)
        width_setter.setWidth('100%')
        height_setter = dialog.IntSetter("height (0=auto)", height)
        height_setter.addValueChangeListener(onHeightChange)
        height_setter.setHeight('100%')
        body.add(width_setter)
        body.add(height_setter)

        # reset
        def onReset(sender):
            colspan_setter.setValue(1)
            rowspan_setter.setValue(1)
            width_setter.setValue(0)
            height_setter.setValue(0)

        reset_bt = Button("Reset", onReset)
        body.add(reset_bt)
        body.setCellHorizontalAlignment(reset_bt, HasAlignment.ALIGN_CENTER)

        _dialog = dialog.GenericDialog("Widget setting", body)
        _dialog.show()

    def setTitle(self, text):
        """change the title in the header of the widget
        @param text: text of the new title"""
        self._title.setText(text)

    def setHeaderInfo(self, text):
        """change the info in the header of the widget
        @param text: text of the new title"""
        try:
            self._info.setHTML(text)
        except TypeError:
            log.error("LiberviaWidget.setInfo: info widget has not been initialized!")

    def isSelectable(self):
        return self._selectable

    def setSelectable(self, selectable):
        if not self._selectable:
            try:
                self.removeClickListener(self)
            except ValueError:
                pass
        if self.selectable and not self in self._clickListeners:
            self.addClickListener(self)
        self._selectable = selectable

    def getWarningData(self):
        """ Return exposition warning level when this widget is selected and something is sent to it
        This method should be overriden by children
        @return: tuple (warning level type/HTML msg). Type can be one of:
            - PUBLIC
            - GROUP
            - ONE2ONE
            - MISC
            - NONE
        """
        if not self._selectable:
            log.error("getWarningLevel must not be called for an unselectable widget")
            raise Exception
        # TODO: cleaner warning types (more general constants)
        return ("NONE", None)

    def setWidget(self, widget, scrollable=True):
        """Set the widget that will be in the body of the LiberviaWidget
        @param widget: widget to put in the body
        @param scrollable: if true, the widget will be in a ScrollPanelWrapper"""
        if scrollable:
            _scrollpanelwrapper = base_panel.ScrollPanelWrapper()
            _scrollpanelwrapper.setStyleName('widgetBody')
            _scrollpanelwrapper.setWidget(widget)
            body_wid = _scrollpanelwrapper
        else:
            body_wid = widget
        self.add(body_wid)
        self.setCellHeight(body_wid, '100%')

    def doDetachChildren(self):
        # We need to force the use of a panel subclass method here,
        # for the same reason as doAttachChildren
        VerticalPanel.doDetachChildren(self)

    def doAttachChildren(self):
        # We need to force the use of a panel subclass method here, else
        # the event will not propagate to children
        VerticalPanel.doAttachChildren(self)


# XXX: WidgetsPanel and MainTabPanel are both here to avoir cyclic import


class WidgetsPanel(base_panel.ScrollPanelWrapper):
    """The panel wanaging the widgets indide a tab"""

    def __init__(self, host, locked=False):
        """

        @param host (SatWebFrontend): host instance
        @param locked (bool): If True, the tab containing self will not be
            removed when there are no more widget inside self. If False, the
            tab will be removed with self's last widget.
        """
        base_panel.ScrollPanelWrapper.__init__(self)
        self.setSize('100%', '100%')
        self.host = host
        self.locked = locked
        self.selected = None
        self.flextable = FlexTable()
        self.flextable.setSize('100%', '100%')
        self.setWidget(self.flextable)
        self.setStyleName('widgetsPanel')
        _bottom = BottomBorderWidget(self.host)
        self.flextable.setWidget(0, 0, _bottom)  # There will be always an Empty widget on the last row,
                                                 # dropping a widget there will add a new row
        td_elt = _bottom.getElement().parentNode
        DOM.setStyleAttribute(td_elt, "height", "1px")  # needed so the cell adapt to the size of the border (specially in webkit)
        self._max_cols = 1  # give the maximum number of columns in a raw

    @property
    def widgets(self):
        return iter(self.flextable)

    def isLocked(self):
        return self.locked

    def changeWidget(self, row, col, wid):
        """Change the widget in the given location, add row or columns when necessary"""
        log.debug(u"changing widget: %s %s %s" % (wid.getDebugName(), row, col))
        last_row = max(0, self.flextable.getRowCount() - 1)
        # try:  # FIXME: except without exception specified !
        prev_wid = self.flextable.getWidget(row, col)
        # except:
        #     log.error("Trying to change an unexisting widget !")
        #     return

        cellFormatter = self.flextable.getFlexCellFormatter()

        if isinstance(prev_wid, BorderWidget):
            # We are on a border, we must create a row and/or columns
            prev_wid.removeStyleName('dragover')

            if isinstance(prev_wid, BottomBorderWidget):
                # We are on the bottom border, we create a new row
                self.flextable.insertRow(last_row)
                self.flextable.setWidget(last_row, 0, LeftBorderWidget(self.host))
                self.flextable.setWidget(last_row, 1, wid)
                self.flextable.setWidget(last_row, 2, RightBorderWidget(self.host))
                cellFormatter.setHorizontalAlignment(last_row, 2, HasAlignment.ALIGN_RIGHT)
                row = last_row

            elif isinstance(prev_wid, LeftBorderWidget):
                if col != 0:
                    log.error("LeftBorderWidget must be on the first column !")
                    return
                self.flextable.insertCell(row, col + 1)
                self.flextable.setWidget(row, 1, wid)

            elif isinstance(prev_wid, RightBorderWidget):
                if col != self.flextable.getCellCount(row) - 1:
                    log.error("RightBorderWidget must be on the last column !")
                    return
                self.flextable.insertCell(row, col)
                self.flextable.setWidget(row, col, wid)

        else:
            prev_wid.removeFromParent()
            self.flextable.setWidget(row, col, wid)

        _max_cols = max(self._max_cols, self.flextable.getCellCount(row))
        if _max_cols != self._max_cols:
            self._max_cols = _max_cols
            self._sizesAdjust()

    def _sizesAdjust(self):
        cellFormatter = self.flextable.getFlexCellFormatter()
        width = 100.0 / max(1, self._max_cols - 2)  # we don't count the borders

        for row_idx in xrange(self.flextable.getRowCount()):
            for col_idx in xrange(self.flextable.getCellCount(row_idx)):
                _widget = self.flextable.getWidget(row_idx, col_idx)
                if _widget and not isinstance(_widget, BorderWidget):
                    td_elt = _widget.getElement().parentNode
                    DOM.setStyleAttribute(td_elt, "width", "%.2f%%" % width)

        last_row = max(0, self.flextable.getRowCount() - 1)
        cellFormatter.setColSpan(last_row, 0, self._max_cols)

    def addWidget(self, wid):
        """Add a widget to a new cell on the next to last row"""
        last_row = max(0, self.flextable.getRowCount() - 1)
        log.debug(u"putting widget %s at %d, %d" % (wid.getDebugName(), last_row, 0))
        self.changeWidget(last_row, 0, wid)

    def removeWidget(self, wid):
        """Remove a widget and the cell where it is"""
        _row, _col = self.flextable.getIndex(wid)
        self.flextable.remove(wid)
        self.flextable.removeCell(_row, _col)
        if not self.getLiberviaRowWidgets(_row):  # we have no more widgets, we remove the row
            self.flextable.removeRow(_row)
        _max_cols = 1
        for row_idx in xrange(self.flextable.getRowCount()):
            _max_cols = max(_max_cols, self.flextable.getCellCount(row_idx))
        if _max_cols != self._max_cols:
            self._max_cols = _max_cols
            self._sizesAdjust()
        current = self

        blank_page = self.getLiberviaWidgetsCount() == 0  # do we still have widgets on the page ?

        if blank_page and not self.isLocked():
            # we now notice the MainTabPanel that the WidgetsPanel is empty and need to be removed
            while current is not None:
                if isinstance(current, MainTabPanel):
                    current.onWidgetPanelRemove(self)
                    return
                current = current.getParent()
            log.error("no MainTabPanel found !")

    def getWidgetCoords(self, wid):
        return self.flextable.getIndex(wid)

    def getLiberviaRowWidgets(self, row):
        """ Return all the LiberviaWidget in the row """
        return [wid for wid in self.getRowWidgets(row) if isinstance(wid, LiberviaWidget)]

    def getRowWidgets(self, row):
        """ Return all the widgets in the row """
        widgets = []
        cols = self.flextable.getCellCount(row)
        for col in xrange(cols):
            widgets.append(self.flextable.getWidget(row, col))
        return widgets

    def getLiberviaWidgetsCount(self):
        """ Get count of contained widgets """
        return len([wid for wid in self.flextable if isinstance(wid, LiberviaWidget)])

    def getIndex(self, wid):
        return self.flextable.getIndex(wid)

    def getColSpan(self, row, col):
        cellFormatter = self.flextable.getFlexCellFormatter()
        return cellFormatter.getColSpan(row, col)

    def setColSpan(self, row, col, value):
        cellFormatter = self.flextable.getFlexCellFormatter()
        return cellFormatter.setColSpan(row, col, value)

    def getRowSpan(self, row, col):
        cellFormatter = self.flextable.getFlexCellFormatter()
        return cellFormatter.getRowSpan(row, col)

    def setRowSpan(self, row, col, value):
        cellFormatter = self.flextable.getFlexCellFormatter()
        return cellFormatter.setRowSpan(row, col, value)


class MainTabPanel(TabPanel, ClickHandler):
    """The panel managing the tabs"""

    def __init__(self, host):
        TabPanel.__init__(self, FloatingTab=True)
        ClickHandler.__init__(self)
        self.host = host
        self.setStyleName('liberviaTabPanel')
        self.tabBar.addTab(DropTab(self, u'✚'), asHTML=False)
        self.tabBar.setVisible(False)  # set to True when profile is logged
        self.tabBar.addStyleDependentName('oneTab')

    def onTabSelected(self, sender, tabIndex):
        if tabIndex < self.getWidgetCount():
            TabPanel.onTabSelected(self, sender, tabIndex)
            self.host.selected_widget = self.getCurrentPanel().selected
            return
        # user clicked the "+" tab
        self.addWidgetsTab(None, select=True)

    def getCurrentPanel(self):
        """ Get the panel of the currently selected tab

        @return: WidgetsPanel
        """
        return self.deck.visibleWidget

    def addTab(self, widget, label, select=False):
        """Create a new tab for the given widget.

        @param widget (Widget): widget to associate to the tab
        @param label (unicode): label of the tab
        @param select (bool): True to select the added tab
        """
        TabPanel.add(self, widget, DropTab(self, label), False)
        if self.getWidgetCount() > 1:
            self.tabBar.removeStyleDependentName('oneTab')
            self.host.resize()
        if select:
            self.selectTab(self.getWidgetCount() - 1)

    def addWidgetsTab(self, label, select=False, locked=False):
        """Create a new tab for containing LiberviaWidgets.

        @param label (unicode): label of the tab (None or '' for user prompt)
        @param select (bool): True to select the added tab
        @param locked (bool): If True, the tab will not be removed when there
            are no more widget inside. If False, the tab will be removed with
            the last widget.
        @return: WidgetsPanel
        """
        widgets_panel = WidgetsPanel(self.host, locked=locked)

        if not label:
            default_label = _(u'new tab')
            try:
                label = Window.prompt(_(u'Name of the new tab'), default_label)
                if not label:  # empty label or user pressed "cancel"
                    return None
            except:  # this happens when the user prevents the page to open the prompt dialog
                label = default_label

        self.addTab(widgets_panel, label, select)
        return widgets_panel

    def onWidgetPanelRemove(self, panel):
        """ Called when a child WidgetsPanel is empty and need to be removed """
        widget_index = self.getWidgetIndex(panel)
        self.remove(panel)
        widgets_count = self.getWidgetCount()
        if widgets_count == 1:
            self.tabBar.addStyleDependentName('oneTab')
            self.host.resize()
        self.selectTab(widget_index if widget_index < widgets_count else widgets_count - 1)


def eventGetData(event):
    """Retrieve the event data.

    @param event(EventObject)
    @return tuple: (event_text, event_type)
    """
    dt = event.dataTransfer
    # 'text', 'text/plain', and 'Text' are equivalent.
    try:
        item, item_type = dt.getData("text/plain").split('\n')  # Workaround for webkit, only text/plain seems to be managed
        if item_type and item_type[-1] == '\0':  # Workaround for what looks like a pyjamas bug: the \0 should not be there, and
            item_type = item_type[:-1]           # .strip('\0') and .replace('\0','') don't work. TODO: check this and fill a bug report
        # item_type = dt.getData("type")
        log.debug(u"event data: %s (type %s)" % (item, item_type))
    except:
        log.debug("event data not found")
        item = '&nbsp;'
        item_type = None
    return item, item_type
