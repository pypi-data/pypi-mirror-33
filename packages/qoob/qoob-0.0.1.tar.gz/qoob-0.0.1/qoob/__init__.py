#!/usr/bin/python3
from PyQt5 import QtDBus
import sys


def main():
    bus = QtDBus.QDBusInterface("org.qoob.session", "/org/qoob/session", "org.qoob.session", QtDBus.QDBusConnection.sessionBus())

    if bus.isValid():
        # Pass the arguments if the bus already exist
        if len(sys.argv) > 2:
            bus.call("parse", sys.argv[1], sys.argv[2])
        elif len(sys.argv) > 1:
            bus.call("parse", sys.argv[1], "")
        sys.exit(0)

    else:
        # Create a new instance
        try:
            import qoob.main as qoob
        except ImportError:
            import main as qoob

        # Pass the arguments
        if len(sys.argv) > 2:
            qoob.main(sys.argv[1], sys.argv[2])
        elif len(sys.argv) > 1:
            qoob.main(sys.argv[1], "")
        else:
            qoob.main()

if __name__ == '__main__':
    main()
