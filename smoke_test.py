import subprocess
import unittest


class IntegrationBaseTest(object):

  def run_ukechord(self, chordpro, py_version=2):
    proc = subprocess.Popen([self.BINARY, "ukechord.py", "-o", "/dev/null"],
                            stdin=subprocess.PIPE)
    proc.communicate(input=chordpro)
    return proc.wait()

  def test_simple(self):
    chordpro = "\n".join(
        "{title:This is an example song}"
        "{subtitle:With an example subtitle}"
        ""
        "This song has [Dm]example [C]lyrics."
        "And [C]another example line."
        ""
        "{start_of_chorus}"
        "[C]This is [D]a [G]chorus!"
        "[C]This is [D]a [G]chorus!"
        "{end_of_chorus}"
        ""
        "And another verse."
        "And no trailing newline."
    ).encode("utf-8")
    self.assertEqual(0, self.run_ukechord(chordpro, py_version=2))
    self.assertEqual(0, self.run_ukechord(chordpro, py_version=3))


class IntegrationTestPython2(IntegrationBaseTest, unittest.TestCase):
  BINARY = "python2"


class IntegrationTestPython3(IntegrationBaseTest, unittest.TestCase):
  BINARY = "python3"


if __name__ == "__main__":
  unittest.main()
