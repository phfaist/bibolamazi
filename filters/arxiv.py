
import shlex;
import argparse;

from core.bibfilter import BibFilter;

MODE_UNPUBLISHED_NOTE = 1;
MODE_EPRINT = 2;


class ArxivNormalizeFilter(BibFilter):
    
    def __init__(self, mode):
        BibFilter.__init__(self);
        self.mode = mode;

    def name(self):
        return "ArXiv clean-up"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        return entry;


def parse_args(optionstring):
    a = argparse.ArgumentParser('bibclean: ArXiv normalize filter')
    a.add_mutually_exclusive_group(required=False)
    a.add_argument('--unpublished-note', dest='unpublished_note',
                          action='store_true')
    a.add_argument('--eprint', action='store_true')

    args = a.parse_args(shlex.split(optionstring));

    mode = -1;
    if (args.unpublished_note):
        mode = MODE_UNPUBLISHED_NOTE;
    elif (args.eprint):
        mode = MODE_EPRINT;

    return { 'mode': mode };


def getclass():
    return ArxivNormalizeFilter;

