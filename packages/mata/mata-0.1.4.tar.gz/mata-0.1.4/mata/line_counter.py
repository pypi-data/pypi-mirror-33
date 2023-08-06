#!/usr/bin/env python3

import os

def countDirectory(prefix=''):
    global files
    global total
    global comments

    if os.getcwd() in oldDirs:
        return
    oldDirs.append(os.getcwd())
    for filename in os.listdir():
        if filename.split('.')[-1] in ('py', 'pyx') and filename not in ['line_counter.py', '__init__.py']:
            for line in open(filename).read().split('\n'):
                total += 1 if line != '' and not line.strip().startswith('#') else 0
                comments += 1 if line.strip().startswith('#') else 0
            files.append((prefix+'/'+filename)[1:])
        elif '.' not in filename:
            try:
                currentDir = os.getcwd()
                os.chdir(filename)
                countDirectory(prefix+'/'+filename)
                os.chdir(currentDir)
            except NotADirectoryError:
                pass

total = 0
comments = 0
files = []
oldDirs = []
countDirectory()

print("Files Scanned: \n - {}\n# of Files: {}".format('\n - '.join(files), len(files)))
print("Lines of Code: {}\nComments: {}".format(total, comments))
print("Code to Comment Ratio: {} : 1".format(round(total/comments, 2)))
