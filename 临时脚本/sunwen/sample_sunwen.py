#!/usr/bin/env python3
"""Sample Sun Wen images by page theme."""
import json

d = json.load(open('/opt/hongloumeng/app/static/sunwen/sunwen_captions.json'))
targets = {
    'canon': [1, 2, 3, 15],
    'customs': [37, 49, 84, 120],
    'history': [10, 11, 28],
    'scholars': [8, 10, 92],
    'editions': [60, 85],
    'library': [80, 112],
    'index': [1, 65, 120],
}
for page, indices in targets.items():
    print('--- ' + page + ' ---')
    for idx in indices:
        entry = d[idx - 1]
        fname = 'sunwen_%03d.jpg' % idx
        print('  ' + fname + ': ' + entry['caption'])
