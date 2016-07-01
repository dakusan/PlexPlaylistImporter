from distutils.core import setup
import py2exe

#Get importers
import os
import glob
ImportsToAdd=['\n\n#Added imports']
ImporterInitFile='Importers/__init__.py'
for ImportFile in glob.glob('Importers/*.py'):
    if(not os.path.samefile(ImportFile, ImporterInitFile) and os.path.isfile(ImportFile)):
        ImportsToAdd.append('import Importers.'+os.path.basename(ImportFile)[:-3])

#Add importers to the importer init file
import io
with open(ImporterInitFile, 'rb+') as ContentFile:
    ImporterInitFileContents=ContentFile.read()
    ContentFile.write(bytes("\n".join(ImportsToAdd), encoding="utf-8"))

setup(
    name='Plex Playlist Importer',
    version='1.1.0',
    description='Import playlists into Plex',
    author='Dakusan',
    url='https://www.castledragmire.com/Projects/Plex_Playlist_Importer',
    options={
        'py2exe':{
            'excludes':['pydoc', 'tarfile', 'difflib', 'pdb', 'distutils', 'html', 'http', 'logging', 'pydoc_data', 'unittest', 'urllib', 'xml', 'win32api', 'win32wnet', 'win32con', 'readline', 'netbios', 'ssl', 'bz2', 'lzma', 'select', 'socket', 'pyexpat', 'unicodedata', 'email'],
            'bundle_files':2,
            'compressed':True,
        },
    },
    zipfile=None,
    console=['PlexPlaylistImporter.py']
)

#Restore the importer init file
with open(ImporterInitFile, 'wb+') as ContentFile:
    ContentFile.write(ImporterInitFileContents)