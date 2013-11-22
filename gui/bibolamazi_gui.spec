# -*- mode: python -*-

import sys
import os
import os.path

from hooks import hookutils

## WARNING: Assuming that CWD is inside the `gui/' directory !!

#bibolamazi_path = '/home/pfaist/ETH/PhD/util/bibolamazi'
bibolamazi_path = os.path.realpath(os.path.join(os.getcwd(), '..'))


##
## set up our import paths well first of all for this same script.
##
sys.path += [bibolamazi_path];
import bibolamazi_init
import filters

##
## All the python files under 'filters/'
##
#filterlist = hookutils.collect_submodules('filters')

##
## pre-compile filter list
##
import filters
filternames = filters.detect_filters()
with open('bibolamazi_compiled_filter_list.py', 'w') as f:
    f.write("""\
filter_list = %r
from filters import %s
""" %(filternames, ", ".join(filternames)))


##
## PyInstaller config part
##
a = Analysis(['bibolamazi_gui.py'],
             pathex=[
                 os.path.join(bibolamazi_path,'gui'),
                 bibolamazi_path,
                 ] + [
                 os.path.join(bibolamazi_path, '3rdparty', x)
                 for x in bibolamazi_init.third_party
                 ],
             hiddenimports=['bibolamazi_compiled_filter_list'],#+filterlist,
             hookspath=None)
pyz = PYZ(a.pure)
if (sys.platform.startswith('darwin')):
    exe = EXE(pyz,
              a.scripts,
              exclude_binaries=True,
              name=os.path.join('dist', 'bibolamazi_gui_exe'),
              debug=True,
              strip=None,
              upx=True,
              console=False,
              )
    coll = COLLECT(exe,
                   a.binaries,
                   a.zipfiles,
                   a.datas,
                   strip=None,
                   upx=True,
                   name=os.path.join('dist', 'bibolamazi_gui'),
                   )
    app = BUNDLE(coll,
                 name=os.path.join('dist', 'Bibolamazi.app'),
                 icon='bibolamazi_icon.icns',
                 )
##     exe = EXE(pyz,
##               a.scripts,
##               exclude_binaries=True,
##               name=os.path.join('dist', 'bibolamazi_gui_exe'),
##               debug=True,
##               strip=None,
##               upx=False,
##               console=True )
##     coll = COLLECT(exe,
##                    a.binaries,
##                    a.zipfiles,
##                    a.datas,
##                    strip=None,
##                    upx=False,
##                    name=os.path.join('dist', 'bibolamazi_gui'))
##     app = BUNDLE(exe,
##                  name=os.path.join('dist', 'Bibolamazi.app'),
##                  icon='bibolamazi_icon.icns',
##                  )
else:
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              name='bibolamazi_gui',
              debug=True,
              strip=None,
              upx=True,
              console=True )
    
