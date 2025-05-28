#!/usr/bin/env python3
"""
Trabalho de Compiladores - Analisador Léxico e Sintático para RPN
Grupo: [NOME DO GRUPO]
Integrantes:
1. [Nome 1]
2. [Nome 2]
3. [Nome 3]
"""

import sys
import struct
import math
import os
from collections import deque

class RPNCalculator:
    def __init__(self):
        self.results = []
        self.memory = 0.0
        self.current_file = ""
        
        # Gramática LL(1)
        self.grammar = {
            'S': [['(', 'E', ')']],
            'E': [
                ['NUMBER', 'NUMBER', 'OPERATOR'],  # Expressão básica
                ['NUMBER', 'RES'],                 # Comando (N RES)
                ['NUMBER', 'MEM'],                 # Comando (V MEM)
                ['MEM'],                           # Comando (MEM)
                ['(', 'E', ')', '(', 'E', ')', 'OPERATOR']  # Expressão aninhada
            ]
        }
        
        # Tabela de análise LL(1)
        self.parsing_table = {
            'S': {'(': ['(', 'E', ')']},
            'E': {
                '(': ['(', 'E', ')', '(', 'E', ')', 'OPERATOR'],
                'NUMBER': ['NUMBER', 'NUMBER', 'OPERATOR'],
                'RES': ['NUMBER', 'RES'],
                'MEM': ['MEM'] if 'MEM' in self.grammar['E'][3] else ['NUMBER', 'MEM']
            }
        }

    def convert_float_to_half(self, f):
        """
            Converte float para half-precision (16 bits) IEEE 754
        """
        f32 = struct.unpack('>I', struct.pack('>f', f))[0]
        
        sign = (f32 >> 31) & 0x1
        exponent = ((f32 >> 23) & 0xFF) - 127
        mantissa = f32 & 0x007FFFFF

        # Handle special cases
        if exponent > 15:
            return 0x7C00 | (sign << 15)  # Infinity
        if exponent < -14:
            return sign << 15  # Zero

        # Convert to half-precision
        exponent_half = exponent + 15
        mantissa_half = mantissa >> 13
        
        # Rounding
        if (mantissa >> 12) & 0x1:
            mantissa_half += 1
            if mantissa_half == 0x400:
                mantissa_half = 0
                exponent_half += 1
                if exponent_half == 31:
                    return 0x7C00 | (sign << 15)

        return (sign << 15) | (exponent_half << 10) | mantissa_half
    
    def convert_half_to_float(self, f16):
        """
            Converte half-precision (16 bits) para float IEEE 754
        """
        sign = (f16 >> 15) & 0x1
        exponent = (f16 >> 10) & 0x1F
        mantissa = f16 & 0x03FF

        if exponent == 0:
            if mantissa == 0:
                return 0.0 if not sign else -0.0
            # Subnormal number
            f = mantissa / 1024.0
            return math.ldexp(f, -14) * (-1 if sign else 1)
        elif exponent == 0x1F:
            if mantissa == 0:
                return float('inf') if not sign else float('-inf')
            return float('nan')

        # Normal number
        exponent -= 15
        mantissa += 1024  # Add implicit leading 1
        f32 = (sign << 31) | ((exponent + 127) << 23) | (mantissa << 13)
        return struct.unpack('>f', struct.pack('>I', f32))[0]

    def lexical_analyzer(self, expression):
        """
            Analisador léxico que retorna tokens com posições
        """
        tokens = []
        i = 0
        n = len(expression)
        line = 1
        column = 1
        
        while i < n:
            if expression[i].isspace():
                if expression[i] == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                i += 1
                continue
                
            # Números (inteiros ou decimais)
            if expression[i].isdigit() or expression[i] == '.':
                start = i
                start_col = column
                has_decimal = False
                while i < n and (expression[i].isdigit() or expression[i] == '.'):
                    if expression[i] == '.':
                        if has_decimal:
                            raise ValueError(f"Erro léxico: Número com ponto decimal duplo (linha {line}, coluna {column})")
                        has_decimal = True
                    i += 1
                    column += 1
                
                num_str = expression[start:i]
                if num_str.endswith('.'):
                    raise ValueError(f"Erro léxico: Número termina com ponto (linha {line}, coluna {column-1})")
                
                tokens.append({
                    'value': num_str,
                    'type': 'NUMBER',
                    'line': line,
                    'column': start_col
                })
                continue
                
            # Operadores
            if expression[i] in '+-*/%^|':
                tokens.append({
                    'value': expression[i],
                    'type': 'OPERATOR',
                    'line': line,
                    'column': column
                })
                i += 1
                column += 1
                continue
                
            # Parênteses
            if expression[i] in '()':
                tokens.append({
                    'value': expression[i],
                    'type': 'PAREN',
                    'line': line,
                    'column': column
                })
                i += 1
                column += 1
                continue
                
            # Comandos (RES, MEM)
            if expression[i].isalpha():
                start = i
                start_col = column
                while i < n and expression[i].isalpha():
                    i += 1
                    column += 1
                cmd = expression[start:i].upper()
                
                if cmd in ('RES', 'MEM'):
                    tokens.append({
                        'value': cmd,
                        'type': 'COMMAND',
                        'line': line,
                        'column': start_col
                    })
                else:
                    raise ValueError(f"Erro léxico: Comando desconhecido '{cmd}' (linha {line}, coluna {start_col})")
                continue
                
            raise ValueError(f"Erro léxico: Caractere inválido '{expression[i]}' (linha {line}, coluna {column})")
        
        return tokens

    def syntactic_analyzer(self, tokens):
        """
            Analisador sintático LL(1) com geração de AST
        """
        stack = deque(['S'])  # Pilha para análise LL(1)
        ast = {'type': 'Program', 'body': []}
        i = 0
        n = len(tokens)
        
        while stack and i < n:
            top = stack.pop()
            current_token = tokens[i] if i < n else None
            
            if top in self.grammar:
                # Não-terminal - aplicar regra da gramática
                if current_token and current_token['value'] in self.parsing_table[top]:
                    production = self.parsing_table[top][current_token['value']]
                    # Empilha em ordem reversa
                    for symbol in reversed(production):
                        stack.append(symbol)
                else:
                    expected = list(self.parsing_table[top].keys())
                    raise ValueError(
                        f"Erro sintático: Esperado {expected} mas encontrado '{current_token['value']}' "
                        f"(linha {current_token['line']}, coluna {current_token['column']})"
                    )
            else:
                # Terminal - verificar correspondência
                if (top == 'NUMBER' and current_token['type'] == 'NUMBER') or \
                   (top == 'OPERATOR' and current_token['type'] == 'OPERATOR') or \
                   (top == 'RES' and current_token['value'] == 'RES') or \
                   (top == 'MEM' and current_token['value'] == 'MEM') or \
                   (top == current_token['value']):
                    
                    # Construir AST
                    if top == 'NUMBER':
                        ast['body'].append({
                            'type': 'Literal',
                            'value': float(current_token['value']),
                            'raw': current_token['value'],
                            'loc': {
                                'line': current_token['line'],
                                'column': current_token['column']
                            }
                        })
                    elif top == 'OPERATOR':
                        ast['body'].append({
                            'type': 'Operator',
                            'value': current_token['value'],
                            'loc': {
                                'line': current_token['line'],
                                'column': current_token['column']
                            }
                        })
                    elif top in ('RES', 'MEM'):
                        ast['body'].append({
                            'type': 'Command',
                            'value': current_token['value'],
                            'loc': {
                                'line': current_token['line'],
                                'column': current_token['column']
                            }
                        })
                    
                    i += 1
                else:
                    raise ValueError(
                        f"Erro sintático: Esperado '{top}' mas encontrado '{current_token['value']}' "
                        f"(linha {current_token['line']}, coluna {current_token['column']})"
                    )
        
        if stack:
            raise ValueError("Erro sintático: Fim inesperado da expressão")
        
        return ast

    def evaluate_ast(self, ast):
        """
            Avalia a AST gerada pelo analisador sintático
        """
        stack = []
        
        for node in ast['body']:
            if node['type'] == 'Literal':
                stack.append(node['value'])
            elif node['type'] == 'Operator':
                if len(stack) < 2:
                    raise ValueError("Erro de avaliação: Operador sem operandos suficientes")
                b = stack.pop()
                a = stack.pop()
                result = self.apply_operator(a, b, node['value'])
                stack.append(result)
            elif node['type'] == 'Command':
                if node['value'] == 'MEM':
                    stack.append(self.convert_half_to_float(self.memory))
                elif node['value'] == 'RES':
                    if len(stack) < 1:
                        raise ValueError("Erro de avaliação: Comando RES sem argumento")
                    n = int(stack.pop())
                    if n < len(self.results):
                        stack.append(self.results[-(n+1)])
                    else:
                        raise ValueError(f"Erro: Não há {n} resultados anteriores")
        
        if len(stack) != 1:
            raise ValueError("Erro de avaliação: Expressão mal formada")
        
        result = stack[0]
        self.results.append(result)
        return result

    def apply_operator(self, a, b, operator):
        """
            Aplica operador aos operandos
        """
        if operator == '+':
            return a + b
        elif operator == '-':
            return a - b
        elif operator == '*':
            return a * b
        elif operator == '/':
            if b == 0:
                raise ValueError("Divisão por zero")
            return a // b if isinstance(a, int) and isinstance(b, int) else a / b
        elif operator == '%':
            if b == 0:
                raise ValueError("Módulo por zero")
            return a % b
        elif operator == '^':
            if not isinstance(b, int) or b < 0:
                raise ValueError("Expoente deve ser inteiro positivo")
            return math.pow(a, b)
        elif operator == '|':
            return max(a, b)
        else:
            raise ValueError(f"Operador desconhecido '{operator}'")

    def print_ast(self, ast, level=0):
        """
            Imprime a AST em formato canônico (árvore)
        """
        indent = "  " * level
        if ast['type'] == 'Program':
            print(f"{indent}Program")
            for node in ast['body']:
                self.print_ast(node, level + 1)
        elif ast['type'] == 'Literal':
            print(f"{indent}Literal({ast['value']})")
        elif ast['type'] == 'Operator':
            print(f"{indent}Operator({ast['value']})")
        elif ast['type'] == 'Command':
            print(f"{indent}Command({ast['value']})")

    def generate_error_report(self, line_num, line, error_msg):
        """
            Gera um relatório de erro detalhado
        """
        print("=== Relatório de Erro ===")
        print(f"Arquivo: {self.current_file}")
        print(f"Linha: {line_num}")
        print(f"Código: {line}")
        print(f"Erro: {error_msg}")
        print("Sugestões de correção:")
        
        if "Erro léxico" in error_msg:
            if "Número com ponto decimal duplo" in error_msg:
                print("- Remover o ponto decimal extra")
            elif "Número termina com ponto" in error_msg:
                print("- Completar a parte decimal ou remover o ponto")
            elif "Comando desconhecido" in error_msg:
                print("- Use apenas comandos RES ou MEM")
            else:
                print("- Verifique caracteres inválidos na expressão")
        
        elif "Erro sintático" in error_msg:
            if "Esperado '('" in error_msg:
                print("- Certifique-se que a expressão começa com '('")
            elif "Esperado ')'" in error_msg:
                print("- Certifique-se que a expressão termina com ')'")
            elif "Fim inesperado" in error_msg:
                print("- Expressão incompleta - verifique parênteses")
            else:
                print("- Verifique a estrutura da expressão RPN")
        
        print("=======================\n")

    def process_file(self, filename):
        """
            Processa um arquivo de entrada
        """
        self.current_file = filename
        print(f"\n=== Processando arquivo: {filename} ===\n")
        
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                print(f"Expressão {line_num}: {line}")
                
                try:
                    # Análise léxica
                    tokens = self.lexical_analyzer(line)
                    print("\nTokens:")
                    for token in tokens:
                        print(f"  <{token['value']}, {token['type']}, linha {token['line']}, coluna {token['column']}>")
                    
                    # Análise sintática e geração de AST
                    ast = self.syntactic_analyzer(tokens)
                    print("\nÁrvore Sintática Abstrata (AST):")
                    self.print_ast(ast)
                    
                    # Avaliação
                    result = self.evaluate_ast(ast)
                    if result is not None:
                        print(f"\nResultado: {result}\n")
                    
                except ValueError as e:
                    print(f"\nErro na linha {line_num}: {str(e)}\n")
                    self.generate_error_report(line_num, line, str(e))

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 analisador_rpn.py <arquivo_entrada>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    calculator = RPNCalculator()
    
    if os.path.isfile(input_path):
        if input_path.endswith('.txt'):
            calculator.process_file(input_path)
        else:
            print("Erro: O arquivo deve ter extensão .txt")
    elif os.path.isdir(input_path):
        print("Erro: Por favor, especifique um arquivo, não um diretório")
    else:
        print(f"Erro: Arquivo ou diretório não encontrado: {input_path}")

if __name__ == "__main__":
    main()