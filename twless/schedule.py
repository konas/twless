# -*- coding=utf-8 -*-
'''
:author: konas
:contact: konasyan2009@gmail.com
:description:

    hook in stackless schedule.

'''
import sys
import stackless
import functools
import traceback
from twless.tasklet import UsrTasklet,SysTasklet
from twless.metrics import TaskletMetrics
from twless.context import waitOnDeferred
from twless.defer import NanoDeferred
from twisted.internet import reactor
from twisted.python.failure import Failure
from twisted.internet.defer import Deferred
from twisted.python import log

def _doStacklessSchedule():
    stackless.schedule()
    TaskletMetrics.scheduled = 0

def scheduleStackless():
    '''
    schedule Stackless in twisted main loop

    :return: void
    '''
    if TaskletMetrics.scheduled:
        return
    TaskletMetrics.scheduled = 1
    reactor.callLater(0,_doStacklessSchedule)


def _user_tasklet_main(function,args,kwargs,defer):
    try:
        ret = function(*args,**kwargs)
        if isinstance(ret, (Deferred,NanoDeferred)):
            dret = waitOnDeferred(ret,throwError=1)
            ret = dret
        defer.callback(ret)
    except BaseException as e:
        print('-----------------Exception-------------------------------')
        traceback.print_exc()
        print('---------------------------------------------------------')
        if isinstance(e,Failure):
            e = e.value
        defer.callback(e)



def _startUserTasklet(callee):
    '''
        actual tasklet launch place,must be called inside main loop.

    :param callee:
    :return:
    '''
    UsrTasklet(callee)()
    scheduleStackless()

def startUserTasklet(function,*args,**kwargs):
    '''
        | start new user tasklet.
        | the new tasklet is always create and schedule in main loop(system tasklet)

    :param function:
    :param args:
    :param kwargs:
    :return:
            defer object
                | when tasklet finish execution,the defer will callback with return value(or exception)
                | application can wait for this defer that indicate tasklet is finish,or just skip it.
    '''
    defer = NanoDeferred()
    # defer = Deferred()
    callee = functools.partial(_user_tasklet_main,function, args, kwargs,defer)


    if TaskletMetrics.curUsrTasklet:
        #
        #   still in user tasklet,wait for next main loop.
        #
        reactor.callLater(0,_startUserTasklet,callee)
    else:
        #
        #   in main loop, start immediately
        #
        _startUserTasklet(callee)

    return defer


class SchedulingCallback:
    '''
    | this class is used to hook in stackless schedule callback to monitor the switching between tasklets.
    | by such kind of monitoring,twless can identity current executing tasklet is SysTasklet or UsrTasklet.if in UsrTasklet executing period,\
      twless switch to tasklet context of executing UsrTasklet.

    '''

    def __init__(self, pre_cb):
        '''
        :param pre_cb: previous callback function in stackless
        '''

        self.previousCB = pre_cb


    def __call__(self, prevTasklet, nextTasklet):
        '''
        :param prevTasklet:     previous tasklet in execute chain
        :param nextTasklet:     next tasklet in execute chain
        :return:
        '''
        if isinstance(nextTasklet, UsrTasklet):
            TaskletMetrics.curUsrTasklet = nextTasklet
            TaskletMetrics.curUsrTaskletContext = nextTasklet.context
        else:
            TaskletMetrics.curUsrTasklet = None
            TaskletMetrics.curUsrTaskletContext = None

        if self.previousCB:
            self.previousCB(prevTasklet, nextTasklet)

class _ModuelState:
    Inited = 0



def _initialize():
    if _ModuelState.Inited:
        return
    _ModuelState.Inited = 1

    # log.startLogging(sys.stdout)

    if hasattr(stackless, 'get_schedule_callback'):
        precb = stackless.get_schedule_callback()
    elif hasattr(stackless, '_schedule_callback'):
        precb = stackless._schedule_callback
    else:
        precb = None

    stackless.set_schedule_callback(SchedulingCallback(precb))
    curTasklet = stackless.getcurrent()
    if isinstance(curTasklet, UsrTasklet):
        TaskletMetrics.curUsrTasklet = curTasklet
        TaskletMetrics.curUsrTaskletContext = curTasklet.context
    else:
        TaskletMetrics.curUsrTasklet = None
        TaskletMetrics.curUsrTaskletContext = None



def runReactor(taskFunc, *args, **kwargs):
    _initialize()
    startUserTasklet(taskFunc, *args, **kwargs)
    # DeferTasklet.run()
    t = SysTasklet(reactor.run)
    t()
    stackless.run()


def exitReactor():
    reactor.callLater(0, reactor.stop)



