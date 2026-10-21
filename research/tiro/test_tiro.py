import pathlib
import unittest

from tiro import canon, lint, parse, render

EXAMPLES = pathlib.Path(__file__).parent / "examples"


def load(name):
    return parse((EXAMPLES / name).read_text(encoding="utf-8"))


class ParseErrors(unittest.TestCase):
    def assertError(self, text, fragment):
        errors = parse(text).errors
        self.assertTrue(any(fragment in e for e in errors), errors)

    def test_undeclared_symbol(self):
        self.assertError("s1 obs $watchers are present", "used before it was declared")

    def test_dependency_must_be_earlier(self):
        self.assertError("s1 inf x <- s2\ns2 obs y", "not an earlier step")

    def test_inference_must_cite_support(self):
        self.assertError("s1 inf the answer is 4", "must cite")

    def test_only_actions_are_irreversible(self):
        self.assertError("s1 obs! x", "only act steps")

    def test_confidence_only_on_epistemic_steps(self):
        self.assertError("s1 obs x ~0.5", "not allowed on obs")


class Examples(unittest.TestCase):
    def test_examples_parse_cleanly(self):
        for path in EXAMPLES.glob("*.tiro"):
            with self.subTest(path.name):
                self.assertEqual(parse(path.read_text(encoding="utf-8")).errors, [])

    def test_irreversible_action_on_assumption_hits_breakpoint(self):
        _, breakpoints = lint(load("free_disk.tiro"))
        self.assertEqual(len(breakpoints), 1)
        self.assertIn("s3 (asm ~0.5)", breakpoints[0])

    def test_violated_expectation_is_reported(self):
        warnings, breakpoints = lint(load("fix_encoding.tiro"))
        self.assertEqual(warnings, ["s13: expectation s9 was violated"])
        self.assertEqual(breakpoints, [])

    def test_action_without_expectation_is_flagged(self):
        warnings, _ = lint(parse("s1 plan restart the server\ns2 act systemctl restart api <- s1"))
        self.assertTrue(any("no stated expectation" in w for w in warnings))

    def test_render_glosses_symbol_on_first_use_only(self):
        text = render(load("fix_encoding.tiro"))
        self.assertEqual(text.count('("tests/test_io.py::test_read")'), 1)


class Canonical(unittest.TestCase):
    def test_canon_erases_surface_choices(self):
        out = canon(load("channels.tiro"))
        self.assertNotIn("watchers", out)
        self.assertNotIn("6137", out)
        self.assertIn("s2 hyp $S1 only check the first paragraph <- s1 ~0.6", out)
        self.assertIn("s4 ans summary covering all five sections <- s1 s2 s3", out)

    def test_canon_is_idempotent(self):
        once = canon(load("channels.tiro"))
        self.assertEqual(canon(parse(once)), once)


if __name__ == "__main__":
    unittest.main()
