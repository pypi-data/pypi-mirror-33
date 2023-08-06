''' Independent script to check consistency of data.

.. in development

Checks to perform:

- uniqueness of locations in static data.
- no duplication of sources within a device.
- location <-> zone is a one-to-one relationship.
- feeds require a zone_id if the device-id is MusicCast.
- device require at least 1 input (source or feed).
- device requires at least 1 zone.
- first level must have a 'devices' token (enforced in the schema).

'''

import sys
import json


def main():
    ''' docstring'''
    # import json file
    try: filename = sys.argv[1]
    except IndexError:
        print 'I need a filename as first argument.'
        return
    with open(filename, 'r') as fh:
        data = json.load(fh)
    print data
    return

if __name__ == '__main__':
    main()
