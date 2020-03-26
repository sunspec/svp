
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



import os
import xml.etree.ElementTree as ET
import csv
import math
import xlsxwriter
import natsort

RESULT_TYPE_RESULT = 'result'
RESULT_TYPE_SUITE = 'suite'
RESULT_TYPE_TEST = 'test'
RESULT_TYPE_SCRIPT = 'script'
RESULT_TYPE_FILE = 'file'

type_ext = {RESULT_TYPE_SUITE: '.ste',
            RESULT_TYPE_TEST: '.tst',
            RESULT_TYPE_SCRIPT: '.py'}

RESULT_RUNNING = 'Running'
RESULT_STOPPED = 'Stopped'
RESULT_COMPLETE = 'Complete'
RESULT_PASS = 'Pass'
RESULT_FAIL = 'Fail'

PARAM_TYPE_STR = 'string'
PARAM_TYPE_INT = 'int'
PARAM_TYPE_FLOAT = 'float'
PARAM_TYPE_BOOL = 'bool'

param_types = {'int': int, 'float': float, 'string': str, 'bool': bool,
               int: 'int', float: 'float', str: 'string', bool: 'bool'}

RESULT_TAG = 'result'
RESULT_ATTR_NAME = 'name'
RESULT_ATTR_TYPE = 'type'
RESULT_ATTR_STATUS = 'status'
RESULT_ATTR_FILENAME = 'filename'
RESULT_PARAMS = 'params'
RESULT_PARAM = 'param'
RESULT_PARAM_ATTR_NAME = 'name'
RESULT_PARAM_ATTR_TYPE = 'type'
RESULT_RESULTS = 'results'

INDEX_COL_FILE = 0
INDEX_COL_DESC = 1
INDEX_COL_NOTES = 2

index_hdr = [('File', 30),
             ('Description', 80),
             ('Notes', 80)]

XL_COL_WIDTH_DEFAULT = 10

def xl_col(index):
    return chr(index + 65)

def find_result(results_dir, result_dir):
    r_target = None
    rlt_name = os.path.split(results_dir)[1]
    rlt_file = os.path.join(results_dir, rlt_name) + '.rlt'
    path = os.path.normpath(result_dir)
    path = path.split(os.sep)
    r = Result()
    r.from_xml(filename=rlt_file)
    r_target = r.find(path)
    return r_target

def result_workbook(file, results_dir, result_dir, index=True):
    r = find_result(results_dir, result_dir)
    if r is not None:
        r.to_xlsx(filename=os.path.join(results_dir, result_dir, file), results_dir=results_dir, index=index,
                  index_row=0)
    else:
        raise ResultError('Error creating summary workbook - resource not found: %s %s' % (results_dir, result_dir))


class ResultError(Exception):
    pass


class Result(object):

    def __init__(self, name=None, type=None, status=None, filename=None, params=None, result_path=None):
        self.name = name
        self.type = type
        self.status = status
        self.filename = filename
        self.params = []
        self.result_path = result_path
        self.ref = None
        self.results_index = 0
        if params is not None:
            self.params = params
        else:
            self.params = {}
        self.results = []

    def __str__(self):
        return self.to_str()

    def find(self, path):
        result = None
        for r in self.results:
            if r.name == path[0]:
                if len(path) > 1:
                    result = r.find(path[1:])
                else:
                    result = r
        return result

    def next_result(self):
        if self.results_index < len(self.results):
            result = self.results[self.results_index]
            self.results_index += 1
            return result

    def add_result(self, result):
        self.results.append(result)

    def file(self):
        return self.name + type_ext.get(self.type, '')

    def to_str(self, indent=''):
        s = '%sname = %s  type = %s  status = %s  filename = %s\n%s  params = %s\n%s  results = \n  ' % (
            indent, self.name, self.type, self.status, self.filename, indent, self.params, indent
        )
        indent += '  '
        for r in self.results:
            s += '%s' % (r.to_str(indent=indent))
        return s

    def from_xml(self, element=None, filename=None):
        if element is None and filename is not None:
            element = ET.ElementTree(file=filename).getroot()
            self.result_path, file = os.path.split(filename)
        if element is None:
            raise ResultError('No xml document element')
        if element.tag != RESULT_TAG:
            raise ResultError('Unexpected result root element: %s' % (element.tag))
        self.name = element.attrib.get(RESULT_ATTR_NAME)
        self.type = element.attrib.get(RESULT_ATTR_TYPE)
        self.status = element.attrib.get(RESULT_ATTR_STATUS)
        self.filename = element.attrib.get(RESULT_ATTR_FILENAME)
        self.params = {}
        self.results = []
        if self.name is None:
            raise ResultError('Result name missing')

        for e in element.findall('*'):
            if e.tag == RESULT_PARAMS:
                for e_param in e.findall('*'):
                    if e_param.tag == RESULT_PARAM:
                        name = e_param.attrib.get(RESULT_PARAM_ATTR_NAME)
                        param_type = e_param.attrib.get(RESULT_PARAM_ATTR_TYPE)
                        if name:
                            vtype = param_types.get(param_type, str)
                            self.params[name] = vtype(e_param.text)
            elif e.tag == RESULT_RESULTS:
                for e_param in e.findall('*'):
                    if e_param.tag == RESULT_TAG:
                        result = Result(result_path=self.result_path)
                        self.results.append(result)
                        result.from_xml(e_param)

    def to_xml(self, parent=None, filename=None):
        attr = {}
        if self.name:
            attr[RESULT_ATTR_NAME] = self.name
        if self.type:
            attr[RESULT_ATTR_TYPE] = self.type
        if self.status:
            attr[RESULT_ATTR_STATUS] = self.status
        if self.filename:
            attr[RESULT_ATTR_FILENAME] = self.filename
        if parent is not None:
            e = ET.SubElement(parent, RESULT_TAG, attrib=attr)
        else:
            e = ET.Element(RESULT_TAG, attrib=attr)

        e_params = ET.SubElement(e, RESULT_PARAMS)

        params = natsort.natsorted(self.params, key=self.params.get)
        for p in params:
            value_type = None
            value_str = None
            attr = {RESULT_PARAM_ATTR_NAME: p}
            value = self.params.get(p)
            if value is not None:
                value_type = param_types.get(type(value), PARAM_TYPE_STR)
                value_str = str(value)

            if value_type is not None:
                attr[RESULT_PARAM_ATTR_TYPE] = value_type

            e_param = ET.SubElement(e_params, RESULT_PARAM, attrib=attr)
            if value_str is not None:
                e_param.text = value_str

        e_results = ET.SubElement(e, RESULT_RESULTS)
        for r in self.results:
            r.to_xml(e_results)

        return e

    def to_xml_str(self, pretty_print=False):
        e = self.to_xml()

        if pretty_print:
            xml_indent(e)

        return ET.tostring(e, encoding='unicode')

    def to_xml_file(self, filename=None, pretty_print=True, replace_existing=True):
        xml = self.to_xml_str(pretty_print)
        if filename is None and self.filename is not None:
            filename = self.filename

        if filename is not None:
            if replace_existing is False and os.path.exists(filename):
                raise ResultError('File %s already exists' % (filename))
            f = open(filename, 'w')
            f.write(xml)
            f.close()
        else:
            print (xml)

    def to_xlsx(self, wb=None, filename=None, results_dir=None, index=True, index_row=0):
        print ('to_xlsx: {} {}'.format (wb, filename))
        result_wb = wb
        if result_wb is None:
            result_wb = ResultWorkbook(filename=filename)
            if index:
                result_wb.add_index()
                index_row = 1
        if self.type == RESULT_TYPE_FILE:
            name, ext = os.path.splitext(self.filename)
            if ext == '.csv':
                index_row = result_wb.add_csv_file(os.path.join(results_dir, self.filename), self.name,
                                                   relative_value_names = ['TIME'], params=self.params,
                                                   index_row=index_row)
        print ('results = {}'.format(self.results))
        for r in self.results:
            print ('result in: {}'.format(self.filename))
            index_row = r.to_xlsx(wb=result_wb, results_dir=results_dir, index=index, index_row=index_row)
            print ('result out: {}'.format(self.filename))
        if wb is None:
            result_wb.close()

        return index_row


class ResultWorkbook(object):

    def __init__(self, filename):
        self.wb = xlsxwriter.Workbook(filename)
        self.ws_index = None
        self.hdr_format = self.wb.add_format()
        self.link_format = self.wb.add_format({'color': 'blue', 'underline': 1})

        self.hdr_format.set_text_wrap()
        self.hdr_format.set_align('center')
        self.hdr_format.set_align('vcenter')
        self.hdr_format.set_bold()

        self.link_format.set_align('center')
        self.link_format.set_align('vcenter')

    def add_index(self):
        print ('add_index')
        self.ws_index = self.wb.add_worksheet('Index')
        col = 0
        for i in range(len(index_hdr)):
            width = index_hdr[i][1]
            if width:
                self.ws_index.set_column(i, i, width)
            self.ws_index.write(0, col,index_hdr[i][0], self.hdr_format)
            col += 1

    def add_index_entry(self, title, index_row, desc=None, notes=None):
        print ('add_index_entry: {}'.format(title))
        self.ws_index.write_url(index_row, INDEX_COL_FILE, 'internal:%s!A1' % (title),
                                       string=title)
        if desc is not None:
            self.ws_index.write(index_row, INDEX_COL_DESC, desc)
        if notes is not None:
            self.ws_index.write(index_row, INDEX_COL_NOTES, notes)
        return index_row + 1


    def add_chart(self, ws, params=None, index_row=None):
        print ('add chart')
        # get fieldnames in first row of worksheet
        colors = ['blue', 'green', 'purple', 'orange', 'red', 'brown', 'yellow']
        color_idx = 0
        point_names = params.get('plot.point_names', [])

        x_points = []
        y_points = []
        y2_points = []
        if params is not None:
            points = params.get('plot.x.points')
            if points is not None:
                x_points = [x.strip() for x in points.split(',')]
            points = params.get('plot.y.points')
            if points is not None:
                y_points = [x.strip() for x in points.split(',')]
            points = params.get('plot.y2.points')
            if points is not None:
                y2_points = [x.strip() for x in points.split(',')]

        title = params.get('plot.title', '')
        # chartsheet = self.wb.add_chartsheet(title)
        ws_chart = self.wb.add_worksheet(title)
        if index_row is not None:
            index_row = self.add_index_entry(title, index_row)

        chart = self.wb.add_chart({'type': 'scatter', 'subtype': 'straight'})
        # chartsheet.set_chart(chart)
        ws_chart.insert_chart('A1', chart, {'x_offset': 25, 'y_offset': 10})

        chart.set_title({'name': title})
        chart.set_size({'width': 1200, 'height': 600})
        chart.set_x_axis({'name': params.get('plot.x.title', '')})
        chart.set_y_axis({'name': params.get('plot.y.title', '')})
        chart.set_y2_axis({'name': params.get('plot.y2.title', '')})
        chart.set_style(2)
        print ('ws name = {}'.format(ws.get_name()))

        # chart.x_axis.title = params.get('plot.x.title', '')
        # chart.y_axis.title = params.get('plot.y.title', '')

        count = params.get('plot.point_value_count', 1)
        ws_name = ws.get_name()
        categories = []

        if len(x_points) > 0:
            # only support one x point for now
            name = x_points[0]
            try:
                # col = point_names.index(name) + 1
                # categories = [ws_name, 2, 0, count + 1, 0]
                col_index = point_names.index(name)
                col = xl_col(col_index)
                categories = '=%s!$%s$%s:$%s$%s' % (ws_name, col, 2, col, count + 1)
            except ValueError:
                print ('Value error for x point: {}'.format(name))

        if len(y_points) > 0:
            for name in y_points:
                try:
                    min_error = params.get('plot.%s.min_error' % name)
                    max_error = params.get('plot.%s.max_error' % name)
                    print ('min_error, max_error = {} {}'.format(min_error, max_error))
                    col_index = point_names.index(name)
                    col = xl_col(col_index)
                    line_color = params.get('plot.%s.color' % name, colors[color_idx])
                    point = params.get('plot.%s.point' % name, 'False')
                    if point == 'True':
                        marker = {'type': 'circle',
                                  'size': 5,
                                  # 'fill': {'color': line_color}
                        }
                    else:
                        marker = {}
                    series = {
                        'name': name,
                        'categories': categories,
                        # 'values': [ws_name, 2, col, count, col],
                        'values': '=%s!$%s$%s:$%s$%s' % (ws_name, col, 2, col, count + 1),
                        # 'line': {'color': line_color, 'width': 1.5},
                        'line': {'width': 1.5},
                        'marker' : marker,
                    }
                    if min_error and max_error:
                        min_col = xl_col(point_names.index(min_error))
                        max_col = xl_col(point_names.index(max_error))
                        min_values = '=%s!$%s$%s:$%s$%s' % (ws_name, min_col, 2, min_col, count + 1)
                        max_values = '=%s!$%s$%s:$%s$%s' % (ws_name, max_col, 2, max_col, count + 1)
                        print ('min_values = %s'.format(min_values))
                        print ('max_values = %s'.format(max_values))
                        series['y_error_bars'] = {
                            'type': 'custom',
                            'direction': 'both',
                            # 'value': 10
                            'plus_values': max_values,
                            'minus_values': min_values
                        }
                    print ('series = {}'.format(series))
                    chart.add_series(series)
                    color_idx += 1

                except ValueError:
                    print ('Value error for y1 point: %s'.format (name))

        if len(y2_points) > 0:
            for name in y2_points:
                try:
                    col = point_names.index(name)
                    line_color = params.get('plot.%s.color' % name, colors[color_idx])
                    point = params.get('plot.%s.point' % name, 'False')
                    if point == 'True':
                        marker = {'type': 'circle',
                                  'size': 5,
                                  # 'fill': {'color': line_color}
                        }
                    else:
                        marker = {}
                    chart.add_series({
                        'name': name,
                        'categories': categories,
                        'values': [ws_name, 2, col, count, col],
                        # 'line': {'color': line_color, 'width': 1.5},
                        'line': {'width': 1.5},
                        'marker' : marker,
                        'y2_axis': 1
                    })

                except ValueError:
                    print ('Value error for y2 point: {}'.format(name))

        return index_row

    def add_csv_file(self, filename, title, relative_value_names=None, params=None, index_row=None):
        print ('add_csv_file: {}'.format (title))
        col_width = []
        line = 1
        ws = self.wb.add_worksheet(title)
        if index_row is not None:
            index_row = self.add_index_entry(title, index_row)
        f = None
        relative_value_index = []
        relative_value_start = []
        if relative_value_names is None:
            relative_value_names = []
        if params is None:
            params = {}
        try:
            f = open(filename)
            '''
            reader = csv.reader(f, skipinitialspace=True)
            print 'reader = %s %s' % (filename, reader)
            for row in reader:
            '''
            print ('filename = {} {}'.format (filename, f))
            for rec in f:
                row = [x.strip() for x in rec.split(',')]
                # print 'row = %s' % (row)
                for i in range(len(row)):
                    try:
                        v = float(row[i])
                        if math.isnan(v) or math.isinf(v):
                            row[i] = ''
                        else:
                            row[i] = v
                    except ValueError:
                        pass
                    # adjust column width if necessary
                    width = len(str(row[i])) + 4
                    if width < XL_COL_WIDTH_DEFAULT:
                        width = XL_COL_WIDTH_DEFAULT
                    try:
                        curr_width = col_width[i]
                    except IndexError:
                        curr_width = 0
                    if width > curr_width:
                        col_width.insert(i, width)
                        ws.set_column(i, i, width)
                # find fields to be treated as relative value
                if line == 1:
                    params['plot.point_names'] = row
                    for i in range(len(row)):
                        width = len(row[i]) + 4
                        if width < XL_COL_WIDTH_DEFAULT:
                            width = XL_COL_WIDTH_DEFAULT
                        ws.set_column(i, i, width)
                    if relative_value_names is not None:
                        for name in relative_value_names:
                            try:
                                index = row.index(name)
                                relative_value_index.append(index)
                            except ValueError:
                                print ('Value error for relative value name: {}'.format (name))
                # get initial value for relative value fields
                elif line == 2:
                    for index in relative_value_index:
                        relative_value_start.append(row[index])
                        row[index] = 0
                else:
                    for index in relative_value_index:
                        row[index] = row[index] - relative_value_start[index]
                ws.write_row(line - 1, 0, row)
                line += 1
            params['plot.point_value_count'] = line - 1

            if title[-4:] == '.csv':
                chart_title = title[:-4]
            else:
                chart_title = title + '_chart'

            print ('params - plot: {} - {}'.format(params, params.get('plot.title')))
            if params is not None and params.get('plot.title') is not None:
                index_row = self.add_chart(ws, params=params, index_row=index_row)

        except Exception as e:
            print ('add_csv_file error: {}'.format(e))
            raise
        finally:
            if f:
                f.close()

        return index_row

    def save(self, filename=None):
        pass

    def close(self):
        if self.wb is not None:
            self.wb.close()

""" Simple XML pretty print support function

"""
def xml_indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

if __name__ == "__main__":

    result = Result(name='Result', type='suite')
    result1 = Result(name='Result 1', type='test', status='complete')
    result1.results.append(Result(name='Result 1 Log', type='log', filename='log/file/name/1'))
    result2 = Result(name='Result 2', type='test', status='complete', params={'param 1': 'param 1 value'})
    result2.results.append(Result(name='Result 2 Log', type='log', filename='log/file/name/2'))
    result.results.append(result1)
    result.results.append(result2)

    xml_str = result.to_xml_str(pretty_print=True)
    print (xml_str)
    print (result)
    print ('-------------------')
    result_xml = Result()
    root = ET.fromstring(xml_str)
    result_xml.from_xml(root)
    print (result_xml)

