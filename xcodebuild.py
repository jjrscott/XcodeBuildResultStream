#!/usr/bin/env python3.9

# MIT License
#
# Copyright (c) 2021 John Scott
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import shlex
import re
import subprocess
import json
import sys
import uuid
import select

def main():
    args = sys.argv
    args[0] = 'xcodebuild'

    descriptor_for_reading, descriptor_to_give_to_xcodebuild_for_writing = os.pipe() # new file descriptor read , fd write

    args += ['-resultBundlePath', '/tmp/' + str(uuid.uuid1()) + 'xcresult']
    args += ['-resultStreamPath', f'/dev/fd/{descriptor_to_give_to_xcodebuild_for_writing}']

    result_stream = open(descriptor_for_reading)

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, pass_fds=[descriptor_to_give_to_xcodebuild_for_writing])
    os.close(descriptor_to_give_to_xcodebuild_for_writing)

    lines_read = 0
    while True:
        lines_read += read_stream(result_stream, blocking=False)
        try:
            process.wait(timeout=1)
            break
        except subprocess.TimeoutExpired:
            pass
    lines_read += read_stream(result_stream, blocking=True)
    result_stream.close()

    if lines_read == 0:
        while line := process.stderr.readline().decode():
            if match := re.match(r'xcodebuild: error: *([^\n]+)', line):
                print_line('Error', match.group(1), color=31)
    exit(process.returncode)

def readline(file, blocking=True):
    ready = True
    if not blocking:
        ready = select.select([file], [], [], 1)[0]

    line = None
    if ready:
        line = file.readline()
    return line

def print_line(prefix, line, color=30):
    line = line.rstrip()
    print(f'\u001b[1;{color}m{prefix}\u001b[0m {line}')

def read_stream(fp, blocking=True):
    lines_read = 0
    while line := readline(fp, blocking=blocking):
        lines_read += 1
        # print(line, end='')
        data = json.loads(line)
        if data['name']['_value'] == 'issueEmitted':
            # print(re.sub('\n?$', '\n', json.dumps(data['structuredPayload'], sort_keys=True, indent=2)))

            severity = data['structuredPayload']['severity']['_value']
            issueType = data['structuredPayload']['issue']['issueType']['_value']
            message = data['structuredPayload']['issue']['message']['_value']

            if severity in {'warning'}:
                print_line(issueType, message, color=33)
            elif severity in {'error'}:
                print_line(issueType, message, color=31)
            elif severity in {'testFailure'}:
                pass
            else:
                exit(re.sub('\n?$', '\n', json.dumps(data, sort_keys=True, indent=2)))

        elif data['name']['_value'] == 'logMessageEmitted':
            pass
            # print(data['name']['_value'], data['structuredPayload']['message']['title']['_value'])
        elif data['name']['_value'] == 'logSectionCreated':
            # print(re.sub('\n?$', '\n', json.dumps(data, sort_keys=True, indent=2)))
            title = data['structuredPayload']['head']['title']['_value']
            if match := re.match(r"^Run custom shell script '(.*?)'$", title):
                title = 'Script '+match.groups(0)[0]
            words = title.split(' ', 1)
            if len(words) > 1:
                print_line(words[0], words[1])
            # print(data['structuredPayload']['head']['title']['_value'])
        elif data['name']['_value'] == 'logTextAppended':
            pass
            # print(data['name']['_value'], data['structuredPayload']['text']['_value'].rstrip())
        elif data['name']['_value'] == 'testSuiteStarted':
            print_line('Test Suite Started', data['structuredPayload']['testIdentifier']['identifier']['_value'])
        elif data['name']['_value'] == 'testStarted':
            print_line('Test', data['structuredPayload']['testIdentifier']['identifier']['_value'])
        elif data['name']['_value'] == 'testFinished':
            test_identifier = data['structuredPayload']['test']['identifier']['_value']
            test_status = data['structuredPayload']['test']['testStatus']['_value']
            if test_status in {'Success'}:
                print_line(test_status, test_identifier, color=32)
            elif test_status in {'Failure'}:
                print_line(test_status, test_identifier, color=31)
            else:
                exit(re.sub('\n?$', '\n', json.dumps(data['structuredPayload']['test']['testStatus'], sort_keys=True, indent=2)))
        elif data['name']['_value'] == 'testSuiteFinished':
            pass
        elif data['name']['_value'] == 'actionFinished':
            continue
            status = data['structuredPayload']['tail']['buildResult']['status']['_value']

            if status == 'succeeded':
                print_line('Succeeded', '', color=32)
            elif status == 'failed':
                print_line('Failed', '', color=31)
            else:
                print_line(status.upper(), '', color=45)
            # print(re.sub('\n?$', '\n', json.dumps(data['structuredPayload']['tail'], sort_keys=True, indent=2)))
        elif data['name']['_value'] not in ['invocationStarted', 'actionStarted', 'logSectionAttached', 'logSectionClosed', 'invocationFinished']:
            exit(re.sub('\n?$', '\n', json.dumps(data, sort_keys=True, indent=2)))
            print(data['name']['_value'])
    return lines_read

main()
