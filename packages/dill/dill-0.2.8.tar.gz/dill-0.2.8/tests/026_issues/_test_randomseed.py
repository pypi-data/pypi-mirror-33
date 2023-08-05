"""
multiprocessing has a known issue where certain global random states (and thus the seeds) are copied to all the spawned processes (most notably for anything depending on numpy.random). A potential fix for this is to provide processing (the pathos fork) or pathos.multiprocessing with a "set random_state" function. Then optionally, provide some API extension to enable easy triggering of the "special" seeding (i.e. generating a new random state for each process).
"""

# see mystic's random_state function
