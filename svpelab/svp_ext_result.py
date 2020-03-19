
import os
import wxmplot
import numpy
import openpyxl
from . import result as rslt
import csv
import xlsxwriter

'''
def menu(result, result_dir, result_name):
    if result is not None and result.filename is not None:
        ext = os.path.splitext(result.filename)[1]
        if ext == '.csv':
            rm = ResultMenu(result, result_dir, result_name)
            return rm.menu_items
'''

def menu(result, result_dir, result_name):
    if result is not None:
        rm = ResultMenu(result, result_dir, result_name)
        return rm.menu_items


class ResultWorkbook(object):

    def __init__(self, filename):
        self.wb = xlsxwriter.Workbook(filename)

        '''
        # remove initial sheet that is added at creation
        self.wb.remove_sheet(self.wb.active)
        '''

    def add_chart(self, ws, params=None):
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
        chartsheet = self.wb.add_chartsheet(title)
        chart = self.wb.add_chart({'type': 'scatter', 'subtype': 'straight'})
        chartsheet.set_chart(chart)

        chart.set_title({'name': title})
        chart.set_x_axis({'name': params.get('plot.x.title', '')})
        chart.set_y_axis({'name': params.get('plot.y.title', '')})
        chart.set_y2_axis({'name': params.get('plot.y2.title', '')})
        chart.set_style(1)
        print('ws name = %s' % (ws.get_name()))

        # chart.x_axis.title = params.get('plot.x.title', '')
        # chart.y_axis.title = params.get('plot.y.title', '')

        count = params.get('plot.point_value_count', 1)
        ws_name = ws.get_name()
        categories = []

        if len(x_points) > 0:
            # only support one x point for now
            name = x_points[0]
            try:
                col = point_names.index(name) + 1
                categories = [ws_name, 3, 0, count, 0]
            except ValueError:
                pass

        if len(y_points) > 0:
            for name in y_points:
                try:
                    col = point_names.index(name)
                    print('col = %s' % col)
                    line_color = params.get('plot.%s.color' % name, colors[color_idx])
                    point = params.get('plot.%s.point' % name, 'False')
                    if point == 'True':
                        marker = {'type': 'circle',
                                  'size': 6,
                                  'fill': {'color': line_color}
                        }
                    else:
                        marker = {}
                    chart.add_series({
                        'name': name,
                        'categories': categories,
                        'values': [ws_name, 3, col, count, col],
                        'line': {'color': line_color, 'width': 1.5},
                        'marker' : marker
                    })
                    color_idx += 1

                except ValueError:
                    pass

        if len(y2_points) > 0:
            for name in y2_points:
                try:
                    col = point_names.index(name)
                    print('col = %s' % col)
                    line_color = params.get('plot.%s.color' % name, colors[color_idx])
                    point = params.get('plot.%s.point' % name, 'False')
                    if point == 'True':
                        marker = {'type': 'circle',
                                  'size': 6,
                                  'fill': {'color': line_color}
                        }
                    else:
                        marker = {}
                    chart.add_series({
                        'name': name,
                        'categories': categories,
                        'values': [ws_name, 3, col, count, col],
                        'line': {'color': line_color, 'width': 1.5},
                        'marker' : marker,
                        'y2_axis': 1
                    })

                except ValueError:
                    pass

        '''
        idx = self.wb.sheetnames.index(ws.title) - 1
        if idx < 0:
            idx = 0
        cs = self.wb.create_chartsheet(title=params.get('plot.title', None), index=idx)
        cs.add_chart(chart)
        '''

    def add_csv_file(self, filename, title, relative_value_names=None, params=None):
        line = 1
        ws = self.wb.add_worksheet(title)
        f = None
        relative_value_index = []
        relative_value_start = []
        if relative_value_names is None:
            relative_value_names = []
        if params is None:
            params = {}
        try:
            f = open(filename)
            reader = csv.reader(f, skipinitialspace=True)
            for row in reader:
                for i in range(len(row)):
                    try:
                        row[i] = float(row[i])
                    except ValueError:
                        pass
                # find fields to be treated as relative value
                if line == 1:
                    params['plot.point_names'] = row
                    if relative_value_names is not None:
                        for name in relative_value_names:
                            try:
                                index = row.index(name)
                                relative_value_index.append(index)
                            except ValueError:
                                pass
                # get initial value for relative value fields
                elif line == 2:
                    for index in relative_value_index:
                        relative_value_start.append(row[index])
                        row[index] = 0
                else:
                    for index in relative_value_index:
                        row[index] = row[index] - relative_value_start[index]
                line += 1
                ws.write_row(line - 1, 0, row)
            params['plot.point_value_count'] = line - 1

            if title[-4:] == '.csv':
                chart_title = title[:-4]
            else:
                chart_title = title + '_chart'

            print('params - plot: %s - %s' % (params, params.get('plot.title')))
            if params is not None and params.get('plot.title') is not None:
                self.add_chart(ws, params=params)

            '''
            self.add_chart(ws, params={'plot.title': chart_title,
                                       'plot.x.title': 'Time (secs)',
                                       'plot.x.points': 'TIME',
                                       'plot.y.points': 'AC_VRMS_1',
                                       'plot.y.title': 'Voltage (V)',
                                       'plot.y2.points': 'AC_IRMS_1',
                                       'plot.y2.title': 'Current (A)'})
            '''

        except Exception as e:
            raise
        finally:
            if f:
                f.close()

    def save(self, filename=None):
        if filename:
            self.filename = filename
        self.wb.save(self.filename)

    def close(self):
        if self.wb is not None:
            self.wb.close()


class ResultWorkbookOPX(object):

    def __init__(self, filename=None):
        self.wb = openpyxl.Workbook()
        self.filename = None

        # remove initial sheet that is added at creation
        self.wb.remove_sheet(self.wb.active)

    def add_chart(self, ws, params=None):
        # get fieldnames in first row of worksheet
        colors = ['blue', 'green', 'purple', 'orange', 'red']
        color_idx = 0
        point_names = []
        for c in ws.rows[0]:
            point_names.append(c.value)

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

        chart = openpyxl.chart.ScatterChart(scatterStyle='line')
        chart.title = params.get('plot.title', None)
        chart.style = 13
        chart.x_axis.title = params.get('plot.x.title', '')
        chart.y_axis.title = params.get('plot.y.title', '')

        x_values = None
        if len(x_points) > 0:
            # only support one x point for now
            name = x_points[0]
            try:
                col = point_names.index(name) + 1
                print('x: %s %s' % (col, ws.max_row))
                x_values = openpyxl.chart.Reference(ws, min_col=col, min_row=2, max_row=ws.max_row)
            except ValueError:
                pass

        if len(y_points) > 0:
            for name in y_points:
                try:
                    col = point_names.index(name) + 1
                    values = openpyxl.chart.Reference(ws, min_col=col, min_row=2, max_row=ws.max_row)
                    series = openpyxl.chart.Series(values, x_values, title=name)

                    # lineProp = drawing.line.LineProperties(prstDash='dash')
                    lineProp = openpyxl.drawing.line.LineProperties(
                        solidFill = openpyxl.drawing.colors.ColorChoice(prstClr=colors[color_idx]))
                    color_idx += 1
                    series.graphicalProperties.line = lineProp
                    series.graphicalProperties.line.width = 20000 # width in EMUs
                    chart.series.append(series)

                except ValueError:
                    pass

        if len(y2_points) > 0:
            for name in y2_points:
                try:
                    col = point_names.index(name) + 1
                    values = openpyxl.chart.Reference(ws, min_col=col, min_row=2, max_row=ws.max_row)
                    series = openpyxl.chart.Series(values, x_values, title=name)

                    # lineProp = drawing.line.LineProperties(prstDash='dash')
                    lineProp = openpyxl.drawing.line.LineProperties(
                        solidFill = openpyxl.drawing.colors.ColorChoice(prstClr=colors[color_idx]))
                    color_idx += 1
                    series.graphicalProperties.line = lineProp
                    series.graphicalProperties.line.width = 20000 # width in EMUs
                    chart2 = openpyxl.chart.ScatterChart(scatterStyle='line')
                    chart2.style = 13
                    # chart.y_axis.title = params.get('plot.y.title', '')
                    chart2.series.append(series)
                    chart2.y_axis.axId = 200
                    chart2.y_axis.title = params.get('plot.y2.title', '')
                    chart.y_axis.crosses = "max"
                    chart += chart2

                except ValueError:
                    pass

        idx = self.wb.sheetnames.index(ws.title) - 1
        if idx < 0:
            idx = 0
        cs = self.wb.create_chartsheet(title=params.get('plot.title', None), index=idx)
        cs.add_chart(chart)

    def add_csv_file(self, filename, title, relative_value_names=None, params=None):
        line = 1
        ws = self.wb.create_sheet(title=title)
        f = None
        relative_value_index = []
        relative_value_start = []
        if relative_value_names is None:
            relative_value_names = []
        try:
            f = open(filename)
            reader = csv.reader(f, skipinitialspace=True)
            for row in reader:
                for i in range(len(row)):
                    try:
                        row[i] = float(row[i])
                    except ValueError:
                        pass
                # find fields to be treated as relative value
                if line == 1:
                    line += 1
                    if relative_value_names is not None:
                        for name in relative_value_names:
                            try:
                                index = row.index(name)
                                relative_value_index.append(index)
                            except ValueError:
                                pass
                # get initial value for relative value fields
                elif line == 2:
                    line += 1
                    for index in relative_value_index:
                        relative_value_start.append(row[index])
                        row[index] = 0
                else:
                    for index in relative_value_index:
                        row[index] = row[index] - relative_value_start[index]
                ws.append(row)

            if title[-4:] == '.csv':
                chart_title = title[:-4]
            else:
                chart_title = title + '_chart'

            print('params - plot: %s - %s' % (params, params.get('plot.title')))
            if params is not None and params.get('plot.title') is not None:
                self.add_chart(ws, params=params)

            """
            self.add_chart(ws, params={'plot.title': chart_title,
                                       'plot.x.title': 'Time (secs)',
                                       'plot.x.points': 'TIME',
                                       'plot.y.points': 'AC_VRMS_1',
                                       'plot.y.title': 'Voltage (V)',
                                       'plot.y2.points': 'AC_IRMS_1',
                                       'plot.y2.title': 'Current (A)'})
            """
        except Exception as e:
            raise
        finally:
            if f:
                f.close()

    def save(self, filename=None):
        if filename:
            self.filename = filename
        self.wb.save(self.filename)


class ResultMenu(object):

    def __init__(self, result, result_dir, result_name):
        self.result = result
        self.result_dir = result_dir
        self.result_name = result_name

        self.menu_open_items = [('WXMPlot', '', None, self.plot_wxmplot, None),
                                ('Pyplot', '', None, self.plot_pyplot, None)]

        self.menu_items = [('Open with', '', self.menu_open_items, None, None),
                           ('', '', None, None, None),
                           ('Create Excel Workbook (.xlsx)', '', None, self.create_xlsx, None),
                           ('Create Excel Workbook Alt(.xlsx)', '', None, self.create_xlsx_alt, None),
                           ('', '', None, None, None),
                           ('Other', '', None, None, None)]


    def result_other(self, arg=None):
        pass

    def create_xlsx(self, arg=None):
        filename = os.path.join(self.result_dir, self.result_name, self.result_name + '.xlsx')
        print('creating result: %s %s %s' % (self.result_dir, self.result_name, self.result_name))
        self.to_xlsx(self.result, filename=filename)

    def to_xlsx(self, r, wb=None, filename=None):
        '''
        self.params={'plot.title': self.name,
                     'plot.x.title': 'Time (secs)',
                     'plot.x.points': 'TIME',
                     'plot.y.points': 'AC_VRMS_1',
                     'plot.y.title': 'Voltage (V)',
                     'plot.y2.points': 'AC_IRMS_1',
                     'plot.y2.title': 'Current (A)'}
        '''

        result_wb = wb
        if result_wb is None:
            result_wb = ResultWorkbook(filename=filename)
        if r.type == rslt.RESULT_TYPE_FILE:
            name, ext = os.path.splitext(r.filename)
            if ext == '.csv':
                result_wb.add_csv_file(os.path.join(self.result_dir, self.result_name, r.filename), r.name,
                                       relative_value_names = ['TIME'], params=r.params)
        for result in r.results:
            self.to_xlsx(result, wb=result_wb)
        if wb is None:
            result_wb.close()

    def create_xlsx_alt(self, arg=None):
        filename = os.path.join(self.result_dir, self.result_name, self.result_name + '.xlsx')
        print('creating result: %s %s %s' % (self.result_dir, self.result_name, self.result_name))
        self.to_xlsx_alt(self.result, filename=filename)

    def to_xlsx_alt(self, r, wb=None, filename=None):
        '''
        self.params={'plot.title': self.name,
                     'plot.x.title': 'Time (secs)',
                     'plot.x.points': 'TIME',
                     'plot.y.points': 'AC_VRMS_1',
                     'plot.y.title': 'Voltage (V)',
                     'plot.y2.points': 'AC_IRMS_1',
                     'plot.y2.title': 'Current (A)'}
        '''

        result_wb = wb
        if result_wb is None:
            result_wb = ResultWorkbookOPX(filename=filename)
        if r.type == rslt.RESULT_TYPE_FILE:
            name, ext = os.path.splitext(r.filename)
            if ext == '.csv':
                result_wb.add_csv_file(os.path.join(self.result_dir, self.result_name, r.filename), r.name,
                                       relative_value_names = ['TIME'], params=r.params)
        for result in r.results:
            self.to_xlsx(result, wb=result_wb)
        if wb is None:
            print('saving')
            result_wb.save(filename=filename)

    def plot_wxmplot(self, arg=None):
        frame = wxmplot.PlotFrame()
        filename = os.path.join(self.result_dir, self.result_name, self.result.filename)
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
                    value_arrays[i].append(0)
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

        frame.SetTitle(self.result.name)
        frame.Show()

    def plot_pyplot(self, arg=None):
        print('plot_pyplot')


if __name__ == "__main__":

  params={'plot.title': 'title_name',
          'plot.x.title': 'Time (secs)',
          'plot.x.points': 'TIME',
          'plot.y.points': 'AC_Q_1, Q_TARGET',
          'plot.Q_TARGET.point': 'True',
          'plot.y.title': 'Reactive Power (var)',
          'plot.y2.points': 'AC_VRMS_1',
          'plot.y2.title': 'Voltage (V)'
  }

  wb = ResultWorkbook('worktest.xlsx')
  wb.add_csv_file('vv.csv', 'title', relative_value_names=['TIME'], params=params)
  wb.close()
