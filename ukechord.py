#!/usr/bin/python2
"""./ukechord.py -o out.pdf input.chd

Generate Ukulele song sheets with chords.

Input files are in ChordPro-ish format, output files in PDF format.
"""

import optparse
import sys

from reportlab.lib import pagesizes

import chordpro
import pdfwriter


def _parse_options(args):
  """Return (options, args)."""
  parser = optparse.OptionParser(usage=__doc__)
  parser.add_option("-o", "--output", dest="outfile",
                    help="set output filename (default: stdout)",
                    default="-")
  options, args = parser.parse_args(args)

  if options.outfile == "-":
    options.outfile = "/dev/stdout"

  if len(args) == 1:
    options.infile = args[0]
  elif not args:
    options.infile = "/dev/stdin"
  else:
    parser.error("Need at least one input file.")

  return options, args


def main(args):
  opts, args = _parse_options(args)

  with open(opts.outfile, "w") as outfile:
    with open(opts.infile, "r") as infile:
      pdf_writer = pdfwriter.PdfWriter(outfile, pagesizes.A4)
      chordpro.convert(infile, pdf_writer)


if __name__ == "__main__":
  main(sys.argv[1:])
