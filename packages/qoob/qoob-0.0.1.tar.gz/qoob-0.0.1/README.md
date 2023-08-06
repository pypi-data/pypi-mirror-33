# qoob
- Cross-platform foobar-like music player
- Written in Python 3 and Qt 5

# Features
- Folder structure library organization
- Metadata is parsed from file header when available
- Missing metadata is guessed with regex, from title and folder structure
- Realtime library filter to quickly find a specific media
- Tray icon with playback control and notifications
- Customizable notification and title format
- Customizable sorting routine
- Hotkeys and command line interface

# Screenshots
**Library view**

![alt tag](https://gitlab.com/william.belanger/qoob/raw/master/screenshots/library.png)


**Options and playlists**
![alt tag](https://gitlab.com/william.belanger/qoob/raw/master/screenshots/options.png)


# Command line interface
- Playback: --play-pause --stop --previous --next --shuffle on/off
- Delete current media from disk: --delete
- Load folder: --folder \<path\>
- Load file: --file \<path\>
- Exit application: --quit

# Hotkeys
- Space: play-pause
- Backspace: remove selection from playlist
- Delete: delete selection from disk
- Ctrl + X: cut selection
- Ctrl + C: copy selection
- Ctrl + V: paste selection

# Installation
- Arch Linux: install 'qoob-git' from the AUR
- Linux (non-Arch): sudo pip install qoob
- Windows:
     Install the lastest version of Python, along with the PyPi utility (pip)
    - Open the command prompt (cmd.exe) with administrator privileges
    - Type 'python -m pip install pyqt5 mutagen'
    - Clone the repository and extract the qoob folder
    - Create a shortcut to run the script manually with 'python your_installation_path/qoob/\_\_init\_\_.py'

# Todo
- Customizable hotkeys
- Customizable headers
