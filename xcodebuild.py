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

did_get_results = False

def main():
    args = sys.argv
    args[0] = 'xcodebuild'

    build_path = 'build'

    system('rm', '-rf', build_path)

    result_stream_path = os.path.join(build_path, 'ResultStream.json')

    args += ['-resultBundlePath', os.path.join(build_path, 'Result.xcresult')]
    args += ['-resultStreamPath', result_stream_path]
    args += ['-derivedDataPath', build_path]

    system('mkdir', '-p', build_path)
    system('touch', result_stream_path)

    args += ['-resultBundleVersion', '3']

    process_stdout_path = os.path.join(build_path, 'StandardOut.txt')
    process_stderr_path = os.path.join(build_path, 'StandardError.txt')
    system('touch', process_stdout_path)
    system('touch', process_stderr_path)

    command = " ".join(map(lambda arg:shlex.quote(arg), args))
    print(u"\u001b[1mSystem\u001b[0m"+' '+command)

    process = subprocess.Popen(args, stdout=open(process_stdout_path, 'wb'), stderr=open(process_stderr_path, 'wb'))

    with open(result_stream_path, 'r') as results_stream:
        while True:
            read_lines(results_stream)
            try:
                process.wait(timeout=1)
                break
            except subprocess.TimeoutExpired:
                pass
        read_lines(results_stream)

    if not did_get_results:
        with open(process_stderr_path, 'r') as process_stderr:
            while line := process_stderr.readline():
                line = line.replace('xcodebuild: error:', u"\u001b[1m\u001b[31mError\u001b[0m")
                print(line, end='')
        # print(u"\u001b[1m\u001b[31mFailed\u001b[0m")

def read_lines(fp):
    global did_get_results
    while line := fp.readline():
        did_get_results = True
        # print(line, end='')
        data = json.loads(line)
        if data['name']['_value'] == 'issueEmitted':
            # print(re.sub('\n?$', '\n', json.dumps(data['structuredPayload'], sort_keys=True, indent=2)))

            severity = data['structuredPayload']['severity']['_value']
            issueType = data['structuredPayload']['issue']['issueType']['_value']
            message = data['structuredPayload']['issue']['message']['_value']

            color = ''
            if severity == 'warning':
                color = u"\u001b[33m"
            elif severity == 'error':
                color = u"\u001b[31m"
            else:
                color = u"\u001b[44m"


            print(u"\u001b[1m"+color+issueType+u"\u001b[0m"+' '+message)
        elif data['name']['_value'] == 'logMessageEmitted':
            pass
            # print(data['name']['_value'], data['structuredPayload']['message']['title']['_value'])
        elif data['name']['_value'] == 'logSectionCreated':
            title = data['structuredPayload']['head']['title']['_value']
            if match := re.match(r"^Run custom shell script '(.*?)'$", title):
                title = 'Script '+match.groups(0)[0]
            words = title.split(' ', 1)
            print(u"\u001b[1m"+words[0]+u"\u001b[0m"+' '+words[1])
            # print(data['structuredPayload']['head']['title']['_value'])
        elif data['name']['_value'] == 'logTextAppended':
            pass
            # print(data['name']['_value'], data['structuredPayload']['text']['_value'].rstrip())
        elif data['name']['_value'] == 'actionFinished':
            continue
            status = data['structuredPayload']['tail']['buildResult']['status']['_value']

            message = ''

            if status == 'succeeded':
                message = u"\u001b[1m\u001b[32mSucceeded\u001b[0m"
            elif status == 'failed':
                message = u"\u001b[1m\u001b[31mFailed\u001b[0m"
            else:
                message = u"\u001b[1m\u001b[45m"+status.upper()+u"\u001b[0m"
            print(message)
            # print(re.sub('\n?$', '\n', json.dumps(data['structuredPayload']['tail'], sort_keys=True, indent=2)))
        elif data['name']['_value'] not in ['invocationStarted', 'actionStarted', 'logSectionAttached', 'logSectionClosed', 'invocationFinished']:
            print(data['name']['_value'])

def system(*args):
    command = " ".join(map(lambda arg:shlex.quote(arg), args))
    print(u"\u001b[1mSystem\u001b[0m"+' '+command)
    result = subprocess.run(args)
    if result.returncode != 0:
        exit(result)

main()
