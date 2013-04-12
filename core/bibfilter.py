

class BibFilter:

    # constants
    BIB_FILTER_SINGLE_ENTRY = 1;
    BIB_FILTER_ENTRY_LIST = 2;
    BIB_FILTER_FILE = 3;

    
    def __init__(self, *pargs, **kwargs):
        pass

    def name(self):
        return None;

    def action(self):
        return -1;


    def filter_bibentry(self, x):
        return x;

    def filter_bibentry_list(self, x):
        return x;

    def filter_bibfilterfile(self, x):
        return x;


    
