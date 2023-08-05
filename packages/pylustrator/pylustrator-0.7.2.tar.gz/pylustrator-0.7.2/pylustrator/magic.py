import theano.tensor as T
import theano
import numpy as np

nodes = []
compiled_functions = {}
iteration = -1
name_results = 0

def getLetter(index):
    name = chr(ord("A") + index)
    return name

def getNewName():
    global name_index
    name = chr(ord("A") + name_index)
    name_index += 1
    return name

def getResultsName():
    global name_results
    name = "res%d_%d" % (iteration, name_results)
    name_results += 1
    return name

def init_loop():
    global iteration, name_results
    iteration = -1
    name_results = 0

def pre_loop():
    global nodes, iteration, name_results
    for node in nodes:
        node.loop_started = True
    iteration += 1
    #print("pre_loop", iteration)
    name_results = 1

class connection:
    loop_started = False
    loop_result = False
    a = None

    def __init__(self, name, func, *args):
        global nodes
        self.name = name
        self.vars = args
        self.func = func
        self.t = self.func(*self.vars)
        self.compiled = None
        self.inputs = self.calculateInputs()
        nodes.append(self)

    def data(self):
        return self.func(*self.vars)

    def applyFunction(self, name, func, *args):
        global iteration
        if self.loop_started is True:
            #print(iteration, self.printLine2())
            self.eval()
            self.name = getResultsName()
            self.loop_started = False

        return connection(name, func, *args)

    def __add__(self, other):
        if not isinstance(other, connection):
            other = node(other)
        return self.applyFunction("+", lambda a, b: a.t+b.t, self, other)

    def __sub__(self, other):
        return self.applyFunction("-", lambda a, b: a.t-b.t, self, other)

    def __mul__(self, other):
        return self.applyFunction("*", lambda a, b: a.t*b.t, self, other)

    def __getitem__(self, item):
        return self.applyFunction("[", lambda a, b: a.t[b], self, item)

    def calculateInputs(self):
        inputs = []
        for var in self.vars:
            new_inputs = var.getInputs()
            for var2 in new_inputs:
                if var2 not in inputs:
                    inputs.extend(var2.getInputs())
        return inputs

    def getInputs(self):
        return self.inputs

    def eval(self, name=None):
        global compiled_functions
        if self.a is not None:
            return
        if self.printLine() in compiled_functions:
            self.compiled = compiled_functions[self.printLine()]
        inputs = self.getInputs()
        if self.compiled is None:
            input_tensors = [i.t for i in inputs]
            #self.compiled = theano.function(input_tensors, self.t, allow_input_downcast=True)
            self.compiled = theano.function([], self.t, allow_input_downcast=True)
            print("Compile", self.printLine())
            #compiled_functions[self.printLine()] = self.compiled
        #print(iteration, "eval", self.printLine2(), *[i.a for i in inputs])
        #data = self.compiled(*[i.a for i in inputs])
        data = self.compiled()
        self.setValue(data)
        #self.a = data
        #self.t = T.TensorType(data.dtype, [False]*len(data.shape))(None)
        #self.inputs = [self]
        self.vars = []
        if name is None:
            self.name = getNewName()

    def __str__(self):
        self.eval()
        return str(self.a)

    def printLayer(self, parent, depth=0):
        if depth == 0:
            return parent.vars
        else:
            liste = []
            for var in parent.vars:
                liste.extend(self.printLayer(var, depth-1))
            return liste

    def getName(self, node):
        if len(node.vars) == 0:
            name = node.name
            if name not in self.translationTable:
                self.translationTable[name] = getLetter(self.translationIndex)
                self.translationIndex += 1
            name = self.translationTable[name]
            return name
        return "("+self.getName(node.vars[0])+" "+node.name+" "+self.getName(node.vars[1])+")"

    def printLine(self):
        self.translationTable = {}
        self.translationIndex = 0
        string = self.getName(self)
        return string

    def printLine2(self):
        if len(self.vars) == 0:
            return self.name
        return "("+self.vars[0].printLine2()+" "+self.name+" "+self.vars[1].printLine2()+")"

    def printLine(self):
        self.translationTable = {}
        self.translationIndex = 0
        string = self.getName(self)
        return string

    def printTree(self):
        layer = []
        depth = 0
        print(0, [self.name])
        while True:
            liste = self.printLayer(self, depth=depth)
            if len(liste) == 0:
                break
            print(depth+1, [l.name for l in liste])
            depth += 1

    def setValue(self, a):
        global no_wrap
        no_wrap = True
        self.a = a
        if isinstance(a, np.ndarray):
            # self.t = T.TensorType(T.config.floatX, [False]*len(a.shape))(None)
            # self.t = T.TensorType(a.dtype, [False] * len(a.shape))(None)

            self.t = theano.shared(a)
        elif isinstance(a, int):
            self.t = T.scalar("int64")
        else:
            self.t = T.scalar()
        no_wrap = False

        self.vars = []

name_index = 0
name_results = 0
class node(connection):
    def __init__(self, a):
        self.name = getNewName()
        self.setValue(a)



    def data(self):
        return self.a

    def getInputs(self):
        return [self]

no_wrap = False
def wrap(func):
    def array(*args, **kwargs):
        global no_wrap
        a = func(*args, **kwargs)
        if no_wrap:
            return a
        return node(a)
    return array

def trange(*args):
    init_loop()
    iterator = range(*args)
    for i in iterator:
        pre_loop()
        yield i


import time

for i in range(2):
    np.array = wrap(np.array)
    t0 = time.time()
    #const = np.array(np.arange(1000000))
    n = 1000000
    #n = 3
    N = 10
    #N = 3
    a = np.array(np.arange(n))#+5
    b = np.array(np.arange(n))#+5
    c = b
    print(c)
    for i in trange(N):
        c = c*a+a#+i
    #print(c.printLine())
    print(str(c)[:100])
    print(time.time()-t0)
    #print(compiled_functions)
    np.array = wrap(np.array)
    break

