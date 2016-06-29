import os
import re
import glob

#Handler info
DefaultImportHandler='m3u' #If extension is not found, use this importer
ImportHandlers={} #List of file extensions as keys (must be lower case) with data of {Name:PRETTY_NAME, ImportFunc:FUNCTION(PlaylistPath))

#Import from playlist
#Returns list of absolute paths
def DoImport(PlaylistPath, FileTypeOverride, PlaylistEncoding):
    #Attempt to get extension via FileTypeOverride
    Extension=None
    if FileTypeOverride is not None:
        Extension=re.search(r'[^\.\r\n]+$', FileTypeOverride)  #Remove everything before the "."
        if Extension is not None:
            Extension=Extension.group(0).lower()

    #If no valid FileTypeOverride, get extension from the file path
    if Extension is None:
        (_, Extension)=os.path.splitext(PlaylistPath)
        Extension=Extension[1:].lower()

    #Determine the final extension to use
    if(Extension not in ImportHandlers):
        Extension=DefaultImportHandler
    ImportHandler=ImportHandlers[Extension]

    #Execute the import handler
    try:
        return ImportHandler['ImportFunc'](PlaylistPath, 'utf-8' if PlaylistEncoding is None else PlaylistEncoding)
    except Exception as E:
        raise Exception("ListImporter '%s': %s" % (ImportHandler['Name'], str(E)))

#Import all importer modules
for ImportFile in glob.glob(os.path.dirname(__file__)+'/*.py'):
    if(not os.path.samefile(ImportFile, __file__) and os.path.isfile(ImportFile)):
        __import__('Importers.'+os.path.basename(ImportFile)[:-3])