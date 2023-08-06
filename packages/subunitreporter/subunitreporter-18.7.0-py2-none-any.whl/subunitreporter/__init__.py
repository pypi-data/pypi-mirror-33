# Copyright Least Authority TFA GmbH
# See LICENSE for details.

from __future__ import (
    division,
    absolute_import,
    print_function,
    unicode_literals,
)

from sys import stdout
import attr

from zope.interface import implementer

from testtools import ExtendedToStreamDecorator
from subunit.v2 import StreamResultToBytes
from subunit.test_results import  AutoTimingTestResultDecorator

from twisted.trial.itrial import IReporter
from twisted.trial.util import excInfoOrFailureToExcInfo

def _make_subunit(reporter):
    return AutoTimingTestResultDecorator(
        ExtendedToStreamDecorator(
            StreamResultToBytes(
                reporter.stream,
            ),
        ),
    )

@attr.s
@implementer(IReporter)
class _SubunitReporter(object):
    """
    Reports test output using the subunit v2 protocol.
    """
    stream = attr.ib(default=stdout)

    _subunit = attr.ib(
        default=attr.Factory(
            _make_subunit,
            takes_self=True,
        ),
        repr=False,
        cmp=False,
        hash=None,
        init=False,
    )

    def done(self):
        """
        Record that the entire test suite run is finished.

        No-op because the end of a subunit protocol data stream is what
        signals completion.
        """

    def shouldStop(self):
        """
        Should the test runner should stop running tests now?
        """
        return self._subunit.shouldStop
    shouldStop = property(shouldStop)

    def stop(self):
        """
        Signal that the test runner should stop running tests.
        """
        return self._subunit.stop()

    def wasSuccessful(self):
        """
        Meaningless introspection on number of errors and failures.

        :return: ``True`` because the test runner doesn't need to know.
        """
        return True

    def startTest(self, test):
        """
        Record that ``test`` has started.
        """
        return self._subunit.startTest(test)

    def stopTest(self, test):
        """
        Record that ``test`` has completed.
        """
        return self._subunit.stopTest(test)

    def addSuccess(self, test):
        """
        Record that ``test`` was successful.
        """
        return self._subunit.addSuccess(test)

    def addSkip(self, test, reason):
        """
        Record that ``test`` was skipped for ``reason``.

        :param TestCase test: The test being skipped.

        :param reason: The reason for it being skipped. The result of ``str``
            on this object will be included in the subunit output stream.
        """
        self._subunit.addSkip(test, reason)

    def addError(self, test, err):
        """
        Record that ``test`` failed with an unexpected error ``err``.
        """
        return self._subunit.addError(
            test,
            excInfoOrFailureToExcInfo(err),
        )

    def addFailure(self, test, err):
        """
        Record that ``test`` failed an assertion with the error ``err``.
        """
        return self._subunit.addFailure(
            test,
            excInfoOrFailureToExcInfo(err),
        )

    def addExpectedFailure(self, test, failure, todo):
        """
        Record an expected failure from a test.
        """
        self._subunit.addExpectedFailure(
            test,
            excInfoOrFailureToExcInfo(failure),
        )

    def addUnexpectedSuccess(self, test, todo=None):
        """
        Record an unexpected success.

        Since subunit has no way of expressing this concept, we record a
        success on the subunit stream.
        """
        self.addSuccess(test)


def reporter(stream, tbformat=None, realtime=None, publisher=None):
    """
    Create a trial reporter which emits a subunit v2 stream of test result
    information to the given stream.

    :param stream: A ``write``-able object to which the result stream will be
        written.
    """
    return _SubunitReporter(stream)
