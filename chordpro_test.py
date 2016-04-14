import unittest

import chordpro


class ChordDefinitionTest(unittest.TestCase):

  def testSimpleFret(self):
    name, frets = chordpro._parse_chord_definition(
      " Dm frets 0 1 2 2 fingers 1 2 3 4")
    self.assertEqual("Dm", name)
    self.assertEqual((0, 1, 2, 2), frets)

  def testInvalidFret_garbageAtEnd(self):
    self.assertRaises(
      chordpro.ChordProError,
      chordpro._parse_chord_definition,
      " Dm frets 0 1 2 2 fingers 1 2 3 4xxx")

  def testInvalidFret_garbageAtBeginning(self):
    self.assertRaises(
      chordpro.ChordProError,
      chordpro._parse_chord_definition,
      "xxx Dm frets 0 1 2 2 fingers 1 2 3 4")

  def testInvalidFret_tooHigh(self):
    self.assertRaises(
      chordpro.ChordProError,
      chordpro._parse_chord_definition,
      " Dmextreme frets 0 1 2 5000 fingers 1 2 3 4")


class LineParsingTest(unittest.TestCase):

  def assertParse(self, line, expected_result):
    self.assertEqual(chordpro._chordpro_line(line), expected_result)

  def testEmptyLine(self):
    self.assertParse(" \t  ", ("$empty", None))

  def testCommandWithKeyValue(self):
    self.assertParse("{title:This is an example!}",
                     ("title", "This is an example!"))

  def testCommandWithKeyValueAndColon(self):
    self.assertParse("{title:This is: an example!}",
                     ("title", "This is: an example!"))

  def testCommandWithKeyValueAndCurlyBraces(self):
    """only the outer two curly braces are syntactically meaningful"""
    self.assertParse("{}title{:{{This is {crazy}}}",
                     ("}title{", "{{This is {crazy}}"))

  def testCommandWithKeyValueAndSurroundingWhitespace(self):
    self.assertParse("{  title\t : This is an example!  }",
                     ("  title\t ", " This is an example!  "))

  def testCommandWithJustKey(self):
    self.assertParse("{whatever}", ("whatever", ""))

  def testLyricsNoChords(self):
    self.assertParse(
        "These are lyrics without chord.",
        ("$lyrics", [(None, "These are lyrics without chord.")]))

  def testLyricsWithChords(self):
    self.assertParse(
        "These are lyrics [Dm]with [G7]some [C7]chords.",
        ("$lyrics", [(None, "These are lyrics "),
                     ("Dm", "with "),
                     ("G7", "some "),
                     ("C7", "chords.")]))


class EquivalenceTest(unittest.TestCase):
  def test_equivalence(self):
    """PDFs generated through the AST should match the ones generated directly."""
    # TODO: Only runs in Python3 for now.
    import pdfwriter
    import io
    from reportlab.lib import pagesizes

    infile = io.StringIO("\n".join((
      "{title:This is an example song}",
      "{subtitle:With an example subtitle}",
      "",
      "{define: Dm frets 0 1 2 2 fingers 1 2 3 4}"
      "",
      "This song has [Dm]example [C]lyrics.",
      "And [C]another example line.",
      "{comment: Unclear}",
      "",
      "{start_of_chorus}",
      "[C]This is [D]a [G]chorus!",
      "[C]This is [D]a [G]chorus!",
      "{end_of_chorus}",
      "",
      "{comment: Haha}",
      "",
      "And another verse.",
      "And no trailing newline.",
    )))

    old_out = io.BytesIO()
    old_pdf = pdfwriter.PdfWriter(old_out, pagesizes.A4)
    old_result = chordpro.convert(infile, old_pdf)

    infile.seek(0)
    new_out = io.BytesIO()
    new_pdf = pdfwriter.PdfWriter(new_out, pagesizes.A4)
    new_result = chordpro.to_ast(infile).write_out(new_pdf)

    self.maxDiff = None
    self.assertMultiLineEqual(str(old_out.getvalue()), str(new_out.getvalue()))


if __name__ == "__main__":
  unittest.main()
