import Importers
def _ImportMe(PlaylistPath):
    PlaylistFiles=[]
    with open(PlaylistPath, 'r') as PlaylistFileHandle:
        for LineStr in PlaylistFileHandle:
            PlaylistFiles.append(LineStr.rstrip('\n'))
    return PlaylistFiles

Importers.ImportHandlers['ptl']={'Name':"Plain Text List", 'ImportFunc':_ImportMe}