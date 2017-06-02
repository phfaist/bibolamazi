
import sys as _sys
import os.path as _ospath


_curpath = _ospath.abspath(_ospath.dirname(_ospath.realpath(__file__)))
_thirdparty = _ospath.join(_curpath, '3rdparty')


_sys.path.append(_ospath.join(_thirdparty, 'pybtex'))
_sys.path.append(_ospath.join(_thirdparty, 'arxiv2bib'))
_sys.path.append(_ospath.join(_thirdparty, 'pylatexenc'))

