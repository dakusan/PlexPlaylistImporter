import Importers
import os
import re

#Convert a cygwin path to a windows path
def ConvertCygPath(Path):
    import subprocess
    return subprocess.check_output(['cygpath', '-w', Path]).decode('utf-8').strip('\n')

def _ImportMe(PlaylistPath, PlaylistEncoding):
    PlaylistFiles=[]
    PlaylistDirPath=os.path.dirname(PlaylistPath)+os.sep
    IsFirstLine=True
    try:
        with open(PlaylistPath, 'r', encoding=PlaylistEncoding) as PlaylistFileHandle: #Specify UTF-8 here to avoid Unicode errors
            for LineStr in PlaylistFileHandle:
                #Handle first line of file
                if(IsFirstLine):
                    IsFirstLine=False
                    #Remove UTF8 BOM
                    if re.match(r'^utf.?8$', PlaylistEncoding):
                        if re.match('^\uFEFF', LineStr):
                            LineStr=LineStr[1:]

                #Ignore comments/controls
                if(LineStr[0]=='#'):
                    continue

                #Confirm the file exists
                IsAbsolutePath=(os.path.isabs(LineStr) or LineStr[0:2]=='\\\\' or re.match('[a-z]:\\\\', LineStr, flags=re.I)) #Check for absolute path syntax (plus smb or drive letter)
                LookupPath=os.path.realpath(('' if IsAbsolutePath else PlaylistDirPath)+LineStr.rstrip('\n'))
                if(not os.path.isfile(LookupPath)): #Confirm file exists
                    raise Exception('PlaylistFileNotFound', LineStr)

                #Convert cygwin path
                if(re.match(r'^/cygdrive/', LookupPath, re.I)!=None):
                    LookupPath=ConvertCygPath(LookupPath)

                #Add the relative path to the playlist file list
                PlaylistFiles.append(LookupPath)
    except IOError as E:
        raise Exception("Cannot open playlist file: "+str(E))
    except Exception as E:
        if(len(E.args)>1 and E.args[0]=='PlaylistFileNotFound'):
            raise Exception("Cannot find file listed in playlist (must be relative to the playlist): "+E.args[1])
        else:
            raise E
    return PlaylistFiles

Importers.ImportHandlers['m3u']={'Name':"Winamp playlist", 'ImportFunc':_ImportMe}