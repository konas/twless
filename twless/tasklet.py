# -*- coding=utf-8 -*-
'''
:author: konas
:contact: konasyan2009@gmail.com
:description:



    | this module is foundation in tasklet Scheduling and context managing.
    | basiclly,there are two type of tasklets in twless : **SysTasklet** and **UsrTasklet**.

    SysTasklet
        | this tasklet is created by twless and will running through the whole process lifetime.
        | in twless,there is only one instance of SysTasklet and it equip twisted.internet.reactor@run as execute function.
        | developer doesn't need to know the existence of SysTasklet.

    UsrTasklet
        | this tasklet is created by application and lifetime is also controlled by application.
        | application must assign an execute function to UsrTasklet when create it.when this execute function return,corresponding \
          UsrTasklet destroied(just list physical thread).
        | application can created as many UsrTasklet instances as it want.

'''
import sys
import stackless
from twless.channel import NonBlockChannel
from twless.metrics import TaskletMetrics
from twless.defer import NanoDeferred
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure


ispypy = (sys.version.lower().find('pypy') != -1)
if not ispypy:
    class SysTasklet(stackless.tasklet):
        def __init__(self, func=None):
            '''
            :param func: execute function.
            '''
            stackless.tasklet.__init__(self, func)
    SysTasklet._init = SysTasklet.__init__
else:
    SysTasklet = stackless.tasklet

class UsrTasklet(SysTasklet):
    def __init__(self, func=None):
        SysTasklet.__init__(self, func)
        self._signalChannel = NonBlockChannel() # comminucation channel between tasklet
        self._timer = None      # wait timer for deferred callback/errback

        self.context = dict()   # tasklet context


    def _clearTimeout(self):
        if self._timer is not None:
            if self._timer.active():
                self._timer.cancel()
            self._timeocall = None


    @classmethod
    def current(cls):
        '''
        get current executing UsrTasklet instance

        :return:  UsrTasklet instance or None
        '''
        return TaskletMetrics.curUsrTasklet


    def _callback(self, result):
        '''
        callback of wait deferred.

        :param result: any application value
        :return: void
        '''
        self._clearTimeout()
        self._signalChannel.send_nonblock(result)
        # reactor.callLater(0, self._signalChannel.send_nonblock, result)

    def _errback(self, fault):
        '''
        callback of wait deferred.

        :param fault: Failure instance
        :return: void
        '''
        assert isinstance(fault,Failure)
        self._clearTimeout()
        self._signalChannel.send_exception_noblock(fault.type, fault.value)

    def _timeout(self,d):
        '''
        timeout on deferred waiting.

        :param d: Deferred instance
        :return: void
        '''
        assert isinstance(d,Deferred)
        self._timer = None
        d.cancel()

    def _sleep(self,seconds):
        '''
        sleep seconds and give execution to other tasklets.

        :param seconds: (int,float,long),in seconds
        :return: void
        '''

        d = NanoDeferred()
        reactor.callLater(seconds, d.callback, '')
        return self.wait(d)

    def wait(self, deferred, timeout=0, throwError=False):
        '''
        wait on Deferred until it callback/errback,or timeout(if has)

        :param deferred:    Deferred instance
        :param timeout:     in seconds
        :param throwError:  if error happen,throw exception or not.
        :return:
        '''

        if timeout > 0:
            self._timeocall = reactor.callLater(timeout, self._timeout, deferred)
        deferred.addCallback(self._callback)
        deferred.addErrback(self._errback)
        return self._signalChannel.receive(safeReturn=0 if throwError else 1)











