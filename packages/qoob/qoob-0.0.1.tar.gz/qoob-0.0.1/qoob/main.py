#!/usr/bin/python3
import json
import mutagen
import os
import re
import sys
from PyQt5 import QtGui, QtWidgets, QtCore, QtMultimedia, QtDBus, uic

try:
    import qoob.gui_main
except ImportError:
    pass

# Setup paths and default options
LOCAL_DIR = os.path.dirname(os.path.realpath(__file__)) + "/"
DB_DIR = os.path.expanduser("~/.config/qoob/")

PREFERENCES_DEFAULT = \
{
    "trayIcon": True,
    "trayNotify": True,
    "trayMinimize": True,
    "deleteConfirm": True,
    "cleanFolder": True,
    "resumePlayback": True,
    "stripTitlesBox": True,
    "expandLibrary": True,
    "sortByDefault": False,
    "currentTab": 0,
    "monitorInterval": 0,
    "playbackPosition": 0,
    "currentMediaState": 0,
    "currentMedia": "",
    "fileManager": "spacefm --no-saved-tabs",
    "tooltipFormat": "%title% (%artist%)",
    "titleFormat": "%title% (%artist%) - qoob",
    "sortingRoutine": ["Track (Ascending)", "Album (Ascending)", "Artist (Ascending)", "Disable sorting"],
    "musicDatabase": []
}

# Common variables and function
mappings = {}
mappings["artist"] = ("TPE0", "TPE1", "TPE2", u"©ART", "Author", "Artist", "ARTIST", "artist", "TRACK ARTIST", "TRACKARTIST", "TrackArtist", "Track Artist")
mappings["album"] = ("TALB", "ALBUM", "Album", u"©alb", "album")
mappings["track"] = ("TRCK", "TRACKNUMBER", "Track", "trkn", "tracknumber")
mappings["title"] = ("TIT2", "TITLE", "Title", u"©nam", "title")
allowedFileTypes = (".mp3", ".flac", ".ogg", ".m4a", ".wav")
trackPattern = re.compile(r"\b\d{2}\b|\b\d{2}(?=\D)")


def getTrackChar(match):
    return "" if match.start() == 0 else " - "


def parseAudioHeader(path, metadata=None):
    if path in metadata:
        return metadata[path]
    tags = {"duration": "?"}

    # Try to parse data from file header
    try:
        header = mutagen.File(path)
        if header and header.info:
            s = int(header.info.length)
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            tags["duration"] = "%02d:%02d:%02d" % (h, m, s)

        for target in ("artist", "album", "track", "title"):
            for tag in mappings[target]:
                try:
                    if header:
                        if type(header) is mutagen.flac.FLAC or type(header) is mutagen.oggvorbis.OggVorbis:
                            header = dict(header)
                        result = header[tag][-1]
                        if type(result) is tuple:
                            result = str(result[0])
                        if target == "track":
                            result = result.split("/")[0]
                        tags[target] = result
                        break
                except KeyError:
                    pass
    except:
        print(path)
        print(str(sys.exc_info()[0]), str(sys.exc_info()[1]), "\n")

    # Fallback; guess missing infos from filename and folder structure
    if "artist" not in tags or "album" not in tags or "track" not in tags or "title" not in tags:
        basename = os.path.basename(path)
        title = os.path.splitext(basename)[0]

        # Fetch album and artis from path
        album = os.path.abspath(os.path.join(path, os.pardir))
        artist = os.path.abspath(os.path.join(album, os.pardir))
        album = os.path.basename(album)
        artist = os.path.basename(artist)

        # Fetch track number from title, first strip artist/album in case it contain two digits numbers
        track = re.sub(r"\W*" + artist + r"\W*", "", title, flags=re.IGNORECASE, count=1)
        track = re.sub(r"\W*" + album + r"\W*", "", track, flags=re.IGNORECASE, count=1)
        track = re.search(trackPattern, track)
        track = track.group() if track else ""

        if "artist" not in tags:
            tags["artist"] = artist
        if "album" not in tags:
            tags["album"] = album
        if "track" not in tags:
            tags["track"] = track
        if "title" not in tags:
            newTitle = title
            if gui.ui.stripTitlesBox.isChecked():
                # Remove artist, album and track from title
                newTitle = re.sub(r"\W*" + artist + r"\W*", "", newTitle, flags=re.IGNORECASE, count=1)
                newTitle = re.sub(r"\W*" + album + r"\W*", "", newTitle, flags=re.IGNORECASE, count=1)
                newTitle = re.sub(r"\W*" + track + r"\W*", getTrackChar, newTitle, flags=re.IGNORECASE, count=1)

            if newTitle:
                tags["title"] = newTitle
            else:
                # Only remove track from title
                tags["title"] = re.sub(r"\W*" + track + r"\W*", getTrackChar, title, flags=re.IGNORECASE, count=1)
    metadata[path] = tags
    return tags


class Database(object):
    def __init__(self, dbFile, default=None):
        self.dbFile = DB_DIR + dbFile + ".json"
        if not os.path.isdir(DB_DIR):
            os.mkdir(DB_DIR)
        if os.path.isfile(self.dbFile) and os.stat(self.dbFile).st_size > 0:
            self.load()

            # Look for missing keys
            if default:
                if not set(default) == set(self.db):
                    self.db = self.copyDict(default)
        else:
            self.db = default if default else {}
            with open(self.dbFile, "w") as f:
                f.write(json.dumps(self.db, indent=2, sort_keys=False))

    def load(self):
        with open(self.dbFile, "r") as f:
            self.db = json.load(f)

    def save(self):
        with open(self.dbFile, "w") as f:
            f.write(json.dumps(self.db, indent=2, sort_keys=False))

    def copyDict(self, dictionnary):
        # from https://writeonly.wordpress.com/2009/05/07/deepcopy-is-a-pig-for-simple-data
        output = dict().fromkeys(dictionnary)
        for key, value in dictionnary.items():
            try:
                output[key] = value.copy()  # dictionnaries, sets
            except AttributeError:
                try:
                    output[key] = value[:]  # lists, tuples, strings, unicode
                except TypeError:
                    output[key] = value  # integers
        return output


class PlaylistTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setHeaderLabels(["Artist", "Album", "Track", "Title", "Duration"])
        self.header().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self.header().setStretchLastSection(False)
        self.setAlternatingRowColors(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(parent.menuShow)
        self.itemActivated.connect(parent.playerActivateSelection)
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 200)
        self.setColumnWidth(2, 80)
        self.setColumnWidth(4, 80)


class PlaylistSortBoxWidget(QtWidgets.QCheckBox):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setText("Enable sorting")
        self.clicked.connect(self.toggleSort)
        if parent.ui.sortByDefaultBox.isChecked():
            self.setChecked(True)

    def toggleSort(self):
        self.parent.currentTab.setSortingEnabled(self.isChecked())


class ViewerTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self):
        super().__init__()
        self.setFlags(self.flags() &~ QtCore.Qt.ItemIsDropEnabled)

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key1 = self.text(column)
        key2 = other.text(column)
        try:
            return int(key1) < int(key2)
        except ValueError:
            return key1.lower() < key2.lower()


class MonitorThread(QtCore.QObject):
    libraryScanDoneSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    @QtCore.pyqtSlot()
    def scanAll(self):
        for folder in range(self.parent.ui.dbTree.topLevelItemCount()):
            path = self.parent.ui.dbTree.topLevelItem(folder).text(0)
            self.scanRecursive(path)
            self.libraryScanDoneSignal.emit(path)

    @QtCore.pyqtSlot(str)
    def scanFolder(self, path):
        self.scanRecursive(path)
        self.libraryScanDoneSignal.emit(path)

    def scanRecursive(self, folder):
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if os.path.isdir(path):
                self.scanRecursive(path)
            elif os.path.splitext(path)[1].lower() in allowedFileTypes:
                parseAudioHeader(path, self.parent.metadata.db)


class QDBusServer(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.__dbusAdaptor = QDBusServerAdapter(self)


class QDBusServerAdapter(QtDBus.QDBusAbstractAdaptor):
    QtCore.Q_CLASSINFO("D-Bus Interface", "org.qoob.session")
    QtCore.Q_CLASSINFO("D-Bus Introspection",
    '  <interface name="org.qoob.session">\n'
    '    <method name="parse">\n'
    '      <arg direction="in" type="ss" name="cmd"/>\n'
    '    </method>\n'
    '  </interface>\n')

    def __init__(self, parent):
        super().__init__(parent)

    @QtCore.pyqtSlot(str, str)
    def parse(self, cmd, arg):
        gui.parseCommand(cmd, arg)


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Load databases
        self.preferences = Database("preferences", default=PREFERENCES_DEFAULT)
        self.metadata = Database("metadata")
        self.playlist = Database("playlist")

        # Setup variables
        self.tabs = {}
        self.lastPlayed = []
        self.database = []
        self.copied = []
        self.shuffle = False
        self.lastItem = None
        self.path = ""

        # Setup UI
        if "qoob.gui_main" in sys.modules:
            self.ui = qoob.gui_main.Ui_MainWindow()
            self.ui.setupUi(self)
        else:
            self.ui = uic.loadUi(LOCAL_DIR + "gui_main.ui", self)

        self.initStyle()
        self.initWidgets()
        self.initThreads()
        self.initPreferences()
        self.initTrayIcon()
        self.initTimers()
        self.initEvents()
        self.initPlaylists()

        # Display main window and resume playback
        self.show()
        if self.resumePlayback and self.preferences.db["currentMediaState"] == QtMultimedia.QMediaPlayer.PlayingState:
            self.playerSetMedia(self.preferences.db["currentMedia"])

    def initStyle(self):
        # Init icons
        icons = ["play", "pause", "shuffle_on", "shuffle_off", "tray", "quit", "previous", "next", "stop",
                "copy", "delete", "file", "folder", "paste", "remove", "tab_add", "cut", "refresh", "filter_clear"]
        self.icon = {}
        for icon in icons:
            self.icon[icon] = QtGui.QIcon(LOCAL_DIR + "icons/" + icon + ".svg")
        self.ui.playButton.setIcon(self.icon["play"])
        self.ui.stopButton.setIcon(self.icon["stop"])
        self.ui.nextButton.setIcon(self.icon["next"])
        self.ui.previousButton.setIcon(self.icon["previous"])
        self.ui.shuffleButton.setIcon(self.icon["shuffle_off"])
        self.ui.refreshButton.setIcon(self.icon["refresh"])

        # Init stylesheet
        iconPath = LOCAL_DIR + "icons/"
        stylesheet = "QTabBar::close-button { image: url(" + iconPath + "tab_close.svg); }\n"
        stylesheet += "QTabBar::close-button:hover { image: url(" + iconPath + "tab_hover.svg); }\n"
        stylesheet += "QPushButton#libraryFilterClearButton { border-image: url(" + iconPath + "filter_clear.svg); }\n"
        stylesheet += "QPushButton#libraryFilterClearButton:hover { border-image: url(" + iconPath + "filter_hover.svg); }"
        self.ui.viewTab.setStyleSheet(stylesheet)
        self.ui.libraryFilterClearButton.setStyleSheet(stylesheet)

    def initWidgets(self):
        self.tabs["Library viewer"] = {"playlist": PlaylistTreeWidget(self), "sort": PlaylistSortBoxWidget(self)}
        self.currentTab = self.tabs["Library viewer"]["playlist"]
        self.ui.viewLayout.addWidget(self.tabs["Library viewer"]["playlist"])
        self.ui.viewLayout.addWidget(self.tabs["Library viewer"]["sort"])
        self.ui.statusBar = QtWidgets.QStatusBar()
        self.ui.statusRightLabel = QtWidgets.QLabel()
        self.ui.statusBar.addPermanentWidget(self.ui.statusRightLabel)
        self.setStatusBar(self.ui.statusBar)
        self.setWindowTitle("qoob")
        self.setWindowIcon(self.icon["tray"])
        self.menu = QtWidgets.QMenu()
        self.menu.aboutToShow.connect(self.menuRefresh)

        self.ui.dummyTabButton = QtWidgets.QPushButton()
        self.ui.dummyTabButton.setFixedSize(0, 0)
        self.ui.newTabButton = QtWidgets.QPushButton()
        self.ui.newTabButton.setFlat(True)
        self.ui.newTabButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ui.newTabButton.setFixedSize(30, 20)
        self.ui.newTabButton.setIcon(self.icon["tab_add"])
        self.ui.newTabButton.clicked.connect(self.tabAdd)
        self.ui.viewTab.setTabEnabled(1, False)
        self.ui.viewTab.tabCloseRequested.connect(self.tabClose)
        self.ui.viewTab.tabBar().setTabButton(0, QtWidgets.QTabBar.RightSide, self.ui.dummyTabButton)
        self.ui.viewTab.tabBar().setTabButton(1, QtWidgets.QTabBar.RightSide, self.ui.newTabButton)
        self.ui.viewTab.currentChanged.connect(self.tabChanged)
        self.ui.viewTab.installEventFilter(self)
        self.ui.viewTab.tabBar().installEventFilter(self)

    def initThreads(self):
        # Common threads
        self.random = QtCore.QRandomGenerator()
        self.process = QtCore.QProcess()
        self.player = QtMultimedia.QMediaPlayer()
        self.player.mediaStatusChanged.connect(self.mediaChangedEvent)
        self.player.durationChanged.connect(self.playerUpdateDuration)
        self.player.positionChanged.connect(self.playerUpdateSlider)
        self.player.seekableChanged.connect(self.seekableChangedEvent)

        # Scanner thread
        self.worker = MonitorThread(self)
        self.workerThread = QtCore.QThread()  # Move the Worker object to the Thread object
        self.workerThread.started.connect(self.worker.scanAll)  # Init worker loop() at startup
        self.worker.moveToThread(self.workerThread)
        self.worker.libraryScanDoneSignal.connect(self.libraryScanDoneSignal)  # Connect your signals/slots
        self.workerThread.start()

    def initPreferences(self):
        self.ui.trayIconBox.setChecked(self.preferences.db["trayIcon"])
        self.ui.trayNotifyBox.setChecked(self.preferences.db["trayNotify"])
        self.ui.trayMinimizeBox.setChecked(self.preferences.db["trayMinimize"])
        self.ui.deleteConfirmBox.setChecked(self.preferences.db["deleteConfirm"])
        self.ui.cleanFolderBox.setChecked(self.preferences.db["cleanFolder"])
        self.ui.resumePlaybackBox.setChecked(self.preferences.db["resumePlayback"])
        self.ui.sortByDefaultBox.setChecked(self.preferences.db["sortByDefault"])
        self.ui.stripTitlesBox.setChecked(self.preferences.db["stripTitlesBox"])
        self.ui.expandLibraryBox.setChecked(self.preferences.db["expandLibrary"])
        self.ui.fileManagerLine.setText(self.preferences.db["fileManager"])
        self.ui.tooltipFormatLine.setText(self.preferences.db["tooltipFormat"])
        self.ui.titleFormatLine.setText(self.preferences.db["titleFormat"])
        self.ui.monitorIntervalBox.setValue(self.preferences.db["monitorInterval"])
        self.resumePlayback = self.ui.resumePlaybackBox.isChecked()

        # Load sort routine options
        self.ui.sortSelectedList.addItems(self.preferences.db["sortingRoutine"])
        sortActions = ("Artist (Ascending)", "Artist (Descending)", "Album (Ascending)", "Album (Descending)", "Track (Ascending)", "Track (Descending)", "Title (Ascending)", "Title (Descending)", "Duration (Ascending)", "Duration (Descending)", "Disable sorting")
        for item in sortActions:
            if item not in self.preferences.db["sortingRoutine"]:
                self.ui.sortAvailableList.addItem(item)

        # Load music database folders
        for folder in self.preferences.db["musicDatabase"]:
            self.dbAddButtonEvent(folder)

        # Find the default music folder (linux)
        if not self.preferences.db["musicDatabase"]:
            xdgDirectories = os.path.expanduser("~/.config/user-dirs.dirs")
            if os.path.isfile(xdgDirectories):
                with open(xdgDirectories) as f:
                    for line in f.read().splitlines():
                        line = line.split("=")
                        if line[0] == "XDG_MUSIC_DIR":
                            musicFolder = line[1].replace("$HOME", "~")
                            musicFolder = os.path.expanduser(musicFolder[1:-1])
                            self.dbAddButtonEvent(musicFolder)
                            break

    def initTrayIcon(self):
        trayIcon = QtGui.QIcon(self.icon["tray"].pixmap(64, 64))  # SVG to pixmap conversion (KDE compatibility)
        menu = QtWidgets.QMenu()
        menu.addAction(self.icon["next"], "Next", self.nextButtonEvent)
        menu.addAction(self.icon["previous"], "Previous", self.previousButtonEvent)
        menu.addAction(self.icon["shuffle_on"], "Shuffle", self.shuffleTrayEvent)
        menu.addAction(self.icon["stop"], "Stop", self.stopButtonEvent)
        menu.addAction(self.icon["quit"], "Quit", app.exit)
        self.trayIcon = QtWidgets.QSystemTrayIcon()
        self.trayIcon.setIcon(trayIcon)
        self.trayIcon.setContextMenu(menu)
        self.trayIcon.activated.connect(self.clickEvent)
        if self.ui.trayIconBox.isChecked():
            self.trayIcon.show()

    def initTimers(self):
        self.connectTimer = QtCore.QTimer(interval=500)
        self.connectTimer.timeout.connect(self.playerUpdateStatus)
        self.connectTimer.start()

        self.monitorTimer = QtCore.QTimer()
        self.monitorTimer.timeout.connect(self.libraryScanAll)
        self.librarySetScanInterval()

        self.showTooltipTimer = QtCore.QTimer(singleShot=True)
        self.showTooltipTimer.timeout.connect(self.tooltipDisplay)
        self.hideTooltipTimer = QtCore.QTimer(singleShot=True)
        self.hideTooltipTimer.timeout.connect(QtWidgets.QToolTip.hideText)

    def initEvents(self):
        self.ui.libraryTree.itemSelectionChanged.connect(self.librarySelectItem)
        self.ui.playButton.clicked.connect(self.playButtonEvent)
        self.ui.stopButton.clicked.connect(self.stopButtonEvent)
        self.ui.nextButton.clicked.connect(self.nextButtonEvent)
        self.ui.previousButton.clicked.connect(self.previousButtonEvent)
        self.ui.shuffleButton.clicked.connect(self.shuffleButtonEvent)
        self.ui.refreshButton.clicked.connect(self.refreshButtonEvent)
        self.ui.dbAddButton.clicked.connect(self.dbAddButtonEvent)
        self.ui.dbDeleteButton.clicked.connect(self.dbDeleteButtonEvent)
        self.ui.dbBrowseButton.clicked.connect(self.dbBrowseButtonEvent)
        self.ui.libraryFilterLine.textChanged.connect(self.libraryFilterEvent)
        self.ui.libraryFilterClearButton.clicked.connect(self.ui.libraryFilterLine.clear)
        self.ui.trayIconBox.clicked.connect(self.trayIconBoxEvent)
        self.ui.sortAddButton.clicked.connect(self.sortAddButtonEvent)
        self.ui.sortRemoveButton.clicked.connect(self.sortRemoveButtonEvent)
        self.ui.monitorIntervalBox.valueChanged.connect(self.librarySetScanInterval)
        self.ui.slider.installEventFilter(self)

    def initPlaylists(self):
        for tabName in self.playlist.db:
            if not tabName == "Library viewer":
                self.tabAdd(tabName)

            # Load sorting option
            sort = self.playlist.db[tabName]["sort"]
            self.tabs[tabName]["playlist"].sortByColumn(sort[1], sort[2])
            self.tabs[tabName]["sort"].setChecked(sort[0])
            self.tabs[tabName]["playlist"].setSortingEnabled(sort[0])

            # Load files
            for path in self.playlist.db[tabName]["files"]:
                item = self.viewerAddItem(path, self.tabs[tabName]["playlist"], True)
                if "current" in self.playlist.db[tabName] and path == self.playlist.db[tabName]["current"]:
                    self.tabs[tabName]["playlist"].setCurrentItem(item)
        self.ui.viewTab.tabBar().setCurrentIndex(self.preferences.db["currentTab"])

    def parseCommand(self, cmd, arg):
        if cmd == "--play-pause":
            self.playButtonEvent()
        elif cmd == "--stop":
            self.stopButtonEvent()
        elif cmd == "--previous":
            self.previousButtonEvent()
        elif cmd == "--next":
            self.nextButtonEvent()
        elif cmd == "--quit":
            app.exit()
        elif cmd == "--delete":
            self.viewerSelectionAction("delete prompt")

        elif cmd == "--shuffle":
            if arg == "on":
                self.shuffleButtonEvent(enable=True)
            elif arg == "off":
                self.shuffleButtonEvent(enable=False)
            else:
                self.shuffleButtonEvent()
            self.tooltipCall("Shuffle enabled" if self.shuffle else "Shuffle disabled")

        elif cmd == "--file" and os.path.isfile(arg):
            self.tabs["Library viewer"]["playlist"].clear()
            self.viewerAddItem(arg, self.tabs["Library viewer"]["playlist"])
            self.ui.viewTab.tabBar().setCurrentIndex(0)
            self.playButtonEvent()

        elif cmd == "--folder" and os.path.isdir(arg):
            self.tabs["Library viewer"]["playlist"].clear()
            for root, subfolder, files in os.walk(arg):
                for f in files:
                    self.viewerAddItem(root + "/" + f, self.tabs["Library viewer"]["playlist"])
            self.ui.viewTab.tabBar().setCurrentIndex(0)
            self.viewerSortRoutine()
            self.playButtonEvent()

    def tabChanged(self, index):
        tabName = self.ui.viewTab.tabText(index)
        if tabName:
            self.currentTab = self.tabs[tabName]["playlist"]

    def tabAdd(self, name=None):
        layout = QtWidgets.QVBoxLayout()
        tab = QtWidgets.QWidget(self.ui.viewTab)
        count = self.ui.viewTab.tabBar().count()
        index = 1
        if not name:
            name = "Playlist " + str(index)
        while name in self.tabs:
            index += 1
            name = "Playlist " + str(index)
        self.tabs[name] = {}
        self.tabs[name] = {"playlist": PlaylistTreeWidget(self), "sort": PlaylistSortBoxWidget(self)}
        self.tabs[name]["playlist"].setSortingEnabled(self.tabs[name]["sort"].isChecked())
        self.ui.viewTab.addTab(tab, name)
        self.ui.viewTab.setCurrentWidget(tab)
        self.ui.viewTab.tabBar().moveTab(count - 1, count)
        self.ui.viewTab.currentWidget().setLayout(layout)
        layout.addWidget(self.tabs[name]["playlist"])
        layout.addWidget(self.tabs[name]["sort"])

    def tabClose(self, tab):
        tabName = self.ui.viewTab.tabText(tab)
        del self.tabs[tabName]
        if tabName in self.playlist.db:
            del self.playlist.db[tabName]
            self.playlist.save()
        self.ui.viewTab.removeTab(tab)

        # Prevent landing on the '+' tab
        count = self.ui.viewTab.tabBar().count() - 1
        if count == self.ui.viewTab.tabBar().currentIndex():
            self.ui.viewTab.tabBar().setCurrentIndex(count - 1)

    def tabRenamePrompt(self, oldName):
        msg = QtWidgets.QInputDialog()
        msg.setInputMode(QtWidgets.QInputDialog.TextInput)
        msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg.setWindowTitle("Rename '" + oldName + "'")
        msg.setLabelText("Enter the new name:")
        msg.setTextValue(oldName)
        msg.setFixedSize(250, 100)
        accept = msg.exec_()
        newName = msg.textValue()
        if accept and newName:
            return newName

    def tabRename(self):
        tabIndex = self.ui.viewTab.tabBar().currentIndex()
        oldName = self.ui.viewTab.tabText(tabIndex)
        if not oldName == "Library viewer":
            newName = self.tabRenamePrompt(oldName)
            if newName and newName not in self.tabs:
                self.tabs[newName] = self.tabs.pop(oldName)
                if oldName in self.playlist.db:
                    self.playlist.db[newName] = self.playlist.db.pop(oldName)
                    self.playlist.save()
                self.ui.viewTab.setTabText(tabIndex, newName)

    def libraryAddItem(self, path, parent):
        name = os.path.splitext(os.path.basename(path))[0]
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, name)
        item.setText(1, path)
        if parent is None:
            self.ui.libraryTree.addTopLevelItem(item)
        else:
            parent.addChild(item)
        return item

    def libraryDeleteItem(self, item, path):
        for subItem in range(item.childCount()):
            subItem = item.child(subItem)
            if subItem.childCount() > 0:
                self.libraryDeleteItem(subItem, path)
            elif subItem.text(1) == path:
                index = item.indexOfChild(subItem)
                item.takeChild(index)
                return True

    def librarySelectItem(self):
        self.lastPlayed = []
        self.tabs["Library viewer"]["playlist"].clear()
        for item in self.ui.libraryTree.selectedItems():
            if item.text(1):
                self.libraryScanSelection(item.text(1))
            elif item.text(0) == "All Music":
                for folder in range(self.ui.dbTree.topLevelItemCount()):
                    self.libraryScanSelection(self.ui.dbTree.topLevelItem(folder).text(0))
        self.viewerSortRoutine()
        self.ui.viewTab.tabBar().setCurrentIndex(0)

    def libraryScanAll(self):
        self.ui.libraryTree.clear()
        for path in self.database:
            self.libraryRecursiveScan(path)
        self.ui.libraryTree.sortItems(0, QtCore.Qt.AscendingOrder)

        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, "All Music")
        self.ui.libraryTree.insertTopLevelItem(0, item)

    def libraryScanSelection(self, path):
        for root, subfolder, files in os.walk(path):
            for f in files:
                if f.lower().count(self.ui.libraryFilterLine.text().lower()) > 0:
                    self.viewerAddItem(os.path.join(root, f), self.tabs["Library viewer"]["playlist"])
        if os.path.isfile(path):
            if path.lower().count(self.ui.libraryFilterLine.text().lower()) > 0:
                self.viewerAddItem(path, self.tabs["Library viewer"]["playlist"])

    def libraryRecursiveScan(self, folder, parent=None):
        for f in os.listdir(folder):
            path = os.path.join(folder, f)
            if os.path.isdir(path):
                if self.libraryHasAudioFiles(path):
                    item = self.libraryAddItem(path, parent=parent)
                    self.libraryRecursiveScan(path, item)

            elif os.path.splitext(path)[1].lower() in allowedFileTypes:
                if f.lower().count(self.ui.libraryFilterLine.text().lower()) > 0:
                    self.libraryAddItem(path, parent=parent)

    def libraryHasAudioFiles(self, path):
        for root, subfolders, files in os.walk(path):
            for f in files:
                if os.path.splitext(f)[1].lower() in allowedFileTypes:
                    if f.lower().count(self.ui.libraryFilterLine.text().lower()) > 0:
                        return True
        return False

    def librarySetScanInterval(self, interval=0):
        if interval == 0:
            self.monitorTimer.stop()
        else:
            self.monitorTimer.start(interval * 1000 * 60)

    def libraryScanDoneSignal(self, path):
        for item in range(self.ui.dbTree.topLevelItemCount()):
            item = self.ui.dbTree.topLevelItem(item)
            if item.text(0) == path:
                item.setText(1, "Monitoring")
                break
        if path not in self.database:
            self.database.append(path)
        self.metadata.save()
        self.libraryScanAll()

    def viewerAddItem(self, path, widget, append=False):
        basename = os.path.basename(path)
        extension = os.path.splitext(basename)[1].lower()
        if extension in allowedFileTypes:
            tags = parseAudioHeader(path, self.metadata.db)
            item = ViewerTreeWidgetItem()
            item.setText(0, tags["artist"])
            item.setText(1, tags["album"])
            item.setText(2, tags["track"])
            item.setText(3, tags["title"])
            item.setText(4, tags["duration"])
            item.setText(5, path)

            if append:
                widget.addTopLevelItem(item)
            else:
                index = widget.currentIndex().row()
                if index == -1: index = 0
                widget.insertTopLevelItem(index, item)
            return item

    def viewerSelectionAction(self, action):
        selection = self.currentTab.selectedItems()
        if action == "paste" and self.copied:
            for path in self.copied:
                item = self.viewerAddItem(path, self.currentTab)

            # Select pasted item
            self.currentTab.clearSelection()
            self.currentTab.setCurrentItem(item)

        elif selection:
            files = []
            for item in selection:
                files.append(item.text(5))

            if action == "copy":
                self.copied = files

            if action == "cut":
                self.copied = files
                self.viewerSelectionAction("delete")

            elif action == "delete":
                for item in selection:
                    index = self.currentTab.indexOfTopLevelItem(item)
                    self.currentTab.takeTopLevelItem(index)

                # Select next available item
                count = self.currentTab.topLevelItemCount()
                if index == count: index = count-1
                item = self.currentTab.topLevelItem(index)
                self.currentTab.clearSelection()
                self.currentTab.setCurrentItem(item)

            elif action == "delete prompt":
                self.viewerDeletePrompt(files)

            elif action == "browse":
                folder = os.path.abspath(os.path.join(self.currentTab.currentItem().text(5), os.pardir))
                cmd = self.ui.fileManagerLine.text() + ' "' + folder + '"'
                self.process.startDetached(cmd)

    def viewerSetColor(self, item, color):
        if item:
            try:
                for i in range(5):
                    if color == "none":
                        item.setData(i, QtCore.Qt.BackgroundRole, None)
                        item.setData(i, QtCore.Qt.ForegroundRole, None)
                    elif color == "green":
                        item.setForeground(i, QtGui.QColor("#004000"))
                        item.setBackground(i, QtGui.QColor("#c6efce"))
                    elif color == "yellow":
                        item.setForeground(i, QtGui.QColor("#553400"))
                        item.setBackground(i, QtGui.QColor("#ffeb9c"))
                    elif color == "red":
                        item.setForeground(i, QtGui.QColor("#9c0006"))
                        item.setBackground(i, QtGui.QColor("#ffc7ce"))
            except RuntimeError:
                pass

    def viewerSortRoutine(self):
        viewer = self.tabs["Library viewer"]["playlist"]
        headers = {"Artist": 0, "Album": 1, "Track": 2, "Title": 3, "Duration": 4}
        sortingRoutine = []
        for item in range(self.ui.sortSelectedList.count()):
            sortingRoutine.append(self.ui.sortSelectedList.item(item).text())
        for action in sortingRoutine:
            if action == "Disable sorting":
                self.tabs["Library viewer"]["sort"].setChecked(False)
                viewer.setSortingEnabled(False)
            else:
                self.tabs["Library viewer"]["sort"].setChecked(True)
                action = action.split()
                header = headers[action[0]]
                if action[1] == "(Ascending)":
                    direction = QtCore.Qt.AscendingOrder
                elif action[1] == "(Descending)":
                    direction = QtCore.Qt.DescendingOrder
                viewer.setSortingEnabled(True)
                viewer.sortByColumn(header, direction)

    def viewerDeletePrompt(self, files):
        if self.ui.deleteConfirmBox.isChecked():
            names = ""
            for f in files:
                names += "\n" + os.path.basename(f)
            msg = QtWidgets.QMessageBox()
            msg.setWindowFlags(msg.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Delete confirmation")
            msg.setText("Please confirm deletion of :\n" + names)
            msg.setStandardButtons(QtWidgets.QMessageBox.Apply | QtWidgets.QMessageBox.Cancel)
            if msg.exec_() == QtWidgets.QMessageBox.Apply:
                self.viewerDeleteFiles(files)
        else:
            self.viewerDeleteFiles(files)

    def viewerDeleteFiles(self, files):
        self.viewerSelectionAction("delete")
        for f in files:
            if os.path.isfile(f):
                os.remove(f)

            # Remove empty folder
            if self.ui.cleanFolderBox.isChecked():
                parent = os.path.abspath(os.path.join(f, os.pardir))
                if len(os.listdir(parent)) == 0:
                    os.rmdir(parent)
                    self.libraryScanAll()
                    return

            # Remove item from library tree
            for item in range(self.ui.libraryTree.topLevelItemCount()):
                item = self.ui.libraryTree.topLevelItem(item)
                if self.libraryDeleteItem(item, f):
                    break

    def menuRefresh(self):
        self.menu.clear()
        if self.copied:
            self.menu.addAction(self.icon["paste"], "Paste selection", lambda: self.viewerSelectionAction("paste"))
        if self.currentTab.selectedItems():
            self.menu.addAction(self.icon["cut"], "Cut selection", lambda: self.viewerSelectionAction("cut"))
            self.menu.addAction(self.icon["copy"], "Copy selection", lambda: self.viewerSelectionAction("copy"))
            if self.ui.fileManagerLine.text():
                self.menu.addAction(self.icon["folder"], "Browse song folder", lambda: self.viewerSelectionAction("browse"))
            self.menu.addSeparator()
            self.menu.addAction(self.icon["remove"], "Delete from playlist", lambda: self.viewerSelectionAction("delete"))
            self.menu.addAction(self.icon["delete"], "Delete from disk", lambda: self.viewerSelectionAction("delete prompt"))

    def menuShow(self):
        if self.currentTab.selectedItems() or self.copied:
            self.menu.popup(QtGui.QCursor.pos())

    def tooltipCall(self, tooltip):
        if self.ui.trayNotifyBox.isChecked() and self.ui.trayIconBox.isChecked():
            self.trayIcon.setToolTip(tooltip)
            self.showTooltipTimer.start(200)
            self.hideTooltipTimer.start(4000)

    def tooltipFormat(self, tooltip):
        replace = ("artist", "album", "track", "title")
        for tag in replace:
            tooltip = tooltip.replace("%" + tag + "%", self.tags[tag])
        return tooltip

    def tooltipDisplay(self):
        pos = QtCore.QRect(self.trayIcon.geometry())
        pos = QtCore.QPoint(pos.x(), pos.y())
        QtWidgets.QToolTip.showText(pos, self.trayIcon.toolTip(), self)
        self.trayIcon.setToolTip("")

    def playerUpdateSlider(self, progress):
        if not self.ui.slider.isSliderDown():
            self.ui.slider.setValue(progress)

    def playerActivateSelection(self):
        if self.currentTab.currentItem():
            self.viewerSetColor(self.lastItem, "none")
            self.lastItem = self.currentTab.currentItem()
            self.viewerSetColor(self.lastItem, "green")
            self.playerSetMedia(self.lastItem.text(5))
            self.tooltipCall(self.tooltipFormat(self.ui.tooltipFormatLine.text()))
        elif self.currentTab.topLevelItemCount() > 0:
            next = self.currentTab.topLevelItem(0)
            self.currentTab.setCurrentItem(next)
            self.playerActivateSelection()

    def playerSetMedia(self, path):
        self.path = path
        self.media = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(self.path))
        self.player.setMedia(self.media)
        self.player.play()
        self.ui.playButton.setIcon(self.icon["pause"])
        self.tags = parseAudioHeader(self.path, self.metadata.db)
        self.setWindowTitle(self.tooltipFormat(self.ui.titleFormatLine.text()))

    def playerUpdateStatus(self):
        if self.player.duration() > -1:
            if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
                state = "Now playing: " + self.tags["title"] + " (" + self.tags["artist"] + ")"
            elif self.player.state() == QtMultimedia.QMediaPlayer.PausedState:
                state = "Paused"
            elif self.player.state() == QtMultimedia.QMediaPlayer.StoppedState:
                state = "Stopped"

            s = self.ui.slider.value() / 1000
            m, s = divmod(s, 60)
            h, m = divmod(m, 60)
            elapsed = "%02d:%02d:%02d" % (h, m, s)
            self.ui.statusRightLabel.setText("    " + elapsed + " / " + self.duration)
            self.ui.statusBar.showMessage(state)

    def playerUpdateDuration(self, duration):
        s = duration / 1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        self.duration = "%02d:%02d:%02d" % (h, m, s)
        self.ui.slider.setRange(0, self.player.duration())

    def shuffleTrayEvent(self):
        self.shuffleButtonEvent()
        status = "Shuffle enabled" if self.shuffle else "Shuffle disabled"
        self.tooltipCall(status)

    def shuffleButtonEvent(self, checked=False, enable=None):
        self.shuffle = not self.shuffle if enable is None else enable
        if self.shuffle:
            self.ui.shuffleButton.setIcon(self.icon["shuffle_on"])
        else:
            self.ui.shuffleButton.setIcon(self.icon["shuffle_off"])

    def eventFilter(self, obj, event):
        eventType = event.type()
        if obj == self.ui.slider and eventType == QtCore.QEvent.MouseButtonRelease:
            mouseEvent = QtGui.QMouseEvent(event)
            position = QtWidgets.QStyle.sliderValueFromPosition(obj.minimum(), obj.maximum(), mouseEvent.x(), obj.width())
            self.ui.slider.setValue(position)
            self.player.setPosition(obj.value())

        elif obj == self.ui.viewTab.tabBar() and eventType == QtCore.QEvent.MouseButtonDblClick:
            self.tabRename()

        elif obj == self.ui.viewTab and eventType == QtCore.QEvent.ShortcutOverride:
            ctrl = (event.modifiers() == QtCore.Qt.ControlModifier)
            if ctrl and event.key() == QtCore.Qt.Key_C:
                self.viewerSelectionAction("copy")
            if ctrl and event.key() == QtCore.Qt.Key_X:
                self.viewerSelectionAction("cut")
            elif ctrl and event.key() == QtCore.Qt.Key_V:
                self.viewerSelectionAction("paste")
            elif event.key() == QtCore.Qt.Key_Backspace:
                self.viewerSelectionAction("delete")
            elif event.key() == QtCore.Qt.Key_Delete:
                self.viewerSelectionAction("delete prompt")
            elif event.key() == QtCore.Qt.Key_Space:
                self.playButtonEvent()
        return QtCore.QObject.event(obj, event)

    def changeEvent(self, event):
        # Override minimize event
        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                if self.ui.trayMinimizeBox.isChecked() and self.ui.trayIconBox.isChecked():
                    self.setWindowState(QtCore.Qt.WindowNoState)
                    self.hide() if self.isVisible() else self.show()

    def closeEvent(self, event):
        # Save playlists
        playlist = {}
        for index in range(self.ui.viewTab.count() - 1):
            tabName = self.ui.viewTab.tabText(index)
            currentTab = self.tabs[tabName]
            playlist[tabName] = {}
            playlist[tabName]["sort"] = (currentTab["sort"].isChecked(), currentTab["playlist"].sortColumn(), currentTab["playlist"].header().sortIndicatorOrder())
            if currentTab["playlist"].currentItem():
                playlist[tabName]["current"] = currentTab["playlist"].currentItem().text(5)
            playlist[tabName]["files"] = []
            for item in range(currentTab["playlist"].topLevelItemCount()):
                item = currentTab["playlist"].topLevelItem(item)
                playlist[tabName]["files"].append(item.text(5))
        self.playlist.db = playlist
        self.playlist.save()

        # Save preferences
        self.preferences.db["trayIcon"] = self.ui.trayIconBox.isChecked()
        self.preferences.db["trayNotify"] = self.ui.trayNotifyBox.isChecked()
        self.preferences.db["trayMinimize"] = self.ui.trayMinimizeBox.isChecked()
        self.preferences.db["deleteConfirm"] = self.ui.deleteConfirmBox.isChecked()
        self.preferences.db["cleanFolder"] = self.ui.cleanFolderBox.isChecked()
        self.preferences.db["resumePlayback"] = self.ui.resumePlaybackBox.isChecked()
        self.preferences.db["sortByDefault"] = self.ui.sortByDefaultBox.isChecked()
        self.preferences.db["stripTitlesBox"] = self.ui.stripTitlesBox.isChecked()
        self.preferences.db["expandLibrary"] = self.ui.expandLibraryBox.isChecked()
        self.preferences.db["monitorInterval"] = self.ui.monitorIntervalBox.value()
        self.preferences.db["fileManager"] = self.ui.fileManagerLine.text()
        self.preferences.db["tooltipFormat"] = self.ui.tooltipFormatLine.text()
        self.preferences.db["titleFormat"] = self.ui.titleFormatLine.text()
        self.preferences.db["currentTab"] = self.ui.viewTab.tabBar().currentIndex()
        self.preferences.db["playbackPosition"] = self.player.position()
        self.preferences.db["currentMediaState"] = self.player.state()
        self.preferences.db["currentMedia"] = self.path

        musicDatabase = []
        for item in range(self.ui.dbTree.topLevelItemCount()):
            item = self.ui.dbTree.topLevelItem(item)
            musicDatabase.append(item.text(0))
        self.preferences.db["musicDatabase"] = musicDatabase

        sortingRoutine = []
        for item in range(self.ui.sortSelectedList.count()):
            sortingRoutine.append(self.ui.sortSelectedList.item(item).text())
        self.preferences.db["sortingRoutine"] = sortingRoutine

        self.preferences.save()

    def clickEvent(self, event):
        if event == QtWidgets.QSystemTrayIcon.Trigger:
            if self.ui.trayMinimizeBox.isChecked():
                self.hide() if self.isVisible() else self.show()
        elif event == QtWidgets.QSystemTrayIcon.MiddleClick:
            self.playButtonEvent()
            if self.player.state() == QtMultimedia.QMediaPlayer.PausedState:
                self.tooltipCall("Paused")

    def mediaChangedEvent(self, event):
        if event == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.nextButtonEvent()
        elif event == QtMultimedia.QMediaPlayer.InvalidMedia:
            self.viewerSetColor(self.currentTab.currentItem(), "red")
            self.nextButtonEvent()

    def refreshButtonEvent(self):
        for folder in range(self.ui.dbTree.topLevelItemCount()):
            self.ui.dbTree.topLevelItem(folder).setText(1, "Scanning")
        self.tabs["Library viewer"]["playlist"].clear()
        self.ui.libraryTree.clear()
        self.metadata.db = {}
        self.metadata.save()
        self.database = []
        QtCore.QMetaObject.invokeMethod(self.worker, "scanAll", QtCore.Qt.QueuedConnection)

    def playButtonEvent(self):
        if self.currentTab.topLevelItemCount() > 0:
            if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
                self.player.pause()
                self.ui.playButton.setIcon(self.icon["play"])
            elif self.player.state() == QtMultimedia.QMediaPlayer.PausedState:
                self.ui.playButton.setIcon(self.icon["pause"])
                if self.currentTab.currentItem():
                    if not self.path == self.currentTab.currentItem().text(5):
                        self.playerActivateSelection()
                        return
                self.player.play()
            else:
                self.playerActivateSelection()
                self.lastPlayed.append(self.currentTab.currentIndex().row())

    def trayIconBoxEvent(self):
        if self.ui.trayIconBox.isChecked():
            self.trayIcon.show()
        else:
            self.trayIcon.hide()

    def sortAddButtonEvent(self):
        item = self.ui.sortAvailableList.currentItem()
        if item:
            row = self.ui.sortAvailableList.currentRow()
            item = self.ui.sortAvailableList.takeItem(row)
            self.ui.sortSelectedList.addItem(item)

    def sortRemoveButtonEvent(self):
        row = self.ui.sortSelectedList.currentRow()
        item = self.ui.sortSelectedList.takeItem(row)
        if item:
            self.ui.sortAvailableList.addItem(item)

    def seekableChangedEvent(self):
        if self.resumePlayback and self.player.isSeekable():
            self.resumePlayback = False
            self.player.setPosition(self.preferences.db["playbackPosition"])

    def nextButtonEvent(self):
        currentRow = self.currentTab.currentIndex().row()
        countRow = self.currentTab.topLevelItemCount()
        if self.currentTab.currentItem():
            if self.shuffle:
                if len(self.lastPlayed) == countRow:
                    self.stopButtonEvent()
                    return
                next = self.random.bounded(countRow)
                while next in self.lastPlayed:
                    next = self.random.bounded(countRow)
                next = self.currentTab.topLevelItem(next)
            elif currentRow == countRow - 1:
                self.stopButtonEvent()
                return
            else:
                next = self.currentTab.itemBelow(self.currentTab.currentItem())
            self.currentTab.setCurrentItem(next)
            self.playerActivateSelection()
            self.lastPlayed.append(currentRow)
        elif self.currentTab.topLevelItemCount() > 0:
            next = self.currentTab.topLevelItem(0)
            self.currentTab.setCurrentItem(next)

    def previousButtonEvent(self):
        if self.currentTab.currentItem():
            if self.lastPlayed:
                previous = self.lastPlayed.pop()
                previous = self.currentTab.topLevelItem(previous)
            else:
                previous = self.currentTab.itemAbove(self.currentTab.currentItem())
                if previous is None:
                    previous = self.currentTab.topLevelItem(0)
            self.currentTab.setCurrentItem(previous)
            self.playerActivateSelection()
        elif self.currentTab.topLevelItemCount() > 0:
            next = self.currentTab.topLevelItem(0)
            self.currentTab.setCurrentItem(next)

    def stopButtonEvent(self):
        self.player.stop()
        self.lastPlayed = []
        self.ui.playButton.setIcon(self.icon["play"])
        self.ui.slider.setValue(0)

    def libraryFilterEvent(self):
        self.libraryScanAll()
        if self.ui.expandLibraryBox.isChecked():
            count = self.ui.libraryTree.topLevelItemCount()
            for item in range(self.ui.libraryTree.topLevelItemCount()):
                count += self.ui.libraryTree.topLevelItem(item).childCount()
            if (count * 12) <= self.ui.libraryTree.height():  # Where 12px is the height of one item
                self.ui.libraryTree.expandAll()

    def dbAddButtonEvent(self, path=None):
        if not path:
            path = self.ui.dbLine.text()
        if os.path.isdir(path):
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, path)
            item.setText(1, "Scanning")
            self.ui.dbTree.addTopLevelItem(item)
            self.ui.dbLine.setText("")
            QtCore.QMetaObject.invokeMethod(self.worker, "scanFolder", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, path))

    def dbDeleteButtonEvent(self):
        row = self.ui.dbTree.currentIndex().row()
        if row > -1:
            item = self.ui.dbTree.takeTopLevelItem(row)
            path = item.text(0)
            self.ui.dbLine.setText(path)
            if path in self.database:
                self.database.remove(path)
                self.libraryScanAll()

    def dbBrowseButtonEvent(self):
        browser = QtWidgets.QFileDialog()
        browser.setFileMode(QtWidgets.QFileDialog.Directory)
        browser.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        if browser.exec_():
            self.ui.dbLine.setText(browser.selectedFiles()[0])


def main(cmd=None, arg=None):
    global app, gui
    app = QtWidgets.QApplication([])
    bus = QtDBus.QDBusConnection.sessionBus()
    server = QDBusServer()
    bus.registerObject('/org/qoob/session', server)
    bus.registerService('org.qoob.session')
    gui = Main()

    # Handle init command (if any)
    if cmd and arg:
        gui.parseCommand(cmd, arg)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
