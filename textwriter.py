import contextlib

class TextWriter(object):

  def __init__(self, writer):
    self._writer = writer
    self._chords = {}

  def _print(self, line=""):
    self._writer.write("%s\n" % line)

  def addLine(self, line):
    for chord, text in line:
      if chord:
        self._writer.write("[%s]" % chord)
      self._writer.write(text)
    self._writer.write("\n")

  def addComment(self, comment):
    self._print("// %s" % comment)

  def setTitle(self, title, subtitle):
    if title:
      self._print(title)
    if subtitle:
      self._print(subtitle)
    self._print("=" * 79)

  def startLyrics(self):
    pass

  @contextlib.contextmanager
  def chorusSection(self):
    self._print("- Chorus -")
    yield

  def finish(self):
    if self._chords:
      self._print("Chords: %s" % ", ".join(self._chords.iterkeys()))
