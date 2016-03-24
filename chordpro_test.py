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


if __name__ == "__main__":
  unittest.main()
