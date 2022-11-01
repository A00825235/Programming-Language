from copy import deepcopy

class Interpreter:
    def __init__(self):
        self.line = dict()
        self.stack = dict()
        self.stackExp1 = [[0]*100 for i in range(100)]
        self.stackExp = [[0]*100 for i in range(100)]
        self.count = 0
        self.stackPos = 0
        self.variables = dict()
        self.ignoreLines = []
        self.debug = False

    def addExp(self, term):
        self.stackExp1[self.stackPos][self.count] = term
        self.count += 1
        return self.stackExp1[self.stackPos]
    
    def addVariable(self, key, pos):
        self.stackExp1[self.stackPos][self.count] = '#'
        self.stackExp[pos] = self.stackExp1[self.stackPos]
        self.line[pos] = 'variable', key
        self.stackPos += 1
        self.count = 0
    
    def newExp(self, pos):
        self.stackExp1[self.stackPos][self.count] = '#'
        self.stackExp[pos] = self.stackExp1[self.stackPos]
        self.line[pos] = 'exp'
        self.stackPos += 1
        self.count = 0
        return self.stackExp[pos]

    def addFor(self, var, range, pos, posBegin, posEnd):
        self.line[pos] = 'for', var, range, posBegin, posEnd

    def addPrint(self, pos):
        self.line[pos] = 'print', pos

    def addBreak(self, pos):
        self.line[pos] = 'break', pos

    def addPrintVariable(self, id, pos):
        self.line[pos] = 'print id', id

    def addIfStatementExp(self, sign, pos, posBegin, posEnd):
        self.line[pos] = 'if', sign[0], posBegin + 1, posEnd - 1, sign[1]

    def addIfElseStatementExp(self, sign, pos, ifPosBegin, ifPosEnd, elsePosBegin, elsePosEnd):
        self.line[pos] = 'if else', sign[0], ifPosBegin + 1, ifPosEnd - 1, sign[1], elsePosBegin, elsePosEnd

    def addIfStatement(self, boolean, posBegin, posEnd):
        if(not boolean):
            self.ignoreLines += range(posBegin, posEnd)

    def addIfElseStatement(self, boolean, ifPosBegin, ifPosEnd, elsePosBegin, elsePosEnd):
        if(not boolean):
            self.ignoreLines += range(ifPosBegin, ifPosEnd)
        else:
            self.ignoreLines += range(elsePosBegin, elsePosEnd)

    def addWhileLoop(self, sign, pos, posBegin, posEnd):
        self.line[pos] = 'while', sign[0], posBegin + 1, posEnd - 1, sign[1]

    def addInput(self, key, pos):
        self.line[pos] = 'input', key

    def runFor(self, pc):
        key = self.line[pc][1]
        if not (key in self.variables):
            self.variables[key] = 1

        previousValue = self.variables[key]
        posBegin = self.line[pc][3]
        posEnd = self.line[pc][4]
        range = self.line[pc][2]
        pc = posBegin
        while self.variables[key] <= range:
            pc += 1
            if pc in self.line and not self.ignoreLines.__contains__(pc):
                tag = self.line[pc][0]
                if(tag == 'for'):
                    self.runFor(pc)
                    pc = self.line[pc][4]
                elif(tag == 'while'):
                    self.executeWhile(pc, self.line[pc][2], self.line[pc][3])
                    pc = self.line[pc][3]
                elif(tag == 'if'):
                    self.executeIf(pc)
                elif(tag == 'if else'):
                    self.executeIfElse(pc)
                elif(tag == 'print'):
                    print(calculateExp(self.stackExp, pc, self.variables))
                elif(tag == 'print id'):
                    print(self.variables[self.line[pc][1]])
                elif(tag == 'input'):
                    self.variables[self.line[pc][1]] = int(input('Enter value for ' + self.line[pc][1] + ': '))
                elif(tag == 'variable'):
                    self.variables[self.line[pc][1]] = calculateExp(self.stackExp, pc, self.variables)    
                elif(tag == 'break'):
                    pc = posEnd
                    break
            if pc == posEnd:
                self.variables[key] += 1
                pc = posBegin
        self.variables[key] = previousValue
    
    def executeIfElse(self, pc):
        value1 = self.line[pc][4][0]
        value2 = self.line[pc][4][1]
        if not isinstance(value1, int):
            value1 = self.variables[self.line[pc][4][0]]
        if not isinstance(value2, int):
            value2 = self.variables[self.line[pc][4][1]]
        if not Logic.bool(self.line[pc][1], value1, value2):
            z = self.line[pc][2]
            while z <= self.line[pc][3]:
                self.ignoreLines.append(z)
                z += 1
            z = self.line[pc][5]
            while z <= self.line[pc][6]:
                while self.ignoreLines.__contains__(z):
                    self.ignoreLines.remove(z)
                z += 1
        else:
            z = self.line[pc][5]
            while z <= self.line[pc][6]:
                self.ignoreLines.append(z)
                z += 1
            z = self.line[pc][2]
            while z <= self.line[pc][3]:
                while self.ignoreLines.__contains__(z):
                    self.ignoreLines.remove(z)
                z += 1
    
    def executeIf(self, pc):
        value1 = self.line[pc][4][0]
        value2 = self.line[pc][4][1]
        if not isinstance(value1, int):
            value1 = self.variables[self.line[pc][4][0]]
        if not isinstance(value2, int):
            value2 = self.variables[self.line[pc][4][1]]
        if not Logic.bool(self.line[pc][1], value1, value2):
            z = self.line[pc][2]
            while z <= self.line[pc][3]:
                self.ignoreLines.append(z)
                z += 1
        else:
            z = self.line[pc][2]
            while z <= self.line[pc][3]:
                while self.ignoreLines.__contains__(z):
                    self.ignoreLines.remove(z)
                z += 1

    def executeWhile(self, pc, posBegin, posEnd):
        pc += 1
        value1 = self.line[posBegin - 1][4][0]
        value2 = self.line[posBegin - 1][4][1]
        if not isinstance(value1, int):
            value1 = self.variables[self.line[posBegin - 1][4][0]]
        if not isinstance(value2, int):
            value2 = self.variables[self.line[posBegin - 1][4][1]]
        if not Logic.bool(self.line[posBegin - 1][1], value1, value2):
            pc = posEnd
            return
        
        while Logic.bool(self.line[posBegin - 1][1], value1, value2):
            value1 = self.line[posBegin - 1][4][0]
            value2 = self.line[posBegin - 1][4][1]
            if not isinstance(value1, int):
                value1 = self.variables[self.line[posBegin - 1][4][0]]
            if not isinstance(value2, int):
                value2 = self.variables[self.line[posBegin - 1][4][1]]
            if not Logic.bool(self.line[posBegin - 1][1], value1, value2):
                break
            if pc in self.line and not self.ignoreLines.__contains__(pc):
                tag = self.line[pc][0]
                if(tag == 'for'):
                    self.runFor(pc)
                    pc = self.line[pc][4]
                elif(tag == 'while'):
                    self.executeWhile(pc, self.line[pc][2], self.line[pc][3])
                    pc = self.line[pc][3]
                elif(tag == 'print'):
                    print(calculateExp(self.stackExp, pc, self.variables))
                elif(tag == 'if'):
                    self.executeIf(pc)
                elif(tag == 'if else'):
                    self.executeIfElse(pc)
                elif(tag == 'print id'):
                    print(self.variables[self.line[pc][1]])
                elif(tag == 'input'):
                    self.variables[self.line[pc][1]] = int(input('Enter value for ' + self.line[pc][1] + ': '))
                elif(tag == 'variable'):
                    self.variables[self.line[pc][1]] = calculateExp(self.stackExp, pc, self.variables)
                    if self.debug:
                        print('Line #', pc, ' data:', self.variables[self.line[pc][1]])
                elif(tag == 'break'):
                    pc = posEnd
                    break
            pc += 1
            if pc > posEnd:
                pc = posBegin
        pc = posBegin - 1
    
    def run(self, end):
        pc = 0
        while pc < end:
            if pc in self.line and not self.ignoreLines.__contains__(pc):
                tag = self.line[pc][0]
                if(tag == 'for'):
                    self.runFor(pc)
                    pc = self.line[pc][4]
                elif(tag == 'while'):
                    self.executeWhile(pc, self.line[pc][2], self.line[pc][3])
                    pc = self.line[pc][3]
                elif(tag == 'print'):
                    print(calculateExp(self.stackExp, pc, self.variables))
                elif(tag == 'if'):
                    self.executeIf(pc)
                elif(tag == 'if else'):
                    self.executeIfElse(pc)
                elif(tag == 'print id'):
                    print(self.variables[self.line[pc][1]])
                elif(tag == 'input'):
                    self.variables[self.line[pc][1]] = int(input('Enter value for ' + self.line[pc][1] + ': '))
                elif(tag == 'variable'):
                    self.variables[self.line[pc][1]] = calculateExp(self.stackExp, pc, self.variables)
                    if self.debug:
                        print('Line #', pc, ' data:', self.variables[self.line[pc][1]])
            pc += 1
    
def calculateExp(s, pos, variables):
    count = 0
    total = 0
    curr1 = ''
    curr2 = ''
    check = 0
    pos1 = 0
    pos2 = 0

    stack = deepcopy(s)

    while True:
        value = stack[pos][count]
        if value == '#':
            if isinstance(curr2, int):
                total += curr2
            else:
                total += curr1
            break
        if value == '?':
            total = total
        elif value == '%':
            if isinstance(curr2, int):
                stack[pos][pos1] = curr1 % curr2
                stack[pos][pos2] = '?'
                stack[pos][count] = '?'
                curr1 = '?'
                curr2 = '?'
                check = 0
                count = -1
            else:
                total %= curr1
        elif value == '+':
            if isinstance(curr2, int):
                stack[pos][pos1] = curr1 + curr2
                stack[pos][pos2] = '?'
                stack[pos][count] = '?'
                curr1 = '?'
                curr2 = '?'
                check = 0
                count = -1
            else:
                total += curr1
        elif value == '-':
            if isinstance(curr2, int):
                stack[pos][pos1] = curr1 - curr2
                stack[pos][pos2] = '?'
                stack[pos][count] = '?'
                curr1 = '?'
                curr2 = '?'
                check = 0
                count = -1
            else:
                total -= curr1
        elif value == '*':
            if isinstance(curr2, int):
                stack[pos][pos1] = curr1 * curr2
                stack[pos][pos2] = '?'
                stack[pos][count] = '?'
                curr1 = '?'
                curr2 = '?'
                check = 0
                count = -1
            else:
                total *= curr1
        elif value == '/':
            if isinstance(curr2, int):
                stack[pos][pos1] = int(curr1 / curr2)
                stack[pos][pos2] = '?'
                stack[pos][count] = '?'
                curr1 = '?'
                curr2 = '?'
                check = 0
                count = -1
            else:
                total /= curr1
        else:
            if isinstance(value, int):
                if check % 2 == 0:
                    curr1 = value
                    pos1 = count
                    check += 1
                else:
                    curr2 = value
                    pos2 = count
                    check += 1
            else:
                if check % 2 == 0:
                    if isinstance(value, list):
                        curr1 = value[0]
                    elif isinstance(value, int):
                        curr1 = value
                    else:
                        curr1 = variables[value]
                    pos1 = count
                    check += 1
                else:
                    if isinstance(value, list):
                        curr2 = value[0]
                    elif isinstance(value, int):
                        curr2 = value
                    else:
                        curr2 = variables[value]
                    pos2 = count
                    check += 1
        count += 1
    return total


class Logic:
    def bool(sign, value1, value2):
        if sign == '&':
            return value1 and value2
        elif sign == '|':
            return value1 or value2
        elif sign == '>':
            return value1 > value2
        elif sign == '<':
            return value1 < value2
        elif sign == 'LEQ':
            return value1 >= value2
        elif sign == 'GEQ':
            return value1 <= value2
        elif sign == 'EQ':
            return value1 == value2
        elif sign == 'NEQ':
            return value1 != value2