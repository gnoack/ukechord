"""Read ChordPro files and output them through a PDFWriter object"""

import re


class ChordProError(Exception):
  """Error in a ChordPro input."""
  pass


def _analyze_chordpro_textline(line):
  """Analyze the text and chords in a line of text.

  Args:
    line: The line of text, with chords in square brackets.

  Returns:
    A list of (chord, textchunk) tuples.
    The chord is None for a leading piece of text without preceding chord.

  Example:
    Input:  "This is [Dm]an example [C]line."
    Output: [(None, "This is "), ("Dm", "an example "), ("C", "line.")]
  """
  matches = list(re.finditer(r"\[([^\]]+)\]([^\[]*)", line))
  if matches:
    result = []
    if matches[0].start(0):
      result.append((None, line[:matches[0].start(0)]))
    for match in matches:
      result.append(match.groups())
    return result
  return [(None, line)]


def _chordpro_line(line):
  """Analyze a ChordPro line into a key value pair.

  For commands of the form "{key:value}", those will be the key and value.
  For empty lines, key is "$empty", and value is None.
  For text lines, returns "$lyrics" as key
    and a list of (chord, text) tuples as value
  """
  line = line.strip()
  if not line:
    return ("$empty", None)

  if line.startswith("{") and line.endswith("}"):
    key, unused_colon, value = line[1:-1].partition(":")
    return (key, value)
  else:
    return ("$lyrics", _analyze_chordpro_textline(line))


def _interpret_chordpro_lines(lines, pdf_writer, in_chorus=False):
  for key, value in lines:
    if key == "$empty":
      pdf_writer.addLine("")
    elif key == "$lyrics":
      # Text
      pdf_writer.addLine(value)
    elif key == "comment":
      pdf_writer.addComment(value)
    elif key in ("soc", "start-of-chorus", "start_of_chorus"):
      if in_chorus:
        raise ChordProError("ChordPro: Nested choruses are not supported.")
      with pdf_writer.chorusSection():
        _interpret_chordpro_lines(lines, pdf_writer, in_chorus=True)
    elif key in ("eoc", "end-of-chorus", "end_of_chorus"):
      if in_chorus:
        return
      raise ChordProError(
          "End-of-chorus ChordPro command without matching start.")
    elif key == "define":
      continue  # TODO: Support this!
    elif key in ("title", "subtitle"):
      continue  # Handled earlier.
    elif key == "fontsize":
      pdf_writer.setFontsize(int(value))
    else:
      raise ChordProError("Unknown ChordPro command: %s", key)


def _chordpro_set_title(lines, pdf_writer):
  keys_and_values = dict(lines)
  title = keys_and_values.get("title", "").strip()
  subtitle = keys_and_values.get("subtitle", "").strip()
  pdf_writer.setTitle(title, subtitle)
  pdf_writer.startLyrics()


def convert(infile, pdf_writer):
  """Read the ChordPro file infile and emit it through the given PDF writer.

  Args:
    infile: A readable file-like object.
    pdf_writer: A PDF writer for emitting the document.
  """
  lines = [_chordpro_line(line) for line in infile.readlines()]
  _chordpro_set_title(lines, pdf_writer)
  try:
    _interpret_chordpro_lines(iter(lines), pdf_writer)
  finally:
    pdf_writer.finish()
