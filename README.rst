
what is twless?
==============================================

| twless is a coroutine framework based on twisted and stackless python.
| it provide simple and nature way to create coroutining runtime envirement,\
  no ``async/await``, ``yield`` , ``callback`` infection and circling is needed,\
  eveything is just straight-forward,easy to understand.

look at this simple example:

    .. code-block:: python

        from twless.schedule import runReactor,exitReactor,startUserTasklet
        from twless.context import sleepInTasklet

        class TestContext:
            counter = 0

        def worker(idx):
            '''

                tasklet(coroutine) execute function

            '''
            print('worker #{0} start...'.format(idx))
            # sleep 1 second and continue.
            sleepInTasklet(1)
            print('worker #{0} finish.'.format(idx))
            TestContext.counter -= 1
            if TestContext.counter <= 0:
                # when all workers finish,exit from current process.
                exitReactor()

        def main():
            #
            # start up 100 tasklet(coroutine)
            for idx in xrange(100):
                startUserTasklet(worker,idx)
                TestContext.counter += 1


        if __name__ == '__main__':
            runReactor(main)
