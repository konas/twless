# -*- coding=utf-8 -*-
'''
:author: konas
:contact: konasyan2009@gmail.com
:description:
    global metrics for tasklet runtime
'''

class TaskletMetrics:
    curUsrTasklet = None
    curUsrTaskletContext = None

    # flag for manually schedule tasklet only once in individual twisted main loop.
    scheduled = 0
