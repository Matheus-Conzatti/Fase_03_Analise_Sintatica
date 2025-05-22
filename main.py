import sys
import struct
import math
import os

class RPNCalculator:
    """
    Implements a calculator for evaluating expressions in Reverse Polish Notation (RPN).
    Supports basic arithmetic operations, special memory commands, and nested expressions.
    """
    
    def __init__(self):
        """
        Initializes the RPN calculator with default values.
        Sets up the list of previous results and memory.
        """
        # Stores previous results of expressions
        self.results = []
        # Memory for (V MEM) command
        self.memory = 0.0
    
    def convertFloatToHalf(self, f):
        """
        Converts a number to half-precision (16 bits) according to IEEE754 standard.
        
        Parameters:
            value: Float value to be converted
        Returns:
            Value converted to half-precision (16 bits) representation
        """
        # Converts float to bits (uint32)
        bin_f = struct.unpack('>I', struct.pack('>f', f))[0]

        sinal = (bin_f >> 16) & 0x8000
        exp = ((bin_f >> 23) & 0xFF) - 127 + 15
        mantissa = (bin_f >> 13) & 0x03FF

        if exp <= 0:
            return sinal # Subnormal or zero
        elif exp >= 31:
            return sinal | 0x7C00 # Infinity or NaN
        return sinal | (exp << 10) | mantissa
    
    def convertHalfToFloat(self, f16):
        """
        Converts a half-precision (16 bits) number to float according to IEEE754 standard.
        
        Parameters:
            f16: Value in half-precision (16 bits) to be converted
        Returns:
            Value converted to float
        """
        sinal = (f16 >> 15) & 0x1
        exp = (f16 >> 10) & 0x1F
        frac = f16 & 0x03FF
        f32Sinal = sinal << 31
        f32Exp = 0
        f32Frac = 0

        if exp == 0:
            if frac == 0:
                f32Sinal = 0
                f32Frac = 0
            else:
                exp = 1
                while (frac & 0x0400) == 0:
                    frac <<= 1
                    exp -= 1
                frac &= 0x03FF
                f32Exp = (127 - 15 + exp) << 23
                f32Frac = frac << 13
        elif exp == 0x1F:
            f32Exp = 0xFF << 23
            f32Frac = frac << 13
        else:
            f32Exp = (exp + (127 - 15)) << 23
            f32Frac = frac << 13
        
        f32Bits = f32Sinal | f32Exp | f32Frac
        return struct.unpack('>f', struct.pack('>I', f32Bits))[0]

    def evaluate_expression(self, expression):
        """
        Evaluates an RPN expression and returns the final result.
        Supports special commands such as (N RES), (V MEM), and (MEM).
        
        - If you write (2 RES), it will retrieve the result calculated 2 lines ago
        - If you write (5 MEM), it will store the number 5 in the calculator's memory
        - If you write (MEM), it will retrieve the number stored in memory
        
        Parameters:
            expression: String containing the RPN expression to be evaluated
        Returns:
            Result of the expression evaluation
        """
        try:
            tokens = self.lexical_analyzer(expression.strip())
            self.syntactic_analyzer(tokens)

            expr = expression.split()

            if expr.startswith('(') and expr.endswith(')'):
                inner = expr[1:-1].strip()
                parts= inner.split()
                if len(parts) == 2 and parts[1].upper() == 'RES' and parts[0].isdigit():
                    n = int(parts[0])
                    if n < len(self.results):
                        return self.convertFloatToHalf(self.results[-(n+1)])
                    else:
                        raise ValueError(f"Erro: Não há {n} resultados anteriores.")
                if len(parts) == 2 and parts[1].upper() == 'MEM':
                    try:
                        value = float(parts[0])
                        self.memory = self.convertFloatToHalf(value)
                        return self.memory
                    except ValueError:
                        raise ValueError(f"Erro: '{parts[0]}' não é um número válido.")
                if len(parts) == 1 and parts[0].upper() == 'MEM':
                    return self.memory
            return self.evaluate_tokens(self.tokenize_expression(expression))
        except ValueError as e:
            print(f"Erro ao avaliar a expressão: {str(e)}")
            return None
            
    def evaluate_tokens(self, expression):
        """
        Evaluates a list of tokens in RPN notation and returns the result.
        Handles the logic for processing expressions, operand stack, and nested sub-expressions.
        
        Parameters:
            tokens: List of tokens (operands, operators, and parentheses)
            
        Returns:
            Result of the token evaluation
        """
        tokens = []
        i = 0
        n = len(expression)
        while i < n:
            if expression[i].isspace():
                i += 1
                continue
            if expression[i] in '()+-*/^%|':
                tokens.append(expression[i])
                i += 1
                continue
            if expression[i].isdigit() or expression[i] == '.':
                start = i
                has_decimal = False
                while i < n and (expression[i].isdigit() or (expression[i] == '.' and not has_decimal)):
                    if expression[i] == '.':
                        has_decimal = True
                    i += 1
                tokens.append(expression[start:i])
                continue
            if expression[i].isalpha():
                start = i
                while i < n and expression[i].isalpha():
                    i += 1
                tokens.append(expression[start:i].upper())
                continue
            raise ValueError(f"Caractere inválido '{expression[i]}' na posição {i}")
        return tokens

    def operate(self, a, b, operator):
        """
        Performs the mathematical operation between two operands a and b with the given operator.
        
        Parameters:
            a: First operand (float)
            b: Second operand (float)
            operator: Operator (string)
        Returns:
            Result of the operation
        """
        if operator == '+':
            return a + b
        elif operator == '-':
            return a - b
        elif operator == '*':
            return a * b
        elif operator == '/':
            if b == 0:
                raise ValueError("Error: Division by zero.")
            return a / b
        elif operator == '%':
            return a % b
        elif operator == '^':
            return math.pow(a, b)
        elif operator == '|':
            return max(a, b)
        else:
            raise ValueError(f"Error: Invalid operator '{operator}'")
    
    def tokenize_expression(self, expression):
        """
        Tokenizes the RPN expression, splitting it into its components (operators, operands, special commands).
        
        Parameters:
            expression: RPN expression as a string
        Returns:
            List of tokens
        """
        tokens = []
        i = 0
        n = len(expression)
        while i < n:
            if expression[i].issapace():
                i += 1
                continue
            if expression[i] in '()+-*/^%|':
                tokens.append(expression[i])
                i += 1
                continue
            if expression[i].isdigit() or expression[i] == '.':
                start = i
                has_decimal = False
                while i < n and (expression[i].isdigit() or (expression[i] == '.' and not has_decimal)):
                    if expression[i] == '.':
                        has_decimal = True
                    i += 1
                tokens.append(expression[start:i])
                continue
            if expression[i].isalpha():
                start = i
                while i < n and expression[i].isalpha():
                    i += 1
                tokens.append(expression[start:i].upper())
                continue
            raise ValueError(f"Invalid character '{expression[i]}' at position {i}")
        return tokens
    
    def process_input(self, path):
        """
            Processes individual files or directories.
        """
        if os.path.isfile(path):
            if path.endswith('.txt'):
                self.process_File(path)
            else:
                print(f"Error: '{path}' is not a .txt file")
        elif os.path.isdir(path):
            # Iterate through .txt files in the directory
            for fname in os.listdir(path):
                if fname.endswith('.txt'):
                    full_path = os.path.join(path, fname)
                    self.process_File(full_path)
        else:
            print(f"Error: '{path}' not found or is not valid")
    
    def process_File(self, filename):
        """
            Processes a file containing RPN expressions (one per line).
            Evaluates each expression and stores the result.
            
            Parameters:
                filename: Path to the file to be processed
            Returns:
                List with the results of each expression in the file
        """
        print(f"---- File: {os.path.basename(filename)} ----\n")
        with open(filename, 'r') as f:
            lines = f.readlines()
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line:
                    print(f"Expression {i+1}: {line}")
                    # Show token string
                    tok_list = self.lexical_analyzer(line)
                    token_str = ' '.join([f"< {t['value']}, {t['type']}, {t['position']} >" for t in tok_list])
                    print(f"Tokens: {token_str}")
                    result = self.evaluate_expression(line)
                    if result is not None:
                        self.results.append(result)
                        print(f"Result: {result}\n")
    
    def lexical_analyzer(self, expression):
        """
            Lexical Analyzer - Transforms the expression into tokens with additional information
            Returns a list of dictionaries containing:
            - 'value': token value
            - 'type': token type (NUMBER, OPERATOR, PAREN, COMMAND)
            - 'position': initial position within the expression
        """
        tokens = []
        i = 0
        n = len(expression)
        
        while i < n:
            if expression[i].isspace():
                i += 1
                continue
                
            # Check for parentheses
            if expression[i] in '()':
                tokens.append({'value': expression[i], 'type': 'PAREN', 'position': i})
                i += 1
                continue
                
            # Check for operators
            if expression[i] in '+-*/%|^':
                tokens.append({'value': expression[i], 'type': 'OPERATOR', 'position': i})
                i += 1
                continue
                
            # Check for numbers (integers and decimals)
            if expression[i].isdigit() or expression[i] == '.':
                start = i
                has_decimal = False
                while i < n:
                    if expression[i].isdigit():
                        i += 1
                    elif expression[i] == '.' and not has_decimal:
                        has_decimal = True
                        i += 1
                    else:
                        break
                
                # Check if the token is valid (does not end with a dot)
                if expression[i-1] == '.':
                    raise ValueError(f"Invalid number at position {start}")
                
                tokens.append({'value': expression[start:i],'type': 'NUMBER','position': start})
                continue
                
            # Check for commands (RES, MEM)
            if expression[i].isalpha():
                start = i
                while i < n and expression[i].isalpha():
                    i += 1
                token_value = expression[start:i].upper()
                
                if token_value in ('RES', 'MEM'):
                    tokens.append({'value': token_value,'type': 'COMMAND','position': start})
                else:
                    raise ValueError(f"Unknown command '{token_value}' at position {start}")
                continue
            raise ValueError(f"Invalid character '{expression[i]}' at position {i}") 
        return tokens
    
    def syntactic_analyzer(self, tokens):
        """
            Checks whether the token structure is valid.
            Returns True if the syntax is correct, False otherwise.
        """
        stack = []
        i = 0
        n = len(tokens)
        
        def expect(token_type=None, token_value=None):
            nonlocal i
            if i >= n:
                raise ValueError("Unexpected end of expression")
            if token_type and tokens[i]['type'] != token_type:
                raise ValueError(f"Expected {token_type}, found {tokens[i]['type']} at position {tokens[i]['position']}")
            if token_value and tokens[i]['value'] != token_value:
                raise ValueError(f"Expected '{token_value}', found '{tokens[i]['value']}' at position {tokens[i]['position']}")
            i += 1
        
            try:
                while i < n:
                    if tokens[i]['value'] == '(':
                        stack.append(tokens[i])
                        expect('PAREN', '(')
                        
                        # Check if it's a special command
                        if i + 2 < n and tokens[i]['type'] == 'NUMBER' and tokens[i+1]['type'] == 'COMMAND':
                            expect('NUMBER')
                            expect('COMMAND')
                            expect('PAREN', ')')
                            stack.pop()
                            continue
                        elif i + 1 < n and tokens[i]['type'] == 'COMMAND' and tokens[i]['value'] == 'MEM':
                            expect('COMMAND', 'MEM')
                            expect('PAREN', ')')
                            stack.pop()
                            continue
                        
                        # Otherwise, it's a normal expression
                        # First operand (can be number or subexpression)
                        if i < n and tokens[i]['type'] in ('NUMBER', 'PAREN'):
                            if tokens[i]['value'] == '(':
                                self.syntactic_analyzer(tokens[i:])
                            else:
                                expect('NUMBER')
                        
                        # Second operand
                        if i < n and tokens[i]['type'] in ('NUMBER', 'PAREN'):
                            if tokens[i]['value'] == '(':
                                self.syntactic_analyzer(tokens[i:])
                            else:
                                expect('NUMBER')
                        
                        # Operator
                        expect('OPERATOR')
                        
                        # Closing
                        expect('PAREN', ')')
                        stack.pop()
                    else:
                        i += 1
                
                if stack:
                    raise ValueError(f"Unclosed parenthesis at position {stack[-1]['position']}")
                
                return True
            except ValueError as e:
                raise ValueError(f"Syntax error: {str(e)}")
            
def main():
    """
        Main function that coordinates program execution.
        Processes the input file specified as a command-line argument,
        evaluates the expressions, and generates the corresponding output.
    """
    calculator = RPNCalculator()

    if len(sys.argv) > 1:
        path = sys.argv[1]
        calculator.process_input(path)
    else:
         print("Usage: python3 main.py <input_file>")

# Example usage:
if __name__ == "__main__":
    main()
