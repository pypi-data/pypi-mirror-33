"""
I have a main script that passes a function and a list of strings to a (Pathos) ProcessPool.map function. The problem I am having is that when I run the process from command line and try to Ctrl + C out of the main thread I am unable to end the process and then when I close the terminal and examine processes on the machine I can see all of the python processes that the ProcessPool spun off are still alive and don't appear able to exit. Am I misusing the library?
"""


accounts = ['THIS', 'ACCT', 'HAS', '$$$']
executor = ProcessPool()
executor.map(testScript.run_for_account, accounts)
