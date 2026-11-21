import unittest
from run_qemu import CASES, expected_failures, results_from


class ResultTests(unittest.TestCase):
    def test_crash_or_missing_case_cannot_pass(self):
        with self.assertRaises(ValueError):
            results_from("CASE_RESULT baseline PASS\nSUITE_DONE\n")
        with self.assertRaises(ValueError):
            results_from("".join(f"CASE_RESULT {name} PASS\n" for name in CASES))

    def test_failed_regression_is_preserved(self):
        output = "".join(f"CASE_RESULT {name} {'FAIL' if name == 'boot_error' else 'PASS'}\n"
                         for name in CASES) + "SUITE_DONE\n"
        self.assertEqual(results_from(output)["boot_error"], "FAIL")
        with self.assertRaises(ValueError):
            results_from(output + "CASE_RESULT baseline PASS\n")

    def test_expected_failures_validation(self):
        self.assertEqual(expected_failures(True, []), CASES - {"baseline"})
        self.assertEqual(expected_failures(False, ["stall_timeout"]), {"stall_timeout"})
        self.assertEqual(expected_failures(False, []), set())
        with self.assertRaises(ValueError):
            expected_failures(False, ["unknown_case"])


if __name__ == "__main__":
    unittest.main()
