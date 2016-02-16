import subprocess
import unittest


class IntegrationBaseTest(object):

  def pythonBinary(self):
    raise NotImplementedError("subclass responsibility")

  def runUkechord(self, chordpro):
    proc = subprocess.Popen(
        [self.pythonBinary(), "ukechord.py", "-o", "/dev/null"],
        stdin=subprocess.PIPE)
    proc.communicate(input=chordpro)
    return proc.wait()

  def testSimple(self):
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
    self.assertEqual(0, self.runUkechord(chordpro))


class Python2IntegrationTest(IntegrationBaseTest, unittest.TestCase):

  def pythonBinary(self):
    return "python2"


class Python3IntegrationTest(IntegrationBaseTest, unittest.TestCase):

  def pythonBinary(self):
    return "python3"


if __name__ == "__main__":
  unittest.main()
