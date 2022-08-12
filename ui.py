#!/usr/bin/env python




"""

Copyright 2018, SunSpec Alliance

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import textwrap
from builtins import input
from builtins import range


import os
import sys
import multiprocessing
import argparse
import traceback
from importlib.machinery import SourceFileLoader as imp
import importlib
import datetime
import time
import struct
import hashlib
import glob
import multiprocessing
import wx
import wx.adv
import xlsxwriter

import numpy
import wxmplot
import shutil


import app as svp
import result as rslt
import script
import svptreectrl as treectrl

'''
import sunspec.core.util as util
import sunspec.core.device as device_module

import argparse
import xdrlib
import visa
import openpyxl
'''

wx_app = None

VERSION = '2.0.0'

APP_NAME = 'SVP'
APP_LABEL = 'System Validation Platform'
APP_PROG_NAME = 'sunssvp'
APP_STDOUT = APP_PROG_NAME + '.log'

OP_ADD_SUITE = 1
OP_ADD_TEST = 2
OP_ADD_WORKING_DIR = 3
OP_DELETE = 12
OP_EDIT = 4
OP_EXIT = 5
OP_MOVE_DOWN = 6
OP_MOVE_UP = 7
OP_NEW_DIR = 8
OP_NEW_SUITE = 9
OP_NEW_TEST = 10
OP_REMOVE = 11
OP_RUN = 13
OP_RESCAN = 14
OP_MOVE = 15
OP_DELETE_ALL = 16
OP_ABOUT = 17
OP_COPY = 18
OP_OPEN = 19
OP_RESULT = 20
OP_PKG = 30


OP_ID_MIN = 1
OP_ID_MAX = 20

TEXT_WRAP = 250

ITEM_OPEN_PREFIX = 'o_'
ITEM_CLOSED_PREFIX = 'c_'
ITEM_SUITE_MEMBERS = '__suite_members__'

run_context_list = []

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

images_path = resource_path("images")

'''
def get_default_icon(filename):
    "Retrieve the default icon of a filename"
    (root, extension) = os.path.splitext(filename)
    if extension:
        value_name = _winreg.QueryValue(_winreg.HKEY_CLASSES_ROOT, extension)
        try:
            value_name = _winreg.QueryValue(_winreg.HKEY_CLASSES_ROOT, extension)
        except _winreg.error:
            value_name = None
    else:
        value_name = None
    if value_name:
         try:
             icon = _winreg.QueryValue(_winreg.HKEY_CLASSES_ROOT, value_name + "\\DefaultIcon")
         except _winreg.error:
            icon = None
    else:
        icon = None
    return icon
'''

'''
def get_wx_icon(exe, index):
    ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
    ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
    large, small = win32gui.ExtractIconEx(exe, index)
    if len(small) == 0:
        return False
    win32gui.DestroyIcon(large[0])
    hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
    icon_bmp = win32ui.CreateBitmap()
    icon_bmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
    hdc = hdc.CreateCompatibleDC()
    hdc.SelectObject(icon_bmp)
    hdc.DrawIcon((0,0), small[0]) #draw the icon before getting bits
    icon_info = icon_bmp.GetInfo()
    icon_buffer = icon_bmp.GetBitmapBits(True)
    icon = PILImage.frombuffer('RGB', (icon_info['bmWidth'], icon_info['bmHeight']), icon_buffer, 'raw', 'BGRX', 0, 1)
    win32gui.DestroyIcon(small[0])
    return icon
'''

def pil_to_image(pil, alpha=True):
    """Convert PIL Image to wx.Image."""
    if alpha:
        image = wx.EmptyImage(*pil.size)
        image.SetData( pil.convert( "RGB").tostring() )
        image.SetAlphaData(pil.convert("RGBA").tostring()[3::4])
    else:
        image = wx.EmptyImage(pil.size[0], pil.size[1])
        new_image = pil.convert('RGB')
        data = new_image.tostring()
        image.SetData(data)
    return image

'''
def get_icon_image(filename):
    try:
        icon_path = get_default_icon(filename)
        if '.exe,' in icon_path:
            params = icon_path.split(',')
            if len(params) == 2:
                index = int(params[1])
                pil = get_wx_icon(params[0], index)
                if pil:
                    image = pil_to_image(pil)
                    return image
    except Exception:
        pass
'''

image_list = None
images = {}
result_to_image = {}
image_open = None
image_closed = None

def init_image_list():
    global image_list, images, result_to_image, image_open, image_closed
    image_list = wx.ImageList(16, 16, True)

    image = wx.Image(os.path.join(images_path, 'working_dir.gif'))
    images['working_dir'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'suites.gif'))
    images['suites'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'suite_dir.gif'))
    images['suite_dir'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'suite.gif'))
    images['suite'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'tests.gif'))
    images['tests'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'test_dir.gif'))
    images['test_dir'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'test.gif'))
    images['test'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'scripts.gif'))
    images['scripts'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'script_dir.gif'))
    images['script_dir'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'script.gif'))
    images['script'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'result_dir.png'))
    images['results'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'result_dir.png'))
    images['result_dir'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'result.png'))
    images['result'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'result.png'))
    images['file'] = image_list.Add(wx.Bitmap(image))
    image_open = wx.Image(os.path.join(images_path, 'open_64s.gif'))
    images['open'] = image_list.Add(wx.Bitmap(image_open))
    image_closed = wx.Image(os.path.join(images_path, 'closed_64s.gif'))
    images['closed'] = image_list.Add(wx.Bitmap(image_closed))

    image = wx.Image(os.path.join(images_path, 'complete.gif'))
    images['complete'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'pass.gif'))
    images['pass'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'error.gif'))
    images['error'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'running.gif'))
    images['running'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'stopped.gif'))
    images['stopped'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'none.png'))
    images['none'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'pause_64.gif'))
    images['pause_1'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'pause_96.gif'))
    images['pause_2'] = image_list.Add(wx.Bitmap(image))

    image = wx.Image(os.path.join(images_path, 'result.png'))
    images['csv'] = image_list.Add(wx.Bitmap(image))
    image = wx.Image(os.path.join(images_path, 'excel.png'))
    images['xlsx'] = image_list.Add(wx.Bitmap(image))

    result_to_image = {
        rslt.RESULT_TYPE_RESULT: images['result'],
        rslt.RESULT_TYPE_SUITE: images['suite'],
        rslt.RESULT_TYPE_TEST: images['test'],
        rslt.RESULT_TYPE_SCRIPT: images['script'],
        rslt.RESULT_TYPE_FILE: images['result'],
        'Running': images['running'],
        'Stopped': images['stopped'],
        'Complete': images['complete'],
        'Pass': images['pass'],
        'Fail': images['error'],
        'none': images['none']
    }

    '''
    # add .csv file image
    icon = get_icon_image('file.csv')
    if icon is not None:
        bm = wx.Bitmap(icon)
    else:
        bm = images['file']
    images['csv'] = image_list.Add(bm)

    # add .xlsx file image
    icon = get_icon_image('file.xlsx')
    if icon is not None:
        bm = wx.Bitmap(icon)
    else:
        bm = images['file']
    images['xlsx'] = image_list.Add(bm)
    '''

def result_image(result):
    image = None
    if result.type == rslt.RESULT_TYPE_FILE:
        if result.filename:
            name, ext = os.path.splitext(result.filename)
            if ext == '.csv':
                image = images['csv']
            elif ext == '.xlsx':
                image = images['xlsx']
    if image is None:
        image = result_to_image.get(result.type, -1)
    return image

class UIError(Exception):
    pass

def verify_delete(name):
    pass

def makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise


class EditSuiteDialog(wx.Dialog):
    def __init__(self, parent, entity):
        wx.Dialog.__init__(self, None, -1, 'Edit Suite - %s' % (entity.name), size=(900,500),
                           style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.entity = entity
        self.suite = None
        self.result = None
        self.members = []
        self.edit_params = {}
        self.params = {}
        self.closed_panels = {}
        self.globals = True

        self.working_dir = os.path.join(entity.working_dir_path())
        path = entity.path()
        path.append(entity.name + svp.SUITE_EXT)
        filename = os.path.join(*path)
        self.suite = svp.Suite(filename=filename)
        self.suite.merge_param_defs(self.working_dir)

        self.open_image = wx.Image(os.path.join(images_path, 'open_64s.gif'), wx.BITMAP_TYPE_GIF)
        self.closed_image = wx.Image(os.path.join(images_path, 'closed_64s.gif'), wx.BITMAP_TYPE_GIF)

        window = wx.ScrolledWindow(self, -1)
        window.SetScrollbars(1, 1, 2000, 2000)
        window.SetDoubleBuffered(True)

        self.members_label = wx.Panel(window, -1)
        open_bitmap = wx.StaticBitmap(parent=self.members_label, name=ITEM_OPEN_PREFIX + ITEM_SUITE_MEMBERS,
                                      bitmap=wx.Bitmap(self.open_image), pos=(0,0))
        open_bitmap.Bind(wx.EVT_LEFT_DOWN, self.toggle_group_panel)
        closed_bitmap = wx.StaticBitmap(parent=self.members_label, name=ITEM_CLOSED_PREFIX + ITEM_SUITE_MEMBERS,
                                        bitmap=wx.Bitmap(self.closed_image), pos=(0,2))
        closed_bitmap.Bind(wx.EVT_LEFT_DOWN, self.toggle_group_panel)
        open_bitmap.group_toggle = closed_bitmap
        closed_bitmap.group_toggle = open_bitmap
        text = wx.StaticText(self.members_label, -1, 'Suite Members', pos=(20,2))
        font = text.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetFont(font)
        text.Wrap(TEXT_WRAP)

        panel_name = ITEM_SUITE_MEMBERS
        self.members_panel = wx.Panel(window, name=panel_name, size=(0,250))
        self.members_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.members_panel.SetSizer(self.members_panel_sizer)
        self.members_box = wx.StaticBox(self.members_panel)
        members_box_sizer = wx.StaticBoxSizer(self.members_box, wx.HORIZONTAL)
        self.members_panel_sizer.Add(members_box_sizer, 1, wx.EXPAND)
        self.members_label.suite_group_panel = self.members_panel

        self.members_tree = treectrl.CustomTreeCtrl(self.members_panel, agwStyle=(wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|
                                                                      wx.TR_NO_LINES|wx.TR_HAS_VARIABLE_ROW_HEIGHT))
        self.members_button_up = wx.Button(self.members_panel, id=-1, label='Move Up')
        self.members_button_up.Bind(wx.EVT_BUTTON, self.OnUp)
        self.members_button_down = wx.Button(self.members_panel, id=-1, label='Move Down')
        self.members_button_down.Bind(wx.EVT_BUTTON, self.OnDown)
        self.members_button_remove = wx.Button(self.members_panel, id=-1, label='Remove')
        self.members_button_remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        self.members_button_add = wx.Button(self.members_panel, id=-1, label='Add')
        self.members_button_add.Bind(wx.EVT_BUTTON, self.OnAdd)
        self.members_tree.AssignImageList(entity.entity_tree.image_list)
        self.members_tree.SetBackgroundColour('white')
        self.members_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)

        self.members_avail_tree = treectrl.CustomTreeCtrl(self.members_panel,
                                                          agwStyle=(wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_NO_LINES))
        self.members_avail_tree.AssignImageList(entity.entity_tree.image_list)
        self.members_avail_tree.SetBackgroundColour('white')
        self.members_avail_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnAvailSelectionChanged)
        self.members_avail_tree.Bind(wx.EVT_LEFT_DOWN, self.OnAvailTreeCtrlButtonDown)
        self.members_avail_tree.Bind(wx.EVT_MIDDLE_DOWN, self.OnAvailTreeCtrlButtonDown)
        self.members_avail_tree.Bind(wx.EVT_RIGHT_DOWN, self.OnAvailTreeCtrlButtonDown)

        self.members_button_up.Disable()
        self.members_button_down.Disable()
        self.members_button_remove.Disable()
        self.members_button_add.Disable()

        members_root = self.members_tree.AddRoot('root')
        for m in self.suite.members:
            name, ext = os.path.splitext(m)
            if ext == svp.SUITE_EXT:
                image = entity.entity_tree.images['suite']
            elif ext == svp.TEST_EXT:
                image = entity.entity_tree.images['test']
            else:
                ### log
                continue

            item = self.members_tree.AppendItem(members_root, name, image=image)
            self.members_tree.SetItemPyData(item, m)

        item = self.members_avail_tree.AddRoot('root')
        dir_entry = entity.get_dir(svp.SUITES_DIR)
        if dir_entry:
            suites_item = self.add_entry(item, dir_entry)
            suites_item.Expand()
        dir_entry = entity.get_dir(svp.TESTS_DIR)
        if dir_entry:
            tests_item = self.add_entry(item, dir_entry)
            tests_item.Expand()

        ok = wx.Button(self, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

        members_sizer = wx.BoxSizer(wx.VERTICAL)
        members_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        members_button_sizer.Add(self.members_button_up, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        members_button_sizer.Add(self.members_button_down, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        members_button_sizer.Add(self.members_button_remove, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        members_sizer.Add(self.members_tree, 1, wx.EXPAND|wx.RIGHT, 15)
        members_sizer.Add(members_button_sizer, 0, wx.ALIGN_CENTER)
        members_avail_sizer = wx.BoxSizer(wx.VERTICAL)
        members_avail_sizer.Add(self.members_avail_tree, 1, wx.EXPAND)
        members_avail_sizer.Add(self.members_button_add, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        members_box_sizer.Add(members_sizer, 1, wx.EXPAND|wx.LEFT|wx.TOP, 10)
        members_box_sizer.Add(members_avail_sizer, 1, wx.EXPAND|wx.RIGHT|wx.TOP, 10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        window_sizer = wx.BoxSizer(wx.VERTICAL)
        params_panel = wx.Panel(window)

        self.params_panel = params_panel
        params_panel.panel_sizer = wx.GridBagSizer(hgap=30, vgap=0)
        params_panel.panel_sizer.SetEmptyCellSize((0,0))
        params_panel.SetSizer(params_panel.panel_sizer)
        self.render(params_panel)

        btns = wx.StdDialogButtonSizer()
        btns.AddButton(ok)
        btns.AddButton(cancel)
        btns.Realize()
        sizer.Add(window, 1, wx.EXPAND|wx.LEFT|wx.TOP, 15)
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL, 10)
        window_sizer.Add(self.members_label, 0, wx.EXPAND|wx.ALIGN_LEFT|wx.TOP)
        window_sizer.Add(self.members_panel, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, 20)
        window_sizer.Add(params_panel, 1, wx.EXPAND)
        window.SetSizer(window_sizer)
        self.SetSizer(sizer)
        self.Layout()

    def render(self, params_panel):
        # save edit params during render
        self.params = {}
        self.update_params()
        params_panel.panel_sizer.Clear(delete_windows=True)
        params_panel.Hide()
        self.edit_params = {}
        row = 0
        row = self.render_globals(params_panel, row=row)
        if self.suite.globals is True:
            self.render_group(params_panel, self.suite.param_defs, row)
        self.params = {}
        params_panel.Show()
        self.Layout()

    def show_group(self, parent, show):
        start_row = parent.group_start_row
        end_row = parent.group_end_row
        if end_row > start_row:
            name = parent.GetName()
            row = start_row + 1
            while row <= end_row:
                sizer_item = self.params_panel.panel_sizer.FindItemAtPosition((row, 0))
                if sizer_item is not None:
                    item = sizer_item.GetWindow()
                    if item is not None:
                        try:
                            first_row = item.group_start_row
                            last_row = item.group_end_row
                        except Exception:
                            first_row = None
                        if show and first_row:
                            item.Show()
                            closed = self.closed_panels.get(item.GetName())
                            group_show = not closed
                            self.show_group(item, group_show)
                            row = last_row + 1
                        else:
                            for col in range(0, 3):
                                sizer_item = self.params_panel.panel_sizer.FindItemAtPosition((row, col))
                                if sizer_item is not None:
                                    if show:
                                        sizer_item.GetWindow().Show()
                                        try:
                                            del self.closed_panels[name]
                                        except:
                                            pass
                                    else:
                                        sizer_item.GetWindow().Hide()
                                        self.closed_panels[name] = True
                            row += 1

    def toggle_group_panel(self, evt):
        item_toggle = evt.GetEventObject()
        item = item_toggle.group_toggle
        item_toggle.Hide()
        item.Show()
        parent = item.GetParent()
        item_panel = parent.suite_group_panel
        item_name = item.GetName()
        if item_name[:2] == ITEM_OPEN_PREFIX:
            item_panel.Show()
        else:
            item_panel.Hide()

        self.Layout()

    def toggle_group(self, evt):
        item_toggle = evt.GetEventObject()
        item = item_toggle.group_toggle
        item_toggle.Hide()
        item.Show()
        item_name = item.GetName()
        show = False
        if item_name[:2] == ITEM_OPEN_PREFIX:
            show = True
        parent = item.GetParent()
        self.show_group(parent, show)

        self.Layout()

    def render_group(self, params_panel, group, row=0, pad=0, show=True):
        if group is not None:
            closed = self.closed_panels.get(group.qname)
            show = not closed
            if script.param_is_active(self.suite.param_defs, group.qname, self.param_value) is not None:
                label_panel = None
                if group.name != script.SCRIPT_PARAM_ROOT:
                    label_panel = wx.Panel(params_panel, -1, name=group.qname)
                    open_bitmap = wx.StaticBitmap(parent=label_panel, name=ITEM_OPEN_PREFIX + group.qname,
                                                  bitmap=wx.Bitmap(self.open_image), pos=(0,0))
                    open_bitmap.Bind(wx.EVT_LEFT_DOWN, self.toggle_group)
                    closed_bitmap = wx.StaticBitmap(parent=label_panel, name=ITEM_CLOSED_PREFIX + group.qname,
                                                    bitmap=wx.Bitmap(self.closed_image), pos=(0,2))
                    closed_bitmap.Bind(wx.EVT_LEFT_DOWN, self.toggle_group)
                    open_bitmap.group_toggle = closed_bitmap
                    closed_bitmap.group_toggle = open_bitmap
                    if self.closed_panels.get(group.qname):
                        open_bitmap.Hide()
                    else:
                        closed_bitmap.Hide()
                    label_panel.group_start_row = row

                    text = wx.StaticText(label_panel, -1, group.label, pos=(20, 2))
                    font = text.GetFont()
                    font.SetWeight(wx.FONTWEIGHT_BOLD)
                    text.SetFont(font)
                    # text.Wrap(TEXT_WRAP)

                    params_panel.panel_sizer.Add(label_panel, pos=(row, 0), border=pad, flag=wx.LEFT)
                    row += 1

                    pad += 20

                index_count = group.index_count
                index_start = group.index_start
                if index_count is not None:
                    if type(index_count) == str:
                        index_count = self.param_value(index_count)
                    if type(index_start) == str:
                        index_start = self.param_value(index_start)
                    if index_count is not None and index_start is not None:
                        for i in range(index_start, index_start + index_count):
                            for param in group.params:
                                edit_param = self.edit_params.get(param.qname)
                                if edit_param is None:
                                    edit_param = EditParam(param)
                                    edit_param.index_count = index_count
                                    edit_param.index_start = index_start
                                    self.edit_params[param.qname] = edit_param
                                row = self.render_param(params_panel, param, index=i, row=row, pad=pad)
                else:
                    for param in group.params:
                        index_count = param.index_count
                        index_start = param.index_start
                        if index_count is not None:
                            if type(index_count) == str:
                                index_count = self.param_value(index_count)
                            if type(index_start) == str:
                                index_start = self.param_value(index_start)
                            if index_count is not None and index_start is not None:
                                edit_param = self.edit_params.get(param.qname)
                                if edit_param is None:
                                    edit_param = EditParam(param)
                                    edit_param.index_count = index_count
                                    edit_param.index_start = index_start
                                    self.edit_params[param.qname] = edit_param
                                for i in range(index_start, index_start + index_count):
                                    row = self.render_param(params_panel, param, index=i, row=row, pad=pad)
                        else:
                            row = self.render_param(params_panel, param, index=None, row=row, pad=pad)

                '''
                for g in group.param_groups:
                    row = self.render_group(params_panel, g, row=row, pad=pad)
                if group.index_count is not None:
                    for i in xrange(group.index_start, group.index_count + 1):
                        for param in group.params:
                            row = self.render_param(params_panel, param, index=i, row=row, pad=pad)
                else:
                    for param in group.params:
                        if param.index_count is not None:
                            for i in xrange(param.index_start, param.index_count + 1):
                                row = self.render_param(params_panel, param, index=i, row=row, pad=pad)
                        else:
                            row = self.render_param(params_panel, param, index=None, row=row, pad=pad)
                '''

                for g in group.param_groups:
                    row = self.render_group(params_panel, g, row=row, pad=pad)

                if label_panel is not None:
                    label_panel.group_end_row = row - 1
                    self.show_group(label_panel, show)
        return row

    def render_globals(self, params_panel, row=0, pad=0):
        if self.suite.globals is True:
            current_value = 'Enabled'
        else:
            current_value = 'Disabled'
        text = wx.StaticText(params_panel, -1, 'Global Parameters')
        text.Wrap(TEXT_WRAP)
        params_panel.panel_sizer.Add(text, pos=(row, 0), border=pad, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        choices = ['Disabled', 'Enabled']
        self.globals_entry = wx.Choice(params_panel, -1, name='globals', choices=choices)
        entry_index = self.globals_entry.FindString(current_value)
        if entry_index != wx.NOT_FOUND:
            self.globals_entry.SetSelection(entry_index)
        self.globals_entry.Bind(wx.EVT_CHOICE, self.OnChangeGlobals)
        params_panel.panel_sizer.Add(self.globals_entry, pos=(row, 1), border=0, flag=wx.LEFT)
        row += 1
        return row

    def render_param(self, params_panel, param, index=None, row=0, pad=0):
        if script.param_is_active(self.suite.param_defs, param.qname, self.param_value) is not None:
            if index is not None:
                edit_param = self.edit_params.get(param.qname)
                if edit_param is None:
                    edit_param = EditParam(param)
                    self.edit_params[param.qname] = edit_param
                label = '%s %d' % (param.label, index)
                current_value = self.param_value(param.qname, index=index)
            else:
                label = param.label
                current_value = self.param_value(param.qname)
                edit_param = EditParam(param)
                self.edit_params[param.qname] = edit_param

            text = wx.StaticText(params_panel, -1, label)
            text.Wrap(TEXT_WRAP)
            if param.desc is not None:
                text.SetToolTip(wx.ToolTip(param.desc))
            params_panel.panel_sizer.Add(text, pos=(row, 0), border=pad, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
            if param.values:
                choices = [str(v) for v in param.values]
                entry = wx.Choice(params_panel, -1, name=param.qname, choices=choices)
                entry_index = entry.FindString(str(current_value))
                if entry_index != wx.NOT_FOUND:
                    entry.SetSelection(entry_index)
                entry.Bind(wx.EVT_CHOICE, self.OnChange)
                edit_param.param_value = edit_param.param_choice_get
                params_panel.panel_sizer.Add(entry, pos=(row, 1), border=0, flag=wx.LEFT)
            else:
                if param.ptype == script.PTYPE_DIR:
                    entry = wx.TextCtrl(params_panel, -1, str(current_value), size=(350, -1))
                    params_panel.panel_sizer.Add(entry, pos=(row, 1), border=0, flag=wx.LEFT)
                    button = wx.Button(params_panel, -1, label='Browse...', name=param.qname)
                    button.Bind(wx.EVT_BUTTON, self.OnDir)
                    params_panel.panel_sizer.Add(button, pos=(row, 2), border=0, flag=wx.LEFT | wx.EXPAND)
                elif param.ptype == script.PTYPE_FILE:
                    entry = wx.TextCtrl(params_panel, -1, str(current_value), size=(350, -1))
                    params_panel.panel_sizer.Add(entry, pos=(row, 1), border=0, flag=wx.LEFT)
                    button = wx.Button(params_panel, -1, label='Browse...', name=param.qname)
                    button.Bind(wx.EVT_BUTTON, self.OnFile)
                    params_panel.panel_sizer.Add(button, pos=(row, 2), border=0, flag=wx.LEFT | wx.EXPAND)
                else:
                    entry = wx.TextCtrl(params_panel, -1, str(current_value), name=param.qname, size=(150, -1))
                    params_panel.panel_sizer.Add(entry, pos=(row, 1), border=0, flag=wx.LEFT)

            row += 1
            edit_param.param_entry(entry, index)
            if param.referenced:
                pass # bind to change, does it work for choice too?
            # value.Bind(wx.EVT_CHOICE, self.OnChoice)
        return row

    def param_value(self, name, param_defs=None, param_value=None, index=None):
        value = None
        p = self.edit_params.get(name)
        if p is not None:
            if index is not None:
                if p.value is None:
                    p.value = self.params.get(name)
                    if p.value is None:
                        p.value = self.suite.params.get(name)
                        if p.value is None and self.suite.param_defs is not None:
                            p.value = self.suite.param_defs.param_value(name, param_defs=self.suite.param_defs,
                                                                        param_value=self.param_value)
            return p.param_value(index=index)
        else:
            value = self.params.get(name)
            if value is not None:
                return value
            value = self.suite.params.get(name)
            if value is not None:
                return value
            if self.suite.param_defs is not None:
                value = self.suite.param_defs.param_value(name, param_defs=self.suite.param_defs,
                                                          param_value=self.param_value)
        return value

    def update_suite_members(self):
        self.suite.members = []
        tree = self.members_tree
        item, cookie = tree.GetFirstChild(tree.GetRootItem())
        while item is not None:
            name = tree.GetItemPyData(item)
            if name is not None:
                self.suite.members.append(name)
            item = tree.GetNextSibling(item)
        self.suite.merge_param_defs(self.working_dir)

    def update_params(self):
        self.params = {}
        for name, p in list(self.edit_params.items()):
            if script.param_is_active(self.suite.param_defs, name, self.param_value) is not None:
                if len(p.indexed_entries) > 0:
                    value = {'index_count': p.param.index_count, 'index_start': p.param.index_start}
                    for key, v in list(p.indexed_entries.items()):
                        value[key] = p.param_value(index=key)
                    self.params[name] = value
                else:
                    self.params[name] = p.param_value()
        self.globals = self.suite.globals

    def OnChange(self, evt):
        ctrl = evt.GetEventObject()
        p = self.edit_params.get(ctrl.GetName())
        if p is not None:
            '''
            if p.param.referenced is True:
                # re-render params
                self.render(self.params_panel)
                # discard saved param values after re-rendering
                self.params = {}
            '''
            # re-render params
            self.render(self.params_panel)
            # discard saved param values after re-rendering
            self.params = {}

    def OnChangeGlobals(self, evt):
        ctrl = evt.GetEventObject()
        index = ctrl.GetCurrentSelection()
        if index == 0:
            self.suite.globals = False
        else:
            self.suite.globals = True

        self.render(self.params_panel)
        # discard saved param values after re-rendering
        self.params = {}

    def OnDir(self, evt):
        button = evt.GetEventObject()
        path = wx.DirSelector()
        if path:
            p = self.edit_params.get(button.GetName())
            if p is not None:
                p.entry.SetValue(path)

    def OnFile(self, evt):
        button = evt.GetEventObject()
        path = wx.FileSelector()
        if path:
            p = self.edit_params.get(button.GetName())
            if p is not None:
                p.entry.SetValue(path)

    def OnOk(self, evt):
        # update members
        tree = self.members_tree
        item, cookie = tree.GetFirstChild(tree.GetRootItem())
        while item is not None:
            name = tree.GetItemPyData(item)
            if name is not None:
                self.members.append(name)
            item = tree.GetNextSibling(item)
        # update params
        self.update_params()
        self.result = True
        self.Destroy()

    def OnCancel(self, evt):
        self.Destroy()

    def OnAdd(self, evt):
        item = self.members_avail_tree.GetSelection()
        if item is not None:
            entity = self.members_avail_tree.GetItemPyData(item)

        if entity is not None:
            try:
                entity_type = type(entity)
                if entity_type == SuiteEntry:
                    filename = self.entity.absolute_filename()
                    add_filename = entity.absolute_filename()
                    suite = svp.Suite(filename=add_filename)
                    if suite.contains_suite(self.entity.working_dir_path(),filename):
                        raise UIError('Adding suite will create a circular reference')
                elif entity_type != TestEntry:
                    ### log
                    return
                name = entity.relative_name()

                item = self.members_tree.AppendItem(self.members_tree.GetRootItem(), name, image=entity.image)
                self.members_tree.SetItemPyData(item, name + entity.ext)
                self.update_suite_members()
                self.render(self.params_panel)
            except Exception as e:
                wx.MessageBox('Error: %s' % str(e), caption='Add error',
                              style=wx.OK | wx.ICON_ERROR)

    def move(self, item, next):
        if next is not None:
            new = self.members_tree.InsertItem(
                self.members_tree.GetItemParent(item),
                next,
                self.members_tree.GetItemText(item),
                image=self.members_tree.GetItemImage(item),
                selImage=self.members_tree.GetItemImage(item, wx.TreeItemIcon_Selected))
            if self.members_tree.GetItemPyData(item):
                self.members_tree.SetItemPyData(new, self.members_tree.GetItemPyData(item))
        else:
            new = self.members_tree.PrependItem(
                self.members_tree.GetItemParent(item),
                self.members_tree.GetItemText(item),
                image=self.members_tree.GetItemImage(item),
                selImage=self.members_tree.GetItemImage(item, wx.TreeItemIcon_Selected))
            if self.members_tree.GetItemPyData(item):
                self.members_tree.SetItemPyData(new, self.members_tree.GetItemPyData(item))
        self.members_tree.Delete(item)
        self.members_tree.SelectItem(new)

    def OnUp(self, evt):
        item = self.members_tree.GetSelection()
        parent = self.members_tree.GetRootItem()
        if item is not None:
            if item != parent:
                prev = self.members_tree.GetPrevSibling(item)
                if prev is not None:
                    next = self.members_tree.GetPrevSibling(prev)
                    self.move(item, next)

    def OnDown(self, evt):
        item = self.members_tree.GetSelection()
        parent = self.members_tree.GetRootItem()
        if item is not None:
            if item != parent:
                next = self.members_tree.GetNextSibling(item)
                if next is not None:
                    self.move(item, next)

    def OnRemove(self, evt):
        item = self.members_tree.GetSelection()
        if item is not None:
            try:
                next = self.members_tree.GetNextSibling(item)
                if next is None:
                    next = self.members_tree.GetPrevSibling(item)
                self.members_tree.Delete(item)
                self.members_button_remove.Disable()
                if next is not None:
                    self.members_tree.SelectItem(next)
                self.update_suite_members()
                self.render(self.params_panel)
            except Exception as e:
                raise UIError('Error creating member path: %s' % str(e))

    def add_entry(self, parent, entity):
        item = None
        if parent is None:
            item = self.members_avail_tree.AddRoot(entity.name, image=entity.image)
        else:
            add = True
            if type(entity) == SuiteEntry:
                filename = self.entity.absolute_filename()
                add_filename = entity.absolute_filename()
                suite = svp.Suite(filename=add_filename)
                add = not suite.contains_suite(self.entity.working_dir_path(),filename)
            if add:
                item = self.members_avail_tree.AppendItem(parent, entity.name, image=entity.image)
        if item is not None:
            self.members_avail_tree.SetItemPyData(item, entity)
            for e in entity.entries:
                self.add_entry(item, e)
            return item

    def OnSelectionChanged(self, event):
        item = self.members_tree.GetSelection()
        parent = self.members_tree.GetRootItem()
        if item is not None:
            if item == parent:
                self.members_button_up.Disable()
                self.members_button_down.Disable()
                self.members_button_remove.Disable()
                return

            try:
                self.members_button_remove.Enable()
                if item != self.members_tree.GetFirstChild(parent)[0]:
                    self.members_button_up.Enable()
                else:
                    self.members_button_up.Disable()
                if item != self.members_tree.GetLastChild(parent):
                    self.members_button_down.Enable()
                else:
                    self.members_button_down.Disable()
            except Exception as e:
                raise UIError('Error creating member path: %s' % str(e))

    def OnAvailSelectionChanged(self, event):
        item = self.members_avail_tree.GetSelection()
        if item is not None:
            entity = self.members_avail_tree.GetItemPyData(item)

        if entity is not None:
            try:
                path = entity.path()
                path.append(entity.name)
                if type(entity) == SuiteEntry:
                    i = path.index(svp.SUITES_DIR)
                elif type(entity) == TestEntry:
                    i = path.index(svp.TESTS_DIR)
                else:
                    self.members_button_add.Disable()
                    # entity.entity_tree.Unselect()
                    entity.entity_tree.SelectItem(entity.entity_tree.GetRootItem())
                    return
                self.members_button_add.Enable()
            except Exception as e:
                raise UIError('Error creating member path: %s' % str(e))

    def OnAvailTreeCtrlButtonDown(self, event):
        item, flags = self.members_avail_tree.HitTest(event.GetPosition())
        accept = True
        if flags & (wx.TREE_HITTEST_ONITEMLABEL|wx.TREE_HITTEST_ONITEMICON):
            if item is not None:
                entity = self.members_avail_tree.GetItemPyData(item)
                if type(entity) != SuiteEntry and type(entity) != TestEntry:
                    accept = False
        if accept:
            event.Skip()


class EditParam(object):
    def param_choice_get(self, index=None):
        if self.entry is not None:
            selection = self.entry.GetStringSelection()
            if selection:
                return self.param.vtype(selection)

    def param_text_get(self, index=None):
        entry = self.entry
        if index is not None:
            entry = self.indexed_entries.get(index)
            if entry is None:
                if type(self.value) == dict:
                    value = self.value.get(index)
                    if value is None:
                        value = script.param_default.get(self.param.vtype)
                    return value
        if entry is not None:
            return self.param.vtype(entry.GetValue())

    def param_entry(self, entry, index=None):
        if index is not None:
            self.indexed_entries[index] = entry
        else:
            self.entry = entry

    def __init__(self, param, entry=None):
        self.param = param
        self.value = None
        self.entry = entry
        self.index_count = None
        self.index_start = None
        self.indexed_entries = {}
        self.param_value = self.param_text_get


class EditTestDialog(wx.Dialog):
    def __init__(self, parent, entity, test_script):
        wx.Dialog.__init__(self, None, -1, 'Edit Test - %s' % (test_script.config.name), size=(900,500),
                           style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.parent = parent
        self.entity = entity
        self.test_script = test_script
        self.edit_params = {}
        self.params = {}
        self.closed_panels = {}
        self.result = None

        self.open_image = wx.Image(os.path.join(images_path, 'open_64s.gif'), wx.BITMAP_TYPE_GIF)
        self.closed_image = wx.Image(os.path.join(images_path, 'closed_64s.gif'), wx.BITMAP_TYPE_GIF)

        ok = wx.Button(self, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
        # ifile = wx.Button(self, id=wx.ID_HELP, label='Import')
        # self.Bind(wx.EVT_BUTTON, self.OnImport, id=wx.ID_HELP)

        sizer = wx.BoxSizer(wx.VERTICAL)
        btns = wx.StdDialogButtonSizer()
        btns.AddButton(ok)
        btns.AddButton(cancel)
        # btns.AddButton(ifile)
        btns.Realize()

        self.params_panel = wx.ScrolledWindow(self, -1)
        params_panel = self.params_panel
        params_panel.SetScrollbars(1, 1, 2000, 2000)
        params_panel.SetDoubleBuffered(True)
        params_panel.panel_sizer = wx.GridBagSizer(hgap=30, vgap=0)
        params_panel.panel_sizer.SetEmptyCellSize((0,0))
        # params_panel.SetBackgroundColour('white')

        sizer.Add(params_panel, 1, wx.EXPAND|wx.LEFT|wx.TOP, 15)
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL, 15)
        self.SetSizer(sizer)
        params_panel.SetSizer(params_panel.panel_sizer)

        self.render(params_panel)

    def render(self, params_panel):
        # save edit params during render
        #### self.params = {}
        self.update_params()
        params_panel.panel_sizer.Clear(delete_windows=True)
        params_panel.Hide()
        self.edit_params = {}
        row = 1

        text = wx.StaticText(params_panel, -1, 'Script')
        font = text.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetFont(font)
        text.Wrap(TEXT_WRAP)
        params_panel.panel_sizer.Add(text, pos=(row, 0), border=20, flag=wx.LEFT)
        text = wx.StaticText(params_panel, -1, self.test_script.config.script)
        text.Wrap(TEXT_WRAP)
        params_panel.panel_sizer.Add(text, pos=(row, 1), flag=wx.LEFT)
        row += 1

        self.render_group(params_panel, self.test_script.info.param_defs, row)
        #### self.params = {}
        params_panel.Show()
        self.Layout()

    def show_group(self, parent, show):
        start_row = parent.group_start_row
        end_row = parent.group_end_row
        if end_row > start_row:
            name = parent.GetName()
            row = start_row + 1
            while row <= end_row:
                sizer_item = self.params_panel.panel_sizer.FindItemAtPosition((row, 0))
                if sizer_item is not None:
                    item = sizer_item.GetWindow()
                    if item is not None:
                        try:
                            first_row = item.group_start_row
                            last_row = item.group_end_row
                        except Exception:
                            first_row = None
                        if show and first_row:
                            item.Show()
                            closed = self.closed_panels.get(item.GetName())
                            group_show = not closed
                            self.show_group(item, group_show)
                            row = last_row + 1
                        else:
                            for col in range(0, 3):
                                sizer_item = self.params_panel.panel_sizer.FindItemAtPosition((row, col))
                                if sizer_item is not None:
                                    if show:
                                        sizer_item.GetWindow().Show()
                                        try:
                                            del self.closed_panels[name]
                                        except:
                                            pass
                                    else:
                                        sizer_item.GetWindow().Hide()
                                        self.closed_panels[name] = True
                            row += 1

    def toggle_group_panel(self, evt):
        item_toggle = evt.GetEventObject()
        item = item_toggle.group_toggle
        item_toggle.Hide()
        item.Show()
        parent = item.GetParent()
        item_panel = parent.suite_group_panel
        item_name = item.GetName()
        if item_name[:2] == ITEM_OPEN_PREFIX:
            item_panel.Show()
        else:
            item_panel.Hide()

        self.Layout()

    def toggle_group(self, evt):
        item_toggle = evt.GetEventObject()
        item = item_toggle.group_toggle
        item_toggle.Hide()
        item.Show()
        item_name = item.GetName()
        show = False
        if item_name[:2] == ITEM_OPEN_PREFIX:
            show = True
        parent = item.GetParent()
        self.show_group(parent, show)

        self.Layout()

    def render_group(self, params_panel, group, row=0, pad=0, show=True):
        closed = self.closed_panels.get(group.qname)
        show = not closed
        if script.param_is_active(self.test_script.param_defs, group.qname, self.param_value) is not None:
            label_panel = None
            if group.name != script.SCRIPT_PARAM_ROOT:
                label_panel = wx.Panel(params_panel, -1, name=group.qname)
                open_bitmap = wx.StaticBitmap(parent=label_panel, name=ITEM_OPEN_PREFIX + group.qname,
                                              bitmap=wx.Bitmap(self.open_image), pos=(0,0))
                open_bitmap.Bind(wx.EVT_LEFT_DOWN, self.toggle_group)
                closed_bitmap = wx.StaticBitmap(parent=label_panel, name=ITEM_CLOSED_PREFIX + group.qname,
                                                bitmap=wx.Bitmap(self.closed_image), pos=(0,2))
                closed_bitmap.Bind(wx.EVT_LEFT_DOWN, self.toggle_group)
                open_bitmap.group_toggle = closed_bitmap
                closed_bitmap.group_toggle = open_bitmap
                if self.closed_panels.get(group.qname):
                    open_bitmap.Hide()
                else:
                    closed_bitmap.Hide()
                label_panel.group_start_row = row

                text = wx.StaticText(label_panel, -1, group.label, pos=(20, 2))
                font = text.GetFont()
                font.SetWeight(wx.FONTWEIGHT_BOLD)
                text.SetFont(font)
                # text.Wrap(TEXT_WRAP)

                params_panel.panel_sizer.Add(label_panel, pos=(row, 0), border=pad, flag=wx.LEFT)
                row += 1

                pad += 20

            index_count = group.index_count
            index_start = group.index_start
            if index_count is not None:
                if type(index_count) == str:
                    index_count = self.param_value(index_count)
                if type(index_start) == str:
                    index_start = self.param_value(index_start)
                if index_count is not None and index_start is not None:
                    for i in range(index_start, index_start + index_count):
                        for param in group.params:
                            edit_param = self.edit_params.get(param.qname)
                            if edit_param is None:
                                edit_param = EditParam(param)
                                edit_param.index_count = index_count
                                edit_param.index_start = index_start
                                self.edit_params[param.qname] = edit_param
                            row = self.render_param(params_panel, param, index=i, row=row, pad=pad)
            else:
                for param in group.params:
                    index_count = param.index_count
                    index_start = param.index_start
                    if index_count is not None:
                        if type(index_count) == str:
                            index_count = self.param_value(index_count)
                        if type(index_start) == str:
                            index_start = self.param_value(index_start)
                        if index_count is not None and index_start is not None:
                            edit_param = self.edit_params.get(param.qname)
                            if edit_param is None:
                                edit_param = EditParam(param)
                                edit_param.index_count = index_count
                                edit_param.index_start = index_start
                                self.edit_params[param.qname] = edit_param
                            for i in range(index_start, index_start + index_count):
                                row = self.render_param(params_panel, param, index=i, row=row, pad=pad)
                    else:
                        row = self.render_param(params_panel, param, index=None, row=row, pad=pad)

            for g in group.param_groups:
                row = self.render_group(params_panel, g, row=row, pad=pad)

            if label_panel is not None:
                label_panel.group_end_row = row - 1
                self.show_group(label_panel, show)
        return row

    def render_param(self, params_panel, param, index=None, row=0, pad=0):
        if script.param_is_active(self.test_script.param_defs, param.qname, self.param_value) is not None:
            if index is not None:
                edit_param = self.edit_params.get(param.qname)
                if edit_param is None:
                    edit_param = EditParam(param)
                    self.edit_params[param.qname] = edit_param
                label = '%s %d' % (param.label, index)
                current_value = self.param_value(param.qname, index)
            else:
                label = param.label
                current_value = self.param_value(param.qname)
                edit_param = EditParam(param)
                self.edit_params[param.qname] = edit_param

            text = wx.StaticText(params_panel, -1, label)
            text.Wrap(TEXT_WRAP)
            if param.desc is not None:
                text.SetToolTip(wx.ToolTip(param.desc))
            params_panel.panel_sizer.Add(text, pos=(row, 0), border=pad, flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
            if param.values:
                choices = [str(v) for v in param.values]
                entry = wx.Choice(params_panel, -1, name=param.qname, choices=choices)
                entry_index = entry.FindString(str(current_value))
                if entry_index != wx.NOT_FOUND:
                    entry.SetSelection(entry_index)
                entry.Bind(wx.EVT_CHOICE, self.OnChange)
                edit_param.param_value = edit_param.param_choice_get
                params_panel.panel_sizer.Add(entry, pos=(row, 1), border=0, flag=wx.LEFT)
            else:
                if param.ptype == script.PTYPE_DIR:
                    entry = wx.TextCtrl(params_panel, -1, str(current_value), size=(350, -1))
                    params_panel.panel_sizer.Add(entry, pos=(row, 1), border=0, flag=wx.LEFT)
                    button = wx.Button(params_panel, -1, label='Browse...', name=param.qname)
                    button.Bind(wx.EVT_BUTTON, self.OnDir)
                    params_panel.panel_sizer.Add(button, pos=(row, 2), border=0, flag=wx.LEFT | wx.EXPAND)
                elif param.ptype == script.PTYPE_FILE:
                    entry = wx.TextCtrl(params_panel, -1, str(current_value), size=(350, -1))
                    params_panel.panel_sizer.Add(entry, pos=(row, 1), border=0, flag=wx.LEFT)
                    button = wx.Button(params_panel, -1, label='Browse...', name=param.qname)
                    button.Bind(wx.EVT_BUTTON, self.OnFile)
                    params_panel.panel_sizer.Add(button, pos=(row, 2), border=0, flag=wx.LEFT | wx.EXPAND)
                else:
                    entry = wx.TextCtrl(params_panel, -1, str(current_value), name=param.qname, size=(150, -1))
                    params_panel.panel_sizer.Add(entry, pos=(row, 1), border=0, flag=wx.LEFT)

            row += 1
            edit_param.param_entry(entry, index)
            if param.referenced:
                pass # bind to change, does it work for choice too?
            # value.Bind(wx.EVT_CHOICE, self.OnChoice)
        return row

    def param_value(self, name, index=None):
        p = self.edit_params.get(name)
        if p is not None:
            if index is not None:
                if p.value is None:
                    value = self.params.get(name)
                    if value is not None:
                        p.value = value
                    else:
                        p.value = self.test_script.param_value(name, param_defs=self.test_script.param_defs,
                                                               param_value=self.param_value)
            return p.param_value(index=index)
        else:
            value = self.params.get(name)
            if value is not None:
                return value
            return self.test_script.param_value(name, param_defs=self.test_script.param_defs,
                                                param_value=self.param_value)

    def OnChange(self, evt):
        ctrl = evt.GetEventObject()
        p = self.edit_params.get(ctrl.GetName())
        if p is not None:
            '''
            if p.param.referenced is True:
                # re-render params
                self.render(self.params_panel)
                # discard saved param values after re-rendering
                self.params = {}
            '''
            ### rerender always for now
            # re-render params
            self.render(self.params_panel)
            # discard saved param values after re-rendering
            #### self.params = {}

    def OnDir(self, evt):
        button = evt.GetEventObject()
        path = wx.DirSelector()
        if path:
            p = self.edit_params.get(button.GetName())
            if p is not None:
                p.entry.SetValue(path)

    def OnFile(self, evt):
        button = evt.GetEventObject()
        path = wx.FileSelector()
        if path:
            p = self.edit_params.get(button.GetName())
            if p is not None:
                p.entry.SetValue(path)

    def OnImport(self, evt):
        button = evt.GetEventObject()
        path = wx.FileSelector()
        if path:
            p = self.edit_params.get(button.GetName())
            if p is not None:
                pass

    def OnOk(self, evt):
        self.update_params()
        self.result = True
        self.Destroy()

    def OnCancel(self, evt):
        self.Destroy()

    def update_params(self):
        #### self.params = {}
        for name, p in list(self.edit_params.items()):
            if script.param_is_active(self.test_script.param_defs, name, self.param_value) is not None:
                if p.index_count is not None:
                    value = {'index_count': p.index_count, 'index_start': p.index_start}
                    for key, v in list(p.indexed_entries.items()):
                        value[key] = p.param_value(index=key)
                    self.params[name] = value
                else:
                    self.params[name] = p.param_value()

class NewTestDialog(wx.Dialog):
    def __init__(self, parent, entity_tree, entity, title='New Test'):
        wx.Dialog.__init__(self, None, -1, title, size=(400, 400))
        self.test_name = ''
        self.script_path = ''
        self.tree = treectrl.CustomTreeCtrl(self, agwStyle=(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_NO_LINES))
        self.tree.AssignImageList(entity_tree.image_list)
        self.tree.SetBackgroundColour('white')
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)
        self.tree.Bind(wx.EVT_LEFT_DOWN, self.OnTreeCtrlLeftDown)

        # item = self.tree.AddRoot('root')
        # for entity in entity_list:
        item = self.add_entry(None, entity)
        item.Expand()

        ok = wx.Button(self, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.ID_OK)
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, 'Test Name:'), 0, wx.ALIGN_LEFT|wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 15)
        self.test_name = wx.TextCtrl(self, -1)
        self.test_name.SetFocus()
        sizer.Add(self.test_name, 0, wx.EXPAND|wx.LEFT|wx.RIGHT, 15)
        sizer.Add(wx.StaticText(self, -1, 'Script:'), 0, wx.ALIGN_LEFT|wx.EXPAND|wx.LEFT|wx.TOP, 15)
        sizer.Add(self.tree, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 15)
        self.script_path = wx.TextCtrl(self, -1)
        sizer.Add(self.script_path, 0, wx.EXPAND|wx.RIGHT|wx.LEFT|wx.TOP, 15)
        btns = wx.StdDialogButtonSizer()
        btns.AddButton(ok)
        btns.AddButton(cancel)
        btns.Realize()
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL, 15)
        self.SetSizer(sizer)
        self.Layout()

    def OnOk(self, evt):
        error = None
        if not self.test_name.GetValue():
            error = 'No test name provided'
        elif not self.script_path.GetValue():
            error = 'No script selected'
        if error is not None:
            wx.MessageBox(error, caption='New test error', style=wx.OK | wx.ICON_ERROR)
        else:
            self.Destroy()

    def OnCancel(self, evt):
        self.test_name.SetValue('')
        self.script_path.SetValue('')
        self.Destroy()

    def add_entry(self, parent, entity):
        if parent is None:
            item = self.tree.AddRoot(entity.name, image=entity.image)
        else:
            item = self.tree.AppendItem(parent, entity.name, image=entity.image)
        self.tree.SetItemPyData(item, entity)
        for e in entity.entries:
            self.add_entry(item, e)
        return item

    def OnSelectionChanged(self, event):
        item = self.tree.GetSelection()
        if item is not None:
            entity = self.tree.GetItemPyData(item)

        if entity is not None:
            try:
                path = entity.path()
                path.append(entity.name)
                i = path.index(svp.SCRIPTS_DIR)
                name = script.PATH_SEP.join(path[i+1:])
                self.script_path.SetValue(name)
            except Exception as e:
                raise UIError('Error creating script path: %s' % str(e))

    def OnTreeCtrlLeftDown(self, event):
        item, flags = self.tree.HitTest(event.GetPosition())
        accept = True
        if flags & (wx.TREE_HITTEST_ONITEMLABEL|wx.TREE_HITTEST_ONITEMICON):
            if item is not None:
                entity = self.tree.GetItemPyData(item)
                if type(entity) != ScriptEntry:
                    accept = False
        if accept:
            event.Skip()


class EntityTree(treectrl.CustomTreeCtrl):

    popup_menu_new_items = [(wx.ID_ANY, 'Directory...', '', None, OP_NEW_DIR),
                            (wx.ID_ANY, 'Suite...', '', None, OP_NEW_SUITE),
                            (wx.ID_ANY, 'Test...', '', None, OP_NEW_TEST)]

    popup_menu_add_items = [(wx.ID_ANY, 'Suite...', '', None, OP_ADD_SUITE),
                            (wx.ID_ANY, 'Test...', '', None, OP_ADD_TEST)]

    popup_menu_items = [(wx.ID_ANY, 'New', '', popup_menu_new_items, None),
                  (wx.ID_ANY, 'Open', '', None, OP_OPEN),
                  (wx.ID_ANY, '', '', None, None),
                  (wx.ID_ANY, 'Copy', '', None, OP_COPY),
                  (wx.ID_ANY, 'Edit', '', None, OP_EDIT),
                  (wx.ID_ANY, 'Move/Rename', '', None, OP_MOVE),
                  (wx.ID_ANY, 'Rescan', '', None, OP_RESCAN),
                  (wx.ID_ANY, '', '', None, None),
                  (wx.ID_DELETE, 'Delete', '', None, OP_DELETE),
                  (wx.ID_ANY, 'Delete All', '', None, OP_DELETE_ALL),
                  (wx.ID_REMOVE, 'Remove', '', None, OP_REMOVE),
                  (wx.ID_ANY, '', '', None, None),
                  # (wx.ID_ANY, 'Add', '', popup_menu_add_items, None),
                  # (wx.ID_ANY,'Remove', '', None, OP_REMOVE),
                  # (wx.ID_ANY,'Move Up', '', None, OP_MOVE_UP),
                  # (wx.ID_ANY,'Move Down', '', None, OP_MOVE_DOWN),
                  # (wx.ID_ANY, '', '', None, None),
                  (wx.ID_ANY, 'Run', '', None, OP_RUN),
                  (wx.ID_ANY, '', '', None, None),
                  (wx.ID_ANY, 'Result', '', None, OP_RESULT)]

    #def OnCompareItems(self):
    #    pass

    def __init__(self, parent, dir_names=None, image_path='', entity_window=None):
        # wx.TreeCtrl.__init__(self, parent)
        treectrl.CustomTreeCtrl.__init__(self, parent, agwStyle=(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
                                                                 wx.TR_NO_LINES |
                                                                 treectrl.TR_TOOLTIP_ON_LONG_ITEMS |
                                                                 treectrl.TR_ELLIPSIZE_LONG_ITEMS |
                                                                 treectrl.TR_HAS_VARIABLE_ROW_HEIGHT))
        # style=(wx.TR_NO_LINES | wx.TR_SINGLE | wx.TR_HIDE_ROOT)
        style=(wx.TR_TWIST_BUTTONS | wx.TR_NO_LINES | wx.TR_SINGLE | wx.TR_HIDE_ROOT)
        # self.SetWindowStyle(self.GetWindowStyle() | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_NO_BUTTONS | wx.TR_NO_LINES)
        # self.SetWindowStyle(style)
        # self.SetWindowStyle(self.GetWindowStyle() | wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT)
        ## self.SetWindowStyle(wx.TR_HIDE_ROOT | wx.TR_FULL_ROW_HIGHLIGHT)
        # self.SetBackgroundColour('pink')
        self.entity_window = entity_window
        self.root = None
        self.dirs = []
        self.name = None
        self.parent = None    # entity parent not wx parent, should always be None

        self.alt_image_list = wx.ImageList(16, 16, True)
        index = self.alt_image_list.Add(wx.Bitmap(image_closed))
        index = self.alt_image_list.Add(wx.Bitmap(image_closed))
        index = self.alt_image_list.Add(wx.Bitmap(image_open))
        index = self.alt_image_list.Add(wx.Bitmap(image_open))
        self.SetButtonsImageList(self.alt_image_list)

        self.image_list = image_list
        self.images = images

        self.AssignImageList(self.image_list)

        self.status_image_list = image_list
        self.status_images = images

        self.AssignStatusImageList(self.status_image_list)

        self.entity_window.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)
        '''
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapsed)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpanded)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpanding)
        '''
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)

        for name in dir_names:
            self.add_working_dir(name)

    def create_menu(self, menu_items, ops=None):
        menu = wx.Menu()
        enabled = False
        for item in menu_items:
            if item[1]:
                func = ext_menu = None
                if ops is not None:
                    op = ops.get(item[4])
                    if op is not None:
                        func = op[0]
                        ext_menu = op[1]
                if ext_menu is not None:
                    submenu, submenu_enabled = self.create_ext_menu(ext_menu)
                    menu_item = menu.AppendSubMenu(submenu, item[1])
                    menu_item.Enable(submenu_enabled)
                elif item[3] is not None:
                    submenu, submenu_enabled = self.create_menu(item[3], ops)
                    menu_item = menu.AppendSubMenu(submenu, item[1])
                    menu_item.Enable(submenu_enabled)
                else:
                    menu_item = menu.Append(item[0], item[1], item[2])
                    menu_item.Enable(False)
                if func is not None:
                    self.Bind(wx.EVT_MENU, func, menu_item)
                    menu_item.Enable(True)
                    enabled = True
            else:
                menu.AppendSeparator()
        return (menu, enabled)

    def create_ext_menu(self, ext_menu_items):
        menu = wx.Menu()
        enabled = False
        for item in ext_menu_items:
            if item[0]:
                if item[2] is not None:
                    submenu, submenu_enabled = self.create_ext_menu(item[2])
                    menu_item = menu.AppendSubMenu(submenu, item[0])
                    menu_item.Enable(submenu_enabled)
                    if submenu_enabled:
                        enabled = True
                else:
                    menu_item = menu.Append(wx.ID_ANY, item[0], item[1])
                    menu_item.Enable(False)
                func = item[3]
                if func is not None:
                    self.Bind(wx.EVT_MENU, func, menu_item)
                    menu_item.Enable(True)
                    enabled = True
            else:
                menu.AppendSeparator()
        return (menu, enabled)

    def update_menu_ops(self, ops=None):
        if ops is None:
            ops = {}
        item = self.GetSelection()
        if item.IsOk():
            entry = self.GetItemPyData(item)
            if entry is not None:
                entry.update_menu_ops(ops)
        return ops

    def create_popup_menu(self, menu_items):
        menu = wx.Menu()
        for item in menu_items:
            if item[1]:
                if item[3] is not None:
                    submenu = self.create_popup_menu(item[3])
                    menu_item = menu.AppendSubMenu(submenu, item[1])
                else:
                    menu_item = menu.Append(item[0], item[1], item[2])
                # menu_item.Enable(False)
            else:
                menu.AppendSeparator()
        return menu

    def add(self, directory):
        d = self.get(directory.name)
        if d is None:
            self.dirs.append(directory)

    def add_dir(self, name=None, image=None):
        # self.AppendItem(self.item, d.name, image=self.image_working_dir)
        d = self.get(name)
        if d is None:
            d = WorkingDirectory(name, parent=self, entity_tree=self, image=image)
            self.dirs.append(d)
            return d

    def add_working_dir(self, name=None):
        d = self.add_dir(name, self.images['working_dir'])
        return d

    def set_working_dir(self, name):
        ### set app working directory
        self.dirs = []
        d = self.add_dir(name, self.images['working_dir'])
        return d

    def remove_dir(self, name=None):
        for i in range(len(self.dirs)):
            if self.dirs[i].name == name:
                del self.dirs[i]
                break

    def build(self, selected=None):
        if self.root is not None:
            self.Delete(self.root)
            self.root = None
        self.root = self.AddRoot('root')

        for d in self.dirs:
            d.build(self, self.root, selected=selected)
            self.Expand(d.item)
            # self.AppendItem(self.root, d.name, image=d.image)

    def dump(self):
        s = ''
        prefix = '\n'
        for d in self.dirs:
            s += d.dump(prefix)
            # prefix = '\n'
        return s

    def get(self, name):
        for d in self.dirs:
            if d.name == name:
                return d

    def scan(self):
        for d in self.dirs:
            try:
                d.scan()
                # self.scan_dir(d)
            except Exception as e:
                wx.MessageBox('Error: %s' % traceback.format_exc(), caption='Error', style=wx.OK | wx.ICON_ERROR)

    def clear_detail(self):
        if self.entity_window is not None:
            self.entity_window.entity_detail_sizer.Clear(delete_windows=True)

    def render_detail(self, entry):
        entity_tree = entry.entity_tree
        entity_window = entity_tree.entity_window
        if entity_window is not None:
            entity_window.update_menu()

        self.clear_detail()

        try:
            info = entry.render_info(entity_window.entity_detail)
            if info is not None:

                # entity_window.entity_detail.SetBackgroundColour('blue')
                entity_window.entity_detail.Refresh()
                # entity_window.entity_detail.SetBackgroundColour('yellow')

                entity_window.entity_detail_sizer.Add(info, 1, wx.EXPAND|wx.ALL)
                #entity_window.entity_detail.Layout()
                # entity_window.entity_detail.Scroll(0, 0)
                entity_window.entity_detail.FitInside()
        except Exception as e:
            wx.MessageBox('Error: %s' % traceback.format_exc(), caption='Error', style=wx.OK | wx.ICON_ERROR)

    def OnShowPopup(self, event):
        item = self.GetSelection()
        entry = self.GetItemPyData(item)
        if self.entity_window is not None:
            ops = self.entity_window.update_menu_ops()
        else:
            ops = self.update_menu_ops()
        menu, enabled = self.create_menu(EntityTree.popup_menu_items, ops)
        # entry.update_popup_menu(menu)

        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(menu, pos)

    def OnSelectionChanged(self, event):
        item = self.GetSelection()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                if entry.error is not None:
                    wx.MessageBox('Error: %s' % entry.error, caption='Error', style=wx.OK | wx.ICON_ERROR)
                else:
                    self.render_detail(entry)

    def OnCollapsed(self, event):
        item = event.GetItem()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                entry.expand(False)
                #entry.expanded = False
                #entry.working_dir().expand(entry.working_dir_relative_name())
                #print '%s collapsed' % ()
        event.Skip()

    def OnExpanded(self, event):
        item = event.GetItem()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                entry.expand(True)
                #entry.expanded = True
                #print '%s expanded' % (entry.working_dir_relative_name())
        event.Skip()

    def OnExpanding(self, event):
        item = event.GetItem()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                entry.expanding()
        event.Skip()

    def OnItemActivated(self, event):
        item = self.GetSelection()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None and entry.is_result():
                filename = entry.result_filename()
                os.startfile(filename)

def add_result_entry(entity, result):
    if entity.is_suite():
        t = rslt.RESULT_TYPE_SUITE
    elif entity.is_test():
        t = rslt.RESULT_TYPE_TEST
    elif entity.is_script():
        t = rslt.RESULT_TYPE_SCRIPT
    else:
        return
    r = rslt.Result(name=entity.relative_name(), type=t)
    result.add_result(r)
    for e in entity.entries:
        add_result_entry(e, r)

def build_result_tree(entity):
    et = rslt.Result(name='results', type=rslt.RESULT_TYPE_RESULT)
    parent_result = None
    results = None
    s = entity.parent
    while s is not None and s.is_suite():
        result = rslt.Result(name=s.name, type=rslt.RESULT_TYPE_SUITE)
        if parent_result is None:
            parent_result = result
        if results is not None:
            result.results.append(results)
        results = result
        s = s.parent

    if parent_result is None:
        parent_result = et
    else:
        et.add_result(results)

    add_result_entry(entity, parent_result)

    return et

class EntityTreeEntry(object):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=-1):
        self.entity_tree = entity_tree
        self.parent = parent
        self.name = name
        self.ext = None
        self.entries = []
        self.image = image
        self.status_image = status_image
        self.item = None
        self.ops = {}
        self.error = None
        self.expanded = False
        self.result = None
        self.result_dir = None

    def op_delete(self, evt, title='Delete',
                  msg='Are you sure you want to delete %s?'):
        try:
            retCode = wx.MessageBox(msg % self.name, title, wx.YES_NO | wx.ICON_QUESTION)
            if (retCode == wx.YES):
                name = self.name
                if self.ext is not None:
                    name += self.ext
                path = self.path() + [name]
                path = os.path.join(*path)
                os.remove(path)
                self.entity_tree.Unselect()
                self.entity_tree.Delete(self.item)
                self.parent.delete(self)
                self.entity_tree.clear_detail()
        except Exception as e:
            wx.MessageBox('Error deleting %s' % (str(e)), 'Delete Error', wx.OK | wx.ICON_ERROR)

    def op_run(self, event):
        dialog = RunDialog(self)
        dialog.CenterOnParent()
        ### dialog.ShowModal()
        dialog.Show()
        ### dialog.Destroy()
        # self.get_working_dir().rescan()

        # self.entity_tree.entity_window.app_wx.process.stop()
        # self.entity_tree.entity_window.app_wx.run_window = None

    def expand(self, expanded):
        name = self.working_dir_relative_name()
        if name:
            self.get_working_dir().update_expanded(name, expanded)
        self.expanded = expanded

    def expanding(self):
        pass

    def is_script(self):
        return False

    def is_suite(self):
        return False

    def is_test(self):
        return False

    def is_dir(self):
        return False

    def absolute_filename_script(self, name):
        return os.path.join(self.working_dir_path(), svp.SCRIPTS_DIR, os.path.normpath(name)) + svp.SCRIPT_EXT

    def _add(self, entry, entry_list, reverse=False):
        prev_entry = None
        for i in range(len(entry_list)):
            if (reverse and ((entry.is_dir() and not entry_list[i].is_dir()) or
                    (entry.is_dir() == entry_list[i].is_dir() and
                    os.path.normcase(entry.name) >= os.path.normcase(entry_list[i].name)))):
                entry_list.insert(i, entry)
                return prev_entry
            elif (not reverse and ((entry.is_dir() and not entry_list[i].is_dir()) or
                    (entry.is_dir() == entry_list[i].is_dir() and
                    os.path.normcase(entry.name) < os.path.normcase(entry_list[i].name)))):
                entry_list.insert(i, entry)
                return prev_entry
            else:
                prev_entry = entry_list[i]
        entry_list.append(entry)
        return prev_entry

    def add_entry(self, name, clazz, entity_tree=None, image=None, status_image=-1, ordered=True,
                  allow_duplicate=False, open_list=None, reverse=False):
        if allow_duplicate is False:
            if self.get(name) is not None:
                raise Exception('Duplicate entry: %s' % name)
        entry = clazz(name, parent=self, entity_tree=entity_tree, image=image, status_image=status_image)
        if ordered is True:
            self._add(entry, self.entries, reverse=reverse)
        else:
            self.entries.append(entry)
        return entry

    def build(self, entity_tree, parent, selected=None):
        # wdc = wx.WindowDC(entity_tree)
        # name = wordwrap(self.name, 200, wdc)
        self.item = entity_tree.AppendItem(parent, self.name, image=self.image, statusImage=self.status_image)
        # self.item = entity_tree.AppendItem(parent, name, image=self.image)
        entity_tree.SetItemPyData(self.item, self)
        if selected is not None:
            if self.working_dir_relative_name() == selected:
                entity_tree.SelectItem(self.item, select=True)
        if self.expanded:
            self.item.Expand()
        # self.item.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapsed)
        # self.item.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpanded)
        for e in self.entries:
            e.build(entity_tree, self.item, selected=selected)

    def insert_entry(self, name, clazz, entity_tree=None, image=None, status_image=-1, ordered=True,
                     allow_duplicate=False, reverse=False):
        prev_entry = None
        if allow_duplicate is False:
            if self.get(name) is not None:
                raise Exception('Duplicate entry: %s' % name)
        entry = clazz(name, parent=self, entity_tree=entity_tree, image=image, status_image=status_image)
        if ordered is True:
            prev_entry = self._add(entry, self.entries, reverse=reverse)
        else:
            if len(self.entries) > 0:
                prev_entry = self.entries[-1]
            self.entries.append(entry)

        if prev_entry:
            entry.item = entity_tree.InsertItem(self.item, prev_entry.item, name, image=image,
                                                statusImage=status_image)
        else:
            entry.item = entity_tree.PrependItem(self.item, name, image=image, statusImage=status_image)
        entity_tree.SetItemPyData(entry.item, entry)
        # self.item.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapsed)
        # self.item.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpanded)
        entity_tree.Expand(self.item)

        return entry

    def get(self, name):
        for e in self.entries:
            if os.path.normcase(e.name) == os.path.normcase(name):
                return e

    def delete(self, entry):
        if entry in self.entries:
            self.entries.remove(entry)

    def dump(self, prefix=''):
        return prefix + str(self)

    def path(self):
        path = []
        parent = self.parent
        while parent and parent.name is not None:
            path.insert(0, parent.name)
            parent = parent.parent
        return path

    def relative_name(self):
        return self.name

    def working_dir_relative_path(self):
        path = []
        if not isinstance(self, WorkingDirectory):
            path = [self.name]
            parent = self.parent
            while parent and not isinstance(parent, WorkingDirectory):
                path.insert(0, parent.name)
                parent = parent.parent
            name = script.PATH_SEP.join(path)
        return path

    def working_dir_relative_name(self):
        name = ''
        path = self.working_dir_relative_path()
        if len(path) > 0:
            name = script.PATH_SEP.join(path)
        return name

    def working_dir_path(self):
        path = None
        if self.parent:
            path = self.parent.working_dir_path()
        return path

    def suites_dir_path(self):
        return os.path.join(self.working_dir_path(), svp.SUITES_DIR)

    def tests_dir_path(self):
        return os.path.join(self.working_dir_path(), svp.TESTS_DIR)

    def scripts_dir_path(self):
        return os.path.join(self.working_dir_path(), svp.SCRIPTS_DIR)

    def results_dir_path(self):
        return os.path.join(self.working_dir_path(), svp.RESULTS_DIR)

    def get_working_dir(self):
        working_dir = self
        if self.parent:
            working_dir = self.parent.get_working_dir()
        return working_dir

    def get_scripts_dir(self):
        scripts_dir = None
        working_dir = self.get_working_dir()
        if working_dir is not None:
            scripts_dir = working_dir.get(svp.SCRIPTS_DIR)
        return scripts_dir

    def get_suites_dir(self):
        suites_dir = None
        working_dir = self.get_working_dir()
        if working_dir is not None:
            suites_dir = working_dir.get(svp.SUITES_DIR)
        return suites_dir

    def get_tests_dir(self):
        tests_dir = None
        working_dir = self.get_working_dir()
        if working_dir is not None:
            tests_dir = working_dir.get(svp.TESTS_DIR)
        return tests_dir

    def get_results_dir(self):
        results_dir = None
        working_dir = self.get_working_dir()
        if working_dir is not None:
            results_dir = working_dir.get(svp.RESULTS_DIR)
        return results_dir

    def get_dir(self, dir_type):
        dir = None
        working_dir = self.get_working_dir()
        if working_dir is not None:
            dir = working_dir.get(dir_type)
        return dir

    def get_parent_suite(self):
        active_suite = None
        if type(self) == SuiteEntry:
            suite = self
        else:
            suite = self.parent
        while suite is not None and suite.is_suite():
            parent_suite = svp.Suite(filename=suite.absolute_filename())
            if parent_suite.globals is True or active_suite is None:
                active_suite = parent_suite
            if type(suite) == SuiteEntry:
                break
            suite = suite.parent
        return active_suite

    def update_menu_ops(self, ops):
        if ops is None:
            ops = {}
        ops.update(self.ops)

    def show_group(self, info_panel, parent, show):
        start_row = parent.group_start_row
        end_row = parent.group_end_row
        if end_row > start_row:
            name = parent.GetName()
            row = start_row + 1
            while row <= end_row:
                sizer_item = info_panel.panel_sizer.FindItemAtPosition((row, 0))
                if sizer_item is not None:
                    item = sizer_item.GetWindow()
                    if item is not None:
                        try:
                            first_row = item.group_start_row
                            last_row = item.group_end_row
                        except Exception:
                            first_row = None
                        if show and first_row:
                            item.Show()
                            closed = item.group_closed
                            group_show = not closed
                            self.show_group(info_panel, item, group_show)
                            row = last_row + 1
                        else:
                            for col in range(0, 3):
                                sizer_item = info_panel.panel_sizer.FindItemAtPosition((row, col))
                                if sizer_item is not None:
                                    if show:
                                        sizer_item.GetWindow().Show()
                                    else:
                                        sizer_item.GetWindow().Hide()
                            row += 1

    def toggle(self, item_toggle):
        item = item_toggle.group_toggle
        item_toggle.Hide()
        item.Show()
        item_name = item.GetName()
        parent = item.GetParent()
        if item_name[:2] == ITEM_OPEN_PREFIX:
            show = True
            parent.group_closed = False
        else:
            show = False
            parent.group_closed = True
        parent.group_toggle = item
        self.show_group(self.info_panel, parent, show)

        self.info_panel.Layout()

    def toggle_group(self, evt):
        item_evt = evt.GetEventObject()
        self.toggle(item_evt)

    def double_click_group(self, evt):
        item_evt = evt.GetEventObject()
        item_toggle = item_evt.group_toggle
        item_evt.group_toggle = item_toggle.group_toggle
        self.toggle(item_toggle)

    def render_group(self, info_panel, param_defs, param_value, group, row=0, pad=0):
        show = True
        if param_defs is not None and script.param_is_active(param_defs, group.qname, param_value) is not None:
            label_panel = None
            if group.name != script.SCRIPT_PARAM_ROOT:
                label_panel = wx.Panel(info_panel, -1)
                label_panel.SetBackgroundColour('white')

                open_bitmap = wx.StaticBitmap(parent=label_panel, name=ITEM_OPEN_PREFIX + group.qname,
                                              bitmap=wx.Bitmap(image_open), pos=(0,0))
                open_bitmap.Bind(wx.EVT_LEFT_DOWN, self.toggle_group)
                closed_bitmap = wx.StaticBitmap(parent=label_panel, name=ITEM_CLOSED_PREFIX + group.qname,
                                                bitmap=wx.Bitmap(image_closed), pos=(0,2))
                closed_bitmap.Bind(wx.EVT_LEFT_DOWN, self.toggle_group)
                open_bitmap.group_toggle = closed_bitmap
                closed_bitmap.group_toggle = open_bitmap
                closed_bitmap.Hide()
                label_panel.group_toggle = open_bitmap
                label_panel.group_closed = False
                label_panel.group_start_row = row

                text = wx.StaticText(label_panel, -1, group.label, pos=(20, 2))
                font = text.GetFont()
                font.SetWeight(wx.FONTWEIGHT_BOLD)
                text.SetFont(font)
                text.Wrap(TEXT_WRAP)
                text.group_toggle = open_bitmap
                text.Bind(wx.EVT_LEFT_DCLICK, self.double_click_group)

                info_panel.panel_sizer.Add(label_panel, pos=(row, 0), border=pad, flag=wx.LEFT)
                row += 1

                pad += 20

            index_count = group.index_count
            index_start = group.index_start
            if index_count is not None:
                if type(index_count) == str:
                    index_count = param_value(index_count)
                if type(index_start) == str:
                    index_start = param_value(index_start)
                if index_count is not None and index_start is not None:
                    for i in range(index_start, index_start + index_count):
                        for param in group.params:
                            row = self.render_param(info_panel, param_defs, param_value, param, index=i, row=row, pad=pad)
            else:
                for param in group.params:
                    index_count = param.index_count
                    index_start = param.index_start
                    if index_count is not None:
                        if type(index_count) == str:
                            index_count = param_value(index_count)
                        if type(index_start) == str:
                            index_start = param_value(index_start)
                        if index_count is not None and index_start is not None:
                            for i in range(index_start, index_start + index_count):
                                row = self.render_param(info_panel, param_defs, param_value, param, index=i, row=row,
                                                        pad=pad)
                    else:
                        row = self.render_param(info_panel, param_defs, param_value, param, index=None, row=row,
                                                pad=pad)

            for g in group.param_groups:
                row = self.render_group(info_panel, param_defs, param_value, g, row=row, pad=pad)

            if label_panel is not None:
                label_panel.group_end_row = row - 1
                self.show_group(info_panel, label_panel, show)

        return row

    def render_param(self, info_panel, param_defs, param_value, param, index=None, row=0, pad=0):
        if script.param_is_active(param_defs, param.qname, param_value) is not None:
            if index is not None:
                label =  '%s %s' % (param.label, index)
                value = ''
                values = param_value(param.qname)
                if type(values) == dict:
                    value = str(values.get(index))
            else:
                label = param.label
                value = str(param_value(param.qname))

            text = wx.StaticText(info_panel, -1, label)
            text.Wrap(TEXT_WRAP)
            if param.desc is not None:
                text.SetToolTip(wx.ToolTip(param.desc))
            info_panel.panel_sizer.Add(text, pos=(row, 0), border=pad, flag=wx.LEFT)
            text = wx.StaticText(info_panel, -1, value)
            text.Wrap(TEXT_WRAP)
            info_panel.panel_sizer.Add(text, pos=(row, 1), border=0, flag=wx.LEFT)
            row += 1
        return row

    def render_globals(self, info_panel, globals=None, row=0, pad=0):
        text = wx.StaticText(info_panel, -1, 'Global Parameters')
        text.Wrap(TEXT_WRAP)
        text.SetToolTip(wx.ToolTip('Global parameters enabled indication'))
        info_panel.panel_sizer.Add(text, pos=(row, 0), border=pad, flag=wx.LEFT)
        if globals is True:
            status = 'Enabled'
        else:
            status = 'Disabled'
        text = wx.StaticText(info_panel, -1, status)
        text.Wrap(TEXT_WRAP)
        info_panel.panel_sizer.Add(text, pos=(row, 1), border=0, flag=wx.LEFT)
        row += 1
        return row

    def render_info(self, parent):
        pass


class Directory(EntityTreeEntry):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=-1):
        EntityTreeEntry.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image,
                                 status_image=status_image)
        self.dirs = []

    def is_dir(self):
        return True

    def add_dir(self, name, clazz, entity_tree=None, image=None, status_image=-1, ordered=True,
                allow_duplicate=False):
        if allow_duplicate is False:
            if self.get(name) is not None:
                raise Exception('Duplicate entry: %s' % name)
        d = clazz(name, parent=self, entity_tree=entity_tree, image=image, status_image=status_image)
        if ordered is True:
            self._add(d, self.dirs)
        else:
            self.dirs.append(d)
        return d

    def build(self, entity_tree, parent, selected=None):
        # wdc = wx.WindowDC(entity_tree)
        # name = wordwrap(self.name, 270, wdc)
        # self.item = entity_tree.AppendItem(parent, self.name, image=self.image)
        self.item = entity_tree.AppendItem(parent, self.name, image=self.image, statusImage=self.status_image)

        entity_tree.SetItemPyData(self.item, self)
        if selected is not None:
            if self.working_dir_relative_name() == selected:
                entity_tree.SelectItem(self.item, select=True)
        if self.expanded:
            self.item.Expand()
        for d in self.dirs:
            d.build(entity_tree, self.item, selected=selected)
        for e in self.entries:
            e.build(entity_tree, self.item, selected=selected)

    def clear(self):
        self.dirs = []
        self.entries = []

    def dump(self, prefix=''):
        s = prefix + str(self)
        next_prefix = '%s  ' % prefix
        for entry in self.dirs:
            s += entry.dump(next_prefix)
        for entry in self.entries:
            s += entry.dump(next_prefix)
        return s

    # def scan(self, ext=None, image_dir=None, image_entry=None):
    #     pass

    def _op_new_dir(self, clazz, image=None, status_image=-1):
        try:
            name = prompt_name('Directory Name:', "New Directory", '')
            if name is not None:
                if self.get(name) is None:
                    path = self.path() + [self.name, name]
                    path = os.path.join(*path)
                    os.mkdir(path)
                    entry = self.insert_entry(name, clazz, entity_tree=self.entity_tree,
                                              image=image, status_image=status_image)
                    self.entity_tree.SelectItem(entry.item, select=True)
                else:
                    wx.MessageBox('%s already exists in %s' % (name, self.name), 'New Directory Error',
                                  wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox('Error adding new directory: %s' % (str(e)), 'New Directory Error', wx.OK | wx.ICON_ERROR)

    def op_new_suite(self, event):
        try:
            suite_name = prompt_name('Suite Name:', 'New Suite', '')
            if suite_name:
                if self.get(suite_name) is not None:
                    wx.MessageBox('%s already exists in %s' % (suite_name, self.name), "New Suite Error",
                                   wx.OK | wx.ICON_ERROR)
                    return

            suite = svp.Suite(name=suite_name)

            path = self.path() + [self.name, suite_name + svp.SUITE_EXT]
            path = os.path.join(*path)
            suite.to_xml_file(filename=path, replace_existing=False)

            entry = self.insert_entry(suite_name, SuiteEntry, entity_tree=self.entity_tree,
                                      image=self.entity_tree.images['suite'])
            self.entity_tree.SelectItem(entry.item, select=True)

            entry.op_edit(entry)
        except Exception as e:
            wx.MessageBox('Error creating suite: %s' % (str(e)), 'New Suite Error', wx.OK | wx.ICON_ERROR)

    def op_new_test(self, event):
        try:
            scripts_dir = self.get_scripts_dir()
            dialog = NewTestDialog(self.parent, self.entity_tree, scripts_dir)
            dialog.CenterOnParent()
            dialog.ShowModal()
            test_name = dialog.test_name.GetValue()
            script_path = dialog.script_path.GetValue()
            script_name = script_path.split(script.PATH_SEP)[-1]

            if not test_name:
                return
            if self.get(test_name) is not None:
                wx.MessageBox('%s already exists in %s' % (test_name, self.name), "New Test Error",
                              wx.OK | wx.ICON_ERROR)
                return

            working_dir = self.working_dir_path()
            # path = [self.working_dir_path(), svp.SCRIPTS_DIR, os.path.normpath(script_path)]
            # path = os.path.join(*path)
            path = os.path.join(working_dir, svp.SCRIPTS_DIR, os.path.normpath(script_path))
            lib_path = os.path.join(working_dir, svp.LIB_DIR)
            test_script = script.load_script(path, lib_path, path_list = svp.extended_path_list)
            script_config = script.ScriptConfig(name=test_name, script=script_path)
            script_config.param_add_default(test_script, test_script.param_defs)
            # self.group_active(test_script.param_defs, test_script)

            path = self.path() + [self.name, test_name + svp.TEST_EXT]
            path = os.path.join(*path)
            script_config.to_xml_file(filename=path, replace_existing=False)

            entry = self.insert_entry(test_name, TestEntry, entity_tree=self.entity_tree,
                                      image=self.entity_tree.images['test'])
            self.entity_tree.SelectItem(entry.item, select=True)
            entry.op_edit(entry)
        except Exception as e:
            raise
            ### wx.MessageBox('Error creating test: %s' % (str(e)), 'New Test Error', wx.OK | wx.ICON_ERROR)

    def op_delete(self, evt, title='Delete Directory',
                  msg='Are you sure you want to delete %s and all its contents?'):
        try:
            retCode = wx.MessageBox(msg % self.name, title, wx.YES_NO | wx.ICON_QUESTION)
            if (retCode == wx.YES):
                path = self.path() + [self.name]
                path = os.path.join(*path)
                shutil.rmtree(path)
                self.entity_tree.Unselect()
                self.entity_tree.Delete(self.item)
                self.parent.delete(self)
        except Exception as e:
            wx.MessageBox('Error deleting directory %s' % (str(e)), 'Delete Directory Error', wx.OK | wx.ICON_ERROR)

class WorkingDirectory(Directory):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=-1):
        Directory.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image, status_image=status_image)
        self.ops = {OP_REMOVE: (self.op_remove, None), OP_RESCAN: (self.op_rescan, None)}
        self.expanded_entries = set()
        self.svp_ext = {}

    def op_remove(self, event):
        self.parent.remove_dir(self.name)
        self.parent.Delete(self.item)
        self.entity_tree.entity_window.svp.remove_directory(self.name)

    def op_rescan(self, event):
        self.rescan()
        svp.member_update(os.path.join(self.name, svp.SUITES_DIR), 'abc.ste', 'xyz.ste')

    def rescan(self):
        selected = None
        item = self.entity_tree.GetSelection()
        if item is not None:
            entity = self.entity_tree.GetItemPyData(item)
            selected = entity.working_dir_relative_name()
        self.entity_tree.DeleteChildren(self.item)
        self.scan()
        for e in self.entries:
            e.build(self.entity_tree, self.item, selected=selected)
        # self.entity_tree.SetSelection(item)

    def move_expanded(self, old_name, new_name):
        pass

    def update_expanded(self, name, expanded):
        try:
            if expanded:
                self.expanded_entries.add(name)
            else:
                self.expanded_entries.remove(name)
        except:
            pass

    def is_expanded(self, name):
        return name in self.expanded_entries

    def working_dir_path(self):
        return self.name

    def get_working_dir(self):
        return self

    def scan(self):
        self.clear()
        try:
            files = os.listdir(os.path.join(self.name))
        except Exception as e:
            self.error = str(e)
            return

        if svp.SUITES_DIR in files:
            d = self.add_entry(svp.SUITES_DIR, SuitesDirectory, entity_tree=self.entity_tree,
                               image=self.entity_tree.images['suites'], ordered=False)
            d.expanded = self.is_expanded(d.name)
            d.scan()
            # self.scan_dir_suites(d, os.path.join(self.name, d.name))
        if svp.TESTS_DIR in files:
            d = self.add_entry(svp.TESTS_DIR, TestsDirectory, entity_tree=self.entity_tree,
                               image=self.entity_tree.images['tests'], ordered=False)
            d.expanded = self.is_expanded(d.name)
            d.scan()
            # self.scan_dir_tests(d, os.path.join(directory.name, d.name))
        if svp.SCRIPTS_DIR in files:
            d = self.add_entry(svp.SCRIPTS_DIR, ScriptsDirectory, entity_tree=self.entity_tree,
                               image=self.entity_tree.images['scripts'], ordered=False)
            d.expanded = self.is_expanded(d.name)
            d.scan()
            # self.scan_dir_scripts(d, os.path.join(directory.name, d.name))
            # self.scan_dir_scripts(d, os.path.join(self.name, svp.LIB_DIR))
        if svp.RESULTS_DIR in files:
            d = self.add_entry(svp.RESULTS_DIR, ResultsDirectory, entity_tree=self.entity_tree,
                               image=self.entity_tree.images['results'], ordered=False)
            d.expanded = self.is_expanded(d.name)
            d.scan()

        if svp.LIB_DIR in files:
            lib_dir = os.path.join(self.name, svp.LIB_DIR)
            self.scan_svp_ext(lib_dir)

    def scan_svp_ext(self, d):
        files = glob.glob(os.path.join(d, 'svp_ext_*.py'))
        for f in files:
            file_path, file_name = os.path.split(f)
            if len(file_name) > 11:
                name = os.path.splitext(file_name)[0]
                i_name = '%s_%s' % (name, str(int(time.time() * 1000)))
                m_name = name[8:]
                if m_name not in self.svp_ext:
                    try:
                        m = imp(i_name, f).load_module()
                        self.svp_ext[m_name] = m
                        print('Imported svp ext: {} {} {}\n{}'.format(f, m_name, i_name, (self.svp_ext)))
                    except Exception as e:
                        print(f"Error importing {f}")
                        print(f"Error message : {e}")
        files = glob.glob(os.path.join(d, '*'))
        for f in files:
            if os.path.isdir(f):
                self.scan_svp_ext(os.path.join(d, f))

class ScriptsDirectory(Directory):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=-1):
        Directory.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image, status_image=status_image)
        self.ops = {OP_NEW_DIR: (self.op_new_dir, None)}

    def op_new_dir(self, event):
        Directory._op_new_dir(self, ScriptDirectory, image=self.entity_tree.images['script_dir'])

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        path = os.path.join(os.path.join(*self.path()), self.name)
        try:
            files = os.listdir(path)
            for f in files:
                file_path = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                if ext == svp.SCRIPT_EXT:
                    try:
                        self.add_entry(name, ScriptEntry, entity_tree=self.entity_tree,
                                       image=self.entity_tree.images['script'])
                        # script.load_script(file_path, lib_path)
                    except Exception as e:
                        raise UIError('Script directory scan error: %s' % str(e))
                else:
                    if os.path.isdir(file_path):
                        d = self.add_entry(f, ScriptDirectory, entity_tree=self.entity_tree,
                                           image=self.entity_tree.images['script_dir'])
                        d.scan()
        except Exception as e:
            raise UIError('Error scanning directory %s: %s' % (path, str(e)))

class ResultsDirectory(Directory):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=-1):
        Directory.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image, status_image=status_image)
        self.ops = {OP_DELETE_ALL: (self.op_delete_all, None)}

    def op_delete_all(self, evt, title='Delete Results',
                  msg='Are you sure you want to delete all the results?'):
        try:
            retCode = wx.MessageBox(msg, title, wx.YES_NO | wx.ICON_QUESTION)
            if (retCode == wx.YES):
                files = glob.glob(os.path.join(os.path.join(*self.path()), self.name, '*'))
                for f in files:
                    shutil.rmtree(f)
                    ### os.remove(f)
                self.get_working_dir().rescan()
        except Exception as e:
            wx.MessageBox('Error deleting directory %s contents' % (str(e)), 'Delete Directory Contents Error', wx.OK | wx.ICON_ERROR)

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        try:
            path = os.path.join(os.path.join(*self.path()), self.name)
            files = os.listdir(path)
            if files is not None:
                files.sort(reverse=True)
            for f in files:
                file_path = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                if os.path.isdir(file_path):
                    result_file = os.path.join(file_path, (name + svp.RESULTS_EXT))
                    if os.path.isfile(result_file):
                        try:
                            result_entry = self.add_entry(name, ResultDirectoryEntry, entity_tree=self.entity_tree,
                                                          image=self.entity_tree.images['result'], ordered=False)
                            result_entry.result = rslt.Result()
                            result_entry.result.from_xml(filename=result_file)
                            result_entry.add_results(name)

                        except Exception as e:
                            raise UIError('Result directory scan error: %s' % str(e))
        except Exception as e:
            raise UIError('Error scanning directory %s: %s' % (path, str(e)))

    def insert_results(self, results):
        result_entry = self.insert_entry(results.name, ResultDirectoryEntry, entity_tree=self.entity_tree,
                                         image=self.entity_tree.images['result'], ordered=True, reverse=True)
        result_entry.result = results
        result_entry.add_results(results.name)
        for e in result_entry.entries:
            e.build(self.entity_tree, result_entry.item)


class ResultDirectoryEntry(EntityTreeEntry):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=-1):
        EntityTreeEntry.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image,
                                 status_image=status_image)
        self.ops = {OP_DELETE: (self.op_delete, None)}

        fname, ext = os.path.splitext(name)
        if ext:
            self.ext = ext

    def op_delete(self, evt, title='Delete Result',
                  msg='Are you sure you want to result %s and all its contents?'):
        try:
            retCode = wx.MessageBox(msg % self.name, title, wx.YES_NO | wx.ICON_QUESTION)
            if (retCode == wx.YES):
                path = self.path() + [self.name]
                path = os.path.join(*path)
                shutil.rmtree(path)
                self.entity_tree.Unselect()
                self.entity_tree.Delete(self.item)
                self.parent.delete(self)
        except Exception as e:
            wx.MessageBox('Error deleting result %s' % (str(e)), 'Delete Result Error', wx.OK | wx.ICON_ERROR)

    def op_open(self, evt, title='Open Result'):
        result_dir = os.path.join(self.working_dir_path(), svp.RESULTS_DIR, self.name)
        dialog = ResultDialog(self, result_dir=result_dir, result_name=self.name,
                              image_list=self.entity_tree.image_list)
        dialog.CenterOnParent()
        dialog.Show()

    def is_result(self):
        return True

    def absolute_filename(self):
        path = self.path()
        path.append(self.name + svp.RESULTS_EXT)
        return os.path.join(*path)

    def relative_path(self):
        path = []
        parent = self.parent
        while parent and parent.name is not svp.RESULTS_DIR:
            path.insert(0, parent.name)
            parent = parent.parent
        return path

    def relative_name(self):
        path = self.relative_path()
        path.append(self.name)
        return script.PATH_SEP.join(path)

    def add_results(self, result_name):
        show_status = False
        for result in self.result.results:
            if result.status is not None or result.type == 'file':
                show_status = True
                break
        for result in self.result.results:
            if show_status is True:
                if result.status is None:
                    status = 'none'
                else:
                    status = result.status
                status_image = result_to_image.get(status, -1)
            else:
                status_image = -1

            entry = self.add_entry(result.name, ResultEntry, entity_tree=self.entity_tree,
                                   image=self.entity_tree.images[result.type],
                                   status_image=status_image,
                                   allow_duplicate=True, ordered=False)
            entry.expanded = True
            entry.result = result
            entry.result_name = result_name
            entry.add_results(result_name)

    def expanding(self):
        pass
        '''
        entry = self.entries[0]
        print entry
        if entry.result == None:
            entry.result = rslt.Result()
            entry.result.from_xml(filename=entry.absolute_filename())
            entry.add_results()
        '''

class ResultEntry(EntityTreeEntry):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=-1):
        EntityTreeEntry.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image,
                                 status_image=status_image)
        self.ext = svp.RESULTS_EXT
        self.ops = {}
        self.result = None

        fname, ext = os.path.splitext(name)
        if ext:
            self.ext = ext

    def update_menu_ops(self, ops):
        submenu = None
        wd = self.get_working_dir()
        m = wd.svp_ext.get('result')
        if m is not None:
            submenu = m.menu(self.result, os.path.join(self.working_dir_path(), svp.RESULTS_DIR), self.result_name)
        self.ops[OP_RESULT] = (None, submenu)
        if ops is None:
            ops = {}
        ops.update(self.ops)

    def op_delete(self, evt, title='Delete Result',
                  msg='Are you sure you want to result %s and all its contents?'):
        try:
            retCode = wx.MessageBox(msg % self.name, title, wx.YES_NO | wx.ICON_QUESTION)
            if (retCode == wx.YES):
                path = self.path() + [self.name]
                path = os.path.join(*path)
                shutil.rmtree(path)
                self.entity_tree.Unselect()
                self.entity_tree.Delete(self.item)
                self.parent.delete(self)
        except Exception as e:
            wx.MessageBox('Error deleting result %s' % (str(e)), 'Delete Result Error', wx.OK | wx.ICON_ERROR)

    def op_open(self, evt, title='Open Result'):
        if self.ext == svp.CSV_EXT:
            frame = wxmplot.PlotFrame()
            filename = os.path.join(self.working_dir_path(), svp.RESULTS_DIR, self.result_name, self.result.filename)
            f = open(filename, 'r')
            names = f.readline().split(',')
            columns = len(names)
            value_arrays = []
            for i in range(columns):
                value_arrays.append([])

            base_time = None
            for line in f:
                values = line.split(',')
                if base_time is None:
                    base_time = float(values[0])
                t = round(float(values[0]) - base_time, 2)
                value_arrays[0].append(t)
                for i in range(1, columns):
                    try:
                        v = float(values[i])
                        value_arrays[i].append(v)
                    except Exception as e:
                        value_arrays[i].append('nan')
                        pass

            time_array = numpy.array(value_arrays[0])
            for i in range(1, columns):
                value_array = numpy.array(value_arrays[i])
                frame.oplot(time_array, value_array, label=names[i])

            '''
            r = numpy.recfromcsv(filename, case_sensitive=True)
            print(repr(r))
            print r.dtype
            names = r.dtype.names
            x = names[0]
            print r[x]
            for name in names[1:]:
                # print name, r[x], r[name]
                frame.oplot(r[x], r[name])
            '''


            # pframe.plot(x, y1, title='Test 2 Axes with different y scales',
            #            xlabel='x (mm)', ylabel='y1', ymin=-0.75, ymax=0.75)
            # pframe.oplot(x, y2, y2label='y2', side='right', ymin=0)

            frame.SetTitle(self.name)
            frame.Show()
            # frame.ToggleWindowStyle(wx.STAY_ON_TOP)
        else:
            result_dir = os.path.join(self.working_dir_path(), svp.RESULTS_DIR, self.name)
            dialog = ResultDialog(self, result_dir=result_dir, result_name=self.name,
                                  image_list=self.entity_tree.image_list)
            dialog.CenterOnParent()
            dialog.Show()

    def is_result(self):
        return True

    def result_filename(self):
        entity = self.parent
        while entity and entity.result:
            if entity.result.type == rslt.RESULT_TYPE_RESULT:
                break
            entity = entity.parent

        filename = os.path.join(self.results_dir_path(), entity.result.name, self.result.filename)
        return filename

    def relative_path(self):
        path = []
        parent = self.parent
        while parent and parent.name is not svp.RESULTS_DIR:
            path.insert(0, parent.name)
            parent = parent.parent
        return path

    def relative_name(self):
        path = self.relative_path()
        path.append(self.name)
        return script.PATH_SEP.join(path)

    def add_results(self, result_name):
        show_status = False
        for result in self.result.results:
            if result.status is not None or result.type == 'file':
                show_status = True
                break
        for result in self.result.results:
            if show_status is True:
                if result.status is None:
                    status = 'none'
                else:
                    status = result.status
                status_image = result_to_image.get(status, -1)
            else:
                status_image = -1
            image = self.entity_tree.images[result.type]
            if result.type == 'file':
                if result.filename is not None:
                    name, ext = os.path.splitext(result.filename)
                    if ext == '.xlsx':
                        image = self.entity_tree.images['xlsx']

            entry = self.add_entry(result.name, ResultEntry, entity_tree=self.entity_tree,
                                   image=image,
                                   status_image=status_image,
                                   allow_duplicate=True, ordered=False)
            entry.expanded = True
            entry.result = result
            entry.result_name = result_name
            entry.add_results(result_name)

    def render_info(self, info_window):
        limit = None
        info_panel = None
        if self.result.filename is not None:
            filename = self.result_filename()
            ext = os.path.splitext(filename)[1]
            if ext != svp.LOG_EXT:
                limit = 1000
                if ext == '.xlsx':
                    return
            f = open(filename)

            info_panel = wx.Panel(info_window, -1)
            # info_panel.Hide()

            info_panel.SetBackgroundColour('white')
            info_log = wx.TextCtrl(info_panel, style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE)
            info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
            info_panel.SetSizer(info_panel_sizer)
            info_panel_sizer.Add(info_log, 1, wx.EXPAND|wx.LEFT|wx.TOP, 5)
            for entry in f:
                if len(entry) > 27 and entry[4] == '-' and entry[7] == '-' and entry[13] == ':' and entry[16] == ':':
                    info_log.SetDefaultStyle(wx.TextAttr((26, 13, 171)))
                    info_log.AppendText(entry[:25])
                    if entry[25] == script.DEBUG:
                        info_log.SetDefaultStyle(wx.TextAttr((119, 29, 169)))
                    elif entry[25] == script.ERROR:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.RED))
                    elif entry[25] == script.WARNING:
                        info_log.SetDefaultStyle(wx.TextAttr((255, 96, 0)))
                    else:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))
                    info_log.AppendText('%s' % (entry[25:]))
                else:
                    info_log.AppendText('%s' % (entry))
                if limit is not None:
                    limit -= 1
                    if limit <= 0:
                        info_log.AppendText('*** Data length truncated in summary display ***')
                        break

            f.close()
            info_log.ShowPosition(0)
            # info_panel.Show()

        return info_panel

    def render_info_(self, parent):
        if self.ext == svp.RESULTS_EXT:
            result_file = os.path.join(self.working_dir_path(), svp.RESULTS_DIR, self.name, self.name + svp.RESULTS_EXT)
            # print result_file, self.absolute_filename()
            # return RunPanel(parent, result_dir=result_dir, result_name=self.name)

            '''
            result_dir = os.path.join(self.working_dir_path(), svp.RESULTS_DIR, self.name)
            dialog = ResultDialog(self, result_dir=result_dir, result_name=self.name,
                                  image_list=self.entity_tree.image_list)
            dialog.CenterOnParent()
            dialog.Show()
            '''

            '''
            filename = os.path.join(self.working_dir_path(), svp.RESULTS_DIR, self.name) + svp.RESULT_LOG_EXT
            f = open(filename)

            info_panel = wx.Panel(parent, -1)
            info_panel.Hide()

            info_panel.SetBackgroundColour('white')
            info_log = wx.TextCtrl(info_panel, style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE)
            info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
            info_panel.SetSizer(info_panel_sizer)
            info_panel_sizer.Add(info_log, 1, wx.EXPAND|wx.LEFT, 10)
            for entry in f:
                if len(entry) > 27 and entry[4] == '-' and entry[7] == '-' and entry[13] == ':' and entry[16] == ':':
                    info_log.SetDefaultStyle(wx.TextAttr((26, 13, 171)))
                    info_log.AppendText(entry[:25])
                    if entry[25] == script.DEBUG:
                        info_log.SetDefaultStyle(wx.TextAttr((119, 29, 169)))
                    elif entry[25] == script.ERROR:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.RED))
                    elif entry[25] == script.WARNING:
                        info_log.SetDefaultStyle(wx.TextAttr((255, 96, 0)))
                    else:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))
                    info_log.AppendText('%s' % (entry[25:]))
                else:
                    info_log.AppendText('%s' % (entry))

            f.close()
            info_log.ShowPosition(0)
            info_panel.Show()
            # info_panel.Layout()

            return info_panel
            '''
        elif self.ext == svp.CSV_EXT:
            '''
            noise = np.random.normal
            n = 201
            x  = np.linspace(0, 100, n)
            y1 = np.sin(x/3.4)/(0.2*x+2) + noise(size=n, scale=0.1)
            y2 = 92 + 65*np.cos(x/16.) * np.exp(-x*x/7e3) + noise(size=n, scale=0.3)
            '''

            frame = wxmplot.PlotFrame()
            filename = os.path.join(self.working_dir_path(), svp.RESULTS_DIR, self.name)
            f = open(filename, 'r')
            names = f.readline().split(',')
            columns = len(names)
            value_arrays = []
            for i in range(columns):
                value_arrays.append([])

            base_time = None
            for line in f:
                values = line.split(',')
                if base_time is None:
                    base_time = float(values[0])
                t = round(float(values[0]) - base_time, 2)
                value_arrays[0].append(t)
                for i in range(1, columns):
                    try:
                        v = float(values[i])
                        value_arrays[i].append(v)
                    except Exception as e:
                        value_arrays[i].append('nan')
                        pass

            time_array = numpy.array(value_arrays[0])
            for i in range(1, columns):
                value_array = numpy.array(value_arrays[i])
                frame.oplot(time_array, value_array, label=names[i])

            '''
            r = numpy.recfromcsv(filename, case_sensitive=True)
            print(repr(r))
            print r.dtype
            names = r.dtype.names
            x = names[0]
            print r[x]
            for name in names[1:]:
                # print name, r[x], r[name]
                frame.oplot(r[x], r[name])
            '''


            # pframe.plot(x, y1, title='Test 2 Axes with different y scales',
            #            xlabel='x (mm)', ylabel='y1', ymin=-0.75, ymax=0.75)
            # pframe.oplot(x, y2, y2label='y2', side='right', ymin=0)

            frame.SetTitle(self.name)
            frame.Show()
            frame.ToggleWindowStyle(wx.STAY_ON_TOP)


class ScriptDirectory(Directory):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        Directory.__init__(self, name, entity_tree=entity_tree, parent=parent,
                           image=entity_tree.images['script_dir'], status_image=status_image)
        self.ops = {OP_DELETE: (self.op_delete, None),
                    OP_NEW_DIR: (self.op_new_dir, None)}

    def op_new_dir(self, event):
        Directory._op_new_dir(self, ScriptDirectory, image=self.entity_tree.images['script_dir'])

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        try:
            path = os.path.join(os.path.join(*self.path()), self.name)
            files = os.listdir(path)
            for f in files:
                file_path = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                if ext == svp.SCRIPT_EXT:
                    try:
                        self.add_entry(name, ScriptEntry, entity_tree=self.entity_tree,
                                       image=self.entity_tree.images['script'])
                        # script.load_script(file_path, lib_path)
                    except Exception as e:
                        raise UIError('Script directory scan error: %s' % str(e))
                else:
                    if os.path.isdir(file_path):
                        d = self.add_entry(f, ScriptDirectory, entity_tree=self.entity_tree,
                                           image=self.entity_tree.images['script_dir'])
                        d.scan()
        except Exception as e:
            raise UIError('Error scanning directory %s: %s' % (path, str(e)))

class SuitesDirectory(Directory):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        Directory.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image, status_image=status_image)
        self.ops = {OP_NEW_DIR: (self.op_new_dir, None),
                    OP_NEW_SUITE: (self.op_new_suite, None)}

    def op_new_dir(self, event):
        Directory._op_new_dir(self, SuiteDirectory, image=self.entity_tree.images['suite_dir'])

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        try:
            path = os.path.join(os.path.join(*self.path()), self.name)
            files = os.listdir(path)
            for f in files:
                try:
                    file_path = os.path.join(path, f)
                    name, ext = os.path.splitext(f)
                    if ext == svp.SUITE_EXT:
                        s = self.add_entry(name, SuiteEntry, entity_tree=self.entity_tree,
                                           image=self.entity_tree.images['suite'])
                        s.scan()
                        # if suite.contains_suite(suite.name) is True:
                        ### recovery???
                        # print 'Circular reference error - suite member contains reference to suite'
                    else:
                        if os.path.isdir(file_path):
                            d = self.add_entry(f, SuiteDirectory, entity_tree=self.entity_tree,
                                               image=self.entity_tree.images['suite_dir'])
                            d.scan()
                except Exception as e:
                    pass
                    # raise UIError('Error scanning directory %s: %s' % (path, str(e)))
        except Exception as e:
            raise UIError('Error scanning directory %s: %s' % (path, str(e)))

class SuiteDirectory(Directory):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        Directory.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image, status_image=status_image)
        self.ops = {OP_DELETE: (self.op_delete, None),
                    OP_NEW_DIR: (self.op_new_dir, None),
                    OP_NEW_SUITE: (self.op_new_suite, None)}

    def op_new_dir(self, event):
        Directory._op_new_dir(self, SuiteDirectory, image=self.entity_tree.images['suite_dir'])

    def op_delete(self, event):
        Directory.op_delete(self, event, msg='Are you sure you want to delete %s and all its contents '
                                             '(Suite members will not be deleted)?')

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        try:
            path = os.path.join(os.path.join(*self.path()), self.name)
            files = os.listdir(path)
            for f in files:
                try:
                    file_path = os.path.join(path, f)
                    name, ext = os.path.splitext(f)
                    if ext == svp.SUITE_EXT:
                        s = self.add_entry(name, SuiteEntry, entity_tree=self.entity_tree,
                                           image=self.entity_tree.images['suite'])
                        s.scan()
                        # if suite.contains_suite(suite.name) is True:
                        ### recovery???
                        # print 'Circular reference error - suite member contains reference to suite'
                    else:
                        if os.path.isdir(file_path):
                            d = self.add_entry(f, SuiteDirectory, entity_tree=self.entity_tree,
                                               image=self.entity_tree.images['suite_dir'])
                            d.scan()
                except Exception as e:
                    pass
                    # raise UIError('Error scanning directory %s: %s' % (path, str(e)))
        except Exception as e:
            raise UIError('Error scanning directory %s: %s' % (path, str(e)))

class TestsDirectory(Directory):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        Directory.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image, status_image=status_image)
        self.ops = {OP_NEW_DIR: (self.op_new_dir, None),
                    OP_NEW_TEST: (self.op_new_test, None)}

    def op_new_dir(self, event):
        Directory._op_new_dir(self, TestDirectory, image=self.entity_tree.images['test_dir'])

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        path = os.path.join(os.path.join(*self.path()), self.name)
        try:
            files = os.listdir(path)
            for f in files:
                file_path = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                if ext == svp.TEST_EXT:
                    self.add_entry(name, TestEntry, entity_tree=self.entity_tree,
                                   image=self.entity_tree.images['test'])
                else:
                    if os.path.isdir(file_path):
                        d = self.add_entry(f, TestDirectory, entity_tree=self.entity_tree,
                                           image=self.entity_tree.images['test_dir'])
                        # d = directory.add_dir(f, TestDirectory, entity_tree=self, image=images['test_dir'])
                        d.scan()
        except Exception as e:
            raise UIError('Error scanning directory %s: %s' % (path, str(e)))

def prompt_name(text, title, default):
    name = None
    dialog = wx.TextEntryDialog(None, text, title, default, style=wx.OK|wx.CANCEL)
    dialog.CenterOnParent()
    if dialog.ShowModal() == wx.ID_OK:
        name = dialog.GetValue()
    dialog.Destroy()
    return name

def prompt_new_test(parent, entity_tree, entity, title='New Test'):
    dialog = NewTestDialog(parent, entity_tree, entity, title=title)
    dialog.CenterOnParent()
    dialog.ShowModal()
    return (dialog.test_name.GetValue(), dialog.script_path.GetValue())


class TestDirectory(Directory):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        Directory.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image, status_image=status_image)
        self.ops = {OP_DELETE: (self.op_delete, None),
                    OP_NEW_DIR: (self.op_new_dir, None),
                    OP_NEW_TEST: (self.op_new_test, None)}

    def op_new_dir(self, event):
        Directory._op_new_dir(self, TestDirectory, image=self.entity_tree.images['test_dir'])

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        path = os.path.join(os.path.join(*self.path()), self.name)
        try:
            files = os.listdir(path)
            for f in files:
                file_path = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                if ext == svp.TEST_EXT:
                    self.add_entry(name, TestEntry, entity_tree=self.entity_tree,
                                   image=self.entity_tree.images['test'])
                else:
                    if os.path.isdir(file_path):
                        d = self.add_entry(f, TestDirectory, entity_tree=self.entity_tree,
                                           image=self.entity_tree.images['test_dir'])
                        # d = directory.add_dir(f, TestDirectory, entity_tree=self, image=images['test_dir'])
                        # d.expanded = d.get_working_dir().is_expanded(self.working_dir_relative_name())
                        d.scan()
        except Exception as e:
            raise UIError('Error scanning directory %s: %s' % (path, str(e)))

class ScriptEntry(EntityTreeEntry):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        EntityTreeEntry.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image,
                                 status_image = status_image)
        self.ext = svp.SCRIPT_EXT
        self.ops = {OP_DELETE: (self.op_delete, None),
                    OP_RUN: (self.op_run, None),
                    OP_MOVE: (self.op_move, None)}

    def op_move(self, event):
        path = self.relative_name()
        dlg = wx.TextEntryDialog(None, 'Move %s to:' % path, 'Move script', path)

        if dlg.ShowModal() == wx.ID_OK:
            scripts_path = self.scripts_dir_path()
            dlg_path = dlg.GetValue()
            if dlg_path:
                new_path, new_name = os.path.split(dlg_path)
                new_full_path = os.path.join(scripts_path, new_path)
                new_full_name = os.path.join(new_full_path, new_name) + svp.SCRIPT_EXT
                if os.path.isdir(new_full_path):
                    if not os.path.exists(new_full_name):
                        old_full_name = os.path.join(scripts_path, path) + svp.SCRIPT_EXT
                        try:
                            os.rename(old_full_name, new_full_name)
                            svp.script_update(self.tests_dir_path(), path, dlg_path)
                            # working_dir = self.get_working_dir()
                            # rel_path = script.PATH_SEP.join([svp.SUITES_DIR, path])
                            # if working_dir.is_expanded(rel_path):
                            #     working_dir.update_expanded(rel_path, False)
                            #     working_dir.update_expanded(script.PATH_SEP.join([svp.SUITES_DIR, dlg_path]), True)

                        except Exception as e:
                            wx.MessageBox('Error moving script %s: %s.' % (dlg_path, str(e)),
                                          caption='Move error', style=wx.OK | wx.ICON_ERROR)
                    else:
                        wx.MessageBox('Destination script name %s already exists.' % (dlg_path),
                                      caption='Destination error', style=wx.OK | wx.ICON_ERROR)
                else:
                    wx.MessageBox('Destination directory %s does not exist in Scripts.' % (new_path),
                                  caption='Destination error', style=wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox('No destination specified.', caption='Destination error', style=wx.OK | wx.ICON_ERROR)

        dlg.Destroy()
        self.get_working_dir().rescan()

    def is_script(self):
        return True

    def absolute_filename(self):
        path = self.path()
        path.append(self.name + svp.SCRIPT_EXT)
        return os.path.join(*path)

    def relative_path(self):
        path = []
        parent = self.parent
        while parent and parent.name is not svp.SCRIPTS_DIR:
            path.insert(0, parent.name)
            parent = parent.parent
        return path

    def relative_name(self):
        path = self.relative_path()
        path.append(self.name)
        return script.PATH_SEP.join(path)

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        path = os.path.join(os.path.join(*self.path()), self.name)
        try:
            files = os.listdir(path)
            for f in files:
                file_path = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                if ext == svp.TEST_EXT:
                    self.add_entry(name, TestEntry, entity_tree=self.entity_tree,
                                   image=self.entity_tree.images['test'])
                else:
                    if os.path.isdir(file_path):
                        d = self.add_entry(f, TestDirectory, entity_tree=self.entity_tree,
                                           image=self.entity_tree.images['test_dir'])
                        # d = directory.add_dir(f, TestDirectory, entity_tree=self, image=images['test_dir'])
                        d.scan()
        except Exception as e:
            raise UIError('Error scanning directory %s: %s' % (path, str(e)))

    def render_info(self, parent):
        path = self.path()
        path.append(self.name)
        path = os.path.join(*path)
        lib_path = os.path.join(self.working_dir_path(), svp.LIB_DIR)
        test_script = script.load_script(path, lib_path, path_list = svp.extended_path_list)

        info_panel = wx.Panel(parent, -1)
        info_panel.Hide()

        title = wx.Panel(info_panel, -1)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title.SetSizer(title_sizer)
        title.SetBackgroundColour('white')
        logo_sizer = wx.BoxSizer(wx.VERTICAL)
        logo_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bitmap = wx.StaticBitmap(parent=title, bitmap=wx.Bitmap(os.path.join(images_path, 'script_32.gif')))
        text = wx.StaticText(title, -1, test_script.name.split('.')[0])
        text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        title_sizer.Add(bitmap, 0, wx.ALIGN_BOTTOM)
        title_sizer.Add(text, 0, wx.ALIGN_BOTTOM|wx.LEFT, 16)
        title_sizer.Add(logo_sizer, 1, wx.EXPAND)
        logo_path = self.working_dir_path()
        for logo in test_script.info.logos:
            ### try to catch all exceptions if bitmap read fails
            bitmap = wx.Bitmap(os.path.join(logo_path, svp.SCRIPTS_DIR, logo))
            logo_h_sizer.Add(wx.StaticBitmap(parent=title, bitmap=bitmap), 0, wx.LEFT, 10)
        # logo_sizer.Add(logo_h_sizer, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)

        params_panel = wx.Panel(info_panel, -1)
        params_panel.panel_sizer = wx.GridBagSizer(hgap=30, vgap=0)
        params_panel.SetSizer(params_panel.panel_sizer)
        params_panel.SetBackgroundColour('white')
        self.render_group(params_panel, test_script.info.param_defs, test_script.info.param_defs.param_value,
                          test_script.info.param_defs, row=0)

        info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel.SetSizer(info_panel_sizer)
        info_panel_content_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel_content_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        info_panel_content_sizer.Add(params_panel, 0, wx.TOP)
        info_panel_sizer.Add(info_panel_content_sizer, 0, wx.ALL, 30)
        info_panel.Show()
        # info_panel.Layout()

        return info_panel

    def render_group(self, info_panel, param_defs, param_value, group, row=0, pad=0):
        if script.param_is_active(param_defs, group.qname, param_value) is not None:
            if group.name != script.SCRIPT_PARAM_ROOT:
                text = wx.StaticText(info_panel, -1, group.label)
                font = text.GetFont()
                font.SetWeight(wx.FONTWEIGHT_BOLD)
                text.SetFont(font)
                text.Wrap(TEXT_WRAP)
                info_panel.panel_sizer.Add(text, pos=(row, 0), border=pad, flag=wx.LEFT)
                pad += 20
            else:
                text = wx.StaticText(info_panel, -1, 'Default')
                font = text.GetFont()
                font.SetWeight(wx.FONTWEIGHT_BOLD)
                text.SetFont(font)
                info_panel.panel_sizer.Add(text, pos=(row, 1), border=pad, flag=wx.LEFT)
                text = wx.StaticText(info_panel, -1, 'Options')
                text.SetFont(font)
                info_panel.panel_sizer.Add(text, pos=(row, 2), border=pad, flag=wx.LEFT)
                pad += 5

            row += 1

            for g in group.param_groups:
                row = self.render_group(info_panel, param_defs, param_value, g, row=row, pad=pad)
            index_count = group.index_count
            index_start = group.index_start
            if index_count is not None:
                if type(index_count) == str:
                    index_count = param_value(index_count)
                if type(index_start) == str:
                    index_start = param_value(index_start)
                if index_count is not None and index_start is not None:
                    for i in range(index_start, index_start + index_count):
                        for param in group.params:
                            row = self.render_param(info_panel, param_defs, param_value, param, index=i, row=row,
                                                    pad=pad)
            else:
                for param in group.params:
                    index_count = param.index_count
                    index_start = param.index_start
                    if index_count is not None:
                        if type(index_count) == str:
                            index_count = param_value(index_count)
                        if type(index_start) == str:
                            index_start = param_value(index_start)
                        if index_count is not None and index_start is not None:
                            for i in range(index_start, index_start + index_count):
                                row = self.render_param(info_panel, param_defs, param_value, param, index=i, row=row,
                                                        pad=pad)
                    else:
                        row = self.render_param(info_panel, param_defs, param_value, param, index=None, row=row, pad=pad)
        return row

    def render_param(self, info_panel, param_defs, param_value, param, index=None, row=0, pad=0):
        if script.param_is_active(param_defs, param.qname, param_value) is not None:
            if index is not None:
                label =  '%s %s' % (param.label, index)
                if type(param.default) == dict:
                    value = param.value.get(index)
                else:
                    value = param.default
            else:
                label = param.label
                value = param.value

            text = wx.StaticText(info_panel, -1, label)
            text.Wrap(TEXT_WRAP)
            if param.desc is not None:
                text.SetToolTip(wx.ToolTip(param.desc))
            info_panel.panel_sizer.Add(text, pos=(row, 0), border=pad, flag=wx.LEFT)
            text = wx.StaticText(info_panel, -1, str(value))
            text.Wrap(TEXT_WRAP)
            info_panel.panel_sizer.Add(text, pos=(row, 1), border=0, flag=wx.LEFT)
            options = ''
            for v in param.values:
                options += '%s, ' % str(v)
            if options:
                options = options[:-2]
            text = wx.StaticText(info_panel, -1, str(options))
            text.Wrap(TEXT_WRAP)
            info_panel.panel_sizer.Add(text, pos=(row, 2), border=0, flag=wx.LEFT)
            row += 1
        return row


class SuiteEntry(EntityTreeEntry):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        EntityTreeEntry.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image,
                                 status_image=status_image)
        self.ext = svp.SUITE_EXT
        self.ops = {OP_COPY: (self.op_copy, None),
                    OP_DELETE: (self.op_delete, None),
                    OP_EDIT: (self.op_edit, None),
                    OP_RUN: (self.op_run, None),
                    OP_MOVE: (self.op_move, None)}
        self.info_panel = None

    def op_copy(self, event):
        path = self.relative_name()
        dlg = wx.TextEntryDialog(None, 'Copy %s to:' % path, 'Copy suite', path)

        if dlg.ShowModal() == wx.ID_OK:
            suites_path = self.suites_dir_path()
            dlg_path = dlg.GetValue()
            if dlg_path:
                new_path, new_name = os.path.split(dlg_path)
                new_full_path = os.path.join(suites_path, new_path)
                new_full_name = os.path.join(new_full_path, new_name) + svp.SUITE_EXT
                if os.path.isdir(new_full_path):
                    if not os.path.exists(new_full_name):
                        old_full_name = os.path.join(suites_path, path) + svp.SUITE_EXT
                        try:
                            shutil.copyfile(old_full_name, new_full_name)
                            if self.name != new_name:
                                suite = svp.Suite(filename=new_full_name)
                                suite.name = new_name
                                suite.to_xml_file()
                        except Exception as e:
                            wx.MessageBox('Error copying suite %s: %s.' % (dlg_path, str(e)),
                                          caption='Copy error', style=wx.OK | wx.ICON_ERROR)
                    else:
                        wx.MessageBox('Destination suite name %s already exists.' % (dlg_path),
                                      caption='Destination error', style=wx.OK | wx.ICON_ERROR)
                else:
                    wx.MessageBox('Destination directory %s does not exist in Suites.' % (new_path),
                                  caption='Destination error', style=wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox('No destination specified.', caption='Destination error', style=wx.OK | wx.ICON_ERROR)

        dlg.Destroy()
        self.get_working_dir().rescan()

    def op_move(self, event):
        path = self.relative_name()
        dlg = wx.TextEntryDialog(None, 'Move %s to:' % path, 'Move suite', path)

        if dlg.ShowModal() == wx.ID_OK:
            suites_path = self.suites_dir_path()
            dlg_path = dlg.GetValue()
            if dlg_path:
                new_path, new_name = os.path.split(dlg_path)
                new_full_path = os.path.join(suites_path, new_path)
                new_full_name = os.path.join(new_full_path, new_name) + svp.SUITE_EXT
                if os.path.isdir(new_full_path):
                    if not os.path.exists(new_full_name):
                        old_full_name = os.path.join(suites_path, path) + svp.SUITE_EXT
                        try:
                            os.rename(old_full_name, new_full_name)
                            if self.name != new_name:
                                suite = svp.Suite(filename=new_full_name)
                                suite.name = new_name
                                suite.to_xml_file()
                            svp.member_update(suites_path, path + svp.SUITE_EXT, dlg_path + svp.SUITE_EXT)
                            # working_dir = self.get_working_dir()
                            # rel_path = script.PATH_SEP.join([svp.SUITES_DIR, path])
                            # if working_dir.is_expanded(rel_path):
                            #     working_dir.update_expanded(rel_path, False)
                            #     working_dir.update_expanded(script.PATH_SEP.join([svp.SUITES_DIR, dlg_path]), True)

                        except Exception as e:
                            wx.MessageBox('Error moving suite %s: %s.' % (dlg_path, str(e)),
                                          caption='Move error', style=wx.OK | wx.ICON_ERROR)
                    else:
                        wx.MessageBox('Destination suite name %s already exists.' % (dlg_path),
                                      caption='Destination error', style=wx.OK | wx.ICON_ERROR)
                else:
                    wx.MessageBox('Destination directory %s does not exist in Suites.' % (new_path),
                                  caption='Destination error', style=wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox('No destination specified.', caption='Destination error', style=wx.OK | wx.ICON_ERROR)

        dlg.Destroy()
        self.get_working_dir().rescan()

    def op_delete(self, event):
        try:
            msg='Are you sure you want to delete %s (suite members will not be deleted, but all ' \
                'references will be removed from other suites)?' % (self.name)
            retCode = wx.MessageBox(msg, 'Delete suite', wx.YES_NO | wx.ICON_QUESTION)
            if (retCode == wx.YES):
                name = self.name
                if self.ext is not None:
                    name += self.ext
                path = self.path() + [name]
                path = os.path.join(*path)
                os.remove(path)
                self.entity_tree.Unselect()
                self.entity_tree.Delete(self.item)
                self.parent.delete(self)
                self.entity_tree.clear_detail()
                # remove references in all other suites
                suites_path = self.suites_dir_path()
                rel_path = self.relative_name() + self.ext
                svp.member_update(suites_path, rel_path, None)
                self.get_working_dir().rescan()
        except Exception as e:
            wx.MessageBox('Error deleting %s' % (str(e)), 'Delete Error', wx.OK | wx.ICON_ERROR)

    def op_edit(self, event):
        dialog = None
        try:
            dialog = EditSuiteDialog(self.parent, self)
            dialog.CenterOnParent()
            dialog.ShowModal()
            if dialog.result is not None:
                suite = svp.Suite(name=self.name)
                suite.members = dialog.members
                suite.params = dialog.params
                suite.globals = dialog.globals
                path = self.path() + [self.name + svp.SUITE_EXT]
                path = os.path.join(*path)
                suite.to_xml_file(filename=path)

                self.entity_tree.DeleteChildren(self.item)
                self.entries = []
                path = os.path.join(*self.path())
                self.scan()
                #self.entity_tree.scan_suite_members(self, suite, path)
                for e in self.entries:
                    e.build(self.entity_tree, self.item)

                self.get_working_dir().rescan()
                # self.entity_tree.render_detail(self)
        except Exception as e:
            wx.MessageBox('Error: %s' % traceback.format_exc(), caption='Error', style=wx.OK | wx.ICON_ERROR)
            if dialog is not None:
                dialog.Destroy()

    def is_suite(self):
        return True

    def get_circular_references(self):
        suites = []

    def absolute_filename(self):
        return os.path.join(os.path.join(*self.path()), self.name + svp.SUITE_EXT)

    def relative_path(self):
        path = []
        parent = self.parent
        while parent and parent.name is not svp.SUITES_DIR:
            path.insert(0, parent.name)
            parent = parent.parent
        return path

    def relative_name(self):
        path = self.relative_path()
        path.append(self.name)
        return script.PATH_SEP.join(path)

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        suite = svp.Suite(filename=self.absolute_filename())
        for m in suite.members:
            name, ext = os.path.splitext(m)
            if ext == svp.SUITE_EXT:
                s = self.add_entry(name, SuiteSuiteEntry, entity_tree=self.entity_tree,
                                   image=self.entity_tree.images['suite'], ordered=False, allow_duplicate=True)
                s.scan()

                # if suite.contains_suite(suite.name) is True:
                ### recovery???
                # print 'Circular reference error - suite member contains reference to suite'
            elif ext == svp.TEST_EXT:
                # file_path = os.path.join(parent.tests_dir_path(), os.path.normpath(m))
                self.add_entry(name, SuiteTestEntry, entity_tree=self.entity_tree,
                               image=self.entity_tree.images['test'], ordered=False, allow_duplicate=True)

    def render_info(self, parent):
        working_dir = os.path.join(self.working_dir_path())
        path = self.path()
        path.append(self.name + svp.SUITE_EXT)
        filename = os.path.join(*path)

        suite = svp.Suite(filename=filename)
        suite.merge_param_defs(working_dir)

        info_panel = wx.Panel(parent, -1)
        self.info_panel = info_panel
        info_panel.Hide()

        title = wx.Panel(info_panel, -1)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title.SetSizer(title_sizer)
        title.SetBackgroundColour('white')
        logo_sizer = wx.BoxSizer(wx.VERTICAL)
        logo_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bitmap = wx.StaticBitmap(parent=title, bitmap=wx.Bitmap(os.path.join(images_path, 'suite_32.gif')))
        text = wx.StaticText(title, -1, self.name.split('.')[0])
        text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        title_sizer.Add(bitmap, 0, wx.ALIGN_BOTTOM)
        title_sizer.Add(text, 0, wx.ALIGN_BOTTOM|wx.LEFT, 16)
        title_sizer.Add(logo_sizer, 1, wx.EXPAND)
        logo_path = self.working_dir_path()
        for logo in suite.logos:
            ### try to catch all exceptions if bitmap read fails
            bitmap = wx.Bitmap(os.path.join(logo_path, svp.SCRIPTS_DIR, logo))
            logo_h_sizer.Add(wx.StaticBitmap(parent=title, bitmap=bitmap), 0, wx.LEFT, 10)
        # logo_sizer.Add(logo_h_sizer, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.LEFT, 60)

        row = 0
        params_panel = wx.Panel(info_panel, -1)
        params_panel.panel_sizer = wx.GridBagSizer(hgap=30, vgap=0)
        params_panel.panel_sizer.SetEmptyCellSize((0,0))
        params_panel.SetSizer(params_panel.panel_sizer)
        params_panel.SetBackgroundColour('white')
        self.info_panel = params_panel

        row = self.render_globals(params_panel, globals=suite.globals, row=row)
        if suite.globals is True:
            self.render_group(params_panel, suite.param_defs, suite.param_value, suite.param_defs, row)

        info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel.SetSizer(info_panel_sizer)
        # info_panel_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        # info_panel_sizer.Add(params_panel, 1, wx.EXPAND|wx.TOP)
        # info_panel_content_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel_content_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel_content_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        info_panel_content_sizer.Add(params_panel, 1, wx.TOP)
        info_panel_sizer.Add(info_panel_content_sizer, 0, wx.ALL, 30)
        info_panel.Show()
        # info_panel.Layout()

        return info_panel

class TestEntry(EntityTreeEntry):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        EntityTreeEntry.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image,
                                 status_image=status_image)
        self.ext = svp.TEST_EXT
        self.ops = {OP_COPY: (self.op_copy, None),
                    OP_DELETE: (self.op_delete, None),
                    OP_EDIT: (self.op_edit, None),
                    OP_RUN: (self.op_run, None),
                    OP_MOVE: (self.op_move, None)}
        self.test_config = None
        self.test_script = None
        self.info_panel = None

    def op_copy(self, event):
        path = self.relative_name()
        dlg = wx.TextEntryDialog(None, 'Copy %s to:' % path, 'Copy test', path)

        if dlg.ShowModal() == wx.ID_OK:
            tests_path = self.tests_dir_path()
            dlg_path = dlg.GetValue()
            if dlg_path:
                new_path, new_name = os.path.split(dlg_path)
                new_full_path = os.path.join(tests_path, new_path)
                new_full_name = os.path.join(new_full_path, new_name) + svp.TEST_EXT
                if os.path.isdir(new_full_path):
                    if not os.path.exists(new_full_name):
                        old_full_name = os.path.join(tests_path, path) + svp.TEST_EXT
                        try:
                            shutil.copyfile(old_full_name, new_full_name)
                            if self.name != new_name:
                                config = script.ScriptConfig(filename=new_full_name)
                                config.name = new_name
                                config.to_xml_file()
                        except Exception as e:
                            wx.MessageBox('Error copying test %s: %s.' % (dlg_path, str(e)),
                                          caption='Copy error', style=wx.OK | wx.ICON_ERROR)
                    else:
                        wx.MessageBox('Destination test name %s already exists.' % (dlg_path),
                                      caption='Destination error', style=wx.OK | wx.ICON_ERROR)
                else:
                    wx.MessageBox('Destination directory %s does not exist in Tests.' % (new_path),
                                  caption='Destination error', style=wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox('No destination specified.', caption='Destination error', style=wx.OK | wx.ICON_ERROR)

        dlg.Destroy()
        self.get_working_dir().rescan()


    def op_move(self, event):
        path = self.relative_name()
        dlg = wx.TextEntryDialog(None, 'Move %s to:' % path, 'Move test', path)

        if dlg.ShowModal() == wx.ID_OK:
            tests_path = self.tests_dir_path()
            dlg_path = dlg.GetValue()
            if dlg_path:
                new_path, new_name = os.path.split(dlg_path)
                new_full_path = os.path.join(tests_path, new_path)
                new_full_name = os.path.join(new_full_path, new_name) + svp.TEST_EXT
                if os.path.isdir(new_full_path):
                    if not os.path.exists(new_full_name):
                        old_full_name = os.path.join(tests_path, path) + svp.TEST_EXT
                        try:
                            os.rename(old_full_name, new_full_name)
                            if self.name != new_name:
                                config = script.ScriptConfig(filename=new_full_name)
                                config.name = new_name
                                config.to_xml_file()
                            svp.member_update(self.suites_dir_path(), path + svp.TEST_EXT, dlg_path + svp.TEST_EXT)
                            working_dir = self.get_working_dir()
                            # rel_path = script.PATH_SEP.join([svp.SUITES_DIR, path])
                            # if working_dir.is_expanded(rel_path):
                            #     working_dir.update_expanded(rel_path, False)
                            #     working_dir.update_expanded(script.PATH_SEP.join([svp.SUITES_DIR, dlg_path]), True)

                        except Exception as e:
                            wx.MessageBox('Error moving test %s: %s.' % (dlg_path, str(e)),
                                          caption='Move error', style=wx.OK | wx.ICON_ERROR)
                    else:
                        wx.MessageBox('Destination test name %s already exists.' % (dlg_path),
                                      caption='Destination error', style=wx.OK | wx.ICON_ERROR)
                else:
                    wx.MessageBox('Destination directory %s does not exist in Tests.' % (new_path),
                                  caption='Destination error', style=wx.OK | wx.ICON_ERROR)
            else:
                wx.MessageBox('No destination specified.', caption='Destination error', style=wx.OK | wx.ICON_ERROR)

        dlg.Destroy()
        self.get_working_dir().rescan()

    def op_delete(self, event):
        try:
            msg='Are you sure you want to delete %s (all ' \
                'references will be removed from suites)?' % (self.name)
            retCode = wx.MessageBox(msg, 'Delete test', wx.YES_NO | wx.ICON_QUESTION)
            if (retCode == wx.YES):
                name = self.name
                if self.ext is not None:
                    name += self.ext
                path = self.path() + [name]
                path = os.path.join(*path)
                os.remove(path)
                self.entity_tree.Unselect()
                self.entity_tree.Delete(self.item)
                self.parent.delete(self)
                self.entity_tree.clear_detail()
                # remove references in all other suites
                suites_path = self.suites_dir_path()
                rel_path = self.relative_name() + self.ext
                svp.member_update(suites_path, rel_path, None)
                self.get_working_dir().rescan()
        except Exception as e:
            wx.MessageBox('Error deleting %s' % (str(e)), 'Delete Error', wx.OK | wx.ICON_ERROR)

    def op_edit(self, event):
        dialog = None
        try:
            self.load()
            dialog = EditTestDialog(self.parent, self, self.test_script)
            dialog.CenterOnParent()
            dialog.ShowModal()
            dialog.Destroy()
            if dialog.result is not None:
                script_config = script.ScriptConfig(name=self.test_config.name, script=self.test_config.script,
                                                    params=dialog.params)
                path = self.path() + [self.name + svp.TEST_EXT]
                path = os.path.join(*path)
                script_config.to_xml_file(filename=path)
                # re-render detail info after config update
                self.entity_tree.render_detail(self)
        except Exception as e:
            wx.MessageBox('Error: %s' % traceback.format_exc(), caption='Error', style=wx.OK | wx.ICON_ERROR)
            if dialog is not None:
                dialog.Destroy()

    def is_test(self):
        return True

    def absolute_filename(self):
        path = self.path()
        path.append(self.name + svp.TEST_EXT)
        return os.path.join(*path)

    def load(self):
        try:
            self.test_config = script.ScriptConfig(filename=self.absolute_filename())
        except Exception as e:
            raise UIError('Error loading test configuration: %s' % str(e))

        working_dir = self.working_dir_path()
        path = os.path.join(working_dir, svp.SCRIPTS_DIR, os.path.normpath(self.test_config.script))
        lib_path = os.path.join(working_dir, svp.LIB_DIR)

        self.test_script = script.load_script(path, lib_path, path_list = svp.extended_path_list)
        self.test_script.config = self.test_config

    def relative_path(self):
        path = []
        parent = self.parent
        while parent and parent.name is not svp.TESTS_DIR:
            path.insert(0, parent.name)
            parent = parent.parent
        return path

    def relative_name(self):
        path = self.relative_path()
        path.append(self.name)
        return script.PATH_SEP.join(path)

    def render_info(self, parent):
        self.load()
        info_panel = wx.Panel(parent, -1)
        self.info_panel = info_panel
        info_panel.Hide()

        title = wx.Panel(info_panel, -1)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title.SetSizer(title_sizer)
        title.SetBackgroundColour('white')
        logo_sizer = wx.BoxSizer(wx.VERTICAL)
        logo_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bitmap = wx.StaticBitmap(parent=title, bitmap=wx.Bitmap(os.path.join(images_path, 'test_32.gif')))
        text = wx.StaticText(title, -1, self.name.split('.')[0])
        text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        title_sizer.Add(bitmap, 0, wx.ALIGN_BOTTOM)
        title_sizer.Add(text, 0, wx.ALIGN_BOTTOM|wx.LEFT, 16)
        title_sizer.Add(logo_sizer, 1, wx.EXPAND)
        logo_path = self.working_dir_path()
        for logo in self.test_script.info.logos:
            ### try to catch all exceptions if bitmap read fails
            bitmap = wx.Bitmap(os.path.join(logo_path, svp.SCRIPTS_DIR, logo))
            logo_h_sizer.Add(wx.StaticBitmap(parent=title, bitmap=bitmap), 0, wx.LEFT, 10)
        # logo_sizer.Add(logo_h_sizer, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.LEFT, 60)

        row = 0
        params_panel = wx.Panel(info_panel, -1)
        self.info_panel = params_panel
        params_panel.panel_sizer = wx.GridBagSizer(hgap=30, vgap=0)
        params_panel.panel_sizer.SetEmptyCellSize((0,0))
        params_panel.SetSizer(params_panel.panel_sizer)
        params_panel.SetBackgroundColour('white')
        text = wx.StaticText(params_panel, -1, 'Script')
        font = text.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetFont(font)
        text.Wrap(TEXT_WRAP)
        params_panel.panel_sizer.Add(text, pos=(row, 0), border=20, flag=wx.LEFT)
        text = wx.StaticText(params_panel, -1, self.test_config.script)
        text.Wrap(TEXT_WRAP)
        params_panel.panel_sizer.Add(text, pos=(row, 1), flag=wx.LEFT)
        row += 1

        self.render_group(params_panel, self.test_script.info.param_defs, self.test_script.param_value,
                          self.test_script.info.param_defs, row)

        info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel.SetSizer(info_panel_sizer)
        # info_panel_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        # info_panel_sizer.Add(params_panel, 1, wx.EXPAND|wx.TOP)
        info_panel_content_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel_content_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        info_panel_content_sizer.Add(params_panel, 1, wx.TOP)
        info_panel_sizer.Add(info_panel_content_sizer, 0, wx.ALL, 30)
        info_panel.Show()
        # info_panel.Layout()

        return info_panel


class SuiteSuiteEntry(EntityTreeEntry):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        EntityTreeEntry.__init__(self, name,  entity_tree=entity_tree, parent=parent, image=image,
                                 status_image=status_image
        )
        self.ext = svp.SUITE_EXT
        self.ops = {OP_RUN: (self.op_run, None)}
        self.info_panel = None

    def op_move_down(self, event):
        pass

    def op_move_up(self, event):
        pass

    def op_remove(self, event):
        pass

    def is_suite(self):
        return True

    def absolute_filename(self):
        return os.path.join(self.working_dir_path(), svp.SUITES_DIR, os.path.normpath(self.name)) + svp.SUITE_EXT

    '''
    def param_value(self, name):
        value = self.parent_suite.param_value(name)
        if value is None:
            value = self.test_script.param_value(name)
        return value
    '''

    def scan(self):
        self.expanded = self.get_working_dir().is_expanded(self.working_dir_relative_name())
        suite = svp.Suite(filename=self.absolute_filename())
        for m in suite.members:
            name, ext = os.path.splitext(m)
            if ext == svp.SUITE_EXT:
                s = self.add_entry(name, SuiteSuiteEntry, entity_tree=self.entity_tree,
                                   image=self.entity_tree.images['suite'], ordered=False, allow_duplicate=True)
                s.scan()

                # if suite.contains_suite(suite.name) is True:
                ### recovery???
                # print 'Circular reference error - suite member contains reference to suite'
            elif ext == svp.TEST_EXT:
                # file_path = os.path.join(parent.tests_dir_path(), os.path.normpath(m))
                self.add_entry(name, SuiteTestEntry, entity_tree=self.entity_tree,
                               image=self.entity_tree.images['test'], ordered=False, allow_duplicate=True)

    def render_info(self, parent):
        parent_suite = self.get_parent_suite()
        suite = svp.Suite(filename=self.absolute_filename())
        suite.merge_param_defs(self.working_dir_path())

        info_panel = wx.Panel(parent, -1)
        self.info_panel = info_panel
        info_panel.Hide()

        title = wx.Panel(info_panel, -1)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title.SetSizer(title_sizer)
        title.SetBackgroundColour('white')
        logo_sizer = wx.BoxSizer(wx.VERTICAL)
        logo_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bitmap = wx.StaticBitmap(parent=title, bitmap=wx.Bitmap(os.path.join(images_path, 'suite_32.gif')))
        text = wx.StaticText(title, -1, self.name.split('.')[0])
        text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        title_sizer.Add(bitmap, 0, wx.ALIGN_BOTTOM)
        title_sizer.Add(text, 0, wx.ALIGN_BOTTOM|wx.LEFT, 16)
        title_sizer.Add(logo_sizer, 1, wx.EXPAND)
        logo_path = self.working_dir_path()
        for logo in suite.logos:
            ### try to catch all exceptions if bitmap read fails
            bitmap = wx.Bitmap(os.path.join(logo_path, svp.SCRIPTS_DIR, logo))
            logo_h_sizer.Add(wx.StaticBitmap(parent=title, bitmap=bitmap), 0, wx.LEFT, 10)
        # logo_sizer.Add(logo_h_sizer, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.LEFT, 60)

        row = 0
        params_panel = wx.Panel(info_panel, -1)
        params_panel.panel_sizer = wx.GridBagSizer(hgap=30, vgap=0)
        params_panel.panel_sizer.SetEmptyCellSize((0,0))
        params_panel.SetSizer(params_panel.panel_sizer)
        params_panel.SetBackgroundColour('white')
        self.info_panel = params_panel

        if parent_suite.globals is True:
            param_value = parent_suite.param_value
        else:
            param_value = suite.param_value

        row = self.render_globals(params_panel, globals=suite.globals, row=row)
        if suite.globals is True:
            self.render_group(params_panel, suite.param_defs, param_value, suite.param_defs, row)

        info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel.SetSizer(info_panel_sizer)
        # info_panel_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        # info_panel_sizer.Add(params_panel, 1, wx.EXPAND|wx.TOP)
        info_panel_content_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel_content_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        info_panel_content_sizer.Add(params_panel, 1, wx.TOP)
        info_panel_sizer.Add(info_panel_content_sizer, 0, wx.ALL, 30)
        info_panel.Show()
        # info_panel.Layout()

        return info_panel


class SuiteTestEntry(EntityTreeEntry):
    def __init__(self, name, entity_tree=None, parent=None, image=None, status_image=None):
        EntityTreeEntry.__init__(self, name, entity_tree=entity_tree, parent=parent, image=image,
                                 status_image=status_image)
        self.ext = svp.TEST_EXT
        self.ops = {OP_RUN: (self.op_run, None)}
        self.suite = None
        self.test_config = None
        self.test_script = None
        self.info_panel = None

    def op_move_down(self, event):
        pass

    def op_move_up(self, event):
        pass

    def op_remove(self, event):
        pass

    def is_test(self):
        return True

    def absolute_filename(self):
        return os.path.join(self.working_dir_path(), svp.TESTS_DIR, os.path.normpath(self.name)) + svp.TEST_EXT

    def load(self):
        try:
            self.test_config = script.ScriptConfig(filename=self.absolute_filename())
        except Exception as e:
            raise UIError('Error loading test configuration: %s' % str(e))

        working_dir = self.working_dir_path()
        path = os.path.join(working_dir, svp.SCRIPTS_DIR, os.path.normpath(self.test_config.script))
        lib_path = os.path.join(working_dir, svp.LIB_DIR)

        self.test_script = script.load_script(path, lib_path, path_list = svp.extended_path_list)
        self.test_script.config = self.test_config

    def param_value(self, name):
        value = self.suite.param_value(name)
        if value is None:
            value = self.test_script.param_value(name)
        return value

    def render_info(self, parent):
        self.suite = self.get_parent_suite()

        self.load()
        info_panel = wx.Panel(parent, -1)
        self.info_panel = info_panel
        info_panel.Hide()

        info_panel.panel_sizer = wx.GridBagSizer(hgap=30, vgap=0)
        info_panel.panel_sizer.SetEmptyCellSize((0,0))
        info_panel.SetBackgroundColour('white')

        title = wx.Panel(info_panel, -1)
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title.SetSizer(title_sizer)
        title.SetBackgroundColour('white')
        logo_sizer = wx.BoxSizer(wx.VERTICAL)
        logo_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        bitmap = wx.StaticBitmap(parent=title, bitmap=wx.Bitmap(os.path.join(images_path, 'test_32.gif')))
        text = wx.StaticText(title, -1, self.name.split('.')[0])
        text.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        title_sizer.Add(bitmap, 0, wx.ALIGN_BOTTOM)
        title_sizer.Add(text, 0, wx.ALIGN_BOTTOM|wx.LEFT, 16)
        title_sizer.Add(logo_sizer, 1, wx.EXPAND)
        logo_path = self.working_dir_path()
        for logo in self.test_script.info.logos:
            ### try to catch all exceptions if bitmap read fails
            bitmap = wx.Bitmap(os.path.join(logo_path, svp.SCRIPTS_DIR, logo))
            logo_h_sizer.Add(wx.StaticBitmap(parent=title, bitmap=bitmap), 0, wx.LEFT, 10)
        # logo_sizer.Add(logo_h_sizer, 0, wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM|wx.LEFT, 60)

        row = 0
        params_panel = wx.Panel(info_panel, -1)
        self.info_panel = params_panel
        params_panel.panel_sizer = wx.GridBagSizer(hgap=30, vgap=0)
        params_panel.panel_sizer.SetEmptyCellSize((0,0))
        params_panel.SetSizer(params_panel.panel_sizer)
        params_panel.SetBackgroundColour('white')
        text = wx.StaticText(params_panel, -1, 'Script')
        font = text.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetFont(font)
        text.Wrap(TEXT_WRAP)
        params_panel.panel_sizer.Add(text, pos=(row, 0), border=20, flag=wx.LEFT)
        text = wx.StaticText(params_panel, -1, self.test_config.script)
        text.Wrap(TEXT_WRAP)
        params_panel.panel_sizer.Add(text, pos=(row, 1), flag=wx.LEFT)
        row += 1

#        self.render_group(params_panel, self.test_script.info.param_defs, self.test_script, self.param_value
#                          self.test_script.info.param_defs, row)
        self.render_group(params_panel, self.test_script.info.param_defs, self.param_value,
                          self.test_script.info.param_defs, row)

        info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel.SetSizer(info_panel_sizer)
        # info_panel_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        # info_panel_sizer.Add(params_panel, 1, wx.EXPAND|wx.TOP)
        info_panel_content_sizer = wx.BoxSizer(wx.VERTICAL)
        info_panel_content_sizer.Add(title, 0, wx.EXPAND|wx.BOTTOM, 16)
        info_panel_content_sizer.Add(params_panel, 1, wx.TOP)
        info_panel_sizer.Add(info_panel_content_sizer, 0, wx.ALL, 30)
        info_panel.Show()
        # info_panel.Layout()

        return info_panel

'''
class AppWx(app.App):
    def __init__(self, window, app_id, config_file=None):
        self.window = window
        self.run_window = None
        self.dir_tree = None
        self.config_file = config_file
        app.App.__init__(self, app_id, config_file=config_file)

    def confirm(self, message):
        retCode = wx.MessageBox(message, caption='Confirm', style=wx.YES_NO | wx.ICON_QUESTION)
        if (retCode == wx.YES):
            return True
        return False

    def log(self, entry):
        if self.run_window:
            self.run_window.log(entry)
        # app.App.log(self, entry)

    def alertx(self, message):
        wx.MessageBox(message, caption='Alert', style=wx.OK | wx.ICON_ERROR)

    def state_update(self, status=None):
        if self.run_window:
            self.run_window.state_update(status)
        app.App.state_update(self)
'''

class ToolFrame(wx.Frame):

    menu_new_items = [(wx.ID_ANY, 'Directory...', '', None, OP_NEW_DIR),
                      (wx.ID_ANY, 'Suite...', '', None, OP_NEW_SUITE),
                      (wx.ID_ANY, 'Test...', '', None, OP_NEW_TEST)]

    menu_add_items = [(wx.ID_ANY, 'Suite...', '', None, OP_ADD_SUITE),
                      (wx.ID_ANY, 'Test...', '', None, OP_ADD_TEST)]

    menu_file_items = [(wx.ID_ANY, 'New', '', menu_new_items, None),
                       (wx.ID_ANY, '', '', None, None),
                       (wx.ID_ANY, 'Add SVP Directory...', '', None, OP_ADD_WORKING_DIR),
                       (wx.ID_ANY, '', '', None, None),
                       (wx.ID_EXIT, 'E&xit', '', None, OP_EXIT)]

    menu_edit_items = [(wx.ID_ANY, 'Edit', '', None, OP_EDIT),
                       (wx.ID_ANY, 'Move/Rename', '', None, OP_MOVE),
                       (wx.ID_ANY, 'Rescan', '', None, OP_RESCAN),
                       (wx.ID_ANY, '', '', None, None),
                       (wx.ID_DELETE, 'Delete', '', None, OP_DELETE),
                       (wx.ID_ANY, 'Delete All', '', None, OP_DELETE_ALL),
                       (wx.ID_REMOVE, 'Remove', '', None, OP_REMOVE)]
                       # (wx.ID_ANY, '', '', None, None),
                       # (wx.ID_ANY, 'Add', '', menu_add_items, None),
                       # (wx.ID_ANY,'Remove', '', None, OP_REMOVE),
                       # (wx.ID_ANY,'Move Up', '', None, OP_MOVE_UP),
                       # (wx.ID_ANY,'Move Down', '', None, OP_MOVE_DOWN)]
    menu_pkg_items = [(wx.ID_ANY, 'Library', '', None, OP_PKG)]
    menu_help_items = [(wx.ID_ANY, 'About', '', None, OP_ABOUT)]

    def __init__(self, parent, title, id):
        wx.Frame.__init__(self, parent, title=title, size=(1250,600), pos=(100,100))

        # initialize app
        self.parent = parent
        self.id = id
        # self.app_wx = AppWx(self.parent, id, config_file=svp.config_filename(APP_NAME))
        self.svp = svp.SVP(id)
        self.info_ctl = None
        self.menu_bar = None

        self.suite = None
        self.test = None
        self.script = None

        self.initpos = 380
        self.sp = wx.SplitterWindow(self, size=self.GetClientSize())
        '''
        self.entity_detail = wx.Panel(self.sp, -1)
        print 'entity detail = ', self.entity_detail
        self.entity_detail.SetBackgroundColour('green')
        '''
        self.entity_detail = wx.ScrolledWindow(self.sp)
        self.entity_detail.SetBackgroundColour('white')
        self.entity_detail.SetScrollbars(1, 1, 2000, 2000)

        entity_tree_panel = wx.Panel(self.sp)
        entity_tree_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        entity_tree_panel.SetSizer(entity_tree_panel_sizer)
        self.entity_tree = EntityTree(entity_tree_panel, dir_names=self.svp.get_directory_paths(),
                                      image_path=images_path, entity_window=self)
        entity_tree_panel_sizer.Add(self.entity_tree, 1, wx.EXPAND|wx.TOP, 5)
        self.entity_tree.scan()
        self.entity_tree.build()

        self.sp.SplitVertically(entity_tree_panel, self.entity_detail, self.initpos)
        self.sp.SetMinimumPaneSize(10)

        self.menu_bar = self.create_menu_bar()

        self.entity_detail_sizer = wx.BoxSizer()
        self.entity_detail.SetSizer(self.entity_detail_sizer) ###

        self.periodic_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.periodic_timer_event, self.periodic_timer)
        self.periodic_timer.Start(200)

    def create_menu_bar(self):
        ops = self.update_menu_ops()
        menu_bar = wx.MenuBar()
        file_menu, enabled = self.create_menu(ToolFrame.menu_file_items, ops)
        menu_bar.Append(file_menu, 'File')
        edit_menu, enabled = self.create_menu(ToolFrame.menu_edit_items, ops)
        menu_bar.Append(edit_menu, 'Edit')
        package_menu, enabled = self.create_menu(ToolFrame.menu_pkg_items, ops)
        menu_bar.Append(package_menu, 'Package')
        help_menu, enabled = self.create_menu(ToolFrame.menu_help_items, ops)
        menu_bar.Append(help_menu, 'Help')
        self.SetMenuBar(menu_bar)
        return menu_bar

    def create_menu(self, menu_items, ops=None):
        menu = wx.Menu()
        enabled = False
        for item in menu_items:
            if item[1]:
                if item[3] is not None:
                    submenu, submenu_enabled = self.create_menu(item[3], ops)
                    menu_item = menu.AppendSubMenu(submenu, item[1])
                    menu_item.Enable(submenu_enabled)
                else:
                    menu_item = menu.Append(item[0], item[1], item[2])
                    menu_item.Enable(False)
                if ops is not None:
                    func = ext_menu = None
                    op = ops.get(item[4])
                    if op is not None:
                        func = op[0]
                        ext_menu = op[1]
                    if func is not None:
                        self.Bind(wx.EVT_MENU, func, menu_item)
                        menu_item.Enable(True)
                        enabled = True
                    if ext_menu is not None:
                        pass
            else:
                menu.AppendSeparator()
        return (menu, enabled)

    def update_menu_ops(self, ops=None):
        if ops is None:
            ops = {}
        ops[OP_ADD_WORKING_DIR] = (self.OnAddWorkingDir, None)
        ops[OP_EXIT] = (self.OnExit, None)
        ops[OP_PKG] = (self.OnPackage, None)
        ops[OP_ABOUT] = (self.OnAbout, None)

        self.entity_tree.update_menu_ops(ops)
        return ops

    def update_menu(self):
        ops = self.update_menu_ops()
        pos = self.menu_bar.FindMenu('File')
        if pos != wx.NOT_FOUND:
            file_menu, enabled = self.create_menu(ToolFrame.menu_file_items, ops)
            self.menu_bar.Replace(pos, file_menu, 'File')
        pos = self.menu_bar.FindMenu('Edit')
        if pos != wx.NOT_FOUND:
            edit_menu, enabled = self.create_menu(ToolFrame.menu_edit_items, ops)
            self.menu_bar.Replace(pos, edit_menu, 'Edit')

    def OnAddWorkingDir(self, evt):
        dialog = wx.DirDialog(None, "Choose a directory:", style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            if path:
                self.svp.add_directory(path)
                self.entity_tree.add_working_dir(dialog.GetPath())
                self.entity_tree.scan()
                self.entity_tree.build()
        dialog.Destroy()

    def OnAbout(self, evt):
        wrapper = textwrap.TextWrapper(width=40,
                                       initial_indent=" " * 4,
                                       subsequent_indent=" " * 4,
                                       break_long_words=True,
                                       break_on_hyphens=True)
        description_str = ("The SunSpec System Validation Platform "
                                 "(SunSpec SVP) provides a framework for "
                                 "testing and validating SunSpec compliant "
                                 "devices and applications.")

        aboutInfo = wx.adv.AboutDialogInfo()
        aboutInfo.SetName("System Validation Platform")
        aboutInfo.SetVersion(VERSION)
        aboutInfo.SetDescription(wrapper.fill(description_str))
        #aboutInfo.SetCopyright("(C) 1992-2012")
        aboutInfo.SetWebSite("https://sunspec.org/sunspec-system-validation-platform-2/",
                             desc= "For mor information visit SunSpec website")
        #aboutInfo.AddDeveloper("My Self")
        wx.adv.AboutBox(aboutInfo)

    def OnPackage(self, evt):
        dialog = wx.DirDialog(None, "Choose a directory for python package:", style = wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            if path:
                sys.path.insert(1, path)
            for p in sys.path:
                print(p)

        dialog.Destroy()


    def OnExit(self, evt):
        self.periodic_timer.Stop()
        self.Close()

    def periodic_timer_event(self, event):
        # if self.svp is not None:
        #     self.svp.periodic()
        if run_context_list:
            for rc in run_context_list:
                rc.periodic()

class PackageDialog(wx.Dialog):
    def __init__(self, parent, title):
        super(PackageDialog, self).__init__(parent, title=title, size=(300, 200))

        self.InitUI()

    def InitUI(self):
        self.count = 0
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        self.text = wx.TextCtrl(pnl, size=(250, 25), style=wx.TE_READONLY)
        self.btn1 = wx.Button(pnl, label="Enter Text")
        self.Bind(wx.EVT_BUTTON, self.OnClick, self.btn1)

        hbox1.Add(self.text, proportion=1, flag=wx.ALIGN_CENTRE)
        hbox2.Add(self.btn1, proportion=1, flag=wx.RIGHT, border=10)

        vbox.Add((0, 30))
        vbox.Add(hbox1, flag=wx.ALIGN_CENTRE)
        vbox.Add((0, 20))
        vbox.Add(hbox2, proportion=1, flag=wx.ALIGN_CENTRE)

        pnl.SetSizer(vbox)
        self.Centre()
        self.Show(True)

    def OnClick(self, e):
        dlg = wx.TextEntryDialog(self, 'Enter Your Name', 'Text Entry Dialog')

        if dlg.ShowModal() == wx.ID_OK:
            self.text.SetValue("Name entered:" + dlg.GetValue())
        dlg.Destroy()

class ResultDialog(wx.Dialog):
    def __init__(self, parent=None, results=None, result_dir=None, result_name=None, title=None, image_list=None):
        wx.Dialog.__init__(self, parent=None, title='Result', size=(1250,600), pos=(100,100),
                           style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)
        self.parent = parent
        self.panel = RunPanel(parent=self, results=None, result_dir=result_dir, result_name=result_name, title=title)

class ResultPanel(wx.Panel):
    def __init__(self, parent, results=None, result_dir=None, result_name=None, title=None):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.result_dir = result_dir
        self.result_name = result_name
        self.entries = []

        if results is not None:
            self.result = results
        else:
            result_file = os.path.join(result_dir, (result_name + svp.RESULTS_EXT))
            self.result = rslt.Result()
            self.result.from_xml(filename=result_file)

        self.image_list = wx.ImageList(16, 16, True)
        self.images = {}

        self.sp = wx.SplitterWindow(self, size=self.GetClientSize(), style=wx.SP_BORDER)
        self.info_window = wx.Panel(self.sp)
        self.info_window.SetBackgroundColour('white')
        self.info_log = wx.TextCtrl(self.info_window, style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE)
        self.result_window = wx.ScrolledWindow(self.sp)
        self.result_window.SetBackgroundColour('white')
        self.result_window.SetScrollbars(1, 1, 2000, 2000)
        self.sp.SplitVertically(self.result_window, self.info_window, 300)
        self.sp.SetMinimumPaneSize(10)

        self.status_bar = wx.Panel(self)
        ###
        self.status_line = wx.Panel(self.status_bar, size=(0,1))
        self.status_line.SetBackgroundColour((192,192,192))
        self.status_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        self.status_bar.SetSizer(self.status_bar_sizer)
        self.status_text = wx.StaticText(self.status_bar, label='Running')
        self.status_bar_sizer.Add(self.status_line, 0, wx.EXPAND)
        status_bar_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        status_bar_v_sizer = wx.BoxSizer(wx.VERTICAL)
        status_bar_ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.status_bar_sizer.Add(status_bar_h_sizer, 0, wx.EXPAND|wx.LEFT, 5)
        status_bar_h_sizer.Add(self.status_text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        status_bar_h_sizer.Add(status_bar_v_sizer, 1, wx.EXPAND)
        status_bar_v_sizer.Add(status_bar_ctrl_sizer, 0, wx.ALIGN_CENTER)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.info_sizer = wx.BoxSizer(wx.VERTICAL)
        self.info_window.SetSizer(self.info_sizer)
        self.info_sizer.Add(self.info_log, 1, wx.EXPAND|wx.TOP|wx.LEFT, 5)

        self.result_window_sizer = wx.BoxSizer(wx.VERTICAL)
        self.result_window.SetSizer(self.result_window_sizer)
        self.result_tree = RunTree(self.result_window, result_dir=result_dir, result=self.result,
                                   info_window=self.info_window, info_sizer=self.info_sizer)
        self.result_tree.SetBackgroundColour('white')
        self.result_window_sizer.Add(self.result_tree, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.BOTTOM, 15)

        ###
        self.run_ctrl = RunCtrl(self.status_bar, self.parent)
        status_bar_ctrl_sizer.Add(self.run_ctrl.run_button, 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        status_bar_ctrl_sizer.Add(self.run_ctrl.stop_button, 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        self.sizer.Add(self.sp, 1, wx.EXPAND)
        self.sizer.Add(self.status_bar, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        '''
        self.run_ctrl = RunCtrl(self.status_bar, self)
        status_bar_ctrl_sizer.Add(self.run_ctrl.run_button, 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        status_bar_ctrl_sizer.Add(self.run_ctrl.stop_button, 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        self.info_window.SetSizer(self.info_sizer)
        self.info_sizer.Add(self.info_log, 1, wx.EXPAND|wx.TOP|wx.LEFT, 5)
        self.run_window_sizer.Add(self.run_tree_window, 1, wx.EXPAND)
        self.sizer.Add(self.sp, 1, wx.EXPAND)
        self.sizer.Add(self.status_bar, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        '''

    def run(self):
        pass
        # self.Layout()

    def update(self, status):
        self.status_text.SetLabelText(status)
        self.run_ctrl.update(status)

    def log(self, timestamp, level, message):
        # green (0, 102, 33)
        # purple (66, 0, 99)
        self.info_log.SetDefaultStyle(wx.TextAttr((26, 13, 171)))
        self.info_log.AppendText('%s ' % (timestamp))
        if level == script.ERROR:
            self.info_log.SetDefaultStyle(wx.TextAttr(wx.RED))
        elif level == script.WARNING:
            # self.info_log.SetDefaultStyle(wx.TextAttr((189, 102, 29)))
            self.info_log.SetDefaultStyle(wx.TextAttr((255, 96, 0)))
        elif level == script.DEBUG:
            self.info_log.SetDefaultStyle(wx.TextAttr((119, 29, 169)))
        else:
            self.info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        self.info_log.AppendText(' %s  %s\n' % (level, message))
        self.info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))


class ResultTree(treectrl.CustomTreeCtrl):

    def __init__(self, parent, entity=None, result_dir=None, result=None, image_path='', run_window=None,
                 info_window=None, info_sizer=None):
        treectrl.CustomTreeCtrl.__init__(self, parent, agwStyle=(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
                                                                 wx.TR_NO_LINES |
                                                                 treectrl.TR_TOOLTIP_ON_LONG_ITEMS |
                                                                 treectrl.TR_ELLIPSIZE_LONG_ITEMS |
                                                                 treectrl.TR_HAS_VARIABLE_ROW_HEIGHT))

        popup_menu_items = [(wx.ID_ANY, 'Open', '', None, OP_OPEN)]

        style=(wx.TR_TWIST_BUTTONS | wx.TR_NO_LINES | wx.TR_SINGLE | wx.TR_HIDE_ROOT)
        self.entity = entity
        self.result_dir = result_dir
        self.result = result
        self.run_window = run_window
        self.info_window = info_window
        self.info_sizer = info_sizer
        self.root = self.AddRoot('root')
        self.image_list = image_list

        self.entries = []
        self.name = None

        self.alt_image_list = wx.ImageList(16, 16, True)
        index = self.alt_image_list.Add(wx.Bitmap(image_closed))
        index = self.alt_image_list.Add(wx.Bitmap(image_closed))
        index = self.alt_image_list.Add(wx.Bitmap(image_open))
        index = self.alt_image_list.Add(wx.Bitmap(image_open))
        self.SetButtonsImageList(self.alt_image_list)

        self.SetImageList(image_list)
        self.SetStatusImageList(image_list)

        if self.result is not None:
            self.entries.append(RunEntry(run_tree=self, parent=self.root, result=self.result))

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)

        '''
        self.entity_window.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapsed)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpanded)
        '''

    def build(self, entity=None, result_dir=None, result=None):
        self.entity = entity
        self.result_dir = result_dir
        self.result = result
        self.entries = []
        self.name = None

        self.DeleteAllItems()

        self.results = build_result_tree(entity)

        if self.result is not None:
            self.entries.append(RunEntry(run_tree=self, parent=self.root, result=self.result))

        pass

    def render_info(self, entry):
        self.info_sizer.Clear(delete_windows=True)

        try:
            info = entry.render_info(self.info_window)
            if info is not None:

                # entity_window.entity_detail.SetBackgroundColour('blue')
                self.info_window.Refresh()
                self.info_window.SetBackgroundColour('white')
                self.info_sizer.Add(info, 1, wx.EXPAND|wx.ALL)
                self.info_window.Layout()
                #entity_window.entity_detail.Layout()
                # entity_window.entity_detail.Scroll(0, 0)
                ## self.info_window.FitInside()
        except Exception as e:
            wx.MessageBox('Error: %s' % traceback.format_exc(), caption='Error', style=wx.OK | wx.ICON_ERROR)

        # p = wx.Panel(self.info_window)
        # p. SetBackgroundColour('blue')
        # self.info_sizer.Add(p, 1, wx.EXPAND)


    def OnSelectionChanged(self, event):
        item = self.GetSelection()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                if entry.error is not None:
                    wx.MessageBox('Error: %s' % entry.error, caption='Error', style=wx.OK | wx.ICON_ERROR)
                else:
                    self.render_info(entry)


class ResultEntry_(object):
    def __init__(self, run_tree=None, parent=None, image=None, entity=None, result=None):
        self.run_tree = run_tree
        self.parent = parent
        self.name = None
        self.result = result
        self.image = image
        self.status_image = -1
        self.item = None
        self.error = None
        self.entries = []

        if result is not None:
            self.name = result.name
            t = self.result.type
            self.image = result_to_image.get(t, -1)
            if t == rslt.RESULT_TYPE_TEST or t == rslt.RESULT_TYPE_SCRIPT or t == rslt.RESULT_TYPE_FILE:
                self.status_image = result_to_image.get(self.result.status, images['none'])
            self.item = run_tree.AppendItem(parent, self.name, image=self.image, statusImage=self.status_image)
            result.ref = self
            run_tree.SetItemPyData(self.item, self)
            for r in result.results:
                self.entries.append(RunEntry(run_tree=run_tree, parent=self.item, result=r))
            self.item.Expand()

    def add_entry(self, result):
        # self.entries.append(RunEntry(run_tree=run_tree, parent=self.item, result=r))
        RunEntry(run_tree=self.run_tree, parent=self.item, result=result)

    def update(self, name=None, status=None):
        if name is not None:
            self.name = name
            self.run_tree.SetItemText(self.item, name)
        if status is not None:
            self.run_tree.SetItemStatusImage(self.item, result_to_image.get(status, images['none']))

    def render_info(self, info_window):
        limit = None
        if self.result.filename is not None:
            filename = os.path.join(self.run_tree.result_dir, self.result.filename)
            ext = os.path.splitext(filename)[1]
            if ext != svp.LOG_EXT:
                limit = 1000
            f = open(filename)

            info_panel = wx.Panel(info_window, -1)
            # info_panel.Hide()

            info_panel.SetBackgroundColour('white')
            info_log = wx.TextCtrl(info_panel, style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE)
            info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
            info_panel.SetSizer(info_panel_sizer)
            info_panel_sizer.Add(info_log, 1, wx.EXPAND|wx.LEFT|wx.TOP, 5)
            for entry in f:
                if len(entry) > 27 and entry[4] == '-' and entry[7] == '-' and entry[13] == ':' and entry[16] == ':':
                    info_log.SetDefaultStyle(wx.TextAttr((26, 13, 171)))
                    info_log.AppendText(entry[:25])
                    if entry[25] == script.DEBUG:
                        info_log.SetDefaultStyle(wx.TextAttr((119, 29, 169)))
                    elif entry[25] == script.ERROR:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.RED))
                    elif entry[25] == script.WARNING:
                        info_log.SetDefaultStyle(wx.TextAttr((255, 96, 0)))
                    else:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))
                    info_log.AppendText('%s' % (entry[25:]))
                else:
                    info_log.AppendText('%s' % (entry))
                if limit is not None:
                    limit -= 1
                    if limit <= 0:
                        info_log.AppendText('*** Data length truncated in summary display ***')
                        break

            f.close()
            info_log.ShowPosition(0)
            # info_panel.Show()

        else:
            info_panel = None

        return info_panel


class RunCtrl(object):
    def __init__(self, parent, run_panel):
        self.parent = parent
        self.run_panel = run_panel
        self.run_bitmap = wx.Bitmap(os.path.join(images_path, 'run_96.gif'), wx.BITMAP_TYPE_GIF)
        self.stop_bitmap = wx.Bitmap(os.path.join(images_path, 'stop_96.gif'), wx.BITMAP_TYPE_GIF)
        self.run_button = wx.BitmapButton(self.parent, bitmap=self.run_bitmap)
        self.run_button.Bind(wx.EVT_BUTTON, self.run)
        self.run_button.Disable()
        self.stop_button = wx.BitmapButton(self.parent, bitmap=self.stop_bitmap)
        self.stop_button.Bind(wx.EVT_BUTTON, self.stop)
        self.stop_button.SetFocus()
        self.stop_button.Enable()

    def update(self, status):
        if status == rslt.RESULT_RUNNING:
            self.stop_button.Enable()
            self.run_button.Disable()
        else:
            self.run_button.Enable()
            self.stop_button.Disable()

    def run(self, event):
        self.run_panel.run_tree.run()

    def stop(self, event):
        self.run_panel.run_tree.run_context.stop()


class RunPanel(wx.Panel):
    def __init__(self, parent, entity, title=None):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.entity = entity
        # self.entries = []

        self.image_list = wx.ImageList(16, 16, True)
        self.images = {}

        self.sp = wx.SplitterWindow(self, size=self.GetClientSize(), style=wx.SP_BORDER)
        self.info_window = wx.Panel(self.sp)
        self.info_window.SetBackgroundColour('white')
        self.info_log = wx.TextCtrl(self.info_window, style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE)
        self.run_window = wx.ScrolledWindow(self.sp)
        self.run_window.SetBackgroundColour('white')
        self.run_window.SetScrollbars(1, 1, 2000, 2000)
        self.sp.SplitVertically(self.run_window, self.info_window, 300)
        self.sp.SetMinimumPaneSize(10)

        self.status_bar = wx.Panel(self)
        ###
        self.status_line = wx.Panel(self.status_bar, size=(0,1))
        self.status_line.SetBackgroundColour((192,192,192))
        self.status_bar_sizer = wx.BoxSizer(wx.VERTICAL)
        self.status_bar.SetSizer(self.status_bar_sizer)
        self.status_text = wx.StaticText(self.status_bar, label='Running')
        self.status_bar_sizer.Add(self.status_line, 0, wx.EXPAND)
        status_bar_h_sizer = wx.BoxSizer(wx.HORIZONTAL)
        status_bar_v_sizer = wx.BoxSizer(wx.VERTICAL)
        status_bar_ctrl_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.status_bar_sizer.Add(status_bar_h_sizer, 0, wx.EXPAND|wx.LEFT, 5)
        status_bar_h_sizer.Add(self.status_text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        status_bar_h_sizer.Add(status_bar_v_sizer, 1, wx.EXPAND)
        status_bar_v_sizer.Add(status_bar_ctrl_sizer, 0, wx.ALIGN_CENTER)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.info_sizer = wx.BoxSizer(wx.VERTICAL)
        self.info_window.SetSizer(self.info_sizer)
        self.info_sizer.Add(self.info_log, 1, wx.EXPAND|wx.TOP|wx.LEFT, 5)

        self.run_window_sizer = wx.BoxSizer(wx.VERTICAL)
        self.run_window.SetSizer(self.run_window_sizer)
        self.run_tree = RunTree(self, self.run_window, entity=self.entity, info_window=self.info_window,
                                   info_sizer=self.info_sizer)
        self.run_tree.SetBackgroundColour('white')
        self.run_window_sizer.Add(self.run_tree, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.BOTTOM, 15)

        self.run_ctrl = RunCtrl(self.status_bar, self)
        status_bar_ctrl_sizer.Add(self.run_ctrl.run_button, 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)
        status_bar_ctrl_sizer.Add(self.run_ctrl.stop_button, 0, wx.TOP|wx.BOTTOM|wx.LEFT|wx.RIGHT, 5)

        self.sizer.Add(self.sp, 1, wx.EXPAND)
        self.sizer.Add(self.status_bar, 0, wx.EXPAND)
        self.SetSizer(self.sizer)

        self.run_tree.run()

    def update(self, status):
        self.status_text.SetLabelText(status)
        self.run_ctrl.update(status)

    def log(self, timestamp, level, message):
        # green (0, 102, 33)
        # purple (66, 0, 99)
        self.info_log.SetDefaultStyle(wx.TextAttr((26, 13, 171)))
        self.info_log.AppendText('%s ' % (timestamp))
        if level == script.ERROR:
            self.info_log.SetDefaultStyle(wx.TextAttr(wx.RED))
        elif level == script.WARNING:
            # self.info_log.SetDefaultStyle(wx.TextAttr((189, 102, 29)))
            self.info_log.SetDefaultStyle(wx.TextAttr((255, 96, 0)))
        elif level == script.DEBUG:
            self.info_log.SetDefaultStyle(wx.TextAttr((119, 29, 169)))
        else:
            self.info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        self.info_log.AppendText(' %s  %s\n' % (level, message))
        self.info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))


class RunTree(treectrl.CustomTreeCtrl):

    def __init__(self, panel, parent, entity=None, run_window=None, info_window=None, info_sizer=None):
        treectrl.CustomTreeCtrl.__init__(self, parent, agwStyle=(wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS |
                                                                 wx.TR_NO_LINES |
                                                                 treectrl.TR_TOOLTIP_ON_LONG_ITEMS |
                                                                 treectrl.TR_ELLIPSIZE_LONG_ITEMS |
                                                                 treectrl.TR_HAS_VARIABLE_ROW_HEIGHT))
        style=(wx.TR_TWIST_BUTTONS | wx.TR_NO_LINES | wx.TR_SINGLE | wx.TR_HIDE_ROOT)
        self.panel = panel
        self.entity = entity
        self.results_dir = entity.results_dir_path()
        self.results = None
        self.run_window = run_window
        self.info_window = info_window
        self.info_sizer = info_sizer
        self.root = None
        self.entries = []
        self.name = None
        self.run_context = None
        self.running = False

        self.alt_image_list = wx.ImageList(16, 16, True)
        index = self.alt_image_list.Add(wx.Bitmap(image_closed))
        index = self.alt_image_list.Add(wx.Bitmap(image_closed))
        index = self.alt_image_list.Add(wx.Bitmap(image_open))
        index = self.alt_image_list.Add(wx.Bitmap(image_open))
        self.SetButtonsImageList(self.alt_image_list)

        self.SetImageList(image_list)
        self.SetStatusImageList(image_list)

        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelectionChanged)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)

        '''
        self.entity_window.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)
        '''
        '''
        self.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.OnCollapsed)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.OnExpanded)
        '''

    def build(self):
        self.results = build_result_tree(self.entity)
        self.entries = []
        self.name = None

        self.DeleteAllItems()

        self.root = self.AddRoot('root')
        if self.results is not None:
            self.entries.append(RunEntry(run_tree=self, parent=self.root, result=self.results))

    def run(self):
        self.panel.info_log.Clear()

        self.build()
        self.run_context = RunContext(run_tree=self, svp_dir=self.entity.get_working_dir().name,
                                      results=self.results,
                                      results_name='__'.join(self.entity.working_dir_relative_path()[1:]))
        run_context_list.append(self.run_context)
        self.running = True
        # self.EnableChildren(self.root, False)
        self.SetSelectable(False)
        self.run_context.run()

    def complete(self):
        self.running = False
        self.SetSelectable(True)
        # self.EnableChildren(self.root, True)
        self.entity.get_results_dir().insert_results(self.results)
        run_context_list.remove(self.run_context)

    def render_info_log(self, entry):
        self.panel.info_log.Clear()
        entry.render_info_log(self.panel.info_log)

    def render_info(self, entry):
        self.info_sizer.Clear(delete_windows=True)

        try:
            info = entry.render_info(self.info_window)
            if info is not None:

                # entity_window.entity_detail.SetBackgroundColour('blue')
                self.info_window.Refresh()
                self.info_window.SetBackgroundColour('white')
                self.info_sizer.Add(info, 1, wx.EXPAND|wx.ALL)
                self.info_window.Layout()
                #entity_window.entity_detail.Layout()
                # entity_window.entity_detail.Scroll(0, 0)
                ## self.info_window.FitInside()
        except Exception as e:
            wx.MessageBox('Error: %s' % traceback.format_exc(), caption='Error', style=wx.OK | wx.ICON_ERROR)

        # p = wx.Panel(self.info_window)
        # p. SetBackgroundColour('blue')
        # self.info_sizer.Add(p, 1, wx.EXPAND)


    def OnSelectionChanged(self, event):
        item = self.GetSelection()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                if entry.error is not None:
                    wx.MessageBox('Error: %s' % entry.error, caption='Error', style=wx.OK | wx.ICON_ERROR)
                else:
                    if not self.running:
                        self.render_info_log(entry)

    def OnItemActivated(self, event):
        item = self.GetSelection()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                filename = os.path.join(self.run_context.results_dir, entry.result.filename)
                os.startfile(filename)

    '''
    def OnCollapsed(self, event):
        item = event.GetItem()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                entry.expand(False)
                #entry.expanded = False
                #entry.working_dir().expand(entry.working_dir_relative_name())
                #print '%s collapsed' % ()
        event.Skip()

    def OnExpanded(self, event):
        item = event.GetItem()
        if item is not None:
            entry = self.GetItemPyData(item)
            if entry is not None:
                entry.expand(True)
                #entry.expanded = True
                #print '%s expanded' % (entry.working_dir_relative_name())
        event.Skip()
    '''

class RunEntry(object):
    def __init__(self, run_tree=None, parent=None, image=None, entity=None, result=None):
        self.run_tree = run_tree
        self.parent = parent
        self.name = None
        self.result = result
        self.image = image
        self.status_image = -1
        self.item = None
        self.error = None
        self.entries = []

        if result is not None:
            self.name = result.name
            t = self.result.type
            # self.image = result_to_image.get(t, -1)
            self.image = result_image(self.result)
            if t == rslt.RESULT_TYPE_TEST or t == rslt.RESULT_TYPE_SCRIPT or t == rslt.RESULT_TYPE_FILE:
                self.status_image = result_to_image.get(self.result.status, images['none'])
            self.item = run_tree.AppendItem(parent, self.name, image=self.image, statusImage=self.status_image)
            result.ref = self
            run_tree.SetItemPyData(self.item, self)
            for r in result.results:
                self.entries.append(RunEntry(run_tree=run_tree, parent=self.item, result=r))
            self.item.Expand()

    def add_entry(self, result):
        # self.entries.append(RunEntry(run_tree=run_tree, parent=self.item, result=r))
        RunEntry(run_tree=self.run_tree, parent=self.item, result=result)

    def update(self, name=None, status=None):
        if name is not None:
            self.name = name
            self.run_tree.SetItemText(self.item, name)
        if status is not None:
            self.run_tree.SetItemStatusImage(self.item, result_to_image.get(status, images['none']))

    def render_info(self, info_window):
        limit = None
        if self.result.filename is not None:
            filename = os.path.join(self.run_tree.run_context.results_dir, self.result.filename)
            ext = os.path.splitext(filename)[1]
            if ext != svp.LOG_EXT:
                limit = 1000
            f = open(filename)

            info_panel = wx.Panel(info_window, -1)
            # info_panel.Hide()

            info_panel.SetBackgroundColour('white')
            info_log = wx.TextCtrl(info_panel, style=wx.TE_RICH|wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE)
            info_panel_sizer = wx.BoxSizer(wx.VERTICAL)
            info_panel.SetSizer(info_panel_sizer)
            info_panel_sizer.Add(info_log, 1, wx.EXPAND|wx.LEFT|wx.TOP, 5)
            for entry in f:
                if len(entry) > 27 and entry[4] == '-' and entry[7] == '-' and entry[13] == ':' and entry[16] == ':':
                    info_log.SetDefaultStyle(wx.TextAttr((26, 13, 171)))
                    info_log.AppendText(entry[:25])
                    if entry[25] == script.DEBUG:
                        info_log.SetDefaultStyle(wx.TextAttr((119, 29, 169)))
                    elif entry[25] == script.ERROR:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.RED))
                    elif entry[25] == script.WARNING:
                        info_log.SetDefaultStyle(wx.TextAttr((255, 96, 0)))
                    else:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))
                    info_log.AppendText('%s' % (entry[25:]))
                else:
                    info_log.AppendText('%s' % (entry))
                if limit is not None:
                    limit -= 1
                    if limit <= 0:
                        info_log.AppendText('*** Data length truncated in summary display ***')
                        break

            f.close()
            info_log.ShowPosition(0)
            # info_panel.Show()

        else:
            info_panel = None

        return info_panel

    def render_info_log(self, info_log):
        if self.result.filename is not None:
            limit = 0
            filename = os.path.join(self.run_tree.run_context.results_dir, self.result.filename)
            # "ext" extracts the extension from the filename
            ext = os.path.splitext(filename)[1]
            if ext != svp.LOG_EXT:
                limit = 1000
            f = open(filename)
            #TODO : need to be handle when it is a excel file
            for entry in f:
                if len(entry) > 27 and entry[4] == '-' and entry[7] == '-' and entry[13] == ':' and entry[16] == ':':
                    info_log.SetDefaultStyle(wx.TextAttr((26, 13, 171)))
                    info_log.AppendText(entry[:25])
                    if entry[25] == script.DEBUG:
                        info_log.SetDefaultStyle(wx.TextAttr((119, 29, 169)))
                    elif entry[25] == script.ERROR:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.RED))
                    elif entry[25] == script.WARNING:
                        info_log.SetDefaultStyle(wx.TextAttr((255, 96, 0)))
                    else:
                        info_log.SetDefaultStyle(wx.TextAttr(wx.BLACK))
                    info_log.AppendText('%s' % (entry[25:]))
                else:
                    info_log.AppendText('%s' % (entry))
                    if limit is not None:
                        limit -= 1
                        if limit <= 0:
                            info_log.AppendText('*** Data length truncated in summary display ***')
                            break

            f.close()
            # info_log.ShowPosition(0)

class RunContext(svp.RunContext):
    def __init__(self, run_tree=None, svp_dir=None, svp_file=None, results=None, results_name=None):
        self.run_tree = run_tree
        svp.RunContext.__init__(self, svp_dir=svp_dir, svp_file=svp_file, results=results, results_name=results_name)

    def add_result(self, result):
        self.active_result.ref.add_entry(result)
        svp.RunContext.add_result(self, result)

    def update_result(self, name=None, status=None, filename=None, params=None):
        if self.status != rslt.RESULT_STOPPED:
            if status is not None:
                self.run_tree.panel.update(status)
            self.active_result.ref.update(name=name, status=status)
            svp.RunContext.update_result(self, name=name, status=status, filename=filename, params=params)

    def log(self, timestamp, level, message):
        self.run_tree.panel.log(timestamp, level, message)
        # svp.RunContext.log(self, timestamp, level, message)

    def alert(self, message):
        wx.MessageBox(message, caption='Alert', style=wx.OK | wx.ICON_ERROR)

    def confirm(self, message):
        retCode = wx.MessageBox(message, caption='Confirm', style=wx.YES_NO | wx.ICON_QUESTION)
        if (retCode == wx.YES):
            return True
        return False

    def complete(self):
        if not self.active:
            self.run_tree.complete()
        svp.RunContext.complete(self)


class RunDialog(wx.Dialog):
    def __init__(self, entity=None, title=None):
        wx.Dialog.__init__(self, parent=None, title='Result', size=(1250,600), pos=(100,100),
                           style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX)
        self.entity = entity
        self.panel = RunPanel(parent=self, entity=entity, title=title)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        if event.CanVeto():
            if self.panel.run_tree.run_context.active:
                self.panel.run_tree.run_context.stop()
            count = 20
            while self.panel.run_tree.run_context.active:
                time.sleep(.1)
                self.panel.run_tree.run_context.periodic()
                if count <= 0:
                    self.panel.run_tree.run_context.terminate()
                    break
                count -= 1
        self.Destroy()


class Tool(object):
    def __init__(self):
        self.xyz = None
        try:
            import win32api

            info = win32api.GetVolumeInformation('C:\\')
            self.xyz = int((info[1]) & 0xffffffff)
        except Exception:
            pass

    def run(self, args=None):
        if args is not None:
            try:
                svp_cmd = svp.SVP(self.id)
                svp_cmd.run({'svp_dir': args.svp_dir,
                             'svp_file': args.target})
                '''
                app_cmd.run(args.svp_dir, args.target, args.result)
                while app_cmd.process is not None and app_cmd.running:
                    app_cmd.periodic()
                    time.sleep(.2)
                '''
            except Exception as e:
                # raise
                print ('sunssvp: error: {}'.format((e)))
                return 1
        else:
            self.wx_app = wx.App(False)
            global wx_app
            wx_app = self.wx_app
            try:
                init_image_list()
                self.frm = ToolFrame(None, APP_LABEL, 111)
                # self.frm.ToggleWindowStyle(wx.STAY_ON_TOP)
                self.frm.Show()
                self.wx_app.SetTopWindow(self.frm)

                self.wx_app.MainLoop()
            except Exception as e:
                wx.MessageBox('Error: %s' % traceback.format_exc(), caption='Error', style=wx.OK | wx.ICON_ERROR)

def main(args=None):
    tool = Tool()
    return tool.run(args)

if __name__ == "__main__":

    # sys.stdout = sys.stderr = open(os.path.join(svp.trace_dir(), 'sunssvp.log'), "w", buffering=0)

    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()

    args = None
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(prog=APP_PROG_NAME)
        parser.add_argument('svp_dir', help='SVP directory')
        parser.add_argument('target', help='suite/test/script in SVP directory')
        args = parser.parse_args()

    err = main(args)
    sys.exit(err)
