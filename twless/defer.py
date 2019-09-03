# -*- coding=utf-8 -*-
'''
:author: konas
:contact: konasyan2009@gmail.com
:description:
    extension on twisted.internet.defer.
'''
from twisted.internet.defer import CancelledError
from twisted.python import failure

class NanoDeferred:
    '''

        a simple class which only has one level callback but implement the interfaces of twisted.internet.defer.Deferred.

    '''
    _called = 0
    _callback = None
    _errback = None

    # def __init__(self):
    #     self.called = 0
    #
    #     self._callback = None
    #     self._errback = None

    def addCallback(self, callee):
        self._callback = callee

    def addErrback(self, callee):
        self._errback = callee

    def addBoth(self, callee):
        self._callback = self._errback = callee

    def callback(self, ret):
        if self._called:
            return

        self._called = 1
        if self._callback:
            self._callback(ret)

    def errback(self, fail=None):
        if self._called:
            return

        if fail is None:
            fail = failure.Failure(captureVars=True)
        elif not isinstance(fail, failure.Failure):
            fail = failure.Failure(fail)

        self._called = 1
        if self._errback:
            self._errback(fail)

    def cancel(self):
        if self._called:
            return

        fail = failure.Failure(CancelledError())
        self.errback(fail)
