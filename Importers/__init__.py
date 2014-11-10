import os
import glob

#Handler info
DefaultImportHandler='m3u' #If extension is not found, use this importer
ImportHandlers={} #List of file extensions as keys (must be lower case) with data of {Name:PRETTY_NAME, ImportFunc:FUNCTION(PlaylistPath))

#Import from playlist
#Returns list of absolute paths
def DoImport(PlaylistPath):
    (_, Extension)=os.path.splitext(PlaylistPath)
    Extension=Extension[1:].lower()
    if(Extension not in ImportHandlers):
        Extension=DefaultImportHandler
    ImportHandler=ImportHandlers[Extension]
    try:
        return ImportHandler['ImportFunc'](PlaylistPath)
    except Exception as E:
        raise Exception("ListImporter '%s': %s" % (ImportHandler['Name'], str(E)))

#Import all importer modules
for ImportFile in glob.glob(os.path.dirname(__file__)+'/*.py'):
    if(not os.path.samefile(ImportFile, __file__) and os.path.isfile(ImportFile)):
        __import__('Importers.'+os.path.basename(ImportFile)[:-3])