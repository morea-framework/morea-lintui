from Toolbox.toolbox import red, green

__author__ = 'casanova'

import unittest
import sys


class CustomTestRunner:
    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def write_update(self, message):
        self.stream.write(message)

    def run(self, test):
        """Run the given test case or test suite."""

        self.write_update("-" * 70 + "\n")

        result = _CustomTestResult(self)
        # startTime = time.time()
        # self.writeUpdate("\n<!-- Individual results -->\n")

        test(result)
        # stopTime = time.time()
        # timeTaken = float(stopTime - startTime)
        # self.writeUpdate("\n<!-- Error/Failure details -->\n")

        self.write_update("-" * 70 + "\n")

        if len(result.errors) != 0 or len(result.failures) != 0:
            self.write_update(
                red(str(len(result.errors) + len(result.failures)) + " tests failed (out of " + str(
                    test.countTestCases()) + ")\n"))
            print 70 * "-"
            raw_input("Press Enter to see the error report...")
            result.printErrors()
        else:
            self.write_update(green("All " + str(test.countTestCases()) + " tests passed \n\n"))

        return result


# noinspection PyPep8Naming
class _CustomTestResult(unittest.TestResult):
    """A test result class that can print

    CustomTestRunner.
    """

    def __init__(self, runner):
        unittest.TestResult.__init__(self)
        self.runner = runner

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        self.runner.write_update("* " + test.shortDescription() + "."*(69-len(test.shortDescription())))

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        self.runner.write_update(green(' Passed\n'))

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        self.runner.write_update(red(' Failed\n'))

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self.runner.write_update(red(' Failed\n'))

    def printErrors(self):
        self.printErrorList('Error', self.errors + self.failures)

    # noinspection PyUnusedLocal
    def printErrorList(self, flavor, errors):
        for test, err in errors:
            self.runner.write_update(test.shortDescription())
            self.runner.write_update(err)
            print "\n" + "-" * 22
