import subprocess
import unittest


_CHORDPRO_DATA = "\n".join((
  "{title:This is an example song}",
  "{subtitle:With an example subtitle}",
  "",
  "This song has [Dm]example [C]lyrics.",
  "And [C]another example line.",
  "",
  "{start_of_chorus}",
  "[C]This is [D]a [G]chorus!",
  "[C]This is [D]a [G]chorus!",
  "{end_of_chorus}",
  "",
  "And another verse.",
  "And no trailing newline.",
)).encode("utf-8")


class IntegrationBaseTest(unittest.TestCase):

  def runUkechord(self, chordpro, python_binary):
    proc = subprocess.Popen(
        [python_binary, "ukechord.py", "-o", "-"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    stdout_data, stderr_data = proc.communicate(input=chordpro)
    self.assertEqual(0, proc.wait())  # Runs successfully
    self.assertFalse(stderr_data)
    self.assertTrue(stdout_data)
    return stdout_data

  def testPython2AndPython3GiveEqualOutput(self):
    python2_output = self.runUkechord(_CHORDPRO_DATA, "python2")
    python3_output = self.runUkechord(_CHORDPRO_DATA, "python3")
    self.assertEqual(python2_output, python3_output)


if __name__ == "__main__":
  unittest.main()
