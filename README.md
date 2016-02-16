# Uke Chord

Make Ukulele song sheets!

## Running

Example:

    ./ukechord.py [-o OUTPUTFILE] INPUTFILE

 * `INPUTFILE` should be in ChordPro format.
 * `OUTPUTFILE` will be in PDF format.

## Installation

Not easily installable yet, but you can run it directly from the directory.

### Dependencies

 * Python 2.7+ or Python 3
 * The [ReportLab](http://www.reportlab.com/opensource/) PDF library

   Install with:

        # Debian:
        apt-get install python3-reportlab  # or python-reportlab

        # Arch Linux:
        pacman -S python-reportlab  # or python2-reportlab
