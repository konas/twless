# -*- coding=utf-8 -*-
'''
:author: konas
:contact: konasyan2009@gmail.com
:description:

    exception classes in twless.

'''

class NotInUsrTaskletError(BaseException):
    '''

        this exception is raised when application attemp to access tasklet context but current tasklet is not UsrTasklet.

    '''
    pass