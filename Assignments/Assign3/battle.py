import sys
import argparse
import copy
import time
# from csp import Constraint, Variable

class Variable:
    '''Class for defining CSP variables.

      On initialization the variable object can be given a name and a
      list containing variable's domain of values. You can reset the
      variable's domain if you want to solve a similar problem where
      the domains have changed.

      To support CSP propagation, the class also maintains a current
      domain for the variable. Values pruned from the variable domain
      are removed from the current domain but not from the original
      domain. Values can be also restored.
    '''

    undoDict = dict()             #stores pruned values indexed by a
                                        #(variable,value) reason pair
    def __init__(self, name, domain):
        '''Create a variable object, specifying its name (a
        string) and domain of values.
        '''
        self._name = name                #text name for variable
        self._dom = list(domain)         #Make a copy of passed domain
        self._curdom = list(domain)      #using list
        self._value = None

        self._checked = False

    def __str__(self):
        return "Variable {}".format(self._name)

    def domain(self):
        '''return copy of variable domain'''
        return(list(self._dom))

    def domainSize(self):
        '''Return the size of the domain'''
        return(len(self.domain()))

    def resetDomain(self, newdomain):
        '''reset the domain of this variable'''
        self._dom = newdomain

        #added
        # if self.domainSize() == 1:
        #     self.setValue(self.domain()[0])

    def getValue(self):
        return self._value

    def setValue(self, value):
        if value != None and not value in self._dom:
            print("Error: tried to assign value {} to variable {} that is not in {}'s domain".format(value,self._name,self._name))
        else:
            self._value = value    

    def unAssign(self):
        self.setValue(None)

    def isAssigned(self):
        return self.getValue() != None

    def name(self):
        return self._name

    def curDomain(self):
        '''return copy of variable current domain. But if variable is assigned
           return just its assigned value (this makes implementing hasSupport easier'''
        if self.isAssigned():
            return([self.getValue()])
        return(list(self._curdom))

    def curDomainSize(self):
        '''Return the size of the current domain'''
        if self.isAssigned():
            return(1)
        return(len(self._curdom))

    def inCurDomain(self, value):
        '''check if value is in current domain'''
        if self.isAssigned():
            return(value==self.getValue())
        return(value in self._curdom)

    def pruneValue(self, value, reasonVar, reasonVal):
        '''Remove value from current domain'''
        try:
            self._curdom.remove(value)
        except:
            print("Error: tried to prune value {} from variable {}'s domain, but value not present!".format(value, self._name))
        dkey = (reasonVar, reasonVal)
        if not dkey in Variable.undoDict:
            Variable.undoDict[dkey] = []
        Variable.undoDict[dkey].append((self, value))

    def restoreVal(self, value):
        self._curdom.append(value)

    def restoreCurDomain(self):
        self._curdom = self.domain()

    def reset(self):
        self.restoreCurDomain()
        self.unAssign()

    def dumpVar(self):
        print("Variable\"{}={}\": Dom = {}, CurDom = {}".format(self._name, self._value, self._dom, self._curdom))

    @staticmethod
    def clearUndoDict():
        undoDict = dict()

    @staticmethod
    def restoreValues(reasonVar, reasonVal):
        dkey = (reasonVar, reasonVal)
        if dkey in Variable.undoDict:
            for (var,val) in Variable.undoDict[dkey]:
                var.restoreVal(val)
            del Variable.undoDict[dkey]



#implement various types of constraints
class Constraint:
    '''Base class for defining constraints. Each constraint can check if
       it has been satisfied, so each type of constraint must be a
       different class. For example a constraint of notEquals(V1,V2)
       must be a different class from a constraint of
       greaterThan(V1,V2), as they must implement different checks of
       satisfaction.

       However one can define a class of general table constraints, as
       below, that can capture many different constraints.

       On initialization the constraint's name can be given as well as
       the constraint's scope. IMPORTANT, the scope is ordered! E.g.,
       the constraint greaterThan(V1,V2) is not the same as the
       contraint greaterThan(V2,V1).
    '''
    def __init__(self, name, scope):
        '''create a constraint object, specify the constraint name (a
        string) and its scope (an ORDERED list of variable
        objects).'''
        self._scope = list(scope)       #variables involved in constraint
        self._name = "baseClass_" + name  #override in subconstraint types!

    def scope(self):
        return list(self._scope)

    def arity(self):
        return len(self._scope)

    def numUnassigned(self):
        i = 0
        for var in self._scope:
            if not var.isAssigned():
                i += 1
        return i

    def unAssignedVars(self):
        return [var for var in self.scope() if not var.isAssigned()]

    # def check(self):
    #     util.raiseNotDefined()

    def name(self):
        return self._name

    def __str__(self):
        return "Cnstr_{}({})".format(self.name(), map(lambda var: var.name(), self.scope()))

    def printConstraint(self):
        print("Cons: {} Vars = {}".format(
            self.name(), [v.name() for v in self.scope()]))


#object for holding a constraint problem
class CSP:
    '''CSP class groups together a set of variables and a set of
       constraints to form a CSP problem. Provides a usesful place
       to put some other functions that depend on which variables
       and constraints are active'''

    def __init__(self, name, variables, constraints):
        '''create a CSP problem object passing it a name, a list of
           variable objects, and a list of constraint objects'''
        self._name = name
        self._variables = variables
        self._constraints = constraints
        self.BOARD_SIZE = 0

        #some sanity checks
        varsInCnst = set()
        for c in constraints:
            varsInCnst = varsInCnst.union(c.scope())
        for v in variables:
            if v not in varsInCnst:
                print("Warning: variable {} is not in any constraint of the CSP {}".format(v.name(), self.name()))
        for v in varsInCnst:
            if v not in variables:
                print("Error: variable {} appears in constraint but specified as one of the variables of the CSP {}".format(v.name(), self.name()))

        self.constraints_of = [[] for i in range(len(variables))]
        for c in constraints:
            for v in c.scope():
                i = variables.index(v)
                self.constraints_of[i].append(c)

    def name(self):
        return self._name

    def variables(self):
        return list(self._variables)

    def constraints(self):
        return list(self._constraints)

    def constraintsOf(self, var):
        '''return constraints with var in their scope'''
        try:
            i = self.variables().index(var)
            return list(self.constraints_of[i])
        except:
            print("Error: tried to find constraint of variable {} that isn't in this CSP {}".format(var, self.name()))

    def unAssignAllVars(self):
        '''unassign all variables'''
        for v in self.variables():
            v.unAssign()

    def check(self, solutions):
        '''each solution is a list of (var, value) pairs. Check to see
           if these satisfy all the constraints. Return list of
           erroneous solutions'''

        #save values to restore later
        current_values = [(var, var.getValue()) for var in self.variables()]
        errs = []

        for s in solutions:
            s_vars = [var for (var, val) in s]

            if len(s_vars) != len(self.variables()):
                errs.append([s, "Solution has incorrect number of variables in it"])
                continue

            if len(set(s_vars)) != len(self.variables()):
                errs.append([s, "Solution has duplicate variable assignments"])
                continue

            if set(s_vars) != set(self.variables()):
                errs.append([s, "Solution has incorrect variable in it"])
                continue

            for (var, val) in s:
                var.setValue(val)

            for c in self.constraints():
                if not c.check():
                    errs.append([s, "Solution does not satisfy constraint {}".format(c.name())])
                    break

        for (var, val) in current_values:
            var.setValue(val)

        return errs
    
    def __str__(self):
        return "CSP {}".format(self.name())
    









class TableConstraint(Constraint):
    '''General type of constraint that can be use to implement any type of
       constraint. But might require a lot of space to do so.

       A table constraint explicitly stores the set of satisfying
       tuples of assignments.'''

    def __init__(self, name, scope, SA):
        '''Init by specifying a name and a set variables the constraint is over.
           Along with a list of satisfying assignments.
           Each satisfying assignment is itself a list, of length equal to
           the number of variables in the constraints scope.
           If sa is a single satisfying assignment, e.g, sa=SA[0]
           then sa[i] is the value that will be assigned to the variable scope[i].


           Example, say you want to specify a constraint alldiff(A,B,C,D) for
           three variables A, B, C each with domain [1,2,3,4]
           Then you would create this constraint using the call
           c = TableConstraint('example', [A,B,C,D],
                               [[1, 2, 3, 4], [1, 2, 4, 3], [1, 3, 2, 4],
                                [1, 3, 4, 2], [1, 4, 2, 3], [1, 4, 3, 2],
                                [2, 1, 3, 4], [2, 1, 4, 3], [2, 3, 1, 4],
                                [2, 3, 4, 1], [2, 4, 1, 3], [2, 4, 3, 1],
                                [3, 1, 2, 4], [3, 1, 4, 2], [3, 2, 1, 4],
                                [3, 2, 4, 1], [3, 4, 1, 2], [3, 4, 2, 1],
                                [4, 1, 2, 3], [4, 1, 3, 2], [4, 2, 1, 3],
                                [4, 2, 3, 1], [4, 3, 1, 2], [4, 3, 2, 1]])
          as these are the only assignments to A,B,C respectively that
          satisfy alldiff(A,B,C,D)
        '''

        Constraint.__init__(self,name, scope)
        self._name = "TableCnstr_" + name
        self.satAssignments = SA

    def check(self):
        '''check if current variable assignments are in the satisfying set'''
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        return assignments in self.satAssignments

    def hasSupport(self, var,val):
        '''check if var=val has an extension to an assignment of all variables in
           constraint's scope that satisfies the constraint. Important only to
           examine values in the variable's current domain as possible extensions'''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in
        vindex = self.scope().index(var)
        # print("initialized false")
        found = False
        for assignment in self.satAssignments:
            # print(assignment[vindex], val)
            if assignment[vindex] != val:
                continue   #this assignment can't work it doesn't make var=val
            found = True   #Otherwise it has potential. Assume found until shown otherwise
            for i, v in enumerate(self.scope()):
                # print("inner")
                # print(v._name)
                # print("vindex", vindex, "i:", i, v.inCurDomain(assignment[i]))
                if i != vindex and not v.inCurDomain(assignment[i]):
                    # print("made false")
                    # print("didnt find support for {}={} because {} not in {}'s curDomain")
                    found = False  #Bummer...this assignment didn't work it assigns
                    break          #a value to v that is not in v's curDomain
                                   #note we skip checking if val in in var's curDomain
            if found:     #if found still true the assigment worked. We can stop
                break
            
        # if not found:
        #     print("Exiting hasSupport: no support found")
        return found     #either way found has the right truth value

def findvals(remainingVars, assignment, finalTestfn, partialTestfn=lambda x: True):
    '''Helper function for finding an assignment to the variables of a constraint
       that together with var=val satisfy the constraint. That is, this
       function looks for a supporing tuple.

       findvals uses recursion to build up a complete assignment, one value
       from every variable's current domain, along with var=val.

       It tries all ways of constructing such an assignment (using
       a recursive depth-first search).

       If partialTestfn is supplied, it will use this function to test
       all partial assignments---if the function returns False
       it will terminate trying to grow that assignment.

       It will test all full assignments to "allVars" using finalTestfn
       returning once it finds a full assignment that passes this test.

       returns True if it finds a suitable full assignment, False if none
       exist. (yes we are using an algorithm that is exactly like backtracking!)'''

    # print "==>findvars([",
    # for v in remainingVars: print v.name(), " ",
    # print "], [",
    # for x,y in assignment: print "({}={}) ".format(x.name(),y),
    # print ""

    #sort the variables call the internal version with the variables sorted
    remainingVars.sort(reverse=True, key=lambda v: v.curDomainSize())
    return findvals_(remainingVars, assignment, finalTestfn, partialTestfn)

def findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
    '''findvals_ internal function with remainingVars sorted by the size of
       their current domain'''
    if len(remainingVars) == 0:
        return finalTestfn(assignment)
    var = remainingVars.pop()
    for val in var.curDomain():
        assignment.append((var, val))
        if partialTestfn(assignment):
            if findvals_(remainingVars, assignment, finalTestfn, partialTestfn):
                return True
        assignment.pop()   #(var,val) didn't work since we didn't do the return
    remainingVars.append(var)
    return False


class NValuesConstraint(Constraint):
    '''NValues constraint over a set of variables.  Among the variables in
       the constraint's scope the number that have been assigned
       values in the set 'required_values' is in the range
       [lower_bound, upper_bound] (lower_bound <= #of variables
       assigned 'required_value' <= upper_bound)

       For example, if we have 4 variables V1, V2, V3, V4, each with
       domain [1, 2, 3, 4], then the call
       NValuesConstraint('test_nvalues', [V1, V2, V3, V4], [1,4], 2,
       3) will only be satisfied by assignments such that at least 2
       the V1, V2, V3, V4 are assigned the value 1 or 4, and at most 3
       of them have been assigned the value 1 or 4.

    '''

    def __init__(self, name, scope, required_values, lower_bound, upper_bound):
        Constraint.__init__(self,name, scope)
        self._name = "NValues_" + name
        self._required = required_values
        self._lb = lower_bound
        self._ub = upper_bound

    def check(self):
        assignments = []
        for v in self.scope():
            if v.isAssigned():
                assignments.append(v.getValue())
            else:
                return True
        rv_count = 0

        #print "Checking {} with assignments = {}".format(self.name(), assignments)

        for v in assignments:
            if v in self._required:
                rv_count += 1

        #print "rv_count = {} test = {}".format(rv_count, self._lb <= rv_count and self._ub >= rv_count)


        return self._lb <= rv_count and self._ub >= rv_count

    def hasSupport(self, var, val):
        '''check if var=val has an extension to an assignment of the
           other variable in the constraint that satisfies the constraint

           HINT: check the implementation of AllDiffConstraint.hasSupport
                 a similar approach is applicable here (but of course
                 there are other ways as well)
        '''
        if var not in self.scope():
            return True   #var=val has support on any constraint it does not participate in

        #define the test functions for findvals
        def valsOK(l):
            '''tests a list of assignments which are pairs (var,val)
               to see if they can satisfy this sum constraint'''
            rv_count = 0
            vals = [val for (var, val) in l]
            for v in vals:
                if v in self._required:
                    rv_count += 1
            least = rv_count + self.arity() - len(vals)
            most =  rv_count
            return self._lb <= least and self._ub >= most
        varsToAssign = self.scope()
        varsToAssign.remove(var)
        x = findvals(varsToAssign, [(var, val)], valsOK, valsOK)
        return x

class IfAllThenOneConstraint(Constraint):
    '''if each variable in left_side equals each value in left_values 
    then one of the variables in right side has to equal one of the values in right_values. 
    hasSupport tested only, check() untested.'''
    def __init__(self, name, left_side, right_side, left_values, right_values):
        Constraint.__init__(self,name, left_side+right_side)
        self._name = "IfAllThenOne_" + name
        self._ls = left_side
        self._rs = right_side
        self._lv = left_values
        self._rv = right_values





def startup(input):

    #open the file
    #read the file
    #create the board
    #return the board and CSP



    f = open(input)

    row_num_constraint = [str(x) for x in f.readline().rstrip()]
    col_constraint = [str(x) for x in f.readline().rstrip()]
    num_ships = [str(x) for x in f.readline().rstrip()]
    temp = f.readlines()
    lines = [[str(x) for x in l.rstrip()] for l in temp]
    f.close()

    # print(row_num_constraint)
    # print(col_constraint)
    # print(num_ships)
    # print(lines)


    size = len(row_num_constraint)
    global BOARD_WIDTH
    BOARD_WIDTH = size

    global BOARD_HEIGHT
    BOARD_HEIGHT = size

    Global_Board = dict()
    var_list = []
    con_list = []


    for i, l in enumerate(lines):
        for j, c in enumerate(l):
           

            if row_num_constraint[i] == '0' or col_constraint[j] == '0':
                dom_list = ['.']
                Global_Board[str(i) + ',' + str(j)] = Variable("V{}{}".format(i,j), dom_list)
                Global_Board[str(i) + ',' + str(j)].setValue('.')
                continue

            
            #'S', '.', '<', '>', '^', 'v', 'M', 'x'
            #S = sub, . = water, < = left, > = right, ^ = top, v = bot, M = middle
            dom_list = ['S', '.', '<', '>', '^', 'v', 'M']
                
            if c != '0':
                dom_list = [c]
                
                Global_Board[str(i) + ',' + str(j)] = Variable("V{}{}".format(i,j), dom_list)
                Global_Board[str(i) + ',' + str(j)].setValue(c)
            else:
            
                #left side of board can't be >
                if j == 0:
                    dom_list.remove('>')

                #right side of board can't be <
                elif j == BOARD_WIDTH-1:
                    dom_list.remove('<')
                
                #top side of board can't be v
                if i == 0:
                    dom_list.remove('v')

                #bottom side of board can't be ^
                elif i == BOARD_HEIGHT-1:
                    dom_list.remove('^')

                
                #corner cannot be M
                if (i == 0 and j == 0) or \
                    (i == 0 and j == BOARD_WIDTH-1) or\
                    (i == BOARD_HEIGHT-1 and j == 0) or \
                    (i == BOARD_HEIGHT-1 and j == BOARD_WIDTH-1):
                    dom_list.remove('M')


            
                Global_Board[str(i) + ',' + str(j)] = Variable("V{}{}".format(i,j), dom_list)


                


        #def __init__(self, name, scope, required_values, lower_bound, upper_bound):
        if row_num_constraint[i] != '0':
            row_con = NValuesConstraint(
                "Row{}".format(i), 
                [Global_Board[str(i) + ',' + str(u)] for u in range(BOARD_WIDTH)],
                ['S', '<', '>', '^', 'v', 'M'],
                int(row_num_constraint[i]),
                int(row_num_constraint[i]))
            con_list.append(row_con)
        

    for k, c in enumerate(col_constraint):
        if c != '0':
            col_con = NValuesConstraint(
                "Col{}".format(k), 
                [Global_Board[str(i) + ',' + str(k)] for i in range(BOARD_HEIGHT)],
                ['S', '<', '>', '^', 'v', 'M'],
                int(c),
                int(c))
            con_list.append(col_con)


    
    con_list += (cell_constraint_gen(Global_Board))
    var_list = list(Global_Board.values())
    # for u in con_list:
        
    #     # print("hi\n")
    #     # print(u._name)
    #     pass
    csp = CSP("Battleship", var_list, con_list)
    csp.BOARD_SIZE = size

    # preprocess(csp)


    return csp, Global_Board, var_list, con_list, num_ships




def preprocess(csp):
    size = csp.BOARD_SIZE
    for i in range(size):
        for j in range(size):
            var = Global_Board[str(i)+','+str(j)]
            if var.isAssigned() and var._checked == False:

                if var._value == '<':
                    if i-1 >= 0 and not Global_Board[str(i-1)+','+str(j)].isAssigned():
                        Global_Board[str(i-1)+','+str(j)].resetDomain(['.'])
                        Global_Board[str(i-1)+','+str(j)].setValue(['.'])
                    if i+1 < size and not Global_Board[str(i+1)+','+str(j)].isAssigned():
                        Global_Board[str(i+1)+','+str(j)].resetDomain(['.'])
                        Global_Board[str(i+1)+','+str(j)].setValue('.')
                    if j-1 >= 0 and not Global_Board[str(i)+','+str(j-1)].isAssigned():
                        Global_Board[str(i)+','+str(j-1)].resetDomain(['.'])
                        Global_Board[str(i)+','+str(j-1)].setValue('.')
                    if j+1 < size and not Global_Board[str(i)+','+str(j+1)].isAssigned():
                        Global_Board[str(i)+','+str(j+1)].resetDomain(['>','M'])

                    #corners
                    if i-1 >= 0 and j-1 >= 0 and not Global_Board[str(i-1)+','+str(j-1)].isAssigned():                        
                        Global_Board[str(i-1)+','+str(j-1)].resetDomain(['.'])
                        Global_Board[str(i-1)+','+str(j-1)].setValue('.')
                    if i-1 >= 0 and j+1 < size and not Global_Board[str(i-1)+','+str(j+1)].isAssigned():                        
                        Global_Board[str(i-1)+','+str(j+1)].resetDomain(['.'])
                        Global_Board[str(i-1)+','+str(j+1)].setValue('.')
                    if i+1 < size and j-1 >= 0 and not Global_Board[str(i+1)+','+str(j-1)].isAssigned():
                        Global_Board[str(i+1)+','+str(j-1)].resetDomain(['.'])
                        Global_Board[str(i+1)+','+str(j-1)].setValue('.')
                    if i+1 < size and j+1 < size and not Global_Board[str(i+1)+','+str(j+1)].isAssigned():
                        Global_Board[str(i+1)+','+str(j+1)].resetDomain(['.'])
                        Global_Board[str(i+1)+','+str(j+1)].setValue('.')


                elif var._value == '>':
                    if i-1 >= 0 and not Global_Board[str(i-1)+','+str(j)].isAssigned():
                        Global_Board[str(i-1)+','+str(j)].setValue('.')
                        Global_Board[str(i-1)+','+str(j)].resetDomain(['.'])
                    if i+1 < size and not Global_Board[str(i+1)+','+str(j)].isAssigned():
                        Global_Board[str(i+1)+','+str(j)].setValue('.')
                        Global_Board[str(i+1)+','+str(j)].resetDomain(['.'])
                    if j-1 >= 0 and not Global_Board[str(i)+','+str(j-1)].isAssigned():
                        Global_Board[str(i)+','+str(j-1)].resetDomain(['<','M'])
                    if j+1 < size and not Global_Board[str(i)+','+str(j+1)].isAssigned():
                        Global_Board[str(i)+','+str(j+1)].setValue('.')
                        Global_Board[str(i)+','+str(j+1)].resetDomain(['.'])

                    #corners
                    if i-1 >= 0 and j-1 >= 0 and not Global_Board[str(i-1)+','+str(j-1)].isAssigned():
                        Global_Board[str(i-1)+','+str(j-1)].setValue('.')
                        Global_Board[str(i-1)+','+str(j-1)].resetDomain(['.'])
                    if i-1 >= 0 and j+1 < size and not Global_Board[str(i-1)+','+str(j+1)].isAssigned():
                        Global_Board[str(i-1)+','+str(j+1)].setValue('.')
                        Global_Board[str(i-1)+','+str(j+1)].resetDomain(['.'])
                    if i+1 < size and j-1 >= 0 and not Global_Board[str(i+1)+','+str(j-1)].isAssigned():
                        Global_Board[str(i+1)+','+str(j-1)].setValue('.')
                        Global_Board[str(i+1)+','+str(j-1)].resetDomain(['.'])
                    if i+1 < size and j+1 < size and not Global_Board[str(i+1)+','+str(j+1)].isAssigned():
                        Global_Board[str(i+1)+','+str(j+1)].setValue('.')
                        Global_Board[str(i+1)+','+str(j+1)].resetDomain(['.'])

                elif var._value == '^':
                    if i-1 >= 0 and not Global_Board[str(i-1)+','+str(j)].isAssigned():
                        Global_Board[str(i-1)+','+str(j)].setValue('.')
                        Global_Board[str(i-1)+','+str(j)].resetDomain(['.'])
                    if i+1 < size and not Global_Board[str(i+1)+','+str(j)].isAssigned():
                        Global_Board[str(i+1)+','+str(j)].resetDomain(['v','M'])
                    if j-1 >= 0 and not Global_Board[str(i)+','+str(j-1)].isAssigned():
                        Global_Board[str(i)+','+str(j-1)].setValue('.')
                        Global_Board[str(i)+','+str(j-1)].resetDomain(['.'])
                    if j+1 < size and not Global_Board[str(i)+','+str(j+1)].isAssigned():
                        Global_Board[str(i)+','+str(j+1)].setValue('.')
                        Global_Board[str(i)+','+str(j+1)].resetDomain(['.'])

                    #corners
                    if i-1 >= 0 and j-1 >= 0 and not Global_Board[str(i-1)+','+str(j-1)].isAssigned():
                        Global_Board[str(i-1)+','+str(j-1)].setValue('.')
                        Global_Board[str(i-1)+','+str(j-1)].resetDomain(['.'])
                    if i-1 >= 0 and j+1 < size and not Global_Board[str(i-1)+','+str(j+1)].isAssigned():
                        Global_Board[str(i-1)+','+str(j+1)].setValue('.')
                        Global_Board[str(i-1)+','+str(j+1)].resetDomain(['.'])
                    if i+1 < size and j-1 >= 0 and not Global_Board[str(i+1)+','+str(j-1)].isAssigned():
                        Global_Board[str(i+1)+','+str(j-1)].setValue('.')
                        Global_Board[str(i+1)+','+str(j-1)].resetDomain(['.'])
                    if i+1 < size and j+1 < size and not Global_Board[str(i+1)+','+str(j+1)].isAssigned():
                        Global_Board[str(i+1)+','+str(j+1)].setValue('.')
                        Global_Board[str(i+1)+','+str(j+1)].resetDomain(['.'])

                elif var._value == 'v':
                    if i-1 >= 0 and not Global_Board[str(i-1)+','+str(j)].isAssigned():
                        Global_Board[str(i-1)+','+str(j)].resetDomain(['^','M'])
                    if i+1 < size and not Global_Board[str(i+1)+','+str(j)].isAssigned():
                        Global_Board[str(i+1)+','+str(j)].setValue('.')
                        Global_Board[str(i+1)+','+str(j)].resetDomain(['.'])
                    if j-1 >= 0 and not Global_Board[str(i)+','+str(j-1)].isAssigned():
                        Global_Board[str(i)+','+str(j-1)].setValue('.')
                        Global_Board[str(i)+','+str(j-1)].resetDomain(['.'])
                    if j+1 < size and not Global_Board[str(i)+','+str(j+1)].isAssigned():
                        Global_Board[str(i)+','+str(j+1)].setValue('.')
                        Global_Board[str(i)+','+str(j+1)].resetDomain(['.'])

                    #corners
                    if i-1 >= 0 and j-1 >= 0:
                        Global_Board[str(i-1)+','+str(j-1)].setValue('.')
                        Global_Board[str(i-1)+','+str(j-1)].resetDomain(['.'])
                    if i-1 >= 0 and j+1 < size:
                        Global_Board[str(i-1)+','+str(j+1)].setValue('.')
                        Global_Board[str(i-1)+','+str(j+1)].resetDomain(['.'])
                    if i+1 < size and j-1 >= 0:
                        Global_Board[str(i+1)+','+str(j-1)].setValue('.')
                        Global_Board[str(i+1)+','+str(j-1)].resetDomain(['.'])
                    if i+1 < size and j+1 < size:
                        Global_Board[str(i+1)+','+str(j+1)].setValue('.')
                        Global_Board[str(i+1)+','+str(j+1)].resetDomain(['.'])


                elif var._value == 'S':
                    if i-1 >= 0:
                        Global_Board[str(i-1)+','+str(j)].setValue('.')
                        Global_Board[str(i-1)+','+str(j)].resetDomain(['.'])
                    if i+1 < size:
                        Global_Board[str(i+1)+','+str(j)].setValue('.')
                        Global_Board[str(i+1)+','+str(j)].resetDomain(['.'])
                    if j-1 >= 0:
                        Global_Board[str(i)+','+str(j-1)].setValue('.')
                        Global_Board[str(i)+','+str(j-1)].resetDomain(['.'])
                    if j+1 < size:
                        Global_Board[str(i)+','+str(j+1)].setValue('.')
                        Global_Board[str(i)+','+str(j+1)].resetDomain(['.'])
                    
                    #corners
                    if i-1 >= 0 and j-1 >= 0:
                        Global_Board[str(i-1)+','+str(j-1)].setValue('.')
                        Global_Board[str(i-1)+','+str(j-1)].resetDomain(['.'])
                    if i-1 >= 0 and j+1 < size:
                        Global_Board[str(i-1)+','+str(j+1)].setValue('.')
                        Global_Board[str(i-1)+','+str(j+1)].resetDomain(['.'])
                    if i+1 < size and j-1 >= 0:
                        Global_Board[str(i+1)+','+str(j-1)].setValue('.')
                        Global_Board[str(i+1)+','+str(j-1)].resetDomain(['.'])
                    if i+1 < size and j+1 < size:
                        Global_Board[str(i+1)+','+str(j+1)].setValue('.')
                        Global_Board[str(i+1)+','+str(j+1)].resetDomain(['.'])
                
                elif var._value == 'M':

                    
                    if i-1 >= 0 and i+1 < size:
                        #above check
                        if not Global_Board[str(i-1)+','+str(j)].inCurDomain('.'):
                            if not Global_Board[str(i+1)+','+str(j)].isAssigned():
                                Global_Board[str(i+1)+','+str(j)].resetDomain(['v','M'])

                                if j-1 >= 0 and not Global_Board[str(i+1)+','+str(j-1)].isAssigned():
                                    Global_Board[str(i)+','+str(j-1)].setValue('.')
                                    Global_Board[str(i)+','+str(j-1)].resetDomain(['.'])
                                if j+1 < size and not Global_Board[str(i+1)+','+str(j+1)].isAssigned():
                                    Global_Board[str(i)+','+str(j+1)].setValue('.')
                                    Global_Board[str(i)+','+str(j+1)].resetDomain(['.'])

                        #below check
                        if not Global_Board[str(i+1)+','+str(j)].inCurDomain('.'):
                            if not Global_Board[str(i-1)+','+str(j)].isAssigned():
                                Global_Board[str(i-1)+','+str(j)].resetDomain(['^','M'])
                                if j-1 >= 0 and not Global_Board[str(i+1)+','+str(j-1)].isAssigned():
                                    Global_Board[str(i)+','+str(j-1)].setValue('.')
                                    Global_Board[str(i)+','+str(j-1)].resetDomain(['.'])
                                if j+1 < size and not Global_Board[str(i+1)+','+str(j+1)].isAssigned():
                                    Global_Board[str(i)+','+str(j+1)].setValue('.')
                                    Global_Board[str(i)+','+str(j+1)].resetDomain(['.'])

                    if j-1 >= 0 and j+1 < size:
                        #left check
                        if not Global_Board[str(i)+','+str(j-1)].inCurDomain('.'):
                            if not Global_Board[str(i)+','+str(j+1)].isAssigned():
                                Global_Board[str(i)+','+str(j+1)].resetDomain(['<','M'])
                                if i-1 >= 0 and not Global_Board[str(i-1)+','+str(j+1)].isAssigned():
                                    Global_Board[str(i-1)+','+str(j)].setValue('.')
                                    Global_Board[str(i-1)+','+str(j)].resetDomain(['.'])
                                if i+1 < size and not Global_Board[str(i+1)+','+str(j+1)].isAssigned():
                                    Global_Board[str(i+1)+','+str(j)].setValue('.')
                                    Global_Board[str(i+1)+','+str(j)].resetDomain(['.'])

                        #right check
                        if not Global_Board[str(i)+','+str(j+1)].inCurDomain('.'):
                            if not Global_Board[str(i)+','+str(j-1)].isAssigned():
                                Global_Board[str(i)+','+str(j-1)].resetDomain(['>','M'])
                                if i-1 >= 0 and not Global_Board[str(i-1)+','+str(j-1)].isAssigned():
                                    Global_Board[str(i-1)+','+str(j)].setValue('.')
                                    Global_Board[str(i-1)+','+str(j)].resetDomain(['.'])
                                if i+1 < size and not Global_Board[str(i+1)+','+str(j-1)].isAssigned():
                                    Global_Board[str(i+1)+','+str(j)].setValue('.')
                                    Global_Board[str(i+1)+','+str(j)].resetDomain(['.'])

                var._checked = True        

def cal_rules():
    rules = dict()
    directions = ['up', 'down', 'left', 'right', 'up-left', 'up-right', 'down-left', 'down-right']
    
    pieces = ['S', '.', 'M', 'v', '^', '<', '>']

    #S
    rules['S'] = dict()
    for d in directions:
        rules['S'][d] = ['.']
    
    #'.'
    rules['.'] = dict()
    for d in directions:
        rules['.'][d] = pieces
    # #remove
    rules['.']['up'].remove('^')
    rules['.']['down'].remove('v')
    rules['.']['left'].remove('<')
    rules['.']['right'].remove('>')


    #M
    rules['M'] = dict()
    rules['M']['up'] = ['^', 'M', '.']
    rules['M']['down'] = ['v', 'M', '.']
    rules['M']['left'] = ['<', 'M', '.']
    rules['M']['right'] = ['>', 'M', '.']
    rules['M']['up-left'] = ['.']
    rules['M']['up-right'] = ['.']
    rules['M']['down-left'] = ['.']
    rules['M']['down-right'] = ['.']

    #v
    rules['v'] = dict()
    for d in directions:
        rules['v'][d] = ['.']
    rules['v']['up'] = ['^', 'M']

    #^
    rules['^'] = dict()
    for d in directions:
        rules['^'][d] = ['.']
    rules['^']['down'] = ['v', 'M']

    #<
    rules['<'] = dict()
    for d in directions:
        rules['<'][d] = ['.']
    rules['<']['right'] = ['>', 'M']

    #>
    rules['>'] = dict()
    for d in directions:
        rules['>'][d] = ['.']
    rules['>']['left'] = ['<', 'M']

    return rules

def possible_moves(i,j):
    dir = ['up', 'down', 'left', 'right', 'up-left', 'up-right', 'down-left', 'down-right']
    
    if i == 0:
        dir.remove('up')
        dir.remove('up-left')
        dir.remove('up-right')

    if i == BOARD_HEIGHT-1:
        dir.remove('down')
        dir.remove('down-right')
        dir.remove('down-left')

    if j == 0:
        dir.remove('left')
        if 'up-left' in dir:
            dir.remove('up-left')
        if 'down-left' in dir:
            dir.remove('down-left')

    if j == BOARD_WIDTH-1:
        dir.remove('right')
        if 'up-right' in dir:
            dir.remove('up-right')
        if 'down-right' in dir:
            dir.remove('down-right')

    return dir



def dir_num(dir):
    if dir == 'up':
        return -1, 0
    elif dir == 'down':
        return 1, 0
    elif dir == 'left':
        return 0, -1
    elif dir == 'right':
        return 0, 1
    elif dir == 'up-left':
        return -1, -1
    elif dir == 'up-right':
        return -1, 1
    elif dir == 'down-left':
        return 1, -1
    elif dir == 'down-right':
        return 1, 1

def cell_constraint_gen(var_dict):
    rules = cal_rules()


    cell_constraint = list()
    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):

            cur_var = var_dict[str(i)+','+str(j)]
            cur_dir = possible_moves(i,j)
            for d in cur_dir:
                y,x = dir_num(d)
                scope = [cur_var, var_dict[str(i+y)+','+str(j+x)]]

                SA = list()
                # temp = list()
                for dom in cur_var.domain():
                    # print("dom: ", dom)
                    # print("cur_var dict: ", rules[dom][d])
                    # if dom not in rules[cur_var.value()][d]:
                    #     cur_var.removeFromDomain(dom)
                    # print(cur_var._name, ":", var_dict[str(i+y)+','+str(j+x)]._name)
                    # print("dom2:", var_dict[str(i+y)+','+str(j+x)].domain())
                    for dom2 in var_dict[str(i+y)+','+str(j+x)].domain():
                        if dom2 in rules[dom][d]:
                            # print("direction: ", d)
                            # print("dom: ", dom, "dom2: ", dom2)
                            SA.append([dom, dom2])

                    if d == 'up' and i+y == 0:
                        for ass in SA:
                            if ass[1] == 'M' and ass[0] in ['v', 'M']:
                                SA.remove(ass)
                    if d == 'down' and i+y == BOARD_HEIGHT-1:
                        for ass in SA:
                            if ass[1] == 'M' and ass[0] in ['^', 'M']:
                                SA.remove(ass)
                    if d == 'left' and j+x == 0:
                        for ass in SA:
                            if ass[1] == 'M' and ass[0] in ['>', 'M']:
                                SA.remove(ass)
                    if d == 'right' and j+x == BOARD_WIDTH-1:
                        for ass in SA:
                            if ass[1] == 'M' and ass[0] in ['<', 'M']:
                                SA.remove(ass)


                # print("\n")

                # print(scope[1])
                # print("SA: ", SA)
                # # print("\n")
                # cell_constraint.append(
                #     TableConstraint("C:{},{}to{},{}".format(i,j,i+y,j+x), 
                #                     scope, SA))


            if "left" in cur_dir and "right" in cur_dir:    
                scope = [cur_var, var_dict[str(i)+','+str(j-1)], var_dict[str(i)+','+str(j+1)]]
                SA = list()
                for dom in cur_var.domain():
                    # for dom2 in var_dict[str(i)+','+str(j-1)].domain():
                    #     if dom2 in rules[dom]['left']:
                    #         for dom3 in var_dict[str(i)+','+str(j+1)].domain():
                    #             if dom3 in rules[dom]['right']:
                    #                 SA.append([dom, dom2, dom3])
                    if dom in ['S', '^', 'v']:
                        SA.append([dom, '.', '.'])
                    elif dom == '.':
                        for left in ['.', 'S', '>', '^', 'v', 'M']:
                            for right in ['.', 'S', '<', '^', 'v', 'M']:
                                SA.append(['.', left, right])
                    elif dom == '<':
                        SA.append(['<', '.', 'M'])
                        SA.append(['<', '.', '>'])
                    elif dom == '>':
                        SA.append(['>', 'M', '.'])
                        SA.append(['>', '<', '.'])
                    elif dom == 'M':
                        SA.append(['M', '<', '>'])
                        SA.append(['M', '<', 'M'])
                        SA.append(['M', 'M', '>'])
                        SA.append(['M', '.', '.'])

                cell_constraint.append(
                    TableConstraint("H:{},{}to{},{}to{},{}".format(i,j,i,j-1,i,j+1), 
                                    scope, SA))
                
            if "up" in cur_dir and "down" in cur_dir:
                scope = [cur_var, var_dict[str(i-1)+','+str(j)], var_dict[str(i+1)+','+str(j)]]
                SA = list()
                for dom in cur_var.domain():
                    # for dom2 in var_dict[str(i-1)+','+str(j)].domain():
                    #     if dom2 in rules[dom]['up']:
                    #         for dom3 in var_dict[str(i+1)+','+str(j)].domain():
                    #             if dom3 in rules[dom]['down']:
                    #                 SA.append([dom, dom2, dom3])
                    if dom in ['S', '<', '>']:
                        SA.append([dom, '.', '.'])
                    elif dom == '.':
                        for up in ['.', 'S', 'v', '<', '>', 'M']:
                            for down in ['.', 'S', '^', '<', '>', 'M']:
                                SA.append(['.', up, down])
                    elif dom == '^':
                        SA.append(['^', '.', 'M'])
                        SA.append(['^', '.', 'v'])
                    elif dom == 'v':
                        SA.append(['v', 'M', '.'])
                        SA.append(['v', '^', '.'])
                    elif dom == 'M':
                        SA.append(['M', '^', 'v'])
                        SA.append(['M', '^', 'M'])
                        SA.append(['M', 'M', 'v'])
                        SA.append(['M', '.', '.'])
                cell_constraint.append(
                    TableConstraint("V:{},{}to{},{}to{},{}".format(i,j,i-1,j,i+1,j), 
                                    scope, SA))
                
            if "left" in cur_dir and "up" in cur_dir:
                scope = [cur_var, var_dict[str(i)+','+str(j-1)], var_dict[str(i-1)+','+str(j)]]
                SA = list()
                for dom in cur_var.domain():
                    # for dom2 in var_dict[str(i)+','+str(j-1)].domain():
                    #     if dom2 in rules[dom]['left']:
                    #         for dom3 in var_dict[str(i-1)+','+str(j)].domain():
                    #             if dom3 in rules[dom]['up'] and dom3 in rules[dom2]['up-right']:
                    #                 SA.append([dom, dom2, dom3])

                    if dom == '.':
                        for up in ['S', '<', '>', 'v', 'M']:
                            SA.append(['.', '.', up])
                        for left in ['S', '>', '^', 'v', 'M']:
                            SA.append(['.', left, '.'])
                        SA.append(['.', '.', '.'])
                    elif dom in ['S', '<', '^']:
                        SA.append([dom, '.', '.'])
                    elif dom == '>':
                        SA.append(['>', 'M', '.'])
                        SA.append(['>', '<', '.']) 
                    elif dom == 'v':
                        SA.append(['v', '.', 'M'])
                        SA.append(['v', '.', '^'])
                    elif dom == 'M':
                        SA.append(['M', '<', '.'])
                        SA.append(['M', '.', '^'])
                        SA.append(['M', 'M', '.'])
                        SA.append(['M', '.', 'M'])

                    

                cell_constraint.append(
                    TableConstraint("LU:{},{}to{},{}to{},{}".format(i,j,i,j-1,i-1,j), 
                                    scope, SA))
            
            if "left" in cur_dir and "down" in cur_dir:
                scope = [cur_var, var_dict[str(i)+','+str(j-1)], var_dict[str(i+1)+','+str(j)]]
                SA = list()
                for dom in cur_var.domain():
                    # for dom2 in var_dict[str(i)+','+str(j-1)].domain():
                    #     if dom2 in rules[dom]['left']:
                    #         for dom3 in var_dict[str(i+1)+','+str(j)].domain():
                    #             if dom3 in rules[dom]['down'] and dom3 in rules[dom2]['down-right']:
                    #                 SA.append([dom, dom2, dom3])

                    if dom == '.':
                        for down in ['S', '<', '>', '^', 'M']:
                            SA.append(['.', '.', down])
                        for left in ['S', '>', '^', 'v', 'M']:
                            SA.append(['.', left, '.'])
                        SA.append(['.', '.', '.'])
                    elif dom in ['S', '<', 'v']:
                        SA.append([dom, '.', '.'])
                    elif dom == '>':
                        SA.append(['>', 'M', '.'])
                        SA.append(['>', '<', '.'])
                    elif dom == '^':
                        SA.append(['^', '.', 'M'])
                        SA.append(['^', '.', 'v'])
                    elif dom == 'M':
                        SA.append(['M', '<', '.'])
                        SA.append(['M', '.', 'v'])
                        SA.append(['M', 'M', '.'])
                        SA.append(['M', '.', 'M'])

                cell_constraint.append(
                    TableConstraint("LD:{},{}to{},{}to{},{}".format(i,j,i,j-1,i+1,j), 
                                    scope, SA))
                
            if "right" in cur_dir and "up" in cur_dir:
                scope = [cur_var, var_dict[str(i)+','+str(j+1)], var_dict[str(i-1)+','+str(j)]]
                SA = list()
                for dom in cur_var.domain():
                    # for dom2 in var_dict[str(i)+','+str(j+1)].domain():
                    #     if dom2 in rules[dom]['right']:
                    #         for dom3 in var_dict[str(i-1)+','+str(j)].domain():
                    #             if dom3 in rules[dom]['up'] and dom3 in rules[dom2]['up-left']:
                    #                 SA.append([dom, dom2, dom3])

                    if dom == '.':
                        for up in ['S', '<', '>', 'v', 'M']:
                            SA.append(['.', '.', up])
                        for right in ['S', '<', '^', 'v', 'M']:
                            SA.append(['.', right, '.'])
                        SA.append(['.', '.', '.'])
                    elif dom in ['S', '>', '^']:
                        SA.append([dom, '.', '.'])
                    elif dom == '<':
                        SA.append(['<', 'M', '.'])
                        SA.append(['<', '>', '.'])
                    elif dom == 'v':
                        SA.append(['v', '.', 'M'])
                        SA.append(['v', '.', '^'])
                    elif dom == 'M':
                        SA.append(['M', '>', '.'])
                        SA.append(['M', '.', '^'])
                        SA.append(['M', 'M', '.'])
                        SA.append(['M', '.', 'M'])
                cell_constraint.append(
                    TableConstraint("RU:{},{}to{},{}to{},{}".format(i,j,i,j+1,i-1,j), 
                                    scope, SA))
            
            if "right" in cur_dir and "down" in cur_dir:
                scope = [cur_var, var_dict[str(i)+','+str(j+1)], var_dict[str(i+1)+','+str(j)]]
                SA = list()
                for dom in cur_var.domain():
                    # for dom2 in var_dict[str(i)+','+str(j+1)].domain():
                    #     if dom2 in rules[dom]['right']:
                    #         for dom3 in var_dict[str(i+1)+','+str(j)].domain():
                    #             if dom3 in rules[dom]['down'] and dom3 in rules[dom2]['down-left']:
                    #                 SA.append([dom, dom2, dom3])

                    if dom == '.':
                        for down in ['S', '<', '>', '^', 'M']:
                            SA.append(['.', '.', down])
                        for right in ['S', '<', '^', 'v', 'M']:
                            SA.append(['.', right, '.'])
                        SA.append(['.', '.', '.'])
                    elif dom in ['S', '>', 'v']:
                        SA.append([dom, '.', '.'])
                    elif dom == '<':
                        SA.append(['<', 'M', '.'])
                        SA.append(['<', '>', '.'])
                    elif dom == '^':
                        SA.append(['^', '.', 'M'])
                        SA.append(['^', '.', 'v'])
                    elif dom == 'M':
                        SA.append(['M', '>', '.'])
                        SA.append(['M', '.', 'v'])
                        SA.append(['M', 'M', '.'])
                        SA.append(['M', '.', 'M'])
                cell_constraint.append(
                    TableConstraint("RD:{},{}to{},{}to{},{}".format(i,j,i,j+1,i+1,j), 
                                    scope, SA))                    
                        
    return cell_constraint


def board_write(csp):
    board = list()
    for i in range(BOARD_HEIGHT):
        board.append(['0' for x in range(BOARD_WIDTH)])


    # print(board)

    for x in csp._variables:
        if x._value is not None:
            board[int(x._name[1])][int(x._name[2])]= x._value


    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            print(board[i][j], end=' ')
        print()

def board_out(csp):
    board = list()
    for i in range(BOARD_HEIGHT):
        board.append(['0' for x in range(BOARD_WIDTH)])


    # print(board)

    for x in csp._variables:
        if x._value is not None:
            board[int(x._name[1])][int(x._name[2])]= x._value

    return board






def check_ship(csp):

    ship_count = {
    '1': 0,
    '2': 0,
    '3': 0,
    '4': 0,
    }

    board = list()
    for i in range(BOARD_HEIGHT):
        board.append(['0' for x in range(BOARD_WIDTH)])


    # print(board)

    for x in csp._variables:
        if x._value is None:
            return False
        board[int(x._name[1])][int(x._name[2])]= x._value

    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            p = board[i][j]
            if p == 'S':
                ship_count['1'] += 1
            elif p == '<':
                if j+1 < BOARD_WIDTH:
                    if board[i][j+1] == '>':
                        ship_count['2'] += 1
                    elif board[i][j+1] == 'M':
                        if j+2 < BOARD_WIDTH:
                            if board[i][j+2] == '>':
                                ship_count['3'] += 1
                            elif board[i][j+2] == 'M':
                                if j+3 < BOARD_WIDTH:
                                    if board[i][j+3] == '>':
                                        ship_count['4'] += 1
                #                     else:
                #                         print("Something terrible has happened!")
                #                 else:
                #                     print("Something terrible has happened!")
                #             else:
                #                 print("Something terrible has happened!")
                #         else:
                #             print("Something terrible has happened!")
                #     else:
                #         print("Something terrible has happened!")
                # else:
                #     print("Something terrible has happened!")
            elif p == '^':
                if i+1 < BOARD_HEIGHT:
                    if board[i+1][j] == 'v':
                        ship_count['2'] += 1
                    elif board[i+1][j] == 'M':
                        if i+2 < BOARD_HEIGHT:
                            if board[i+2][j] == 'v':
                                ship_count['3'] += 1
                            elif board[i+2][j] == 'M':
                                if i+3 < BOARD_HEIGHT:
                                    if board[i+3][j] == 'v':
                                        ship_count['4'] += 1
                #                     else:
                #                         print("Something terrible has happened!")
                #                 else:
                #                     print("Something terrible has happened!")
                #             else:
                #                 print("Something terrible has happened!")
                #         else:
                #             print("Something terrible has happened!")
                #     else:
                #         print("Something terrible has happened!")
                # else:
                #     print("Something terrible has happened!")
                
                






    for x in ship_count.keys():
        if ship_count[x] != SHIP_CONSTRAINT[x]:

            
            return False
    return True

                            

def back_ac3(csp, unassigned_vars):
    if unassigned_vars == []:
        
        if check_ship(csp):
            return copy.deepcopy(csp)
        else:
            return None

    var = unassigned_vars.pop()

    for value in var.curDomain():
        var.setValue(value)
        if ac3_loop(csp, csp.constraintsOf(var), var, value):
            sol = back_ac3(csp, unassigned_vars)
            if sol != None:
                return sol
        Variable.restoreValues(var, value)
    var.setValue(None)
    unassigned_vars.append(var)
    return None


    

def ac3_loop(csp, constraints, assignedvar, assignedval):
    while constraints != []:
        constraint = constraints.pop()
        for var in constraint.scope():
            for val in var.curDomain():
                if not constraint.hasSupport(var, val):
                    
                    var.pruneValue(val, assignedvar, assignedval)

                    if var.curDomainSize() == 0:
                        return False
                    # Add arcs
                    for recheck in csp.constraintsOf(var):
                        if recheck != constraint and not recheck in constraints:
                            constraints.append(recheck)

    return True



def actual(i,j, dom):
    p = [['<','>', '.', '.', '.', '.'],
        ['.', '.', '.', '.', 'S', '.'],
        ['.', '^', '.', '.', '.', '.'],
        ['.', 'M', '.', '.', '.', 'S'],
        ['.', 'v', '.', '^', '.', '.'],
        ['.', '.', '.', 'v', '.', 'S']]

    if p[i][j] not in dom:
        # print("error")
        return False
    return True
            

def output_to_file(filename, solution):
    """
    Output the solution to a given file.

    :param filename: The name of the given file.
    :type filename: str
    :param solution: The solution path.
    :type solution: list
    """
    output_file = open(filename, "w")
    for line in solution:
        for c in line:
            output_file.write(c)
        output_file.write("\n")

    
    output_file.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    args = parser.parse_args()

    global Global_Board
    Global_Board = dict()
    s = time.time()

    csp, Global_Board, var_list, con_list, num_ships = startup(args.inputfile)

    global SHIP_CONSTRAINT
    SHIP_CONSTRAINT = {
    '1': int(num_ships[0]),
    '2': int(num_ships[1]),
    '3': int(num_ships[2]),
    '4': int(num_ships[3]),
    }
    
    # global sol
    # sol = CSP
    
    # print("num_ships: ", num_ships)
    # print("length of var_list: ", len(var_list))
    sol = back_ac3(csp, csp.variables())
    b = board_out(sol)
    output_to_file(args.outputfile, b)
    # board = list()
    # for i in range(BOARD_HEIGHT):
    #     board.append([])
    #     for j in range(BOARD_WIDTH):
    #         board[i].append('.')

    # for x in csp._variables:
    #     board[int(x[1])][int(x[2])] = x._value()

    # print("board: \n", board)



    # print("var_list: ", var_list)
    # print("con_list: ", con_list)

    # for i in range(BOARD_HEIGHT):
    #     for j in range(BOARD_WIDTH):
    #         print(Global_Board[str(i)+','+str(j)]._name, Global_Board[str(i)+','+str(j)]._dom, end='--')
    #         print("\n")
    #         for k in csp.constraintsOf(Global_Board[str(i)+','+str(j)]):
    #             print(k._name, end='\n')
    #             if k._name[0] == 'T':
    #                 print('   ', k.satAssignments)
    #         input()
    #         # print(Global_Board[str(i)+','+str(j)]._name, Global_Board[str(i)+','+str(j)]._dom, end='--')
    #     print()
    # print("Global_Board: ", Global_Board)


    # print(cal_rules())

    f = time.time()
    print(f-s)



    # sys.stdout = open(args.outputfile, 'w')
    # sys.stdout = sys.__stdout__