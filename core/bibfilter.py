


class BibFilterError(Exception):
    def __init__(self, filtername, errorstr):
        if (not isinstance(filtername, basestring)):
            filtername = '<unknown>'
        Exception.__init__(self, "filter `"+filtername+"': "+errorstr);




class BibFilter:

    # constants
    BIB_FILTER_SINGLE_ENTRY = 1;
    BIB_FILTER_BIBLIOGRAPHYDATA = 2;
    BIB_FILTER_BIBFILTERFILE = 3;

    # subclasses should provide meaningful help texts
    helpdescription = "Some filter that filters some entries";
    helptext = "";

   
    def __init__(self, *pargs, **kwargs):
        pass

    def name(self):
        return None;

    def action(self):
        return -1;


    def filter_bibentry(self, x):
        raise BibFilterError(self.name(), 'filter_bibentry() not implemented !')

    def filter_bibliographydata(self, x):
        raise BibFilterError(self.name(), 'filter_bibliographydata() not implemented !')

    def filter_bibfilterfile(self, x):
        raise BibFilterError(self.name(), 'filter_bibfilterfile() not implemented !')



    # convenience functions, no need to override
    @classmethod
    def getHelpDescription(cls):
        return cls.helpdescription.strip();

    @classmethod
    def getHelpText(cls):
        return cls.helptext.strip();
    

