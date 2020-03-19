
import os
import xml.etree.ElementTree as ET

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

param_types = {'int': int, 'float': float, 'string': str,
               int: 'int', float: 'float', str: 'string'}

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


class ResultError(Exception):
    pass


class Result(object):

    def __init__(self, name=None, type=None, status=None, filename=None, params=None):
        self.name = name
        self.type = type
        self.status = status
        self.filename = filename
        self.params = []
        self.ref = None
        self.results_index = 0
        if params is not None:
            self.params = params
        else:
            self.params = {}
        self.results = []

    def __str__(self):
        return self.to_str()

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
                        result = Result()
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

        params = sorted(self.params, key=self.params.get)
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

        return ET.tostring(e)

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
            print(xml)

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
    print(xml_str)
    print(result)
    print('-------------------')
    result_xml = Result()
    root = ET.fromstring(xml_str)
    result_xml.from_xml(root)
    print(result_xml)

