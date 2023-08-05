"""
Has anyone worked to have pytest coverage statistics follow multiprocess processes?

    Coverage as specific support for collecting coverage statistics from tasks using threads, greenlists, and multiprocessor. The multiprocessor specific code:
"""

def multiprocessing_start(_):
    cov = init()
    if cov:
        multiprocessing.util.Finalize(None, cleanup, args=(cov,), exitpriority=1000)


try:
    import multiprocessing.util
except ImportError:
    pass
else:
    multiprocessing.util.register_after_fork(multiprocessing_start, multiprocessing_start)

multiprocessing_finish = cleanup  # in case someone dared to use this internal


"""
    Generating coverage for portions of code under multiprocess, especially in PyCharm, would be helpful.

Is there any guidance on this? Or any experience?
"""
