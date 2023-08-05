"""
I'm using the concurrent.futures ProcessPoolExecutor option.

Installed multiprocess to solve the "Can't pickle <class 'module'>: attribute lookup module on builtins failed" but it didn't work either.

The data is a static keras model which isn't pickable - see https://keras.io/getting-started/faq/#how-can-i-save-a-keras-model.

I have enough memory for each process to hold a copy of the data model or for it to be placed in shared memory for all processes to access. But, how to solve the not pickable problem for a keras model?
"""
