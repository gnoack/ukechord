import re

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


def convert(infile, pdf_writer):
  """Read the ChordPro file infile and emit it through the given PDF writer.

  Args:
    infile: A readable file-like object.
    pdf_writer: A PDF writer for emitting the document.
  """
  lines = map(_chordpro_line, infile.readlines())
  _chordpro_set_title(lines, pdf_writer)
  try:
    _read_chordpro_lines(iter(lines), pdf_writer)
  finally:
    pdf_writer.finish()
