#! /usr/bin/env python3

import empire.server.arguments as arguments
import sys


if __name__ == '__main__':
    args = arguments.args  # todo move arg parsing to root level.

    if args.server:
        import empire.server.empire as server
        server.run(args)

    elif args.client:
        import empire.client.main as client
        client.start()

    sys.exit()
