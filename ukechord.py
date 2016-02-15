#!/usr/bin/python2
"""Generate chord PDFs."""

import contextlib
import re
import sys

from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib import colors
from reportlab.lib.units import cm


pt = 1  # Just for clarity


_UKE_CHORDS = {
  "A7": (0, 1, 0, 0),
  "Dm": (2, 2, 1, 0),
  "E7": (1, 2, 0, 2),
  "A": (2, 1, 0, 0),
  "C": (0, 0, 0, 3),
  "D": (2, 2, 2, 0),
  "D7": (2, 2, 2, 3),
  "G7": (0, 2, 1, 2),
  "G": (0, 2, 3, 2),
  "Bb": (3, 2, 1, 1),
  "C7": (0, 0, 0, 1),
  "Am": (2, 0, 0, 0),
  "Cm": (0, 3, 3, 3),
  "Fm": (1, 0, 1, 3),
  "F": (2, 0, 1, 0),
  "Db": (1, 1, 1, 4),
  "Eb": (0, 3, 3, 1), #?
}


class PdfWriter(object):
  """Writes chord PDFs"""

  def __init__(self, outfile, pagesize):
    self._canvas = canvas.Canvas(outfile, pagesize=pagesize)
    self._canvas.setCreator("Uke Chord Generator v0.5 2016-02-07")
    self._canvas.setFillColor(colors.black)
    self._topmargin = pagesize[1] - 1.5*cm
    self._x = 2*cm
    self._width, self._height = pagesize
    self._leftmargin = 2*cm
    self._rightmargin = self._width - 2*cm

    self._lyrics_text = self._canvas.beginText()
    self._fontsize = 14

    self._chord_text = self._canvas.beginText()
    self._chord_text.setFont("Helvetica-Oblique", 12)

    self._comment_text = self._canvas.beginText()
    self._comment_text.setFont("Helvetica-Bold", 12)
    self._comment_text.setFillColor(colors.white)

    self._seen_chords = []
    self._text_on_last_line = False

  def setFontsize(self, size):
    self._fontsize = size
    self._lyrics_text.setFont("Helvetica", self._fontsize)
    self._comment_text.setFont("Helvetica-Bold", self._fontsize)
    self._chord_text.setFont("Helvetica-Oblique", self._fontsize - 2)

  def setTitle(self, title, subtitle):
    t = self._lyrics_text
    t.setTextOrigin(self._leftmargin, self._topmargin - 20*pt)
    t.setFont("Helvetica-Bold", 20)
    t.textOut(title)
    t.setFont("Helvetica-Oblique", 14)
    t.textLine()
    t.setFillGray(0.5)
    t.textLine(subtitle)
    t.setFillColor(colors.black)
    x, y = t.getCursor()
    with self.fillColor(colors.skyblue):
      self._canvas.rect(x, y, self._rightmargin - x, 7*pt, stroke=0, fill=1)
    t.textLine()
    t._text_on_last_line = False

  def drawChord(self, w, h, name, frets=(0, 0, 0, 0)):
    c = self._canvas
    xs = w / 3.0
    ys = h / 3.0
    # Title
    c.translate(0, -0.5*ys)
    c.drawCentredString(0.5*w, 0.5*ys, name)
    # Lines
    c.translate(0, -4*ys)
    c.lines([(0*xs, i*ys, 3*xs, i*ys) for i in range(5)] +
            [(i*xs, 0*ys, i*xs, 4*ys) for i in range(4)])
    # Frets
    for idx, fret in enumerate(frets):
      if fret:
        c.circle(idx*xs, (4 - fret + 0.5)*ys, xs/3, stroke=0, fill=1)
      else:
        c.circle(idx*xs, 4*ys, xs/3, stroke=1, fill=0)
    # Spacing
    c.translate(0, -1.5*ys)

  @contextlib.contextmanager
  def savedState(self):
    try:
      self._canvas.saveState()
      yield
    finally:
      self._canvas.restoreState()

  def startLyrics(self):
    t = self._lyrics_text
    self._lyricstop = t.getY()
    t.setFont("Helvetica", self._fontsize)
    t.textLine()
    self._text_on_last_line = False

  @contextlib.contextmanager
  def chorusSection(self):
    indent = self._fontsize
    t = self._lyrics_text
    oldx, oldy = t.getCursor()
    t.setTextOrigin(oldx + indent, oldy)
    t.setFont("Helvetica-Bold", self._fontsize)
    yield
    newy = t.getY()
    t.setTextOrigin(oldx, newy)
    t.setFont("Helvetica", self._fontsize)
    with self.fillColor(colors.skyblue):
      self._canvas.rect(
        oldx, oldy + self._fontsize - 3, indent/2.0, newy-oldy,
        stroke=0, fill=1)

  @contextlib.contextmanager
  def fillColor(self, color):
    self._canvas.setFillColor(color)
    yield
    self._canvas.setFillColor(colors.black)

  def chordAbove(self, pos, chord):
    if not chord:
      return

    if chord not in self._seen_chords:
      self._seen_chords.append(chord)
    x, y = pos
    self._chord_text.setTextOrigin(x, y + self._fontsize)
    self._chord_text.textOut(chord)

  def addComment(self, comment):
    margin_bottom = 5
    margin_top = 0
    origx, origy = self._lyrics_text.getCursor()
    self._comment_text.setTextOrigin(origx, origy)
    self._comment_text.textOut(' ' + comment + ' ')
    self._canvas.rect(
      origx, origy - margin_bottom,
      self._comment_text.getX() - origx,
      self._fontsize + margin_bottom + margin_top,
      stroke=0, fill=1)
    self._lyrics_text.textLine()
    self._text_on_last_line = True

  def addLine(self, segments):
    """Add a lyrics line with the given text segments.

    Args:
      segments: A list of (chord, text) tuples.
    """
    t = self._lyrics_text

    has_text = any(text for chord, text in segments)
    if not has_text:
      if self._text_on_last_line:
        t.textLine()
        self._text_on_last_line = False
      return

    if any(chord for chord, text in segments):
      t.textLine()  # Make space for chords.

    for chord, text in segments:
      oldpos = t.getCursor()
      t.textOut(text)
      self.chordAbove(oldpos, chord)
    t.textLine()
    self._text_on_last_line = True

  def finish(self):
    c = self._canvas

    with self.savedState():
      c.translate(self._rightmargin - 1*cm - 0.15*cm, self._lyricstop - 0.48*cm)
      for chordname in self._seen_chords:
        self.drawChord(0.8*cm, 1*cm, chordname, frets=_UKE_CHORDS[chordname])

    c.drawText(self._lyrics_text)
    c.drawText(self._chord_text)
    c.drawText(self._comment_text)
    c.showPage()
    c.save()


def _analyze_chordpro_textline(line):
  matches = list(re.finditer(r"\[([^\]]+)\]([^\[]*)", line))
  if matches:
    result = []
    if matches[0].start(0):
      result.append((None, line[:matches[0].start(0)]))
    for m in matches:
      result.append(m.groups())
    return result
  return [(None, line)]


def _chordpro_line(line):
  line = line.strip()
  if not line:
    return ("$empty", None)

  if line.startswith("{") and line.endswith("}"):
    k, unused_colon, v = line[1:-1].partition(":")
    return (k, v)
  else:
    return ("$lyrics", _analyze_chordpro_textline(line))


def _read_chordpro_lines(lines, pdf_writer, in_chorus=False):
  for k, v in lines:
    if k == "$empty":
      pdf_writer.addLine("")
    elif k == "$lyrics":
      # Text
      pdf_writer.addLine(v)
    elif k == "comment":
      pdf_writer.addComment(v)
    elif k in ("soc", "start-of-chorus", "start_of_chorus"):
      if in_chorus:
        raise Exception("Nested choruses!")
      with pdf_writer.chorusSection():
        _read_chordpro_lines(lines, pdf_writer, in_chorus=True)
    elif k in ("eoc", "end-of-chorus", "end_of_chorus"):
      if in_chorus:
        return
      raise Exception("End of chorus command without matching start.")
    elif k == "define":
      continue  # TODO: Support this!
    elif k in ("title", "subtitle"):
      continue  # Handled earlier.
    elif k == "fontsize":
      pdf_writer.setFontsize(int(v))
    else:
      raise Exception("Unknown command: %s", k)


def _chordpro_set_title(lines, pdf_writer):
  kv = dict(lines)
  pdf_writer.setTitle(kv.get("title", "").strip(),
                      kv.get("subtitle", "").strip())
  pdf_writer.startLyrics()


def read_chordpro(lines, pdf_writer):
  lines = map(_chordpro_line, lines)
  _chordpro_set_title(lines, pdf_writer)
  try:
    _read_chordpro_lines(iter(lines), pdf_writer)
  finally:
    pdf_writer.finish()


def main(args):
  if len(args) == 2:
    outfile = open(args[1], "w")
  elif len(args) == 1:
    outfile = sys.stdout
  else:
    sys.exit("Usage: ukechord INFILENAME [OUTFILENAME]")

  pdf_writer = PdfWriter(outfile, pagesizes.A4)
  read_chordpro(open(args[0]).readlines(), pdf_writer)


if __name__ == "__main__":
  main(sys.argv[1:])
