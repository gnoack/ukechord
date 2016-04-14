import io
import unittest

import textwriter
import song as song_ast

class SimpleConversionTest(unittest.TestCase):
  def assertPrints(self, song, expected_output):
    buf = io.StringIO()
    song.write_out(textwriter.TextWriter(buf))
    self.assertMultiLineEqual(buf.getvalue(), expected_output)

  def test_simple_song(self):
    self.assertPrints(
        song_ast.Song(
            title="Hello, world",
            subtitle="One of the great timeless classics",
            children=[
                song_ast.Verse([
                    song_ast.Line([(None, "Hello, "), ("Bb", "world!")]),
                    song_ast.Line([(None, "Hello, "), ("Bb", "world!")]),
                ]),
                song_ast.Chorus([
                    song_ast.Line([(None, "Hello, "), ("Bb", "world!")]),
                    song_ast.Line([(None, "Hello, "), ("Bb", "world!")]),
                ]),
            ]
        ),
        "\n".join([
            "Hello, world",
            "One of the great timeless classics",
            "=" * 79,
            "",
            "Hello, [Bb]world!",
            "Hello, [Bb]world!",
            "",
            "- Chorus -",
            "Hello, [Bb]world!",
            "Hello, [Bb]world!",
        ]) + "\n"
    )


if __name__ == "__main__":
  unittest.main()
