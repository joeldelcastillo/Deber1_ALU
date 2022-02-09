#  logic.py
#
#  Copyright 2001 by Chris Meyers.
#
#  Define classes for Connector, Logic Circuit, Gate
#


class Connector:
    # Connectors are inputs and outputs. Only outputs should connect
    # to inputs. Be careful NOT to have circular references
    # As an output is changed it propagates the change to its connected inputs
    #


    def __init__(self, owner, name, activates=0, monitor=0):
        self.value = None
        self.owner = owner
        self.name = name
        self.monitor = monitor
        self.connects = []
        self.activates = activates   # If true change kicks evaluate function

    def connect(self, inputs):
        if not isinstance(inputs, list):
            inputs = [inputs]
        for input in inputs:
            self.connects.append(input)

    def set(self, value):
        if self.value == value:
            return      # Ignore if no change
        self.value = value
        if self.activates:
            self.owner.evaluate()
        if self.monitor:
            print("Connector {0}-{1} set to {2}".format(self.owner.name,
                                                        self.name,
                                                        self.value))
        for con in self.connects:
            con.set(value)


class LC:
    # Logic Circuits have names and an evaluation function defined in child
    # classes. They will also contain a set of inputs and outputs.
    def __init__(self, name):
        self.name = name

    def evaluate(self):
        return


class Not(LC):         # Inverter. Input A. Output B.
    def __init__(self, name):
        LC.__init__(self, name)
        self.A = Connector(self, 'A', activates=1)
        self.B = Connector(self, 'B')

    def evaluate(self):
        self.B.set(not self.A.value)


class Gate2(LC):         # two input gates. Inputs A and B. Output C.
    def __init__(self, name):
        LC.__init__(self, name)
        self.A = Connector(self, 'A', activates=1)
        self.B = Connector(self, 'B', activates=1)
        self.C = Connector(self, 'C')


class And(Gate2):       # two input AND Gate
    def __init__(self, name):
        Gate2.__init__(self, name)

    def evaluate(self):
        self.C.set(self.A.value and self.B.value)


class Or(Gate2):         # two input OR gate.
    def __init__(self, name):
        Gate2.__init__(self, name)

    def evaluate(self):
        self.C.set(self.A.value or self.B.value)


class Xor(Gate2):
    def __init__(self, name):
        Gate2.__init__(self, name)
        self.A1 = And("A1")  # See circuit drawing to follow connections
        self.A2 = And("A2")
        self.I1 = Not("I1")
        self.I2 = Not("I2")
        self.O1 = Or("O1")
        self.A.connect([self.A1.A, self.I2.A])
        self.B.connect([self.I1.A, self.A2.A])
        self.I1.B.connect([self.A1.B])
        self.I2.B.connect([self.A2.B])
        self.A1.C.connect([self.O1.A])
        self.A2.C.connect([self.O1.B])
        self.O1.C.connect([self.C])


class HalfAdder(LC):         # One bit adder, A,B in. Sum and Carry out
    def __init__(self, name):
        LC.__init__(self, name)
        self.A = Connector(self, 'A', 1)
        self.B = Connector(self, 'B', 1)
        self.S = Connector(self, 'S')
        self.C = Connector(self, 'C')
        self.X1 = Xor("X1")
        self.A1 = And("A1")
        self.A.connect([self.X1.A, self.A1.A])
        self.B.connect([self.X1.B, self.A1.B])
        self.X1.C.connect([self.S])
        self.A1.C.connect([self.C])


class FullAdder(LC):         # One bit adder, A,B,Cin in. Sum and Cout out
    def __init__(self, name):
        LC.__init__(self, name)
        self.A = Connector(self, 'A', 1, monitor=1)
        self.B = Connector(self, 'B', 1, monitor=1)
        self.Cin = Connector(self, 'Cin', 1, monitor=1)
        self.S = Connector(self, 'S', monitor=1)
        self.Cout = Connector(self, 'Cout', monitor=1)
        self.H1 = HalfAdder("H1")
        self.H2 = HalfAdder("H2")
        self.O1 = Or("O1")
        self.A.connect([self.H1.A])
        self.B.connect([self.H1.B])
        self.Cin.connect([self.H2.A])
        self.H1.S.connect([self.H2.B])
        self.H1.C.connect([self.O1.B])
        self.H2.C.connect([self.O1.A])
        self.H2.S.connect([self.S])
        self.O1.C.connect([self.Cout])


def bit(x, bit):
    return x[bit] == '1'


def addcarry(a, b):
    F0 = FullAdder("F0")
    F1 = FullAdder("F1")
    F0.Cout.connect(F1.Cin)
    F2 = FullAdder("F2")
    F1.Cout.connect(F2.Cin)
    F3 = FullAdder("F3")
    F2.Cout.connect(F3.Cin)
    F4 = FullAdder("F4")
    F3.Cout.connect(F4.Cin)
    F5 = FullAdder("F5")
    F4.Cout.connect(F5.Cin)
    F6 = FullAdder("F6")
    F5.Cout.connect(F6.Cin)
    F7 = FullAdder("F7")
    F6.Cout.connect(F7.Cin)

    F0.Cin.set(0)
    F0.A.set(bit(a, 7))
    F0.B.set(bit(b, 7))
    F1.A.set(bit(a, 6))
    F1.B.set(bit(b, 6))
    F2.A.set(bit(a, 5))
    F2.B.set(bit(b, 5))
    F3.A.set(bit(a, 4))
    F3.B.set(bit(b, 4))
    F4.A.set(bit(a, 3))
    F4.B.set(bit(b, 3))
    F5.A.set(bit(a, 2))
    F5.B.set(bit(b, 2))
    F6.A.set(bit(a, 1))
    F6.B.set(bit(b, 1))
    F7.A.set(bit(a, 0))
    F7.B.set(bit(b, 0))

    return [F7.Cout.value, F7.S.value, F6.S.value, F5.S.value,
            F4.S.value, F3.S.value, F2.S.value, F1.S.value, F0.S.value]


def increment(a, b):
    F0 = FullAdder(And("F0"))
    F1 = FullAdder(And("F1"))
    F0.Cout.connect(F1.Cin)
    F2 = FullAdder(And("F2"))
    F1.Cout.connect(F2.Cin)
    F3 = FullAdder(And("F3"))
    F2.Cout.connect(F3.Cin)
    F4 = FullAdder(And("F4"))
    F3.Cout.connect(F4.Cin)
    F5 = FullAdder(And("F5"))
    F4.Cout.connect(F5.Cin)
    F6 = FullAdder(And("F6"))
    F5.Cout.connect(F6.Cin)
    F7 = FullAdder(And("F7"))
    F6.Cout.connect(F7.Cin)

    F0.Cin.set(0)
    F0.A.set(bit(a, 7))
    F0.B.set(bit(b, 7))
    F0.evaluate()
    F1.A.set(bit(a, 6))
    F1.B.set(bit(b, 6))
    F1.evaluate()
    F2.A.set(bit(a, 5))
    F2.B.set(bit(b, 5))
    F2.evaluate()
    F3.A.set(bit(a, 4))
    F3.B.set(bit(b, 4))
    F3.evaluate()
    F4.A.set(bit(a, 3))
    F4.B.set(bit(b, 3))
    F4.evaluate()
    F5.A.set(bit(a, 2))
    F5.B.set(bit(b, 2))
    F5.evaluate()
    F6.A.set(bit(a, 1))
    F6.B.set(bit(b, 1))
    F6.evaluate()
    F7.A.set(bit(a, 0))
    F7.B.set(bit(b, 0))
    F7.evaluate()

    return [F7.Cout.value, F7.S.value, F6.S.value, F5.S.value,
            F4.S.value,F3.S.value,F2.S.value,F1.S.value,F0.S.value]



def complementOne(a):
    F0 = Not("F0")
    F1 = Not("F1")
    F3 = Not("F3")
    F2 = Not("F2")
    F4 = Not("F4")
    F5 = Not("F5")
    F6 = Not("F6")
    F7 = Not("F7")

    F0.A.set(bit(a, 7))
    F0.evaluate()
    F1.A.set(bit(a, 6))
    F1.evaluate()
    F2.A.set(bit(a, 5))
    F2.evaluate()
    F3.A.set(bit(a, 4))
    F3.evaluate()
    F4.A.set(bit(a, 3))
    F4.evaluate()
    F5.A.set(bit(a, 2))
    F5.evaluate()
    F6.A.set(bit(a, 1))
    F6.evaluate()
    F7.A.set(bit(a, 0))
    F7.evaluate()
    return [F7.B.value, F6.B.value, F5.B.value,
            F4.B.value, F3.B.value, F2.B.value, F1.B.value, F0.B.value]





def negateNumber(a):
    result = complementOne(a)
    b = []
    for j in result:
        if (j == False):
            i = 0
            b.append(i)
        else:
            i = 1
            b.append(i)
    number = "".join([str(_) for _ in b])

    return increment(number, "00000001")

def PassTrough(a):
    def toString(byte):
        s = ""
        for bit in byte:
            x = str(int(bit))
            s += x
        return s

    F0 = Not(Not("F0"))
    F1 = Not(Not("F1"))
    F3 = Not(Not("F3"))
    F2 = Not(Not("F2"))
    F4 = Not(Not("F4"))
    F5 = Not(Not("F5"))
    F6 = Not(Not("F6"))
    F7 = Not(Not("F7"))

    F0.A.set(bit(a, 7))
    F0.evaluate()
    F1.A.set(bit(a, 6))
    F1.evaluate()
    F2.A.set(bit(a, 5))
    F2.evaluate()
    F3.A.set(bit(a, 4))
    F3.evaluate()
    F4.A.set(bit(a, 3))
    F4.evaluate()
    F5.A.set(bit(a, 2))
    F5.evaluate()
    F6.A.set(bit(a, 1))
    F6.evaluate()
    F7.A.set(bit(a, 0))
    F7.evaluate()
    return toString([F7.B.value, F6.B.value, F5.B.value,
            F4.B.value, F3.B.value, F2.B.value, F1.B.value, F0.B.value])

def Substraction (a,b):
    def toString(byte):
        s = ""
        for bit in byte:
            x = str(int(bit))
            s += x
        return s

    b=toString(negateNumber(b))
    c=addcarry(a, b)
    return print(toString(c))


#Substraction('10010101','11000110')
#print(complementOne('11000110'))
#print(negateNumber('11000110'))
#print(PassTrough('11000110'))