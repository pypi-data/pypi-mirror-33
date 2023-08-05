"""
Is the goal to find one solution for A,B,C,D?
# Yes

Is it possible to return a set of inequalities of valid ranges of A,B,C,D?
#### No, I don't think so.  Maybe can be derived from replace_variables...?

Solution provided does not satisfy A > D/B, can you elaborate?
# It does. However, it does not satisfy A*B > D. This is a bug in simplify.
# Symbolic division by a negative isn't handled correctly for 2 inqualities.

What is the meaning of the penalty value?
#

What do the parameters for 'constrain' mean?
# 
"""
