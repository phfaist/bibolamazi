

import re

from core.butils import getbool;
from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;

# for the arxiv info parser tool
import arxiv;



class UrlNormalizeFilter(BibFilter):
    
    helptext = "";

    def __init__(self, Strip=True, StripAllIfDoiOrArxiv=True, StripDoiUrl=True, StripArxivUrl=True,
                 UrlFromDoi=False, UrlFromArxiv=False):
        BibFilter.__init__(self);

        self.strip = getbool(Strip);
        self.stripallifdoiorarxiv = getbool(StripAllIfDoiOrArxiv);
        self.stripdoiurl = getbool(StripDoiUrl);
        self.striparxivurl = getbool(StripArxivUrl);
        self.urlfromdoi = getbool(UrlFromDoi);
        self.urlfromarxiv = getbool(UrlFromArxiv);

        logger.debug('url filter constructor')
        

    def name(self):
        return "URL clean-up"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #
        
        if (self.strip and 'url' in entry.fields):
            del entry.fields['url'];

        #logger.debug("Stripped 'url' entry from field=%r", entry.fields);

        arxivinfo = arxiv.getArXivInfo(entry);

        if ('url' in entry.fields):
            urls = entry.fields['url'].split();
        else:
            urls = [];

        if (self.stripallifdoiorarxiv):
            if ('doi' in entry.fields or arxivinfo is not None):
                entry.fields.pop('url', None)

        if (self.stripdoiurl):
            for url in urls:
                if re.match(r'^http://dx.doi.org/', url):
                    urls.remove(url);
            if (len(urls)):
                entry.fields['url'] = " ".join(urls);
            else:
                entry.fields.pop('url', None)

        if (self.striparxivurl):
            for url in urls:
                if re.match(r'^http://arxiv.org/abs/', url):
                    urls.remove(url);
            if (len(urls)):
                entry.fields['url'] = " ".join(urls);
            else:
                entry.fields.pop('url', None)

        if (self.urlfromdoi):
            if ('doi' in entry.fields):
                urls.append("http://dx.doi.org/"+entry.fields['doi']);
                entry.fields['url'] = " ".join(urls);

        if (self.urlfromarxiv):
            if (arxivinfo is not None):
                urls.append("http://arxiv.org/abs/"+arxivinfo['arxivid']);
                entry.fields['url'] = " ".join(urls);

        return entry


def get_class():
    return UrlNormalizeFilter;

