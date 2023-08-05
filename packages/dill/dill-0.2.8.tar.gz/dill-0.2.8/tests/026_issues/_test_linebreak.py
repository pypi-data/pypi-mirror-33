def run_multiprocess(fxn, arg_list, num_workers):
    pool = multiprocessing.Pool(processes=num_workers)
    results = pool.starmap(fxn, arg_list)
    pool.close()
    pool.join()
    return results

"""
This is not exactly a new issue (e.g. Terminal messed up (not displaying new lines) after running Python script), but it's not reported for the python multiprocess module.

Everything works fine if num_workers = 1, but as soon as it is more than 1, then my Terminal's linebreak no longer works.
"""
