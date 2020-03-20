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

'''
- update param to param_def
- support index attribute (use dict)

'''

'''

An indexed parameter is a parameter that contains multiple values that are referenced by numeric index.
The parameter index has a start value and count. The index start is the index associated with the first
parameter value. The index count is the number of values the parameter contains.

The parameter values are encoded as a dict with each parameter value represented as a entry where the key
is an integer index and the value is the value corresponding to the index. The dict contains two additional keys:
'index_start' and 'index_count' whose values are the integer values for the start index and number of
parameter values, respectively.


'''


from builtins import input
from builtins import range




import sys
import os
import time
import datetime
import importlib
import xml.etree.ElementTree as ET
import shlex
import natsort

import multiprocessing

try:
    # Python 3.4+
    if sys.platform.startswith('win'):
        import multiprocessing.popen_spawn_win32 as forking
    else:
        import multiprocessing.popen_fork as forking
except ImportError:
    import multiprocessing.forking as forking


version = '1.5.9'

# log levels
ERROR = 'E'
WARNING = 'W'
INFO = 'I'
DEBUG = 'D'

# test result codes (should be the same as result.py)
RESULT_COMPLETE = 'Complete'
RESULT_PASS = 'Pass'
RESULT_FAIL = 'Fail'

PARAM_TYPE_STR = 'string'
PARAM_TYPE_INT = 'int'
PARAM_TYPE_FLOAT = 'float'

param_types = {'int': int, 'float': float, 'string': str,
               int: 'int', float: 'float', str: 'string'}

param_default = {int: 0, float: 0., str: ''}

PTYPE_DIR = 'dir'
PTYPE_FILE = 'file'

PARAM_SEP = '.'
PATH_SEP = '/'

SCRIPT_PARAM_ROOT = '_root_'

class _Popen(forking.Popen):
    def __init__(self, *args, **kw):
        if hasattr(sys, 'frozen'):
            # We have to set original _MEIPASS2 value from sys._MEIPASS
            # to get --onefile mode working.
            os.putenv('_MEIPASS2', sys._MEIPASS)
        try:
            super(_Popen, self).__init__(*args, **kw)
        finally:
            if hasattr(sys, 'frozen'):
                # On some platforms (e.g. AIX) 'os.unsetenv()' is not
                # available. In those cases we cannot delete the variable
                # but only set it to the empty string. The bootloader
                # can handle this case.
                if hasattr(os, 'unsetenv'):
                    os.unsetenv('_MEIPASS2')
                else:
                    os.putenv('_MEIPASS2', '')

class Process(multiprocessing.Process):
    _Popen = _Popen


class ScriptFail(Exception):
    pass


class ScriptError(Exception):
    pass


class ScriptParamError(Exception):
    pass


class ScriptConfigError(Exception):
    pass


def result_str(result):
    return result

def is_sequence(arg):
    return (not hasattr(arg, 'strip') and
            hasattr(arg, '__getitem__') or
            hasattr(arg, '__iter__') and
            not isinstance(arg, str))

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

def load_script(path, lib_path, path_list = None):
    if path_list is not None:
        for p in path_list:
            sys.path.insert(0, p)
    if lib_path is not None:
        sys.path.insert(0, lib_path)
    script_path, name = os.path.split(path)
    name, ext = os.path.splitext(name)
    sys.path.insert(0, script_path)
    try:
        m = importlib.import_module(name)
        try:
            try:
                info = m.script_info()
                s = Script(info=info)
            except Exception as e:
                raise e
                # raise ScriptError('%s does not appear to be a script: %s' % (path, str(e)))
        finally:
            if name in sys.modules:
                del sys.modules[name]
            if sys.path[0] == script_path:
                del sys.path[0]
            if lib_path is not None and sys.path[0] == lib_path:
                del sys.path[0]
    except Exception as e:
        raise e
        # raise ScriptError('Error importing module %s: %s' % (path, str(e)))
    return s

def check_active_value(value, active_value):
    if is_sequence(value):
        values = value
    else:
        values = [value]
    for v in values:
        if is_sequence(active_value):
            if v in active_value:
                return v
        else:
            if v == active_value:
                return v

def param_get_active(param_defs, entry, param_value):
    if entry is not None:
        if entry.active is not None:
            if param_is_active(param_defs, entry.active, param_value) is None:
                return
            value = param_value(entry.active)
            if check_active_value(value, entry.active_value) is None:
                # check other entries if present
                active_entry = entry.active_entry(value)
                if active_entry is None:
                    return
                entry = active_entry
        if entry.parent is None or param_is_active(param_defs, entry.parent.qname, param_value):
            return entry

def param_is_active(param_defs, name, param_value):
    entry = param_defs._param_get(param_defs, name, param_value)
    if entry is not None:
        return param_get_active(param_defs, entry, param_value)

def param_update_ref_values(param_defs, name, value, param_value):
    index_count = index_start = None
    entry = param_defs._param_get(param_defs, name, param_value)
    if entry is not None:
        if entry.index_count is not None:
            if type(entry.index_count) == str:
                index_count = param_value(entry.index_count)
                '''
                if index_count is None:
                    raise ScriptParamError('Unable to resolve param name %s referenced in param %s' % (entry.index_count,
                                           entry.qname))
                '''

            else:
                index_count = entry.index_count
        if entry.index_start is not None:
            if type(entry.index_start) == str:
                index_start = param_value(entry.index_start)
                '''
                if index_start is None:
                    raise ScriptParamError('Unable to resolve param name %s referenced in param %s' % (entry.index_count,
                                           entry.qname))
                '''
            else:
                index_start = entry.index_start

        if index_count is not None and index_start is not None:
            entry.index_update(index_count, index_start)

class ScriptInfo(object):

    def __init__(self, name=None, label=None, desc=None, run=None, version=None):
        self.name = name
        self.label = label
        self.desc = desc
        self.run = run
        self.version = '1.0.0'
        self.param_defs = ScriptParamGroupDef(name=SCRIPT_PARAM_ROOT, qname=SCRIPT_PARAM_ROOT)
        self.logos = []

        if not self.label:
            self.label = self.name
        if version is not None:
            self.version = version

    def logo(self, filename):
        self.logos.append(filename)

    def param_group(self, name, group=None, label=None, desc=None, active=None, active_value=None, glob=False,
                    index_count=None, index_start=None):
        return self.param_defs.param_group_add(group=group, name=name, label=label, desc=desc, active=active,
                                               active_value=active_value, glob=glob, index_count=index_count,
                                               index_start=index_start)

    def param(self, name, group=None, label=None, default=None, desc=None, values=None, active=None, glob=False,
              active_value=None, ptype=None, width=None, index_count=None, index_start=None):
        return self.param_defs.param_add(group=group, name=name, label=label, default=default, desc=desc, values=values,
                                         active=active, active_value=active_value, glob=glob, ptype=ptype, width=width,
                                         index_count=index_count, index_start=index_start)

    def param_add_value(self, name, value, sorted=True):
        param = self.param_defs.param_def_get(name, self.param_defs, self.param_defs.param_value, active=False)
        if param is None:
            raise ScriptParamError('param_add_value - unknown param name: %s' % name)
        if value not in param.values:
            param.values.append(value)
            if sorted is True:
                param.values.sort()


class Script(object):
    def __init__(self, env=None, info=None, config=None, config_file=None, params=None):
        self.name = None
        self.desc = None
        self.param_defs = None
        self.info = info
        self.config = config
        self.timers = []
        self.callback = False
        if params is None:
            self.params = {}
        else:
            self.params = params

        self._results_dir = ''
        self._result_dir = ''
        if env is None:
            self.env = {}
        else:
            self.env = env
            self._files_dir = env.get('files_dir', '')
            self._results_dir = env.get('results_dir', '')
            self._result_dir = env.get('result_dir', '')

         # resolve active and references in param defs
        if self.info is not None:
            self.name = self.info.name
            self.desc = self.info.desc
            self.param_defs = self.info.param_defs
            if self.info.param_defs is not None:
                self.info.param_defs.resolve_active(self.info.param_defs, self.param_value)
                self.info.param_defs.resolve_refs(self.info.param_defs, self.param_value)

        try:
            if config_file is not None:
                self.config = ScriptConfig(filename=config_file)
        except Exception as e:
            self.config = config
            self.log('Error loading script config file: %s' % str(e))

    def alert(self, message):
        print (message)

    def config_name(self):
        name = ''
        if self.config is not None:
            name = self.config.name
        return name

    def confirm(self, message):
        while True:
            c = input("%s\nType 'Y' to confirm or 'N' to cancel: " % (str(message))).rstrip('\r\n').lower()
            if c == 'y':
                return True
            elif c == 'n':
                return False

    def fail(self, reason):
        raise ScriptFail(reason)

    def files_dir(self):
        return self._files_dir

    def group_params(self, group=None, params=None):
        if params is None:
            params = {}
        if group is not None:
            param_group = self.param_defs.param_group_get(group)
        else:
            param_group = self.param_defs
        if param_group is not None:
            for param in param_group.params:
                params[param.name] = self.param_value(param.qname)
        return params

    def log(self, message, level=INFO):
        print ('{} {} {}'.format (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), level, message))

    def log_active_params(self, param_group=None, config=None, level=0):
        if param_group is None:
            param_group = self.param_defs
        if config is None:
            config = self.config
        for param in param_group.params:
            if param_is_active(self.param_defs, param.qname, self.param_value):
                self.log('%s%s = %s' % (' ' * (level * 4), param.label, self.param_value(param.qname)))
        for group in param_group.param_groups:
            if param_is_active(self.param_defs, group.qname, self.param_value):
                self.log('%s%s:' % (' ' * (level * 4), group.label))
                self.log_active_params(param_group=group, config=config, level=level+1)

    def log_debug(self, message):
        self.log(message, level=DEBUG)

    def log_error(self, message):
        self.log(message, level=ERROR)

    def log_warning(self, message):
        self.log(message, level=WARNING)

    def param_get(self, name, param_defs=None, param_value=None):
        return self.param_value(name, param_defs, param_value)

    def param_is_global(self, name):
        if self.param_defs is not None:
            param = self.param_defs.find(name)
            if param is not None:
                return param.glob
        return False

    def param_value(self, name, param_defs=None, param_value=None):
        if param_defs is None:
            param_defs = self.param_defs
        if param_value is None:
            param_value = self.param_value
        value = self.params.get(name)
        if value is None:
            if self.config is not None:
                value = self.config.param_value(name, param_defs, param_value)
            if value is None:
                if self.param_defs is not None:
                    value = self.param_defs.param_value(name, param_defs, param_value)
        return value

    def result(self, status=None, params=None):
        s = 'Test result'
        if status is not None:
            s += ' - Status: %s' % (status)
        if params is not None:
            s += ' - Params: %s' % params
        print (s)

    def result_dir(self):
        return self._result_dir

    def results_dir(self):
        return self._results_dir

    def result_file(self, name=None, status=None, params=None):
        s = 'Test result file'
        if name is not None:
            s += ' - %s' % (name)
        if status is not None:
            s += ' - Status: %s' % (status)
        if params is not None:
            s += ' - Params: %s' % (params)
        print (s)

    def result_file_path(self, name):
        return os.path.join(self.result_dir(), name)

    def resolve_active(self):
        if self.param_defs:
            self.param_defs.resolve_active(self.param_defs, self.param_value)

    def resolve_refs(self):
        if self.param_defs:
            self.param_defs.resolve_refs(self.param_defs, self.param_value)

    '''
        Every entry is considered before any entry gets another chance
        A complete pass thorough the timeout list is performed for any sleep call
        sleep() can not be called in a timer callback routine
    '''
    def sleep(self, seconds):
        if self.callback is True:
            raise ScriptError('Can not call sleep() from callback function')
        current_time = time.time()
        wake_time = current_time + seconds
        sleep_time = wake_time - current_time
        while sleep_time > 0:
            timers = self.timers[:]
            for t in timers:
                next = t.next_timeout - current_time
                if next <= 0:
                    self.callback = True
                    t.callback(t.arg)
                    self.callback = False
                    if t.repeating is False:
                        self.timer_cancel(t)
                    else:
                        t.next_timeout += t.period
                        next = t.next_timeout - current_time
                if next < sleep_time:
                    sleep_time = next
            time.sleep(sleep_time)
            current_time = time.time()
            sleep_time = wake_time - current_time

    def timer_cancel(self, timer):
        self.timers.remove(timer)

    def timer_start(self, period, callback, arg=None, repeating=False):
        timer = ScriptTimer(period, callback, arg=arg, repeating=repeating)
        self.timers.append(timer)
        return timer

    def svp_version(self, required=None):
        if required is not None:
            required_version = required.split('.')
            if len(required_version) > 3:
                raise ScriptError('Invalid version format for required version: %s' % (required))
            current_version = version.split('.')
            for i in range(len(required_version)):
                if int(current_version[i]) > int(required_version[i]):
                    break
                elif int(current_version[i]) < int(required_version[i]):
                    raise ScriptError('Current SVP version %s is older than required version %s' % (version, required))
        return version


class ScriptTimer(object):
    def __init__(self, period, callback, arg, repeating=False):
        self.period = period
        self.callback = callback
        self.arg = arg
        self.repeating = repeating
        self.count = 1
        self.next_timeout = time.time() + period


class ScriptParamDef(object):

    def __init__(self, parent=None, name=None, qname=None, label=None, default=None,  desc=None, values=None,
                 active=None, active_value=None, glob=False, ptype=None, width=None, index_count=None,
                 index_start=None):
        self.parent = parent
        self.name = name
        self.qname = qname
        self.label = label
        self.desc = desc
        self.active = active
        self.active_value = active_value
        self.default = default
        self.values = []
        if values is not None:
            if isinstance(values, list):
                self.values = values
            else:
                self.values = [values]
        self.glob = glob
        self.referenced = False
        self.ptype = ptype
        self.width = width
        self.vtype = None
        self.index_count = index_count
        self.index_start = index_start
        self.value = self.default
        self.entries = []

        # default index start to 0 if indexing active
        if self.index_count is not None:
            if self.index_start is None:
                self.index_start = 0
            if type(self.index_count) != str and type(self.index_start) != str:
                self.value = {'index_count': self.index_count, 'index_start': self.index_start}
                for i in range(self.index_start, self.index_start + self.index_count):
                    if type(self.default) == dict:
                        value = self.default.get(i)
                        if value is not None:
                            if self.vtype is None:
                                self.vtype = type(value)
                            else:
                                if self.vtype != type(value):
                                    ### error - multiple value types in parameter
                                    pass
                        else:
                            value = param_default.get(self.vtype)
                        self.value[i] = value
                    else:
                        self.value[i] = self.default
                        if self.vtype is None:
                            self.vtype = type(self.default)
            else:
                self.value = {}
        else:
            self.vtype = type(self.default)

    def active_entry(self, value):
        active_entry = self
        if self.active and check_active_value(value, self.active_value) is None:
            # check other entries if present
            active_entry = None
            for e in self.entries:
                if check_active_value(value, e.active_value) is not None:
                    active_entry = e
                    break
        return active_entry

    def index_update(self, index_count, index_start):
        self.value = {'index_count': index_count, 'index_start': index_start}
        for i in range(index_start, index_start + index_count):
            if type(self.default) == dict:
                value = self.default.get(i)
                if value is not None:
                    if self.vtype is None:
                        self.vtype = type(value)
                    else:
                        if self.vtype != type(value):
                            ### error - multiple value types in parameter
                            pass
                else:
                    value = param_default.get(self.vtype)
                self.value[i] = value
            else:
                self.value[i] = self.default
                if self.vtype is None:
                    self.vtype = type(self.default)

    def dump(self, indent=''):
        return '%sparam - name: %s  label: %s  default: %s  active: %s  active_value: %s  desc: %s  values: %s  referenced: %s  ptype: %s  width: %s' %  (indent,
                self.name, self.label, str(self.default), self.active, self.active_value, self.desc, str(self.values), str(self.referenced),
                str(self.ptype), str(self.width))

    def __str__(self):

        return 'name: %s  label: %s  default: %s  desc: %s  values: %s  referenced: %s  ptype: %s  width: %s' %  (self.name, self.label, str(self.default), self.desc, str(self.values),
                                                                            str(self.referenced), str(self.ptype), str(self.width))

class ScriptParamGroupDef(object):

    def __init__(self, parent=None, name=None, qname=None, label=None, desc=None, active=None, active_value=None,
                 glob=False, index_count=None, index_start=None):
        self.parent = parent
        self.name = name
        self.qname = qname
        self.label = label
        self.desc = desc
        self.active = active
        self.active_value = active_value
        self.glob = glob
        self.entries = []
        self.param_groups = []
        self.params = []
        self.index_count = index_count
        self.index_start = index_start

        # default index start to 0 if indexing active
        if self.index_count is not None:
            if self.index_start is None:
                self.index_start = 0

    def param_group_find(self, name):
        if name == self.name:
            return self
        for g in self.param_groups:
            if g.name == name:
                return g

    def param_find(self, name):
        for p in self.params:
            if p.name == name:
                return p

    def find(self, name):
        e = self.param_group_find(name)
        if e is None:
            e = self.param_find(name)
        return e

    def param_group_find_active(self, param_defs, name, param_value):
        group = None
        if name == self.name:
            group = self
        else:
            for g in self.param_groups:
                if g.name == name:
                    group = g
        if group:
            return param_get_active(param_defs, group, param_value)

    def param_find_active(self, param_defs, name, param_value):
        param = None
        for p in self.params:
            if p.name == name:
                param = p
        if param:
            return param_get_active(param_defs, param, param_value)

    def find_active(self, param_defs, name, param_value):
        e = self.param_group_find_active(param_defs, name, param_value)
        if e is None:
            e = self.param_find_active(param_defs, name, param_value)
        return e

    def param_group_get(self, name):
        if name is None:
            return
        group = self
        path = name.split(PARAM_SEP)
        for i in range(len(path) - 1):
            group = group.param_group_find(path[i])
            if group is None:
                return
        return group.param_group_find(path[-1])

    #def param_def_get(self, name, param_defs, param_value):
    def param_def_get(self, name, param_defs, param_value=None, active=True):
        # print 'param_def_get: %s' % name
        if name is None:
            return
        group = self
        path = name.split(PARAM_SEP)
        for i in range(len(path) - 1):
            if active:
                group = group.param_group_find_active(param_defs, path[i], param_value)
            else:
                group = group.param_group_find(path[i])
            if group is None:
                return
        # print 'returning %s %s' % (path[-1], group.param_find_active(param_defs, path[-1], param_value))
        if active:
            param_def = group.param_find_active(param_defs, path[-1], param_value)
        else:
            param_def = group.param_find(path[-1])
        return param_def

    def _param_get(self, param_defs, name, param_value):
        if name is None:
            return
        group = self
        path = name.split(PARAM_SEP)
        for i in range(len(path) - 1):
            group = group.param_group_find_active(param_defs, path[i], param_value)
            if group is None:
                return
        return group.find_active(param_defs, path[-1], param_value)

    def param_value(self, name, param_defs=None, param_value=None):
        if param_defs is None:
            param_defs = self
        if param_value is None:
            param_value = self.param_value
        param_def = self.param_def_get(name, param_defs, param_value)
        if param_def is not None:
            return param_def.value

    def param_group_add(self, group=None, name=None, label=None, desc=None, active=None, active_value=None, glob=False,
                        index_count=None, index_start=None):
        if name is None:
            raise ScriptParamError('Missing parameter group name')
        group = self
        path = name.split(PARAM_SEP)
        group_name = path[-1]
        if not group_name:
            raise ScriptParamError('Missing parameter group name')
        for i in range(len(path) - 1):
            group = group.param_group_find(path[i])
            if group is None:
                raise ScriptParamError('Parameter group not found: %s' % PARAM_SEP.join(path[:i+1]))
        if group.find(group_name):
            raise ScriptParamError('Duplicate parameter name: %s' % (name))
        g = ScriptParamGroupDef(parent=group, name=group_name, qname=name, label=label, desc=desc, active=active,
                                active_value=active_value, glob=glob, index_count=index_count, index_start=index_start)
        group.param_groups.append(g)

    def param_add(self, group=None, parent=None, name=None, label=None, default=None, desc=None, values=None,
                  active=None, active_value=None, glob=False, ptype=None, width=None, index_count=None,
                  index_start=None):
        if name is None:
            raise ScriptParamError('Missing parameter name')
        group = self
        path = name.split(PARAM_SEP)
        param_name = path[-1]
        if not param_name:
            raise ScriptParamError('Missing parameter name')
        for i in range(len(path) - 1):
            group = group.param_group_find(path[i])
            if group is None:
                raise ScriptParamError('Parameter group not found: %s' % PARAM_SEP.join(path[:i+1]))
        if group.find(param_name):
            raise ScriptParamError('Duplicate parameter name: %s' % (name))
        if group.index_count is not None:
            index_count = group.index_count
            index_start = group.index_start
        g = ScriptParamDef(parent=group, name=param_name, qname=name, label=label, default=default, desc=desc,
                           values=values, active=active, active_value=active_value, glob=glob, ptype=ptype,
                           width=width, index_count=index_count, index_start=index_start)
        group.params.append(g)

    def resolve_active(self, param_defs, param_value):
        for g in self.param_groups:
            g.resolve_active(param_defs, param_value)

        for p in self.params:
            if p.active is not None:
                param = param_defs.param_def_get(p.active, param_defs, param_value)
                if param is not None:
                    param.referenced = True
                '''
                else:
                    raise ScriptParamError('Unable to resolve param name %s referenced in param %s' % (p.active, p.qname))
                '''

    def resolve_refs(self, param_defs, param_value):
        for g in self.param_groups:
            g.resolve_refs(param_defs, param_value)

        for p in self.params:
            param = None
            if type(p.index_count) == str:
                param = param_defs.param_def_get(p.index_count, param_defs=param_defs, param_value=param_value)
                if param is not None:
                    param.referenced = True
            if type(p.index_start) == str:
                param = param_defs.param_def_get(p.index_start, param_defs=param_defs, param_value=param_value)
                if param is not None:
                    param.referenced = True
            if param is not None:
                param_update_ref_values(param_defs, p.qname, p.value, param_defs.param_value)

    def active_entry(self, value):
        active_entry = self
        if self.active and check_active_value(value, self.active_value) is None:
            # check other entries if present
            active_entry = None
            for e in self.entries:
                if check_active_value(value, e.active_value) is not None:
                    active_entry = e
                    break
        return active_entry

    def dump(self, indent=''):
        s = '%sparam group - name: %s  label: %s  desc: %s  active: %s  active_value: %s\n' % (indent,
            self.name, self.label, self.desc, self.active, str(self.active_value))
        indent += '  '
        for group in self.param_groups:
            s += '%s\n' % group.dump(indent)
        for param in self.params:
            s += '%s\n' % param.dump(indent)
        return s

def params_from_xml(params, element):
    for e in element.findall('*'):
        if e.tag == SCRIPT_CFG_PARAMS:
            for e_param in e.findall('*'):
                if e_param.tag == SCRIPT_PARAM:
                    name = e_param.attrib.get(SCRIPT_PARAM_ATTR_NAME)
                    param_type = e_param.attrib.get(SCRIPT_PARAM_ATTR_TYPE)
                    count = e_param.attrib.get(SCRIPT_PARAM_INDEX_COUNT)
                    start = e_param.attrib.get(SCRIPT_PARAM_INDEX_START)
                    if name:
                        vtype = param_types.get(param_type, str)
                        if count is not None and start is not None:
                            count = int(count)
                            start = int(start)
                            value = {'index_count': count, 'index_start': start}
                            values = shlex.split(e_param.text)
                            i = start
                            for v in values:
                                value[i] = vtype(v)
                                i += 1
                            if len(values) != count:
                                ### count/value mismatch
                                pass
                        else:
                            value = vtype(e_param.text)
                        params[name] = value

def params_to_xml(params, parent=None):
    if parent is not None:
        e_params = ET.SubElement(parent, SCRIPT_CFG_PARAMS)
    else:
        e_params = ET.Element(SCRIPT_CFG_PARAMS)
    sorted_params = natsort.natsorted(params, key=params.get)

    for p in sorted_params:
        value_type = None
        value_str = None
        attr = {SCRIPT_PARAM_ATTR_NAME: p}
        value = params.get(p)
        if type(value) == dict:
            start = value.get('index_start')
            count = value.get('index_count')
            attr['index_start'] = str(start)
            attr['index_count'] = str(count)
            if count is not None and start is not None:
                value_str = ''
                value_type = None
                for i in range(start, start + count):
                    v = value.get(i)
                    if value_type is None and v is not None:
                        value_type = param_types.get(type(v), PARAM_TYPE_STR)
                    v_str = str(v)
                    if ' ' in v_str:
                        v_str = '"%s"' % (v_str)
                    value_str += '%s ' % (v_str)
            else:
                ### error unknown dict value type
                pass
        else:
            if value is not None:
                value_type = param_types.get(type(value), PARAM_TYPE_STR)
                value_str = str(value)

        if value_type is not None:
            attr[SCRIPT_PARAM_ATTR_TYPE] = value_type

        e_param = ET.SubElement(e_params, SCRIPT_PARAM, attrib=attr)
        if value_str is not None:
            e_param.text = value_str

    return e_params

# script config xml elements and attributes
SCRIPT_CFG = 'scriptConfig'
SCRIPT_CFG_ATTR_NAME = 'name'
SCRIPT_CFG_ATTR_SCRIPT = 'script'
SCRIPT_CFG_DESC = 'desc'
SCRIPT_CFG_PARAMS = 'params'
SCRIPT_PARAM = 'param'
SCRIPT_PARAM_ATTR_NAME = 'name'
SCRIPT_PARAM_ATTR_LABEL = 'label'
SCRIPT_PARAM_ATTR_TYPE = 'type'
SCRIPT_PARAM_DESC = 'desc'
SCRIPT_PARAM_INDEX_COUNT = 'index_count'
SCRIPT_PARAM_INDEX_START = 'index_start'

class ScriptConfig(object):

    def __init__(self, name=None, script=None, desc=None, params=None, filename=None):
        self.name = name
        self.script = script
        self.desc = desc
        self.params = None
        self.filename = filename

        if params is None:
            self.params = {}
        else:
            self.params = params.copy()

        if filename:
            try:
                self.from_xml(filename=filename)
            except Exception as e:
                raise  ScriptConfigError('Error scanning script configuration file {}: {}'.format(filename, str(e)))

    def param_value(self, name, param_defs=None, param_value=None):
        return self.params.get(name)

    def param_add_default(self, script, param_group_def):
        for g in param_group_def.param_groups:
            self.param_add_default(script, g)
        for p in param_group_def.params:
            if param_is_active(script.param_defs, p.qname, script.param_value):
                #if script.param_is_active(p.qname):
                self.params[p.qname] = p.value

    def from_xml(self, element=None, filename=None):
        if element is None and filename is not None:
            element = ET.ElementTree(file=filename).getroot()
        if element is None:
            raise ScriptConfigError('No xml document element')
        if element.tag != SCRIPT_CFG:
            raise ScriptConfigError('Unexpected script config root element %s' % (element.tag))
        self.name = element.attrib.get(SCRIPT_CFG_ATTR_NAME)
        self.script = element.attrib.get(SCRIPT_CFG_ATTR_SCRIPT)
        if self.name is None:
            raise ScriptConfigError('Script configuration name missing')
        if self.script is None:
            raise ScriptConfigError('Script name missing')
        # self.desc = element.attrib.get(TEST_CFG_ATTR_DESC)

        params_from_xml(self.params, element)

    def params_to_xml(self, parent=None):
        if parent is not None:
            e_params = ET.SubElement(parent, SCRIPT_CFG_PARAMS)
        else:
            e_params = ET.Element(SCRIPT_CFG_PARAMS)
        params = natsort.natsorted(self.params, key= self.params.get)

        for p in params:
            value_type = None
            value_str = None
            attr = {SCRIPT_PARAM_ATTR_NAME: p}
            value = self.params.get(p)
            if type(value) == dict:
                start = value.get('index_start')
                count = value.get('index_count')
                attr['index_start'] = str(start)
                attr['index_count'] = str(count)
                if count is not None and start is not None:
                    value_str = ''
                    value_type = None
                    for i in range(start, start + count):
                        v = value.get(i)
                        if value_type is None and v is not None:
                            value_type = param_types.get(type(v), PARAM_TYPE_STR)
                        v_str = str(v)
                        if ' ' in v_str:
                            v_str = '"%s"' % (v_str)
                        value_str += '%s ' % (v_str)
                else:
                    raise ScriptConfigError('Script configuration error: count = %s start = %s' % (count, start))
            else:
                if value is not None:
                    value_type = param_types.get(type(value), PARAM_TYPE_STR)
                    value_str = str(value)

            if value_type is not None:
                attr[SCRIPT_PARAM_ATTR_TYPE] = value_type

            e_param = ET.SubElement(e_params, SCRIPT_PARAM, attrib=attr)
            if value_str is not None:
                e_param.text = value_str

        return e_params

    def to_xml(self, parent=None, filename=None):
        attr = {}
        if self.name:
            attr[SCRIPT_CFG_ATTR_NAME] = self.name
        if self.script:
            attr[SCRIPT_CFG_ATTR_SCRIPT] = self.script
        if parent is not None:
            e = ET.SubElement(parent, SCRIPT_CFG, attrib=attr)
        else:
            e = ET.Element(SCRIPT_CFG, attrib=attr)

        params_to_xml(self.params, e)

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
                raise ScriptConfigError('File %s already exists' % (filename))
            f = open(filename, 'w')
            f.write(xml)
            f.close()
        else:
            print(xml)
