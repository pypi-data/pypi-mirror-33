"""
I have several challenging non-convex global optimization problems to solve. Currently I use MATLAB's Optimization Toolbox (specifically, fmincon() with algorithm='sqp'), which is quite effective. However, most of my code is in Python, and I'd love to do the optimization in Python as well. Is there a NLP solver with Python bindings that can compete with fmincon()? It must

be able to handle nonlinear equality and inequality constraints
not require the user to provide a Jacobian.
It's okay if it doesn't guarantee a global optimum (fmincon() does not). I'm looking for something that robustly converges to a local optimum even for challenging problems, and even if it's slightly slower than fmincon().

I have tried several of the solvers available through OpenOpt and found them to be inferior to MATLAB's fmincon/sqp.

Just for emphasis I already have a tractable formulation and a good solver. My goal is merely to change languages in order to have a more streamlined workflow.

Geoff points out that some characteristics of the problem may be relevant. They are:

10-400 decision variables
4-100 polynomial equality constraints (polynomial degree ranges from 1 to about 8)
A number of rational inequality constraints equal to about twice the number of decision variables
The objective function is one of the decision variables
The Jacobian of the equality constraints is dense, as is the Jacobian of the inequality constraints.
"""
