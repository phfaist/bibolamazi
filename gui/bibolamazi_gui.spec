# -*- mode: python -*-
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import re

#from hooks import hookutils

## WARNING: Assuming that CWD is inside the `gui/' directory !!

# NOTE: cannot use __file__ here as it refers to the Python PyInstaller egg ?!?
bibolamazi_path = os.path.realpath(os.path.join(os.getcwd(), '..'))
bibolamazigui_dir = os.path.join(bibolamazi_path, 'gui')


##
## Make sure some modules are accessible.
##
#import updater4pyi
#import pybtex
#import arxiv2bib
#import pylatexenc


##
## set up our import paths well first of all for this same script.
##
sys.path.insert(0, bibolamazi_path)
sys.path.insert(0, bibolamazigui_dir)
# no longer have 3rd party libraries in repo
#sys.path.insert(0, os.path.join(bibolamazi_path, '3rdparty', 'pybtex'))
#sys.path.insert(0, os.path.join(bibolamazi_path, '3rdparty', 'arxiv2bib'))
#sys.path.insert(0, os.path.join(bibolamazi_path, '3rdparty', 'pylatexenc'))
import bibolamazi.init
from bibolamazi.core.bibfilter import factory as filterfactory


#import hack_pkg_resources_entry_points


##
## All the python files under 'filters/'
##
#filterlist = hookutils.collect_submodules('filters')

#
# Hack for pybtex plugins, because pybtex uses pkg_resources.iter_entry_points()
#
# pybtex_entry_pts = ["pybtex.database.input",
#                     "pybtex.database.output",
#                     "pybtex.backends",
#                     "pybtex.style.labels",
#                     "pybtex.style.names",
#                     "pybtex.style.sorting",
#                     "pybtex.style.formatting",]                    
# for pkgname in pybtex_entry_pts:
#     hack_pkg_resources_entry_points.register_entry_points(pkgname)


##
## pre-compile filter list
##
tmp_genfiles_dirname = '_tmp_genfiles'
tmp_genfiles_dir = os.path.join(bibolamazigui_dir, tmp_genfiles_dirname)
#import filters
filternames = [finfo.filtername for finfo in filterfactory.detect_filters()]
if not os.path.isdir(tmp_genfiles_dir):
    os.mkdir(tmp_genfiles_dir)
with open(os.path.join(tmp_genfiles_dir,'bibolamazi_compiled_filter_list.py'), 'w') as f:
    f.write("""\
filter_list = %r
from bibolamazi.filters import %s
""" %(filternames, ", ".join(filternames)))


add_data_files = []

if sys.platform.startswith('darwin'):
    # qt.conf for MacOS X
    with open(os.path.join(tmp_genfiles_dir,'qt.conf'), 'w') as f:
        f.write("[Paths]\nPrefix = MacOS/PyQt5/Qt")
    add_data_files += [ ( os.path.join(tmp_genfiles_dir, 'qt.conf'), '.',) ]
else:
    # qt.conf for other platforms
    with open(os.path.join(tmp_genfiles_dir,'qt.conf'), 'w') as f:
        f.write("[Paths]\nPrefix = PyQt5/Qt")
    add_data_files += [ ( os.path.join(tmp_genfiles_dir, 'qt.conf'), '.',) ]


#runhookentrypts = hack_pkg_resources_entry_points.generate_runtime_hook(tmp_genfiles_dir)

##
## PyInstaller config part
##
a = Analysis(['bin/bibolamazi_gui'],
             pathex=[
                 os.path.join(bibolamazi_path,'gui'),
                 bibolamazi_path,
                 tmp_genfiles_dir,
                 ], #+ [ # no longer 3rdparty dir
                 #os.path.join(bibolamazi_path, '3rdparty', x)
                 #    for x in bibolamazi.init.third_party
                 #],
             hiddenimports=[
                 'PyQt5',
                 'bibolamazi_compiled_filter_list'
             ],# + hack_pkg_resources_entry_points.get_hidden_imports(),
             hookspath=[],#[os.path.join(bibolamazi_path,'gui','pyi-hooks')],
             datas=add_data_files,
             #runtime_hooks=[ runhookentrypts ],
             )

if (sys.platform.startswith('win')):
    # have this problem of 'File already installed but should not: pyconfig.h'
    # hack from http://stackoverflow.com/questions/19055089/
    for d in a.datas:
        if 'pyconfig' in d[0]:
            a.datas.remove(d)
            break


pyz = PYZ(a.pure)
if (sys.platform.startswith('darwin')):

    add_plist = '''\
<key>NSPrincipalClass</key>
<string>NSApplication</string>
<key>NSHighResolutionCapable</key>
<string>True</string>
'''

    macosx_deployment_target = os.environ.get('MACOSX_DEPLOYMENT_TARGET', "10.14").strip()

    if tuple([int(i) for i in macosx_deployment_target.split(".")]) >= (10, 14):
        print("Enabling dark mode for Mac OS X deployment target = %r"%(macosx_deployment_target))
        add_plist += '''\
<key>NSRequiresAquaSystemAppearance</key>
<string>False</string>
    '''


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
    # --------------------------------------------
    # edit Info.plist for Retina displays
    bundlename = app.name
    plistname = os.path.join(bundlename, 'Contents', 'Info.plist')
    with open(plistname, 'r') as f:
        infoplistdata = f.read()
    # insert defs for hi-res displays
    (infoplistdata, nsubs) = re.subn('</dict>\s*</plist>', add_plist+'</dict></plist>', infoplistdata)
    if nsubs != 1:
        print("WARNING: COULDN'T MODIFY INFO.PLIST!!")
    else:
        with open(plistname, 'w') as f:
            f.write(infoplistdata)
    # --------------------------------------------

else:
    kwargs = {}
    if (sys.platform.startswith('win')):
        exename = os.path.join('dist', 'bibolamazi-win32.exe')
        kwargs['icon'] = 'bibolamazi_icon.ico'
    else:
        exename = os.path.join('dist', 'bibolamazi_gui')
        
    exe = EXE(pyz,
              a.scripts,
              a.binaries,
              a.zipfiles,
              a.datas,
              name=exename,
              debug=False,
              console=False,
              strip=None,
              upx=False,
              **kwargs
              )
    
