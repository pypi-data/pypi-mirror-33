'''
it seems like I can't attach a debugger anytime after a ParallelPool is instantiated:

Connected to pydev debugger (build 143.2370)
INFO|pp|Creating server instance (pp-1.6.4.7.1)
INFO|pp|Running on Python 2.7.10 darwin
Traceback (most recent call last):
  File "/Applications/PyCharm.app/Contents/helpers/pydev/pydevd.py", line 2411, in <module>
    globals = debugger.run(setup['file'], None, None, is_module)
  File "/Applications/PyCharm.app/Contents/helpers/pydev/pydevd.py", line 1802, in run
    launch(file, globals, locals)  # execute the script
  File "/Users/tterry/iZotope/dsptester/dsptester/run.py", line 14, in <module>
    run()
  File "/Users/tterry/iZotope/dsptester/dsptester/run.py", line 8, in run
    testrunner = DSPTestRunner()
  File "/Users/tterry/iZotope/dsptester/dsptester/dsptestrunner.py", line 38, in __init__
    self.pool = Pool()
  File "/Users/tterry/Envs/dsptester-env/lib/python2.7/site-packages/pathos/parallel.py", line 183, in __init__
    _pool = self._serve(nodes=ncpus, servers=servers)
  File "/Users/tterry/Envs/dsptester-env/lib/python2.7/site-packages/pathos/parallel.py", line 203, in _serve
    _pool = pp.Server(ppservers=servers)
  File "/Users/tterry/Envs/dsptester-env/lib/python2.7/site-packages/pp.py", line 357, in __init__
    self.set_ncpus(ncpus)
  File "/Users/tterry/Envs/dsptester-env/lib/python2.7/site-packages/pp.py", line 521, in set_ncpus
    range(ncpus - len(self.__workers))])
  File "/Users/tterry/Envs/dsptester-env/lib/python2.7/site-packages/pp.py", line 155, in __init__
    self.start()
  File "/Users/tterry/Envs/dsptester-env/lib/python2.7/site-packages/pp.py", line 167, in start
    self.pid = int(self.t.receive())
  File "/Users/tterry/Envs/dsptester-env/lib/python2.7/site-packages/pptransport.py", line 144, in receive
    raise RuntimeError("Communication pipe read error")
RuntimeError: Communication pipe read error

This happens any time I hit a breakpoint after the ParallelPool is created. It does not happen with pathos.multiprocessing.Pool.
'''

