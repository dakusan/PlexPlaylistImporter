import Importers
import os

def _ImportMe(PlaylistPath):
    PlaylistFiles=[]
    PlaylistDirPath=os.path.dirname(PlaylistPath)+os.sep
    try:
        with open(PlaylistPath, 'r', encoding='utf-8') as PlaylistFileHandle: #Specify UTF-8 here to avoid Unicode errors
            for LineStr in PlaylistFileHandle:
                if(LineStr[0]=='#'): #Ignore comments/controls
                    continue
                IsAbsolutePath=(os.path.isabs(LineStr) or LineStr[0:2]=='\\\\' or re.match('[a-z]:\\\\', LineStr, flags=re.I)) #Check for absolute path syntax (plus smb or drive letter)
                LookupPath=os.path.realpath(('' if IsAbsolutePath else PlaylistDirPath)+LineStr.rstrip('\n'))
                if(not os.path.isfile(LookupPath)): #Confirm file exists
                    raise Exception('PlaylistFileNotFound', LineStr)
                PlaylistFiles.append(LookupPath) #Add the relative path to the playlist file list
    except IOError as E:
        raise Exception("Cannot open playlist file: "+str(E))
    except Exception as E:
        if(len(E.args)>1 and E.args[0]=='PlaylistFileNotFound'):
            raise Exception("Cannot find file listed in playlist (must be relative to the playlist): "+E.args[1])
        else:
            raise E
    return PlaylistFiles

Importers.ImportHandlers['m3u']={'Name':"Winamp playlist", 'ImportFunc':_ImportMe}