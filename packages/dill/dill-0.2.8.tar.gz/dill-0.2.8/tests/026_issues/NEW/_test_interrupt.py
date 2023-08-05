from pathos.multiprocessing import ProcessingPool as Pool

class Foo:

    #...

    def init_executor(self):
        if self.n_jobs == 1:
            return

        if self.n_jobs == -1:
            self.pool = Pool()
        else:
            self.pool = Pool(self.n_jobs)

    def _evaluate_population(self, X, y):
        def f(i):
            if not hasattr(i, 'error_vector'):
                return self._evaluate_individual(i, X, y)
            return i

        if hasattr(self, 'pool'):
            self.population[:] = self.pool.map(f, self.population)
        else:
            for i in self.population:
                f(i)


"""
You can see that there's a test script here that succeeds for both multiprocess and multiprocessing: http://bugs.python.org/file16784/test_map_keyboard_interrput.py. The links following the link you referenced seem to indicate that the issue is closed, but not resolved in all cases. So, I'm guessing that the bug persists. Can you share some (complete) minimal test code that reproduces the bug? Apparently, the workaround is to use map_async and get with a timeout.
"""
