import Importers
def _ImportMe(PlaylistPath, PlaylistEncoding):
    PlaylistFiles=[]
    with open(PlaylistPath, 'r', encoding=PlaylistEncoding) as PlaylistFileHandle:
        for LineStr in PlaylistFileHandle:
            PlaylistFiles.append(LineStr.rstrip('\n'))
    return PlaylistFiles

Importers.ImportHandlers['ptl']={'Name':"Plain Text List", 'ImportFunc':_ImportMe}