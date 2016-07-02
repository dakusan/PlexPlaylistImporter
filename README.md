Plex Playlist Importer - v1.1.0.x http://www.castledragmire.com/Projects/Plex_Playlist_Importer

# Import playlists into Plex

My music directories have been growing for over 2 decades in a folder based hierarchy, often using playlists for organization. Plex’s music organization is counterintuitive to this organizational structure, and Plex currently does not have an easy way to import external playlists. Hence this script was born :-)

You can run this by directly dragging playlists onto it.<br>
This script is fully unicode compliant.

##Running and Troubleshooting
* While this script requires Python 3 (compiled against v3.4), a stand-alone Windows binary version is also available on the URL at the top of this file.<br>
* While running the windows executable, if you get an error of “The program can't start because MSVCR100.dll is missing...”, download the “[Microsoft Visual C++ 2010 Redistributable Package (x86)](https://www.microsoft.com/en-us/download/details.aspx?id=5555)”.
* If running through the Python source, The Python sqlite3 lib is required, but it should come with Python.
  * If running this mentions something about “```no such module : FTS4```”, you may need to replace the sqlite3.dll or sqlite3.so for your Python, which can be found at https://www.sqlite.org/download.html .
    * For a Python for Windows install, the DLL location will most likely be located at one of the following locations:
      * ```C:\Python%PYTHON_VERSION%\DLLs```
      * ```C:\Program Files (x86)\Python%PYTHON_VERSION%-32\DLLs```
      * ```C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python%PYTHON_VERSION%\DLLs```

##Parameters:
**usage**:<br>
PlexPlaylistImporter.py [-h] [-p Given_DB_Path] [-e Playlist_Encoding] [-t File_Type_Override] [-f] Playlist_Path Plex_Playlist_Name

**positional arguments**:
<table><tr><th>Arguments</th><th>Explanation</th></tr>
  <tr><td><b>Playlist_Path</b></td><td>The path of the playlist file</td></tr>
  <tr><td><b>Plex_Playlist_Name</b></td><td>
    The name of the playlist in Plex to import to.<ul>
      <li>If not given, the program will prompt for it.</li>
      <li>If the given playlist does not already exist, the program will prompt on whether to create it (unless -f is specified).</li>
    </ul>
  </td></tr>
</table>

**optional arguments**:
<table><tr><th>Arguments</th><th>Explanation</th></tr>
<tr>
  <td><pre><b>-h</b> OR <b>--help</b></pre></td>
  <td>show this help message and exit</td>
</tr><tr>
<td><pre><b>-p</b> OR <b>--sqlitedb-path</b></pre>Given_DB_Path</td><td>The path to the sqlite3 database file<ul>
  <li>The program tries to guess the path for the Plex data directory. If it cannot be found, this path needs to be passed explicitly<ul>
    <li>The default paths are:<ul>
      <li><b>Windows</b>:<ul>
        <li><b>%LOCALAPPDATA%</b>/Plex Media Server/</li>
        <li>C:/Users/<b>%USER%</b>/AppData/Local/Plex Media Server/</li>
      </ul></li>
      <li><b>Linux</b>:<ul>
        <li><b>%PLEX_HOME%</b>/Library/Application Support/Plex Media Server/</li>
      </ul></li>
    </ul></li>
  </ul></li>
  <li>If the database is still not found from the given Plex path, the full path to the database is required<ul>
    <li>Defaults: (<b>%PLEX_PATH%</b> is from the path found from above)<ul>
      <li><b>%PLEX_PATH%</b>/Plug-in Support/Databases/com.plexapp.plugins.library.db</li>
      <li><b>%PLEX_PATH%</b>/Plug-Ins/Databases/com.plexapp.plugins.library.db</li>
    </ul></li>
    <li>Note: When passing a parameter string, environmental variables are not processed</li>
  </ul></li>
</ul></td>
</tr><tr>
  <td><pre><b>-e</b> OR <b>--playlist_encoding</b></pre>Playlist_Encoding</td>
  <td>The encoding the playlist file is in. This is generally “<b>utf-8</b>”, but may also likely be “<b>ISO-8859-1</b>”. Default=<b>utf-8</b></td>
</tr><tr>
  <td><pre><b>-t</b> OR <b>--override-type</b></pre>File_Type_Override</td>
  <td>The file type to encode as. If the file extension is not recognized, the file is parsed as a Winamp playlist (m3u). This allows overriding the determined file type. Default=<b>NONE</b></td>
</tr><tr>
  <td><pre><b>-f</b> OR <b>--force-list</b></pre></td>
  <td>Do not prompt to create the playlist if it does not already exist.</td>
</tr></table>

The only playlist type that is currently supported is Winamp playlists (.m3u).<br>
Playlist importers just collect the absolute files names, and others can easily be dropped into the “Importers” directory without any other code changes.<br>
While the M3U importer (Importers/M3U.py) is the most appropriate to use as a template, I included a second example one (PTL.py) which just pulls in absolute file names with no error checks.

PlexPlaylistImporter.sh is just included to force proper Unicode (utf-8) encoding and column widths on the console.

##How it works
The songs you want to play have to already exist in the Plex database.<br>
When you add a song to Plex (through Plex), it stores the song’s full file path in the Plex database. What this script does is derive all the full song paths in a playlist file that you give it, checks those paths against Plex’s database, and then adds the matches in the proper order into the Plex playlist you specified.<br>
So for this reason, the script must be ran on the same computer running the Plex server so that it can match the paths. (There are, of course, workarounds to this. **However, I highly recommend against it, as I have found that doing this may corrupt the Plex server database**).

##Creating the executable
```python setup.py py2exe```

Copyright and coded by Dakusan - See http://www.castledragmire.com/Copyright for more information.