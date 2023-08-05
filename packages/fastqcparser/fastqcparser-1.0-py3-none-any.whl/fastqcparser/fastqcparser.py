'''
Python module to parse FastQC output data.
'''

from __future__ import print_function
from collections import OrderedDict
import io
from warnings import warn
from zipfile import ZipFile

class FastqcDataError(Exception): pass

def cast(x) :
    cast_x = x
    if isinstance(cast_x, str) :
        try :
            cast_x = int(x)
        except ValueError :
            try :
               cast_x = float(x)
            except ValueError :
                pass
    return cast_x

def next_or_raise(it,msg) :
    # validate first line
    try :
        return next(it)
    except StopIteration :
        raise FastqcDataError(msg)


class FastQCParser(object):
    '''
    Returns a parsed data object for given fastqc data file
    '''

    def __init__(self, fp, **kwargs):
        '''
        :arg fp: Name of fastqc_data text file, fastqc.zip file, or a file
                 pointer to a fastqc_data text file. If a file pointer is
                 provided, the user is expected to close the file after
                 FastQCParser is finished.
        :type file_name: str or file pointer
        '''
        if isinstance(fp,str) : # filename, .txt or .zip
            if fp.endswith('.zip') : # zip archive, open and extract .txt
                with ZipFile(fp) as f :
                    # check for fastqc_data.txt
                    data_fn = [_ for _ in f.namelist() if _.endswith('fastqc_data.txt')]
                    if len(data_fn) == 0 :
                        raise FastqcDataError('No file matching *fastqc_data.txt '
                               'found in zip archive, aborting')
                    elif len(data_fn) > 1 :
                        warn('Multiple files matching *fastqc_data.txt found '
                                'in zip archive:\n{}\nChoosing {}'.format(
                                    '\n'.join(data_fn),
                                    data_fn[0]
                                )
                            )
                    data_fn = data_fn[0]
                    with f.open(data_fn, **kwargs) as data_f :
                        self._parse(io.TextIOWrapper(data_f))
            elif fp.endswith('.txt') :
                with open(fp, **kwargs) as f :
                    self._parse(f)

        else : # file pointer
            self._parse(fp)

        m_mark = '>>'
        m_end = '>>END_MODULE'

    def _parse(self,data_f) :

        self.modules = OrderedDict()

        # validate first line
        header = next_or_raise(data_f,'fastqc data file appears to be empty')

        if not header.startswith('##FastQC') :
            raise FastqcDataError('fastqc data file does not begin with '
                    'expected header (i.e ##FastQC), found {}'.format(header))

        # parse out version
        self.version = header.split('\t')[-1].strip()

        # start parsing modules
        curr_module = None
        for line in data_f :

            line = line.strip()

            if line.strip() == '>>END_MODULE' :
                if curr_module is not None :
                    self.modules[curr_module['name']] = curr_module

            elif line.startswith('>>') : # new module

                module_name, status = line[2:].strip().split('\t')

                # there should always be a column name line after module definition
                line = next_or_raise(data_f,'fastqc module has incomplete '
                        'definition: {}'.format(module_name)
                )

                # all modules should have at least one subsequent line starting with #
                # some have two
                meta_lines = []
                while line.startswith('#') :
                    meta_lines.append(line)
                    line = next_or_raise(data_f,'fastqc module ended prematurely, check format')

                if len(meta_lines) == 0 or not meta_lines[-1].startswith('#') :
                    raise FastqcDataError('Did not find expected fieldnames row '
                            'after module definition line, possibly malformatted '
                            'fastqc data file for module: {}'.format(module_name)
                        )

                fieldnames = meta_lines[-1][1:].strip().split('\t')

                addnl = {}
                if len(meta_lines) > 1 :
                    addnl = dict(_[1:].strip().split('	') for _ in meta_lines[:-1])
                    addnl = {k:cast(v) for k,v in addnl.items()}

                curr_module = {
                    'name': module_name,
                    'status': status,
                    'fieldnames': fieldnames,
                    'data': [[cast(_) for _ in line.strip().split('\t')]],
                    'addnl': addnl
                }

            else :

                curr_module['data'].append([cast(_) for _ in line.strip().split('\t')])

        
        # set fields for basic stats for convenience
        stats = self.modules['Basic Statistics']['data']
        self.filename = stats[0][1]
        self.file_type = stats[1][1]
        self.encoding = stats[2][1]
        self.total_sequences = stats[3][1]
        self.filtered_sequences = stats[4][1]
        self.sequence_length = stats[5][1]
        self.percent_gc = stats[6][1]

    def __enter__(self) :
        return self

    def __exit__(self,*args) :
        return

    def __getitem__(self,item) :
        return self.modules[item]

    def __str__(self) :
        out = ['FastQC version: {}'.format(self.version)]
        out.extend(['{}: {}'.format(*_) for _ in self['Basic Statistics']['data']])

        return '\n'.join(out)
