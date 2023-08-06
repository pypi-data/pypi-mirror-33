import unittest
from pretext_match import Matcher
from pretext_match import And, Or, Not, StartsWith


class TestMessageMatchCheckers(unittest.TestCase):

    def testSimpleAnd(self):
        self.assertTrue(And("a").check("ab"))
        self.assertTrue(And("a", "b").check("ab"))

    def testSimpleAndNoMatch(self):
        self.assertFalse(And("a", "b").check("a"))

    def testSimpleOr(self):
        self.assertTrue(Or("a").check("ab"))
        self.assertTrue(Or("a", "b").check("b cd"))

    def testSimpleOrNoMatch(self):
        self.assertFalse(Or("a", "b").check("c"))

    def testCombinedAndOr(self):
        self.assertTrue(And(Or("a", "b"), "c").check("ac"))
        self.assertTrue(Or(And("a", "b"), "c").check("c"))
        self.assertTrue(Or(And("a", "b"), "c").check("ab"))

    def testCombinedAndOrNoMatch(self):
        self.assertFalse(Or(And("a", "b"), "c").check("D"))
        self.assertFalse(Or(And("a", "b"), "c").check("b"))

    def testDeeplyNestedAndOr(self):
        nested = And("a", "b", Or("X", "Y", And("c", Or("d", "z"))))
        self.assertTrue(nested.check("abcd"))
        self.assertTrue(nested.check("abX"))
        self.assertFalse(nested.check("abx"))
        self.assertFalse(nested.check("abc efghij"))

    def testBasicNot(self):
        self.assertFalse(Not("a").check("a"))
        self.assertTrue(Not("a").check("b"))
        self.assertTrue(Not("a").check("bcd"))
        self.assertFalse(Not("a").check("abc efghij"))

    def testNegatedAnd(self):
        not_a_and_b = Not(And("a", "b"))
        self.assertTrue(not_a_and_b.check("a"))
        self.assertTrue(not_a_and_b.check("b"))
        self.assertFalse(not_a_and_b.check("ab"))
        self.assertFalse(not_a_and_b.check("abc"))
        self.assertTrue(not_a_and_b.check("bc"))
        self.assertTrue(not_a_and_b.check("xyz"))

    def testNegatedOr(self):
        not_a_or_b = Not(Or("a", "b"))
        self.assertFalse(not_a_or_b.check("a"))
        self.assertFalse(not_a_or_b.check("b"))
        self.assertFalse(not_a_or_b.check("ab"))
        self.assertFalse(not_a_or_b.check("abc"))
        self.assertFalse(not_a_or_b.check("bdef"))
        self.assertTrue(not_a_or_b.check("cdef"))

    def testCaesar(self):
        sample = "And Caesar's spirit, raging for revenge, With Ate by his side come hot from hell, Shall in these " \
                 "confines with a monarch's voice  Cry \"Havoc!\" and let slip the dogs of war, That this foul deed " \
                 "shall smell above the earth With carrion men, groaning for burial."
        sample2 = "A coward dies a thousand times before his death, but the valiant taste of death but once. It " \
                  "seems to me most strange that men should fear, seeing that death, a necessary end, will come when " \
                  "it will come."
        no_match = "To be, or not to be: that is the question: Whether 'tis nobler in the mind to suffer The slings " \
                   "and arrows of outrageous fortune, Or to take arms against a sea of troubles, And by opposing end " \
                   "them? To die: to sleep; No more; and, by a sleep to say we end The heart-ache and the thousand " \
                   "natural shocks That flesh is heir to, 'tis a consummation Devoutly to be wish'd. To die, to " \
                   "sleep; To sleep: perchance to dream: ay, there’s the rub."
        caesar_matcher = Matcher(And(
            StartsWith(Or("And Caesar", "A coward")),
            Or("carrion", "valiant"),
            Not("noble"),
            Or(And("monarch", "dogs", "burial"), And("thousand", "death", "fear")),
            "a",
        ))
        self.assertTrue(caesar_matcher.check(sample))
        self.assertTrue(caesar_matcher.check(sample2))
        self.assertFalse(caesar_matcher.check(no_match))


if __name__ == '__main__':
    unittest.main()
