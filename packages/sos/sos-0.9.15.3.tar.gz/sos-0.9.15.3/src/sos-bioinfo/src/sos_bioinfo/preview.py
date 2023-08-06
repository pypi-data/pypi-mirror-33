#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

from sos.utils import short_repr

def preview_bam(filename, kernel=None, style=None):
    import pysam
    res = ''
    with pysam.AlignmentFile(filename, 'rb') as bam:
        headers = bam.header
        for record_type in ('RG', 'PG', 'SQ'):
            if record_type not in headers:
                continue
            else:
                records = headers[record_type]
            res += record_type + ':\n'
            for i, record in enumerate(records):
                if isinstance(record, str):
                    res += '  ' + short_repr(record) + '\n'
                elif isinstance(record, dict):
                    res += '  '
                    for idx, (k, v) in enumerate(record.items()):
                        if idx < 4:
                            res += '{}: {}    '.format(k, short_repr(v))
                        elif idx == 4:
                            res += '...'
                            break
                if i > 4:
                    res += '\n  ...\n'
                    break
                else:
                    res += '\n'
    return res

