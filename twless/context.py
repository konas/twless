# -*- coding=utf-8 -*-
'''
:author: konas
:contact: konasyan2009@gmail.com
:description:

     UsrTasklet Context:
        | every UsrTasklet instance has a python dictionary as attribute.
        | when running in UsrTasklet,application can read/write/delete/clear its tasklet-specfic data in this dictionary through common method:\
          get_int,set_int,delete_key,etc.
        | with same method,same params,different UsrTasklet with access different dictionary.
        | this mechanism is called UsrTasklet Context.
'''
from twless.error import NotInUsrTaskletError
from twless.metrics import TaskletMetrics


def _getTaskletContext():
    '''
        get current tasklet's context

    :return: dict
    '''
    if TaskletMetrics.curUsrTaskletContext is None:
        raise NotInUsrTaskletError()
    return TaskletMetrics.curUsrTaskletContext

def _getTasklet():
    '''
        get current tasklet

    :return: UsrTasklet instance
    '''
    if TaskletMetrics.curUsrTasklet is None:
        raise NotInUsrTaskletError()
    return TaskletMetrics.curUsrTasklet


def sleepInTasklet(seconds):
    '''
        **must call in UsrTasklet scope**

        sleep in current tasklet.

    :param seconds: (int,float,long) in seconds
    :return:
    '''
    tasklet = _getTasklet()
    tasklet._sleep(seconds)

def waitOnDeferred(deferred, timeout=0, throwError=False):
    '''
        **must call in UsrTasklet scope**

        wait on Deferred until it callback/errback,or timeout(if has)

    :param deferred:    Deferred instance
    :param timeout:     in seconds
    :param throwError:  if error happen,throw exception or not.
    :return:
    '''
    tasklet = _getTasklet()
    return tasklet.wait(deferred,timeout,throwError)

