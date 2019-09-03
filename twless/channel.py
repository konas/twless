# -*- coding=utf-8 -*-
'''
:author: konas
:contact: konasyan2009@gmail.com
:description:

    extension class to stackless.channel,provide non-block send feature.
'''
import stackless
from collections import deque

class NonBlockChannel(stackless.channel):
    def __init__(self, label=''):
        '''

        :param label:  channel labal
        '''
        stackless.channel.__init__(self)

        # queue value/exception if not receive on channel
        self.nbQueue = deque()

    def send_nonblock(self, v):
        '''
        send value in non-block style

        :param v: any value
        :return: void
        '''

        if self.balance == 0:
            self.nbQueue.append((0, v))
        else:
            self.send(v)

    def send_exception_noblock(self, ntype, value):
        '''
        send exception in non-block style

        :param ntype:   subclass of BaseException
        :param value:   class instance or parameters
        :return: void
        '''
        if self.balance == 0:
            self.nbQueue.append((1, ntype, value))
        else:
            assert issubclass(ntype,BaseException)
            if isinstance(value, ntype):
                self.send(stackless.bomb(ntype, value))
            else:
                self.send_exception(ntype, value)

    def receive(self,safeReturn=1):
        '''

        :param safeReturn:   if exception happend,return exception instance if safeReturn = 1,otherwise raise it.
        :return: value or exception(if safeReturn == 1)
        '''
        try:
            if self.nbQueue:
                v = self.nbQueue.popleft()
                if v[0] == 0:
                    return v[1]
                else:
                    exType,exValue = v[1], v[2]
                    if isinstance(exValue, exType):
                        raise exValue
                    else:
                        raise exType(exValue)

            r = stackless.channel.receive(self)
            return r
        except BaseException as e:
            if safeReturn:
                print('NonBlockChannel receive exception and return : {0}'.format(repr(e)))
                return e
            else:
                print('NonBlockChannel receive exception and raise : {0}'.format(repr(e)))
                raise e
