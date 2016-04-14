import io
import unittest

import chordpro
import textwriter


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


class SimpleConversionTest(unittest.TestCase):
  def assertGeneratesText(self, infile, expected_outfile):
    with open(expected_outfile, "r", encoding="utf-8") as expected_outfile:
      expected_result = expected_outfile.read()

    with open(infile, "r", encoding="utf-8") as infile:
      with io.StringIO() as outfile:
        chordpro.to_ast(infile).write_out(textwriter.TextWriter(outfile))
        result = outfile.getvalue()

    self.assertMultiLineEqual(result, expected_result)

  def test_simple_song(self):
    """PDFs generated through the AST should match the ones generated directly."""
    self.assertGeneratesText("examples/test1.chd", "examples/test1.txt")


if __name__ == "__main__":
  unittest.main()
