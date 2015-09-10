from Toolbox.toolbox import red, green

__author__ = 'casanova'

import unittest
import sys


class CustomTestRunner:
    def __init__(self, stream=sys.stderr):
        self.stream = stream

    def writeUpdate(self, message):
        self.stream.write(message)

    def run(self, test):
        """Run the given test case or test suite."""

        self.writeUpdate("-" * 70 + "\n")

        result = _CustomTestResult(self)
        # startTime = time.time()
        # self.writeUpdate("\n<!-- Individual results -->\n")

        test(result)
        # stopTime = time.time()
        # timeTaken = float(stopTime - startTime)
        # self.writeUpdate("\n<!-- Error/Failure details -->\n")

        self.writeUpdate("-" * 70 + "\n")

        if len(result.errors) != 0 or len(result.failures) != 0:
            self.writeUpdate(
                red(str(len(result.errors) + len(result.failures)) + " tests failed (out of " + str(
                    test.countTestCases()) + ")\n"))
            print 70 * "-"
            a = raw_input("Press Enter to see the error report...")
            result.printErrors()
        else:
            self.writeUpdate(green("All " + str(test.countTestCases()) + " tests passed \n\n"))

        return result


class _CustomTestResult(unittest.TestResult):
    """A test result class that can print

    CustomTestRunner.
    """

    def __init__(self, runner):
        unittest.TestResult.__init__(self)
        self.runner = runner

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        self.runner.writeUpdate("* " + test.shortDescription() + "."*(69-len(test.shortDescription())))

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        self.runner.writeUpdate(green(' Passed\n'))

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        self.runner.writeUpdate(red(' Failed\n'))

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self.runner.writeUpdate(red(' Failed\n'))

    def printErrors(self):
        self.printErrorList('Error', self.errors + self.failures)

    def printErrorList(self, flavor, errors):
        for test, err in errors:
            self.runner.writeUpdate(test.shortDescription())
            self.runner.writeUpdate(err)
            print "\n" + "-" * 22
