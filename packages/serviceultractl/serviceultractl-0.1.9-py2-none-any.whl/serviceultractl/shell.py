# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from .client import Client


def main():
    try:
        Client().main(sys.argv[1:])
        # Client().main(["ls", "machine", "--clusterid", "c1"])
        # Client().main(["ls", "application"])
    except Exception as e:
        msg = e.message
        if not msg or msg == '':
            msg = "Unknown Error"
        print "ERROR: %s" % msg
        sys.exit(1)


if __name__ == "__main__":
    main()
