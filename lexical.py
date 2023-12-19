import ply.lex as lex

# Token types
tokens = [
    'COMMENT',
    'REGISTER',
    'LOAD_ADDRESS',
    'MOVE',
    'JUMPLINK',
    'LOAD_IMMEDIATE',
    'NEWLINE',
    'SYSCALL',
    'JUMP',
    'WHITESPACE',
    'NAME',
    'NUMBER',
    'LPAREN',
    'RPAREN',
    'COLON',
    'COMMA',
    'DASH'
]

# Token definitions
t_COMMENT = r'\#.*'
t_REGISTER = r'\$[a-zA-Z0-9]+'
t_NEWLINE = r'\n+'
t_WHITESPACE = r'[ \t]+'

# New token definitions for symbols
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r':'
t_COMMA = r','
t_DASH = r'-'

def t_SYSCALL(t):
    r'syscall'
    return t

def t_JUMP(t):
    r'j[ \t]+[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_LOAD_ADDRESS(t):
    r'la'
    return t

def t_MOVE(t):
    r'move'
    return t

def t_JUMPLINK(t):
    r'jal'
    return t

def t_LOAD_IMMEDIATE(t):
    r'li'
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Add identifier information to the symbol table
    t.lexer.symbol_table[t.value] = {'type': 'identifier', 'line': t.lexer.lineno}
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# MIPS code
mips_code = """
main:
    # Prompt user for input
    li $v0, 4
    la $a0, prompt
    syscall

    # Read user input
    li $v0, 5
    syscall
    move $s0, $v0  # Save the user input in $s0

    # Calculate factorial recursively
    move $a0, $s0
    jal factorial  # Jump and link to factorial function
    move $s1, $v0  # Save the result in $s1

    # Display the result
    li $v0, 4
    la $a0, resultMsg
    syscall

    li $v0, 1
    move $a0, $s1
    syscall

    # Exit program
    li $v0, 10
    syscall

# Recursive factorial function
factorial:
    # Function prologue
    addi $sp, $sp, -8  # Adjust stack pointer
    sw $ra, 4($sp)     # Save return address
    sw $a0, 0($sp)     # Save argument

    # Base case: factorial(0) = 1
    beq $a0, $zero, factorial_base_case
    # Recursive case: factorial(n) = n * factorial(n-1)
    addi $a0, $a0, -1   # n-1
    jal factorial       # Recursive call
    lw $a0, 0($sp)      # Restore original argument
    lw $ra, 4($sp)      # Restore return address
    mul $v0, $a0, $v0   # result = n * factorial(n-1)
    j factorial_done

factorial_base_case:
    li $v0, 1  # factorial(0) = 1
    j factorial_done

factorial_done:
    # Function epilogue
    lw $ra, 4($sp)      # Restore return address
    lw $a0, 0($sp)      # Restore argument
    addi $sp, $sp, 8    # Restore stack pointer
    jr $ra              # Jump back to the calling function
"""

# Build the lexer
lexer = lex.lex()

# Initialize the symbol table
lexer.symbol_table = {}

# Pass the MIPS code through the lexer
lexer.input(mips_code)

# Tokenize the input and store tokens and lexemes in a dictionary
token_dict = {token: [] for token in tokens}
while True:
    tok = lexer.token()
    if not tok:
        break  # No more input
    token_dict[tok.type].append(tok.value)

# Print the table header
print("{:<15}{}".format("Token", "Unique Lexemes"))
print("-" * 25)

# Print the table rows
for token, lexemes in token_dict.items():
    # Ignore COMMENT and NEWLINE tokens
    if token not in {'COMMENT', 'NEWLINE', 'WHITESPACE'}:
        unique_lexemes = set(map(str, lexemes))
        print("{:<15}{}".format(token, "\t".join(unique_lexemes)))

# Print the symbol table
print("\nSymbol Table:")
print("{:<15}{}".format("Identifier", "Information"))
print("-" * 25)
for identifier, info in lexer.symbol_table.items():
    print("{:<15}{}".format(identifier, info))
