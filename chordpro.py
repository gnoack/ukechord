"""Read ChordPro files and output them through a PDFWriter object"""

import re

import song
import uke


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
  if not line or line.startswith("#"):
    return ("$empty", None)

  if line.startswith("{") and line.endswith("}"):
    key, unused_colon, value = line[1:-1].partition(":")
    return (key, value)
  else:
    return ("$lyrics", _analyze_chordpro_textline(line))


def _parse_chord_definition(value):
  # TODO: Is it required to define 'fingers' in each chord definition?
  match = re.match(
    r"\s+(?P<name>[A-Za-z0-9/+#]*)\s+"
    r"frets\s+(?P<frets>[\d\s]+)"
    r"fingers\s+(?P<fingers>[\d\s]+)$",
    value)
  # TODO: Implement finger positioning support
  # TODO: Catch too high fret values
  if not match:
    raise ChordProError("Chord definition parsing failed", value)

  frets = [int(fret) for fret in match.group('frets').split(' ') if fret]
  if any(fret > uke.MAX_FRET for fret in frets):
    raise ChordProError("Frets beyond %d don't exist.", uke.MAX_FRET)
  return match.group('name'), tuple(frets)


def _convert_lines_to_ast_nodes(lines, chords, end_of_section_markers=()):
  result = []
  for key, value in lines:
    if key in end_of_section_markers:
      break
    elif key == "$empty":
      pass # ignore
    elif key in ("$lyrics", "comment"):
      if key == "$lyrics":
        first_verse_item = song.Line(value)
      elif key == "comment":
        first_verse_item = song.Comment(value)
      else:
        raise ChordProError("Should never happen. - Programming error")

      # Text
      if end_of_section_markers:
        # If we're in a section, lines are fine.
        result.append(first_verse_item)
      else:
        verse_lines = _convert_lines_to_ast_nodes(
          lines, chords=chords,
          end_of_section_markers=("$empty"))
        result.append(song.Verse([first_verse_item] + verse_lines))
    elif key in ("soc", "start-of-chorus", "start_of_chorus"):
      if end_of_section_markers:
        raise ChordProError("ChordPro: Nested choruses are not supported.")
      result.append(song.Chorus(
        _convert_lines_to_ast_nodes(
          lines, chords=chords,
          end_of_section_markers=("eoc", "end-of-chorus", "end_of_chorus"))))
    elif key == "define":
      name, frets = _parse_chord_definition(value)
      chords[name] = frets
    elif key in ("title", "subtitle"):
      continue  # Handled earlier.
    elif key == "fontsize":
      # TODO: How to handle font size?
      pass  # Should translate to pdf_writer.setFontsize(int(value))
    elif key in ("eoc", "end-of-chorus", "end_of_chorus"):
      # If not already part of breaking condition.
      raise ChordProError(
          "End-of-chorus ChordPro command without matching start.")
    else:
      raise ChordProError("Unknown ChordPro command: %s", key)
  return result


def to_ast(infile):
  lines = [_chordpro_line(line) for line in infile.readlines()]
  keys_and_values = dict(lines)
  title = keys_and_values.get("title", "").strip()
  subtitle = keys_and_values.get("subtitle", "").strip()
  chords = {}
  children = _convert_lines_to_ast_nodes(iter(lines), chords=chords)
  return song.Song(children, title=title, subtitle=subtitle, chords=chords)
