
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
import sys

import multiprocessing
import importlib
import datetime
import copy
import imp

import time
import xml.etree.ElementTree as ET

import result as rslt
import script

extended_path_list = []

class SVPError(Exception):
    pass

def script_update(path, old_name, new_name):
    try:
        files = os.listdir(path)
        for f in files:
            try:
                file_path = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                if ext == TEST_EXT:
                    config = script.ScriptConfig(filename=file_path)
                    if os.path.normcase(config.script) == os.path.normcase(old_name):
                        if new_name is not None:
                            config.script = new_name
                            config.to_xml_file()
                        else:
                            # remove file
                            pass
                else:
                    if os.path.isdir(file_path):
                        script_update(file_path, old_name, new_name)
            except Exception as e:
                pass
    except Exception as e:
        raise SVPError('Error on script update - directory %s: %s' % (path, str(e)))

SUITE_EXT = '.ste'
TEST_EXT = '.tst'
SCRIPT_EXT = '.py'
RESULTS_EXT = '.rlt'
LOG_EXT = '.log'
CSV_EXT = '.csv'

SUITES_DIR = 'Suites'
TESTS_DIR = 'Tests'
SCRIPTS_DIR = 'Scripts'
RESULTS_DIR = 'Results'
LIB_DIR = 'Lib'
FILES_DIR = 'Files'

def test_to_file(name):
    if not is_test_file(name):
        return name + TEST_EXT
    return name

def file_to_test(name):
    if is_test_file(name):
        return name[:-4]
    return name

def is_test_file(name):
    return name.endswith(TEST_EXT)

def file_to_script(name):
    if is_script_file(name):
        return name[:-3]
    return name

def script_to_file(name):
    if not is_script_file(name):
        return name + SCRIPT_EXT
    return name

def is_script_file(name):
    return name.endswith(SCRIPT_EXT)

def is_suite_file(name):
    return name.endswith(SUITE_EXT)

def suite_to_file(name):
    if not is_suite_file(name):
        return name + SUITE_EXT
    return name

def file_to_suite(name):
    if is_suite_file(name):
        return name[:-4]
    return name

def is_log_file(name):
    return name.endswith(LOG_EXT)

'''
class _Popen(multiprocessing.forking.Popen):
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


class MultiProcess(multiprocessing.Process):
    _Popen = _Popen
'''

class MultiProcess(multiprocessing.Process):
    pass

# cmd_line_target_dirs = [SUITES_DIR, TESTS_DIR, SCRIPTS_DIR]

def process_run(filename, env, config, params, lib_path, conn):
    name = script_path = None
    try:
        sys.stdout = sys.stderr = open(os.path.join(trace_dir(), 'sunssvp_script.log'), "w")
        script_path, name = os.path.split(filename)
        name, ext = os.path.splitext(name)
        if lib_path is not None:
            sys.path.insert(0, lib_path)
        sys.path.insert(0, script_path)
        try:
            m = importlib.import_module(name)
            info = m.script_info()
            test_script = RunScript(env=env, info=info, config=config, config_file=None, params=params, conn=conn)
            m.run(test_script)
        except Exception as e:
            raise e
    finally:
        if name in sys.modules:
            del sys.modules[name]
        if sys.path[0] == script_path:
            del sys.path[0]
        if lib_path is not None and sys.path[0] == lib_path:
            del sys.path[0]


class LogEntry(object):
    def __init__(self, message, level=script.INFO, timestamp=None):
        self.message = message
        self.level = level
        self.timestamp = timestamp

        if self.timestamp is None:
            self.timestamp = datetime.datetime.now()

    def timestamp_str(self):
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def __str__(self):
        return '%s  %s  %s' % (self.timestamp_str(), self.level, self.message)

class Directory(object):
    def __init__(self, path=None, working=False):
        self.path = path
        self.working = working

'''
    Suite
'''''

# suite xml elements and attributes
SUITE_ROOT = 'suite'
SUITE_ATTR_NAME = 'name'
SUITE_ATTR_TYPE = 'type'
SUITE_ATTR_GLOBALS = 'globals'
SUITE_PARAMS = 'params'
SUITE_PARAM = 'param'
SUITE_MEMBERS = 'members'
SUITE_MEMBER = 'member'
SUITE_TESTS = 'tests'
SUITE_SUITE = 'suite'
SUITE_TEST = 'test'

def member_update(path, old_name, new_name):
    try:
        files = os.listdir(path)
        for f in files:
            try:
                file_path = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                if ext == SUITE_EXT:
                    suite = Suite(filename=file_path)
                    suite.member_update(old_name, new_name)
                else:
                    if os.path.isdir(file_path):
                        member_update(file_path, old_name, new_name)
            except Exception as e:
                pass
    except Exception as e:
        raise SVPError('Error on member update - directory %s: %s' % (path, str(e)))

class Suite(object):
    def __init__(self, name=None, desc=None, filename=None, parent=None):
        self.name = name
        self.globals = True
        self.desc = desc
        self.filename = filename
        self.members = []
        self.params = {}
        self.param_defs = script.ScriptParamGroupDef(name=script.SCRIPT_PARAM_ROOT, qname=script.SCRIPT_PARAM_ROOT)
        self.scripts = []
        self.logos = []
        self.parent = parent
        self.member_index = 0
        self.result_dir = None
        self.active_params = None
        self.result = None

        if filename:
            self.from_xml(filename=filename)

    def next_member(self):
        if self.member_index >= len(self.members):
            if self.parent is not None:
                return self.parent.next_member()
        else:
            member = self.members[self.member_index]
            self.member_index += 1
            return member

    def member_update(self, old_name, new_name):
        # print 'member_update: %s  %s  %s' % (self.filename, old_name, new_name)
        updated = False
        members = []
        for i in range(len(self.members)):
            # print 'compare: %s %s' % (os.path.normcase(self.members[i]), os.path.normcase(old_name))
            if os.path.normcase(self.members[i]) == os.path.normcase(old_name):
                if new_name is not None:
                    members.append(new_name)
                updated = True
                # print 'updated = %s' % (updated)
            else:
                members.append(self.members[i])
        # print 'update check = %s' % (updated)
        if updated:
            # print self.members
            self.members = members
            self.to_xml_file()

    def merge_suite(self, suite, working_dir):
        for m in suite.members:
          try:
            if is_suite_file(m):
                filename = os.path.join(working_dir, SUITES_DIR, os.path.normpath(m))
                member_suite = Suite(filename=filename)
                self.merge_suite(member_suite, working_dir)
            elif is_test_file(m):
                filename = os.path.join(working_dir, TESTS_DIR, os.path.normpath(m))
                # print 'merge file: ', filename
                script_config = script.ScriptConfig(filename=filename)
                if script_config.script not in self.scripts:
                    self.scripts.append(script_config.script)
                    script_path = os.path.join(working_dir, SCRIPTS_DIR, os.path.normpath(script_config.script))
                    lib_path = os.path.join(working_dir, LIB_DIR)
                    test_script = script.load_script(script_path, lib_path, path_list = extended_path_list)
                    if test_script.param_defs is not None:
                        for group in test_script.param_defs.param_groups:
                            if test_script.param_is_global(group.name):
                                if self.param_defs.param_group_find(group.name) is None:
                                    self.param_defs.param_groups.append(group)

                    # merge logos while we are at it
                    for logo in test_script.info.logos:
                        if logo not in self.logos:
                            self.logos.append(logo)
            else:
                ### log
                pass
          except Exception as e:
              print ("{}".format(e))

    def merge_param_defs(self, working_dir):
        # print 'working_dir =', working_dir
        self.param_defs = script.ScriptParamGroupDef(name=script.SCRIPT_PARAM_ROOT, qname=script.SCRIPT_PARAM_ROOT)
        self.scripts = []
        self.merge_suite(self, working_dir)
        self.param_defs.resolve_active(self.param_defs, self.param_get)
        # print self.scripts

    def contains_suite(self, working_dir, filename):
        if self.filename == filename:
            return True
        for m in self.members:
            if is_suite_file(m):
                member_filename = os.path.join(working_dir, SUITES_DIR, os.path.normpath(m))
                if filename == member_filename:
                    return True
                else:
                    suite = Suite(filename=member_filename)
                    if suite.contains_suite(working_dir, filename):
                        return True
        return False

    def param_get(self, name):
        value = None
        if self.globals is True and self.params is not None:
            value = self.params.get(name)
        if value is None:
            if self.param_defs is not None:
                value = self.param_defs.param_value(name, self.param_defs, self.param_get)
        return value

    def param_value(self, name):
        value = None
        if self.globals is True and self.params is not None:
            value = self.params.get(name)
        if value is None:
            if self.param_defs is not None:
                value = self.param_defs.param_value(name, self.param_defs, self.param_value)
        return value

    def from_xml(self, element=None, filename=None):
        if element is None and filename is not None:
            element = ET.ElementTree(file=filename).getroot()
        if element is None:
            raise SVPError('No xml document element')

        if element.tag != SUITE_ROOT:
            raise SVPError('Unexpected test suite root element %s' % (element.tag))

        self.name = element.attrib.get(SUITE_ATTR_NAME)
        if self.name is None:
            raise SVPError('Suite name missing')
        # self.desc = element.attrib.get(TEST_CFG_ATTR_DESC)
        globals = element.attrib.get(SUITE_ATTR_GLOBALS)
        if globals == 'False':
            self.globals = False

        for e in element.findall('*'):
            if e.tag == SUITE_MEMBERS:
                for e_test in e.findall('*'):
                    if e_test.tag == SUITE_MEMBER:
                        name = e_test.attrib.get(SUITE_ATTR_NAME)
                        if name:
                            self.members.append(name)

        script.params_from_xml(self.params, element)

    def to_xml(self, parent=None, filename=None):
        attr = {}
        if self.name:
            attr[SUITE_ATTR_NAME] = self.name

        if self.globals is not None:
            attr[SUITE_ATTR_GLOBALS] = str(self.globals)

        if parent is not None:
            e = ET.SubElement(parent, SUITE_ROOT, attrib=attr)
        else:
            e = ET.Element(SUITE_ROOT, attrib=attr)

        e_members = ET.SubElement(e, SUITE_MEMBERS)
        for m in self.members:
            attr = {SUITE_ATTR_NAME: m}
            ET.SubElement(e_members, SUITE_MEMBER, attrib=attr)

        script.params_to_xml(self.params, e)

        return e

    def to_xml_str(self, pretty_print=False):
        e = self.to_xml()

        if pretty_print:
            script.xml_indent(e)

        return ET.tostring(e, encoding='unicode')

    def to_xml_file(self, filename=None, pretty_print=True, replace_existing=True):
        xml = self.to_xml_str(pretty_print)
        if filename is None and self.filename is not None:
            filename = self.filename

        if filename is not None:
            if replace_existing is False and os.path.exists(filename):
                raise SVPError('File %s already exists' % (filename))
            f = open(filename, 'w')
            f.write(xml)
            f.close()
        else:
            print (xml)

RUN_MSG_ALERT = 'alert'
RUN_MSG_CONFIRM = 'confirm'
RUN_MSG_LOG = 'log'
RUN_MSG_RESULT = 'result'
RUN_MSG_RESULT_FILE = 'result_file'
RUN_MSG_STATUS = 'status'
RUN_MSG_CMD = 'cmd'

RUN_MSG_CMD_PAUSE = 'pause'
RUN_MSG_CMD_RESUME = 'resume'
RUN_MSG_CMD_STOP = 'stop'

class RunScript(script.Script):
    def __init__(self, env=None, info=None, config=None, config_file=None, params=None, conn=None):
        script.Script.__init__(self, env=env, info=info, config=config, config_file=config_file, params=params)

        self._conn = conn
        self._files_dir = env.get('files_dir', '')
        self._results_dir = env.get('results_dir', '')
        self._result_dir = env.get('result_dir', '')
        self._log_file = os.path.join(self._results_dir, env.get('result_log_file'))

    def conn_msg(self):
        msg = None
        try:
            if self._conn:
                if self._conn.poll() is True:
                    msg = self._conn.recv()
        except Exception as e:
            raise SVPError('Conn msg error: {}'.format (e))

        return msg

    def alert(self, message):
        self._conn.send({'op': RUN_MSG_ALERT,
                         'message': message})

    def confirm(self, message):
        result = False

        self._conn.send({'op': RUN_MSG_CONFIRM,
                         'message': message})

        seconds = 1000
        while seconds > 0:
            msg = self.conn_msg()
            if msg is None:
                time.sleep(.1)
                seconds -= .1
            elif isinstance(msg, dict):
                if  msg.get('op') == RUN_MSG_CONFIRM:
                    result = msg.get('result', False)
                break

        return result

    def log(self, message, level=script.INFO):
        entry = LogEntry(message, level=level)
        if self._log_file is not None:
            log_file = open(self._log_file, 'a')
            log_file.write('%s\n' % (str(entry)))
            log_file.close()
        if self._conn:
            self._conn.send({'op': RUN_MSG_LOG,
                             'timestamp': entry.timestamp_str(),
                             'level': entry.level,
                             'message': entry.message})

    def result(self, status=None, params=None):
        self.log('Test result - %s' % (script.result_str(status)))

        self._conn.send({'op': RUN_MSG_RESULT,
                         'status': status,
                         'params': params})

        # wait for confirmation of completion
        seconds = 5
        while seconds > 0:
            msg = self.conn_msg()
            if msg is None:
                time.sleep(.1)
                seconds -= .1
            elif isinstance(msg, dict):
                if  msg.get('op') == RUN_MSG_RESULT:
                    break

    def result_file(self, name=None, status=None, params=None):

        self._conn.send({'op': RUN_MSG_RESULT_FILE,
                         'name': name,
                         'status': status,
                         'params': params})

        # wait for confirmation of completion
        seconds = 5
        while seconds > 0:
            msg = self.conn_msg()
            if msg is None:
                time.sleep(.1)
                seconds -= .1
            elif isinstance(msg, dict):
                if  msg.get('op') == RUN_MSG_RESULT_FILE:
                    break

    def result_file_path(self, name):
        return os.path.join(self._results_dir, self._result_dir, name)

    def sleep(self, seconds):
        if self.callback is True:
            raise script.ScriptError('Can not call sleep() from callback function')
        current_time = time.time()
        wake_time = current_time + seconds
        while wake_time > current_time:
            sleep_time = .5
            # service timers
            timers = list(self.timers)
            for t in timers:
                next = round(t.next_timeout - current_time, 3)
                if next <= 0:
                    self.callback = True
                    t.callback(t.arg)
                    self.callback = False
                    if t.repeating is False:
                        self.timer_cancel(t)
                    else:
                        t.next_timeout += t.period
                        next = round(t.next_timeout - current_time, 3)
                if next < sleep_time:
                    sleep_time = next

            # service messages
            msg = self.conn_msg()
            if msg is not None:
                if isinstance(msg, dict):
                    if msg.get('op') == RUN_MSG_CMD:
                        self.log('message: %s' % msg)
                        if msg.get('cmd') == RUN_MSG_CMD_STOP:
                            raise script.ScriptError('Commanded stop')
                        elif msg.get('cmd') == RUN_MSG_CMD_PAUSE:
                            self._conn.send(msg)
                            paused = True
                            while paused:
                                msg = self.conn_msg()
                                if msg is None:
                                    time.sleep(.1)
                                    # seconds -= .1
                                elif msg.get('cmd') == RUN_MSG_CMD_RESUME:
                                    self._conn.send(msg)
                                    break
                # elif isinstance(msg, Confirm):
                #     return msg
                # elif isinstance(msg, Alert):
                #     return msg

            if sleep_time > 0:
                time.sleep(sleep_time)
            current_time = time.time()

'''
PROC_STATE_RUNNING = 1
PROC_STATE_COMPLETE = 2
PROC_STATE_RUNNING_PAUSE = 3
PROC_STATE_PAUSED = 4
PROC_STATE_RUNNING_STOP = 5
PROC_STATE_STOPPED = 6
'''

def makedirs(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def result_file_name(name):
    return name.replace(script.PATH_SEP, '__')

PERIODIC_RECV_LIMIT = 10

class RunContext(object):

    def __init__(self, svp_dir, svp_file=None, results=None, results_name=None):
        self.active = False
        self.results_tree = results
        if svp_dir is None or not os.path.isdir(svp_dir):
            raise SVPError('Unknown run context directory: {}'.format(svp_dir))
        self.svp_dir = svp_dir
        self.files_dir = None
        self.results_dir = None
        self.results = None
        self.results_name = results_name
        self.results_id = None
        self.results_file = None
        self.lib_path = os.path.normpath(os.path.join(svp_dir, LIB_DIR))
        self.env = {}

        self.svp_file = svp_file
        self.process = None
        self.log_file = None
        self.test_conn = None
        self.app_conn = None
        self.suites = []
        self.suite = None
        self.suite_params = None
        self.suite_result_dir = ''
        self.result_dir = ''
        self.active_result = None
        self.status = None

    def is_alive(self):
        if self.process is not None:
            return self.process.is_alive()
        return False

    def run(self):
        self.active = True
        # set root result entry
        d = datetime.datetime.now()
        self.results_id = '%d-%02d-%02d_%02d-%02d-%02d-%03d' % (d.year, d.month, d.day, d.hour, d.minute, d.second,
            d.microsecond/1000)
        # create results directory and results file
        if self.results_name is not None:
            self.results_id += '__' + result_file_name(self.results_name)
        self.results_dir = os.path.join(self.svp_dir, RESULTS_DIR, self.results_id)
        makedirs(self.results_dir)
        self.results_file = os.path.join(self.results_dir, self.results_id + RESULTS_EXT)
        self.files_dir = os.path.join(self.svp_dir, FILES_DIR)
        if self.results_tree:
            self.results = self.results_tree
            self.active_result = self.results
            self.update_result(name=self.results_id)
            self.active_result.results_index = 0
            self.svp_file = None
            result = self.active_result.next_result()
            if result is not None:
                self.svp_file = result.file()
                self.active_result = result
        else:
            self.results = rslt.Result(name=self.results_id, type=rslt.RESULT_TYPE_RESULT)
            self.active_result = self.results
            self.update_result()

        # start
        self.run_next()

    def run_next(self):
        while self.suite:
            self.active_result = self.suite.result
            if self.results_tree:
                self.svp_file = None
                result = self.active_result.next_result()
                if result is not None:
                    self.active_result = result
                    self.svp_file = result.file()
            else:
                self.svp_file = self.suite.next_member()
            if self.svp_file is None:
                self.suite = None if not self.suites else self.suites.pop()
                if self.suite is not None:
                    self.suite_params = self.suite.active_params
                    self.suite_result_dir = self.suite.result_dir
                else:
                    self.suite_params = None
                    self.suite_result_dir = self.results_dir
            else:
                break

        if self.svp_file is not None and self.status != rslt.RESULT_STOPPED:
            name, ext = os.path.splitext(self.svp_file)
            if ext == TEST_EXT:
                filename = os.path.normpath(os.path.join(self.svp_dir, TESTS_DIR, self.svp_file))
                script_config = script.ScriptConfig(filename=filename)
                script_filename = os.path.normpath(os.path.join(self.svp_dir, SCRIPTS_DIR, script_config.script))
                self.result_dir = os.path.join(self.suite_result_dir, result_file_name(name))
                makedirs(os.path.join(self.results_dir, self.result_dir))
                log_file = os.path.join(self.result_dir, result_file_name(name) + LOG_EXT)
                if self.results_tree:
                    self.update_result(status=rslt.RESULT_RUNNING, filename=log_file)
                else:
                    result = rslt.Result(name=name, type=rslt.RESULT_TYPE_TEST, filename=log_file)
                    self.active_result.add_result(result)
                    self.active_result = result
                    self.update_result(status=rslt.RESULT_RUNNING)
                env = {'files_dir': self.files_dir,
                       'results_dir': self.results_dir,
                       'result_dir': self.result_dir,
                       'results_id': self.results_id,
                       'result_log_file': log_file}
                self.start(script_filename, env, config=script_config, params=self.suite_params)
            elif ext == SUITE_EXT:
                filename = os.path.normpath(os.path.join(self.svp_dir, SUITES_DIR, self.svp_file))
                suite = Suite(filename=filename, parent=self.suite)
                # use parent suite params if present
                if self.suite is not None:
                    self.suites.append(self.suite)
                if self.suite_params:
                    suite.active_params = self.suite_params
                elif suite.globals:
                    self.suite_params = suite.active_params = suite.params
                suite.result_dir = os.path.join(self.suite_result_dir, result_file_name(name))
                self.suite = suite
                self.suite_result_dir = suite.result_dir
                if self.results_tree:
                    suite.result = self.active_result
                else:
                    suite.result = rslt.Result(name=name, type=rslt.RESULT_TYPE_SUITE)
                    self.active_result.add_result(suite.result)
                    self.active_result = suite.result
                    self.update_result()
                self.run_next()
            elif ext == SCRIPT_EXT:
                script_filename = os.path.normpath(os.path.join(self.svp_dir, SCRIPTS_DIR, self.svp_file))
                self.result_dir = os.path.join(self.suite_result_dir, result_file_name(name))
                makedirs(os.path.join(self.results_dir, self.result_dir))
                log_file = os.path.join(self.result_dir, result_file_name(name) + LOG_EXT)
                if self.results_tree:
                    self.update_result(status=rslt.RESULT_RUNNING, filename=log_file)
                else:
                    result = rslt.Result(name=name, type=rslt.RESULT_TYPE_SCRIPT, filename=log_file)
                    self.active_result.add_result(result)
                    self.active_result = result
                    self.update_result(status=rslt.RESULT_RUNNING)
                env = {'files_dir': self.files_dir,
                       'results_dir': self.results_dir,
                       'result_dir': self.result_dir,
                       'result_log_file': log_file}
                self.start(script_filename, env, config=None, params=None)
            else:
                if ext:
                    raise SVPError('Unknown target file extension: %s' % (ext))
                else:
                    raise SVPError('Target file missing extension')
            self.svp_file = None
        else:
            self.active = False
            self.complete()

    def complete(self):
        pass

    def pause(self):
        pass
        '''
        try:
            if self.process and self.app_conn and self.state == PROC_STATE_RUNNING:
                self.app_conn.send({'op': RUN_MSG_CMD,
                                    'cmd': RUN_MSG_CMD_PAUSE})
                self.state = PROC_STATE_RUNNING_PAUSE
        except Exception, e:
            raise
        '''

    def resume(self):
        pass
        '''
        try:
            if self.process and self.app_conn and self.state == PROC_STATE_PAUSED:
                self.app_conn.send({'op': RUN_MSG_CMD,
                                    'cmd': RUN_MSG_CMD_RESUME})
        except Exception, e:
            raise
        '''

    def start(self, filename, env=None, config=None, params=None):
        if self.process is not None:
            raise SVPError('Execution context process already running')

        try:
            if self.test_conn is not None:
                self.test_conn.close()
                self.test_conn = None
            if self.app_conn is not None:
                self.app_conn.close()
                self.app_conn = None
        except Exception as e:
            pass

        try:
            self.test_conn, self.app_conn = multiprocessing.Pipe()
        except Exception as e:
            print ('Error creating execution context pipe: {}'.format(e))

        try:
            if config is not None:
                script_config = copy.deepcopy(config)
            else:
                script_config = None
            self.process = MultiProcess(name='svp_process', target=process_run, args=(filename, env, script_config,
                                                                                      params, self.lib_path,
                                                                                      self.test_conn))
            self.process.start()
        except Exception as e:
            # raise
            print ('Error creating execution context process: {}'.format(e))
            try:
                if self.process:
                    self.process.terminate()
                    # self.process.join(timeout=0)
            except Exception as e:
                pass

            self.process = None

    def terminate(self):
        if self.process and self.process.is_alive():
            # ### send stop signal to process, stop forcefully for now
            try:
                self.process.terminate()
            except Exception as e:
                print ('Process termination error: {}'.format(e))
        self.status = script.RESULT_FAIL
        self.clean_up()

    def stop(self):
        try:
            if self.process and self.app_conn and self.status == rslt.RESULT_RUNNING:
                self.update_result(status=rslt.RESULT_STOPPED)
                self.app_conn.send({'op': RUN_MSG_CMD,
                                    'cmd': RUN_MSG_CMD_STOP})
        except Exception as e:
            raise e

    def clean_up(self):
        try:
            if self.test_conn is not None:
                self.test_conn.close()
                self.test_conn = None
            if self.app_conn is not None:
                self.app_conn.close()
                self.app_conn = None
        except Exception as e:
            pass

        try:
            if self.process:
                self.process.join(timeout=0)
        except Exception as e:
            pass

        if self.process and self.process.exitcode != 0:
            if self.status != rslt.RESULT_STOPPED:
                self.update_result(status=script.RESULT_FAIL)

        self.process = None

    def periodic(self):
        if self.app_conn:
            count = 0
            msg = None
            while count < PERIODIC_RECV_LIMIT:
                if self.app_conn.poll() is True:
                    try:
                        msg = self.app_conn.recv()
                        if isinstance(msg, dict):
                            op = msg.get('op')
                            if op == RUN_MSG_LOG:
                                timestamp = msg.get('timestamp')
                                level = msg.get('level')
                                message = msg.get('message')
                                self.log(timestamp, level, message)
                            elif op == RUN_MSG_ALERT:
                                message = msg.get('message')
                                self.alert(message)
                            elif op == RUN_MSG_CONFIRM:
                                message = msg.get('message')
                                msg['result'] = self.confirm(message)
                                self.app_conn.send(msg)
                            elif op == RUN_MSG_RESULT:
                                status = msg.get('status')
                                filename = msg.get('filename')
                                params = msg.get('params')
                                self.update_result(status=status, filename=filename, params=params)
                                self.app_conn.send(msg)
                            elif op == RUN_MSG_RESULT_FILE:
                                filename = None
                                status = msg.get('status')
                                name = msg.get('name')
                                params = msg.get('params')
                                if name is not None:
                                    filename = os.path.join(self.result_dir, name)
                                if self.active_result is not None:
                                    result = rslt.Result(name=name, type=rslt.RESULT_TYPE_FILE, status=status,
                                                         filename=filename, params=params)
                                    self.add_result(result)
                                self.app_conn.send(msg)
                            elif op == RUN_MSG_STATUS:
                                pass
                            elif op == RUN_MSG_CMD:
                                cmd = msg.get('cmd')
                                pass
                                '''
                                if cmd == RUN_MSG_CMD_PAUSE and self.process.state == PROC_STATE_RUNNING_PAUSE:
                                    self.state = PROC_STATE_PAUSED
                                elif cmd == RUN_MSG_CMD_RESUME and self.process.state == PROC_STATE_PAUSED:
                                    self.state = PROC_STATE_RUNNING
                                '''
                        else:
                            raise SVPError('Unknown run message type: %s' % (type(msg)))
                    except Exception as e:
                        entry = LogEntry('Error processing app connection for type {}: {}'.format(type(msg), str(e)),
                                         level=script.ERROR)
                        self.log(entry.timestamp_str(), entry.level, entry.message)

                    count += 1
                else:
                    if self.process and not self.process.is_alive():
                        self.clean_up()
                    break

        if self.active and self.process is None:
            self.run_next()

    def add_result(self, result):
        self.active_result.add_result(result)
        self.results.to_xml_file(self.results_file)

    def update_result(self, name=None, status=None, filename=None, params=None):
        print ('update_result: name={}  status={}  filename={}  params={}'.format((name), (status), (filename),
                                                                             (params)))
        self.status = status
        if self.active_result is not None:
            if name is not None:
                self.active_result.name = name
            if status is not None:
                self.active_result.status = status
            if filename is not None:
                self.active_result.filename = filename
            if params is not None:
                self.active_result.params = params
        print ('writing results: {}'.format(self.results_file))
        self.results.to_xml_file(self.results_file)

    def alert(self, message):
        print ("{}".format(message))

    def confirm(self, message):
        pass

    def log(self, timestamp, level, message):
        print ('%s %s %s'.format(timestamp, level, message))


#########################################################################################################

SVP_DIR_CONFIG_FILE = '.svp'

# SVP general configuration file
CONFIG_DIR_ROOT = '.sunspec'
CONFIG_FILE_EXT = '.xml'

APP_CFG = 'appConfig'
APP_CFG_ATTR_NAME = 'name'
APP_CFG_ATTR_TYPE = 'type'
APP_CFG_DIRS = 'dirs'
APP_CFG_DIR = 'dir'
APP_CFG_ATTR_WORKING = 'working'
APP_CFG_ATTR_VAL_TRUE = 'true'
APP_CFG_REG_PARAMS = 'reg_params'
APP_CFG_PARAM = 'param'

app_cfg_type = {'str': str, 'int': int, 'float': float, str: 'str', int: 'int', float: 'float'}

"""
    <appConfig name="TestTool">
      <dirs>
        <dir working="true">C:\\Users\\Fred\\SunSpecTestTool</dir>
        <dir>C:\\Users\Fred\\SomeOtherDir</dir>
      </dirs>
    </appConfig>

"""

def trace_dir():
    user_dir = os.path.expanduser('~')

    # make sure user home directory exists
    if not os.path.exists(user_dir):
        raise SVPError('User home directory %s does not exist' % (user_dir))

    dir = os.path.join(user_dir, CONFIG_DIR_ROOT)

    # create base directory if it does not exist
    try:
        os.makedirs(dir)
    except OSError:
        if not os.path.isdir(dir):
            raise

    return dir

def config_filename(app_name):
    user_dir = os.path.expanduser('~')

    # make sure user home directory exists
    if not os.path.exists(user_dir):
        raise SVPError('User home directory %s does not exist' % (user_dir))

    config_dir = os.path.join(user_dir, CONFIG_DIR_ROOT, app_name)

    # create config directory if it does not exist
    try:
        os.makedirs(config_dir)
    except OSError:
        if not os.path.isdir(config_dir):
            raise

    return os.path.join(config_dir, app_name + CONFIG_FILE_EXT)

class SVP(object):

    def __init__(self, app_id):
        self.app_id = app_id
        self.name = None
        self.dirs = []
        self.config_file = config_filename('SVP')
        self.run_context = None

        # command line related attributes
        self.running = True
        self.dir = None
        self.lib_path = None
        self.result_name = None
        self.suite_params = None
        self.suite = None
        self.env = {}

        self.reg_params = {'name': '',
                           'company': '',
                           'email': '',
                           'id': self.app_id,
                           'key': ''}

        try:
            self.from_xml(filename=self.config_file)
        except Exception as e:
            pass

    def run(self, args=None):

        self.run_target(args.get('svp_dir'), args.get('svp_file'))

        while self.run_context and self.run_context.active:
            self.run_context.periodic()
            time.sleep(.2)

    def run_target(self, svp_dir, svp_file):

        if self.run_context is not None:
            raise SVPError('Run context already active')

        self.run_context = RunContext(svp_dir, svp_file)
        self.run_context.run()

    def from_xml(self, element=None, filename=None):
        if element is None and filename is not None:
            element = ET.ElementTree(file=filename).getroot()

        if element is None:
            raise SVPError('No xml document element')

        if element.tag != APP_CFG:
            raise SVPError('Unexpected app config root element %s' % (element.tag))

        # self.name = element.attrib.get(APP_CFG_ATTR_NAME)

        for e in element.findall('*'):
            if e.tag == APP_CFG_REG_PARAMS:
                for p in e.findall('*'):
                    if p.tag == APP_CFG_PARAM:
                        k = p.attrib.get(APP_CFG_ATTR_NAME)
                        t = app_cfg_type.get(p.attrib.get(APP_CFG_ATTR_TYPE, 'str'), str)
                        try:
                            v = t(p.text)
                        except ValueError:
                            pass
                        if k and v:
                            self.reg_params[k] = v

            elif e.tag == APP_CFG_DIRS:
                for d in e.findall('*'):
                    if d.tag == APP_CFG_DIR:
                        if d.text:
                            working = d.attrib.get(APP_CFG_ATTR_WORKING)
                            if working == APP_CFG_ATTR_VAL_TRUE:
                                working = True
                            else:
                                working = False
                            self.dirs.append(Directory(d.text, working))

    def to_xml(self, parent=None, filename=None):
        attr = {}
        if self.name:
            attr[APP_CFG_ATTR_NAME] = self.name

        if parent is not None:
            e = ET.SubElement(parent, APP_CFG, attrib=attr)
        else:
            e = ET.Element(APP_CFG, attrib=attr)

        # registration params
        e_reg_params = ET.SubElement(e, APP_CFG_REG_PARAMS)
        for k, v in list(self.reg_params.items()):
            if v:
                attr = {'name': k, 'type': app_cfg_type.get(type(v), 'str')}
                e_param = ET.SubElement(e_reg_params, APP_CFG_PARAM, attrib=attr)
                e_param.text = str(v)
        e_dirs = ET.SubElement(e, APP_CFG_DIRS)

        for d in self.dirs:
            attr = {}
            if d.working is True:
                attr[APP_CFG_ATTR_WORKING] = APP_CFG_ATTR_VAL_TRUE
            e_dir = ET.SubElement(e_dirs, APP_CFG_DIR, attrib=attr)
            e_dir.text = d.path

        return e

    def to_xml_str(self, pretty_print=False):
        e = self.to_xml()

        if pretty_print:
            script.xml_indent(e)

        return ET.tostring(e, encoding='unicode')

    def to_xml_file(self, filename=None, pretty_print=True, replace_existing=True):
        xml = self.to_xml_str(pretty_print)

        if filename is not None:
            if replace_existing is False and os.path.exists(filename):
                raise SVPError('File %s already exists' % (filename))
            f = open(filename, 'w')
            f.write(xml)
            f.close()
        else:
            print (xml)

    def config_file_update(self):
        if self.config_file:
            self.to_xml_file(self.config_file)

    def add_directory(self, path):
        paths = self.get_directory_paths()
        if path not in paths:
            d = Directory(path)
            self.dirs.append(d)
            self.config_file_update()

    def remove_directory(self, path):
        try:
            dir = None
            for d in self.dirs:
                if d.path == path:
                    dir = d
                    break
            if dir is not None:
                self.dirs.remove(dir)
                self.config_file_update()
        except Exception as e:
            pass

    def get_directory_paths(self):
        paths = []
        for d in self.dirs:
            paths.append(d.path)
        return paths


SVP_PROG_NAME = 'SVP'

if __name__ == "__main__":
    # On Windows calling this function is necessary.
    multiprocessing.freeze_support()

    app = SVP(1)
    app.run({'svp_dir': 'c:/users/bob/pycharmprojects/svp test/',
             'svp_file': 'suite_a.ste'})


