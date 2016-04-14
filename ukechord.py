#!/usr/bin/python2
"""Generate Ukulele song sheets with chords.

Input files are in ChordPro-ish format, output files in PDF format.
"""

import argparse
import sys

from reportlab.lib import pagesizes

import chordpro
import pdfwriter


def _parse_options(args):
  """Return (options, args)."""
  parser = argparse.ArgumentParser(
      usage="%(prog)s [-o OUTFILE] [INFILE]",
      description=__doc__)
  parser.add_argument("-o", "--output", dest="outfile",
                      nargs="?", default=sys.stdout,
                      type=argparse.FileType('wb'),
                      help="set output filename (default: stdout)")
  parser.add_argument("infile", nargs="?", default=sys.stdin,
                      type=argparse.FileType('r'),
                      help="input filenames (default: stdin)")
  return parser.parse_args(args)


def main(args):
  args = _parse_options(args)

  with args.outfile as outfile:
    if outfile == sys.stdout:
      # TODO: This is a hack to use sys.stdout in binary mode.
      # The input streams use the system encoding. (Set LANG=en_US.UTF-8)
      outfile = getattr(outfile, 'buffer', outfile)

    with args.infile as infile:
      pdf_writer = pdfwriter.PdfWriter(outfile, pagesizes.A4)
      chordpro.to_ast(infile).write_out(pdf_writer)


if __name__ == "__main__":
  main(sys.argv[1:])
