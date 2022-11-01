# Author: Jesus Garcia
# ID: A00825235
# Date: 11/30/2021

import ply.lex as lex
import ply.yacc as yacc
import sys
import os
import utility

interpreter = utility.Interpreter()

reserved = {
    'if' : 'IF',
    'main' : 'MAIN',
    'let' : 'LET',
    'function' : 'FUNCTION',
    'while' : 'WHILE',
    'for' : 'FOR',
    'in' : 'IN',
    'input' : 'INPUT',
    'break' : 'BREAK',
    'else' : 'ELSE',
    'print' : 'PRINT',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'GEQ' : 'GEQ',
    'LEQ' : 'LEQ',
    'NEQ' : 'NEQ',
    'EQ' : 'EQ'
}

tokens = ['INTEGER', 'FLOAT', 'COMMENT', 'ID'] + list(reserved.values())

literals = ['+','-','*','/','(',')','[',']','{','}',';','=','<','>',"'", '|', '&', ',', '%']

t_ignore  = ' \t'


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)    
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT(t):
    r'//.+//'
    pass

def t_ID(t):
    r'[a-zA-Z]+'
    t.type = reserved.get(t.value,'ID')
    return t

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def p_INIT(p):
    '''
	INIT : MAIN '(' ')' '{' S '}'
	'''
    interpreter.run(p.__dict__.get('slice')[6].lineno)
    print("\tSuccesful Execution.")

def p_S(p): 
    '''
    S : S S
    S : 
    ''' 

def p_S_if_exp(p):
    '''
	S : IF '(' LOGIC ')' '{' S '}'
	'''
    interpreter.addIfStatementExp(p[3], p.__dict__.get('slice')[1].lineno, p.__dict__.get('slice')[5].lineno, p.__dict__.get('slice')[7].lineno)

def p_S_if_else_exp(p):
    '''
	S : IF '(' LOGIC ')' '{' S '}' ELSE '{' S '}'
	'''
    interpreter.addIfElseStatementExp(p[3], p.__dict__.get('slice')[1].lineno, p.__dict__.get('slice')[5].lineno, p.__dict__.get('slice')[7].lineno, p.__dict__.get('slice')[8].lineno, p.__dict__.get('slice')[11].lineno)

def p_S_exp(p):
    '''
	S : ID '=' EXP
	'''
    interpreter.addVariable(p[1], p.__dict__.get('slice')[1].lineno)

def p_S_print(p):
    '''
	S : PRINT '(' EXP ')'
	'''
    interpreter.newExp(p.__dict__.get('slice')[1].lineno)
    interpreter.addPrint(p.__dict__.get('slice')[1].lineno)
    
def p_S_print_id(p):
    '''
    S : PRINT '(' ID ')'
	'''
    interpreter.addPrintVariable(p[3], p.__dict__.get('slice')[1].lineno)

def p_S_input(p):
    '''
    S : ID '=' INPUT '(' ')'
	'''
    interpreter.newExp(p.__dict__.get('slice')[1].lineno)
    interpreter.addInput(p[1], p.__dict__.get('slice')[1].lineno)

def p_S_break(p):
    '''
    S : BREAK
	'''
    interpreter.addBreak(p.__dict__.get('slice')[1].lineno)

def p_S_while(p):
    '''
	S : WHILE '(' LOGIC ')' '{' S '}'
	'''
    interpreter.addWhileLoop(p[3], p.__dict__.get('slice')[1].lineno, p.__dict__.get('slice')[5].lineno, p.__dict__.get('slice')[7].lineno)
    
def p_S_for(p):
    '''
	S : FOR '(' ID IN INTEGER ')' '{' S '}'
	'''
    interpreter.addFor(p[3], p[5], p.__dict__.get('slice')[1].lineno, p.__dict__.get('slice')[7].lineno, p.__dict__.get('slice')[9].lineno)

def p_LOGIC_symbol(p):
    '''
    SYMBOL : '>'
    SYMBOL : '<' 
    SYMBOL : LEQ 
    SYMBOL : GEQ 
    SYMBOL : NEQ 
    SYMBOL : EQ 
	'''
    p[0] = p[1]

def p_LOGIC(p):
    '''
    LOGIC : EXP SYMBOL EXP
	'''
    p[0] = [p[2], p[1]]
    interpreter.newExp(p.lexer.lineno)

def p_EXP(p):
    '''
    EXP : EXP '%' TERM
	EXP : EXP '+' TERM
	EXP : EXP '-' TERM
    EXP : TERM
    TERM : TERM '*' FACT
	TERM : TERM '/' FACT
    TERM : FACT
	'''
    if len(p) > 2:
        p[0] = interpreter.addExp(p[2])
    else:
        p[0] = p[1]
    
def p_FACT(p):
    '''
	FACT : INTEGER
    FACT : FLOAT
	'''
    p[0] = interpreter.addExp(p[1])

def p_FACT_paren(p):
    '''
    FACT : '(' EXP ')'
	'''
    p[0] = interpreter.addExp(p[2])

def p_FACT_id(p):
    '''
	FACT : ID
	'''
    p[0] = interpreter.addExp(p[1])

def p_error(p):
    print(p)
    print("\tERROR")

if __name__ == '__main__':
    try:
        filename = os.path.dirname(os.path.abspath(__file__)) + "\example.txt"
        file = open(filename, "r")
    except IOError:
        print("An error occured opening the file...")
        sys.exit(0)
    parser = yacc.yacc()
    text = file.read()
    lexer = lex.lex()
    t = parser.parse(text, lexer=lexer)