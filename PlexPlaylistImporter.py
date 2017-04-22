#!/usr/bin/env python3
#Copyright and coded by Dakusan - See http://www.castledragmire.com/Copyright for more information.
#Plex Playlist Importer - v1.1.0.0 http://www.castledragmire.com/Projects/Plex_Playlist_Importer

import sys
import os
import platform
import sqlite3
import uuid
import argparse
import Importers
from BulletHelpFormatter import BulletHelpFormatter

#Get and confirm the parameter variables
parser=argparse.ArgumentParser(description='Import playlists into plex', formatter_class=BulletHelpFormatter)
parser.add_argument('-p', '--sqlitedb-path', nargs=1, metavar='Given_DB_Path', dest='GivenDBPath',
    help=
"""The path to the sqlite3 database file
* The program tries to guess the path for the Plex data directory. If it cannot be found, this path needs to be passed explicitly
  * The default paths are:
    * Windows:
      * %%LOCALAPPDATA%%/Plex Media Server/
      * C:/Users/%%USER%%/AppData/Local/Plex Media Server/
    * Linux:
      * %%PLEX_HOME%%/Library/Application Support/Plex Media Server/
* If the database is still not found from the given Plex path, the full path to the database is required
  * Defaults: (%%PLEX_PATH%% is from the path found from above)
    * %%PLEX_PATH%%/Plug-in Support/Databases/com.plexapp.plugins.library.db
    * %%PLEX_PATH%%/Plug-Ins/Databases/com.plexapp.plugins.library.db
Note: When passing a parameter string, environmental variables are not processed"""
)
parser.add_argument('-e', '--playlist_encoding', nargs=1, default=['utf-8'], metavar='Playlist_Encoding', dest='PlaylistEncoding', help='The encoding the playlist file is in. This is generally "utf-8", but may also be "ISO-8859-1". Default=utf-8')
parser.add_argument('-t', '--override-type', nargs=1, metavar='File_Type_Override', dest='FileTypeOverride', help='The file type to encode as. If the file extension is not recognized, the file is parsed as a Winamp playlist (m3u). This allows overriding the determined file type. Default=NONE')
parser.add_argument('-f', '--force-list', default=[False], action='store_true', dest='ForceListCreation', help='Do not prompt to create the playlist if it does not already exist.')
parser.add_argument('-i', '--account-id', nargs=1, default=['1'], metavar='Account_ID', dest='AccountID', help='The id of plex account to add playlist to if not master.')
parser.add_argument('-n', '--account-name', nargs=1, default=[''], metavar='Account_Name', dest='AccountName', help='The name of plex account to add playlist to if not master.')
parser.add_argument('PlaylistPath', nargs=1, metavar='Playlist_Path', help='The path of the playlist file')
parser.add_argument('PlexPlaylistName', nargs='?', metavar='Plex_Playlist_Name',
    help=
"""The name of the playlist in Plex to import to.
* If not given, the program will prompt for it.
* If the given playlist does not already exist, the program will prompt on whether to create it (unless -f is specified)."""
)

#Extract args into the global namespace, turning lists into their first value
PlaylistPath=PlexPlaylistName=GivenDBPath=PlaylistEncoding=FileTypeOverride=ForceListCreation=AccountID=AccountName=None #Initiate the variables here so IDEs know they have been defined
args=parser.parse_args()
for name, val in vars(args).items():
    locals()[name]=(val[0] if isinstance(val, type([])) else val) #While settings vars via locals() is not guaranteed, it seems to work in this outer scope

#Confirm the playlist path
PlaylistPath=os.path.realpath(PlaylistPath)
if(not os.path.isfile(PlaylistPath)):
   sys.exit("Given playlist path is not found")

#Confirm the plex path
def ConfirmDBPath(Path):
    #Test for direct DB file path
    if(os.path.isfile(Path)):
       return Path

    #Test for valid path by looking for the file
    DBFileName='com.plexapp.plugins.library.db'
    if(not os.path.isdir(Path)):
       raise Exception("Given Plex path is not a directory (or given filename is not found)")
    for RelativeDBFolderPath in ['Plug-in Support/Databases', 'Plug-Ins/Databases']: #Different possible database folder paths
        PlexDBPath=os.path.realpath('%s/%s/%s' % (Path, RelativeDBFolderPath, DBFileName))
        if(os.path.isfile(PlexDBPath)):
            return PlexDBPath

    #If no valid path is found
    raise Exception("Cannot find DB file from given path. Try searching for com.plexapp.plugins.library.db (or *.db) and passing the result's file path directly")

#Get the plex path from an argument, if given
PlexDBPath=None
if(GivenDBPath is not None):
    try:
        PlexDBPath=ConfirmDBPath(GivenDBPath)
    except Exception as E:
        sys.exit(E)

#If path is not given, attempt to figure it out
if(PlexDBPath is None):
    #Get the user's home directory
    if(platform.system()!='Linux'): #Assume windows for all other system's. Nuts to OSX :-)
        if('LOCALAPPDATA' in os.environ):
            PlexDBPath=os.environ['LOCALAPPDATA']+'/Plex Media Server/'
        elif('USER' in os.environ):
            PlexDBPath=('C:/Users/%s/AppData/Local/Plex Media Server/' % (os.environ['USER'])) #TODO: There might be better environmental variables to check before $USER, as C drive should not be assumed
        else:
            PlexDBPath=''
    else: #Linux. THIS IS UNTESTED
        PlexDBPath=(os.environ['PLEX_HOME']+'/Library/Application Support/Plex Media Server/' if 'PLEX_HOME' in os.environ else '')
    PlexDBPath=os.path.realpath(PlexDBPath)
    try:
        if(PlexDBPath==''):
            raise Exception("Cannot deduce plex path from environmental variables")
        PlexDBPath=ConfirmDBPath(PlexDBPath)
    except Exception as E:
        sys.exit("Cannot guess Plex home directory. Pass your plex home directory as the third parameter")

#Open the playlist file and confirm/retrieve all paths
try:
    PlaylistFiles=Importers.DoImport(PlaylistPath, FileTypeOverride, PlaylistEncoding)
except Exception as E:
    sys.exit(E)

#Get the playlist name if not passed as a program argument
while PlexPlaylistName is None or len(PlexPlaylistName.strip())==0:
    print("Playlist name (Cannot be blank): ", end="")
    sys.stdout.flush()
    PlexPlaylistName=sys.stdin.readline()
PlexPlaylistName=PlexPlaylistName.strip()

#Insert into DB from a Dict
def DBInsert(Cur, TableName, Values):
    Cur.execute(
        'INSERT INTO `%s` (`%s`) VALUES (%s)' % (
            TableName,
            '`, `'.join(Values.keys()),
            ', '.join('?'*len(Values))
        ), tuple(Values.values())
    )

#Perform DB operations
#TODO: This whole section should really use batch lookups and inserts, but not really needed for the scope of the project
try:
    #Connect to the DB
    DB=sqlite3.connect(PlexDBPath)
    Cur=DB.cursor()

    #Get the list of IDs for the playlist's files in the DB
    DBFileIDs=[]
    DBFileDurations=[] #Parallel to DBFileIDs
    for FilePath in PlaylistFiles:
        Cur.execute('SELECT MI.metadata_item_id, MP.duration FROM media_parts AS MP INNER JOIN media_items AS MI ON MI.id=MP.media_item_id WHERE MP.file=? COLLATE NOCASE', (FilePath,)) #TODO: Should only have COLLATE NOCASE on case insensitive file systems
        Val=Cur.fetchone()
        if(Val is None):
            sys.exit("File not found in DB: "+FilePath)
        DBFileIDs.append(Val[0])
        DBFileDurations.append(Val[1] if Val[1] is not None else 0)

    #Confirm/create the plex playlist
    Now=Cur.execute('SELECT DATETIME("NOW")').fetchone()[0]
    PLAYLIST_TYPE=15
    if(PlexPlaylistName==''):
        sys.exit("Playlist name cannot be blank")
    Cur.execute('SELECT id FROM metadata_items WHERE title=? AND metadata_type=?', (PlexPlaylistName, PLAYLIST_TYPE,))
    PlexPlaylistID=Cur.fetchone()
    if(PlexPlaylistID is not None): #Name found
        PlexPlaylistID=PlexPlaylistID[0]
    else: #Name not found
        #Ask user if they want to create the plex playlist
        while(True):
            if ForceListCreation:
                break

            print("Plex playlist is not already created. Would you like to create it now (y/n)? ", end="")
            sys.stdout.flush()
            Answer=sys.stdin.readline()
            if(Answer=='' or (Answer[0].lower()!='y' and Answer[0].lower()!='n')): #No matches
                continue
            if(Answer[0].lower()=='n'): #Do not create, so exit prematurely
                sys.exit()
            break #Yes, create the plex playlist

        #Create the plex playlist
        DBInsert(Cur, 'metadata_items', {
            'metadata_type':PLAYLIST_TYPE, 'media_item_count':0, 'title':PlexPlaylistName, 'title_sort':PlexPlaylistName, 'index':0, 'duration':0, 'added_at':Now, 'updated_at':Now,
            'guid':'com.plexapp.agents.none://'+str(uuid.uuid1()), 'extra_data':'pv%3AdurationInSeconds=1',
            'absolute_index':10 #TODO: Where does this come from?
        })
        PlexPlaylistID=Cur.lastrowid
        
        #BK: Convert AccountName to AccountID
        if(AccountName is not None):
            Cur.execute('SELECT id FROM accounts WHERE name=?', (AccountName,))
            AccountID=Cur.fetchone()
            if(AccountID is not None): #Name found
                AccountID=AccountID[0]
            else: #Name not found
                AccountID='1'
        
        DBInsert(Cur, 'metadata_item_accounts', {
            'account_id':AccountID, 'metadata_item_id':PlexPlaylistID #BK: Made AccountID dynamic
        })
        DB.commit()

    #Insert the items into the playlist
    AddDuration=0
    OrderInc=1000
    CurOrder=Cur.execute('SELECT MAX(`order`) FROM play_queue_generators WHERE playlist_id=?', (PlexPlaylistID,)).fetchone()[0]
    Vars={'playlist_id':PlexPlaylistID, 'metadata_item_id':0, 'order':(0 if CurOrder is None else CurOrder)+OrderInc, 'created_at':Now, 'updated_at':Now, 'uri':''}
    for Index, DBItemID in enumerate(DBFileIDs):
        Vars['metadata_item_id']=DBItemID
        DBInsert(Cur, 'play_queue_generators', Vars)
        Vars['order']+=OrderInc
        AddDuration+=(int)(DBFileDurations[Index]/1000)

    #Update the playlists info
    Cur.execute('UPDATE metadata_items SET duration=duration+?, media_item_count=media_item_count+? WHERE id=?', (AddDuration, len(DBFileIDs), PlexPlaylistID))

    #Commit and return success
    DB.commit()
    print("%i items imported" % len(DBFileIDs))
except Exception as E:
    sys.exit("DB Error: "+str(E))
