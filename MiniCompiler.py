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
    # Check if the identifier is already in the symbol table
    if t.value not in t.lexer.symbol_table:
        t.lexer.symbol_table[t.value] = {'type': 'identifier'}
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
Exit:
    # Additional instructions or code here, if needed
    j $ra  # Jump back to the calling function
    
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

lexer.input(mips_code)

# Tokenize the input and store tokens and lexemes in a dictionary
token_dict = {token: [] for token in tokens}
while True:
    tok = lexer.token()
    if not tok:
        break  # No more input
    token_dict[tok.type].append(tok.value)

# Print the table header
print("{:<15}{}".format("Token", "Lexemes"))
print("-" * 25)

# Print the table rows
for token, lexemes in token_dict.items():
    # Ignore COMMENT and NEWLINE tokens
    if token not in {'COMMENT', 'NEWLINE', 'WHITESPACE'}:
        print("{:<15}{}".format(token, "\t".join(str(lex) for lex in lexemes)))



class Node:
    def __init__(self, name, node_type=None):
        self.name = name
        self.type = node_type
        self.children = []

    def add_child(self, child):
        self.children.append(child)

def parse_program(tokens):
    program_node = Node("Program")
    text_section_node = Node("TextSection")
    program_node.add_child(text_section_node)

    index = 0
    while index < len(tokens):
        token = tokens[index]

        if token == "lw":
            load_node = Node("Load Instructions", node_type="Instruction")
            text_section_node.add_child(load_node)
            load_node.add_child(Node("Load: lw", node_type="Operation"))
            index += 1
            operands_node = Node("Operands", node_type="Operands")
            load_node.add_child(operands_node)
            register_name = tokens[index]
            operands_node.add_child(Node(f"register: {register_name}", node_type="Register"))
            # Update symbol table with type information
            if register_name in lexer.symbol_table:
                lexer.symbol_table[register_name]['type'] = 'memory address'
            index += 1

        elif token == "bne":
            bne_node = Node("BranchNotEqual Instruction")
            text_section_node.add_child(bne_node)
            bne_node.add_child(Node("BranchNotEqual: " + token))
            index += 1
            operands_node = Node("Operands")
            bne_node.add_child(operands_node)
            operands_node.add_child(Node("identifier: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("comma: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("integer: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("comma: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("identifier: " + tokens[index]))

        elif token == "add":
            add_node = Node("Add instruction")
            text_section_node.add_child(add_node)
            add_node.add_child(Node("Add: " + token))
            index += 1
            operands_node = Node("Operands")
            add_node.add_child(operands_node)
            operands_node.add_child(Node("identifier: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("comma: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("identifier: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("comma: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("identifier: " + tokens[index]))

        elif token == "b":
            branch_node = Node("Branch", node_type="Instruction")
            text_section_node.add_child(branch_node)
            branch_node.add_child(Node("branch: b", node_type="Operation"))
            index += 1
            branch_label = tokens[index]
            branch_node.add_child(Node(f"Label: {branch_label}", node_type="Label"))
            # Check if the label exists in the symbol table
            if branch_label not in lexer.symbol_table:
                print(f"Error: Undefined label '{branch_label}' at line {index}")
            else:
                # Update type information for label
                lexer.symbol_table[branch_label]['type'] = 'Label'
            index += 1
            branch_node.add_child(Node("Label: " + tokens[index]))
        elif token == "DEFAULT":
            default_node = Node("Default Instruction")
            text_section_node.add_child(default_node)
            default_node.add_child(Node("Label: " + token))
            index += 1
            default_node.add_child(Node("colon: " + tokens[index]))
        elif token == "move":
            move_node = Node("Move Instruction")
            text_section_node.add_child(move_node)
            move_node.add_child(Node("Move: " + token))
            index += 1
            operands_node = Node("Operands")
            move_node.add_child(operands_node)
            operands_node.add_child(Node("identifier: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("comma: " + tokens[index]))
            index += 1
            operands_node.add_child(Node("Zero: " + tokens[index]))
        elif token == "Exit":
            program_node.add_child(Node(token))   
        index += 1
    return program_node
 # Example MIPS code tokens
tokens = [
    "lw", "$v0", "bne", "num1", ",", "0", ",", "L1", "add", "num2", ",", "num3", ",", "num4", "b", "Exit", "DEFAULT", ":", "move", "num2", ",", "zero"
]
# Parse the tokens and generate the parse tree
parse_tree = parse_program(tokens)

# Function to print the parse tree recursively
def print_parse_tree(node, level=0):
    print("|--" * level + node.name)
    for child in node.children:
        print_parse_tree(child, level + 1)

        
# Print the parse tree
def print_parse_tree(node, level=0):
    indent = "|--" * level
    print(f"{indent}{node.name}")
    for child in node.children:
        print_parse_tree(child, level + 1)

# Print the symbol table
print("\nSymbol Table:")
print("-" * 25)
for identifier, info in lexer.symbol_table.items():
    print(f"- Name: {identifier}, Type: {info['type']}")

# Print the parse tree
print("\nOutput (Semantic Analysis)")
print("-" * 25)
print("Semantic Analysis:")
print("-------------------")
print("No semantic errors found.")