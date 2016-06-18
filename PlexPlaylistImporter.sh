#Get the script's directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [[ `uname -s` == CYGWIN* ]] || [[ `uname -s` == MINGW* ]]; then
    DIR=`cygpath -wa "$DIR"`
fi

#Call with extra variables
/usr/bin/env PYTHONIOENCODING="utf-8" python3 "$DIR/PlexPlaylistImporter.py" "$@"