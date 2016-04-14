"""Abstract syntax tree for songs.

Basic structure:
 * A song consists of verses, choruses and maybe comments.
 * Verses and choruses consist of lines and maybe comments.

Global information like titles and chords
are properties of the top-level Song object.
"""

class Line(object):
  def __init__(self, line):
    self._line = line

  def write_out(self, pdf_writer):
    pdf_writer.addLine(self._line)

  def __repr__(self):
    return repr(self._line)


class Comment(object):
  def __init__(self, comment):
    self._comment = comment

  def write_out(self, pdf_writer):
    pdf_writer.addComment(self._comment)

  def __repr__(self):
    return "/* %s */" % self._comment


class ContainerNode(object):
  def __init__(self, children):
    self._children = children

  def __repr__(self):
    return "<%s: %s>" % (type(self).__name__, " / ".join(map(repr, self._children)))



class Verse(ContainerNode):
  def write_out(self, pdf_writer):
    # TODO: This is a terrible way to separate sections.
    pdf_writer.addLine([])
    for child in self._children:
      child.write_out(pdf_writer)


class Chorus(ContainerNode):
  def write_out(self, pdf_writer):
    # TODO: This is a terrible way to separate sections.
    pdf_writer.addLine([])
    with pdf_writer.chorusSection():
      for child in self._children:
        child.write_out(pdf_writer)


class Song(object):
  def __init__(self, children, title='', subtitle='', chords={}):
    self._children = children
    self._title = title
    self._subtitle = subtitle
    self._chords = chords

  def write_out(self, pdf_writer):
    for name, frets in self._chords.items():
      pdf_writer._chords[name] = frets

    pdf_writer.setTitle(self._title, self._subtitle)
    pdf_writer.startLyrics()
    for child in self._children:
      child.write_out(pdf_writer)
    pdf_writer.finish()

  def __repr__(self):
    return "[%s (%s): %r]" % (self._title, self._subtitle, self._children)
