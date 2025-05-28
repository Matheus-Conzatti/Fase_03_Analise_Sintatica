"""
Trabalho de Compiladores - Analisador Léxico e Sintático para RPN (Versão Otimizada)
Grupo: Grupo 6 - Calculadora RPN
Integrantes:
1. André Ruan Cesar Dal Negro
2. Felipe Abdullah
3. Matheus Conzatti de Souza

GRAMÁTICA FORMAL BNF:
<Programa> ::= <Linha>*
<Linha> ::= <Expressao> | <IfDeclaracao> | <ForDeclaracao>
<Expressao> ::= '(' <Termo> <Termo> <OP_ARITMETICA> ')' | <ComandoEspecial> | <NUMERO>
<Termo> ::= <Expressao> | <NUMERO>
<ComandoEspecial> ::= '(' 'MEM' ')' | '(' <NUMERO> 'MEM' ')' | '(' <NUMERO> 'RES' ')'
<IfDeclaracao> ::= '(' 'SE' <Expressao> 'ENTAO' <Expressao> ('SENAO' <Expressao>)? ')'
<ForDeclaracao> ::= '(' 'PARA' <NUMERO> 'DE' <NUMERO> 'ATE' <NUMERO> ('PASSO' <NUMERO>)? <Expressao> ')'
<OP_ARITMETICA> ::= '+' | '-' | '*' | '|' | '/' | '%' | '^'
<NUMERO> ::= ['-']?[0-9]+('.'[0-9]+)?

CONJUNTOS FIRST:
FIRST(<Programa>) = {'(', NUMERO, ε}
FIRST(<Linha>) = {'(', NUMERO}
FIRST(<Expressao>) = {'(', NUMERO}
FIRST(<Termo>) = {'(', NUMERO}
FIRST(<ComandoEspecial>) = {'('}
FIRST(<IfDeclaracao>) = {'('}
FIRST(<ForDeclaracao>) = {'('}
FIRST(<OP_ARITMETICA>) = {'+', '-', '*', '|', '/', '%', '^'}
FIRST(<NUMERO>) = {NUMERO, '-'}

CONJUNTOS FOLLOW:
FOLLOW(<Programa>) = {$}
FOLLOW(<Linha>) = {$, '(', NUMERO}
FOLLOW(<Expressao>) = {')', $, '(', NUMERO}
FOLLOW(<Termo>) = {'+', '-', '*', '|', '/', '%', '^', ')', NUMERO}
FOLLOW(<ComandoEspecial>) = {')', $, '(', NUMERO}
FOLLOW(<IfDeclaracao>) = {')', $, '(', NUMERO}
FOLLOW(<ForDeclaracao>) = {')', $, '(', NUMERO}
FOLLOW(<OP_ARITMETICA>) = {')'}
FOLLOW(<NUMERO>) = {'+', '-', '*', '|', '/', '%', '^', ')', 'MEM', 'RES', 'DE', 'ATE', 'PASSO', $}

TABELA DE DERIVAÇÃO LL(1):
| Não-Terminal | ( | NUMERO | + | - | * | | | / | % | ^ | MEM | RES | SE | ENTAO | SENAO | PARA | DE | ATE | PASSO | ) | $ |
|--------------|---|--------|---|---|---|---|---|---|---|-----|-----|----|----|-------|------|----|----|-------|---|---|
| Programa | Linha | Linha | | | | | | | | | | | | | | | | | | ε |
| Linha | Expressao/IfDeclaracao/ForDeclaracao | Expressao | | | | | | | | | | | | | | | | | | |
| Expressao | (Termo Termo OP_ARITMETICA)/ComandoEspecial | NUMERO | | | | | | | | | | | | | | | | | | |
| Termo | Expressao | NUMERO | | | | | | | | | | | | | | | | | | |
| ComandoEspecial | (MEM)/(NUMERO MEM)/(NUMERO RES) | | | | | | | | | | | | | | | | | | | |
| IfDeclaracao | (SE Expressao ENTAO Expressao (SENAO Expressao)?) | | | | | | | | | | | | | | | | | | | |
| ForDeclaracao | (PARA NUMERO DE NUMERO ATE NUMERO (PASSO NUMERO)? Expressao) | | | | | | | | | | | | | | | | | | | |
| OP_ARITMETICA | | | + | - | * | | | / | % | ^ | | | | | | | | | | | |
"""

import sys
import os

# --- Classes para os Nós da Árvore de Sintaxe Abstrata (AST) ---
class ASTNode:
    """Nó base para a Árvore de Sintaxe Abstrata."""
    def __init__(self, value=None):
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value if self.value is not None else ''})"

class NumberNode(ASTNode):
    """Representa um número literal."""
    pass

class BinOpNode(ASTNode):
    """Representa uma operação binária."""
    def __init__(self, operator, left, right):
        super().__init__(operator)
        self.left, self.right = left, right
        self.add_child(left)
        self.add_child(right)

class MemAccessNode(ASTNode):
    """Representa o comando (MEM)."""
    def __init__(self):
        super().__init__("MEM_ACCESS")

class MemStoreNode(ASTNode):
    """Representa o comando (V MEM)."""
    def __init__(self, value_node):
        super().__init__("MEM_STORE")
        self.value_node = value_node
        self.add_child(value_node)

class ResAccessNode(ASTNode):
    """Representa o comando (N RES)."""
    def __init__(self, index_node):
        super().__init__("RES_ACCESS")
        self.index_node = index_node
        self.add_child(index_node)

class IfNode(ASTNode):
    """Representa uma declaração if-then-else."""
    def __init__(self, condition, then_branch, else_branch=None):
        super().__init__("IF")
        self.condition, self.then_branch, self.else_branch = condition, then_branch, else_branch
        self.add_child(condition)
        self.add_child(then_branch)
        if else_branch:
            self.add_child(else_branch)

class ForNode(ASTNode):
    """Representa uma declaração de laço for."""
    def __init__(self, var_id_node, start_val_node, end_val_node, step_val_node, body_node):
        super().__init__("FOR")
        self.var_id_node = var_id_node
        self.start_val_node = start_val_node
        self.end_val_node = end_val_node
        self.step_val_node = step_val_node
        self.body_node = body_node

        for node in [var_id_node, start_val_node, end_val_node, step_val_node, body_node]:
            if node:
                self.add_child(node)

class RPNCalculator:
    """Calculadora RPN com analisador léxico, sintático e avaliador."""

    def __init__(self):
        self.results = []
        self.memory = 0
        self.current_file = ""
        self.current_line_num = 0
        self.current_line_content = ""
        self.tokens = []
        self.token_index = 0


    def _tokenize(self, expression):
        """Tokeniza a expressão de forma otimizada."""
        tokens = []
        i = 0
        n = len(expression)

        while i < n:
            char = expression[i]

            if char.isspace():
                i += 1
                continue

            # Check for numbers (including negative numbers and decimals)
            if char.isdigit() or (char == '-' and i + 1 < n and expression[i+1].isdigit()):
                start = i
                if char == '-':
                    i += 1
                while i < n and expression[i].isdigit():
                    i += 1
                # Check for decimal point
                if i < n and expression[i] == '.':
                    i += 1
                    while i < n and expression[i].isdigit():
                        i += 1
                tokens.append(expression[start:i])
                continue
            if char in '+-*|/%^()':
                tokens.append(char)
                i += 1
                continue
            if char.isalpha():
                start = i
                while i < n and (expression[i].isalpha() or expression[i].isdigit()):
                    i += 1
                tokens.append(expression[start:i].upper())
                continue

            raise ValueError(f"Caractere inesperado: '{char}' na posição {i}")

        return tokens

    def _operate(self, a, b, operator):
        """Realiza operações matemáticas."""
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '|': lambda x, y: float(x) / y if y != 0 else self._raise_zero_div("real"), # Real division returns float
            '/': lambda x, y: x // y if y != 0 else self._raise_zero_div("inteira"),
            '%': lambda x, y: x % y if y != 0 else self._raise_zero_div("módulo"),
            '^': lambda x, y: x ** y if y >= 0 else self._raise_exp_error()
        }

        if operator not in operations:
            raise ValueError(f"Operador inválido '{operator}'")

        return operations[operator](a, b)

    def _raise_zero_div(self, op_type):
        raise ZeroDivisionError(f"Divisão {op_type} por zero.")

    def _raise_type_or_zero_div(self, a, b, op_type):
        if b == 0:
            raise ZeroDivisionError(f"Divisão {op_type} por zero.")
        raise TypeError(f"Operandos para '{op_type}' devem ser inteiros.")

    def _raise_exp_error(self):
        raise TypeError("Expoente deve ser um inteiro não-negativo.")

    # --- Métodos do Parser ---
    def _current_token(self):
        return self.tokens[self.token_index] if self.token_index < len(self.tokens) else 'EOF'

    def _advance(self):
        self.token_index += 1

    def _expect(self, expected):
        current = self._current_token()
        if current == expected:
            self._advance()
            return current
        raise SyntaxError(f"Erro na linha {self.current_line_num}: "
                         f"Esperado '{expected}', encontrado '{current}' "
                         f"na expressão: '{self.current_line_content}'")

    def _parse_number(self):
        """Cria um nó de número."""
        token = self._current_token()
        try:
            # Try to parse as float first to support both integers and decimals
            if '.' in token:
                value = float(token)
            else:
                value = int(token)
                # Apply 16-bit integer range check only for integers
                if not (-32768 <= value <= 32767):
                    raise SyntaxError(f"Número inteiro '{value}' fora do range de 16-bit (-32768 a 32767).")
            self._advance()
            return NumberNode(value)
        except ValueError:
            raise SyntaxError(f"Esperado número válido, encontrado '{token}'")

    def _is_number(self, token):
        """Verifica se o token é um número."""
        try:
            # Try to parse as float to support both integers and decimals
            float(token)
            return True
        except ValueError:
            return False

    def _parse_expression(self):
        """Analisa expressões RPN."""
        current = self._current_token()

        if current == '(':
            self._expect('(')

            first = self._current_token()
            second = self.tokens[self.token_index + 1] if self.token_index + 1 < len(self.tokens) else None

            if first == 'SE':
                return self._parse_if()
            elif first == 'PARA':
                return self._parse_for()

            if first == 'MEM':
                self._expect('MEM')
                self._expect(')')
                return MemAccessNode()

            if self._is_number(first) and second in ['MEM', 'RES']:
                num_node = self._parse_number()
                keyword = self._current_token()
                self._advance()
                self._expect(')')

                return MemStoreNode(num_node) if keyword == 'MEM' else ResAccessNode(num_node)

            if self._is_number(first) and second == ')':
                num_node = self._parse_number()
                self._expect(')')
                return num_node

            left = self._parse_term()
            right = self._parse_term()
            operator = self._current_token()

            if operator not in '+-*|/%^':
                raise SyntaxError(f"Esperado operador aritmético, encontrado '{operator}'")

            self._advance()
            self._expect(')')
            return BinOpNode(operator, left, right)

        elif self._is_number(current):
            return self._parse_number()
        else:
            raise SyntaxError(f"Erro na linha {self.current_line_num}: "
                               f"Esperado '(', ou NUMERO, encontrado '{current}' "
                               f"na expressão: '{self.current_line_content}'")

    def _parse_term(self):
        """Analisa termos."""
        current = self._current_token()
        if current == '(':
            next_token = self.tokens[self.token_index + 1] if self.token_index + 1 < len(self.tokens) else None
            if next_token == 'SE':
                return self._parse_if()
            elif next_token == 'PARA':
                return self._parse_for()
            else:
                return self._parse_expression()
        elif self._is_number(current):
            return self._parse_number()
        else:
            raise SyntaxError(f"Erro na linha {self.current_line_num}: "
                               f"Esperado '(', ou NUMERO, encontrado '{current}' "
                               f"na expressão: '{self.current_line_content}'")

    def _parse_line(self):
        """Analisa uma linha completa."""
        current = self._current_token()

        if current == '(':
            next_token = self.tokens[self.token_index + 1] if self.token_index + 1 < len(self.tokens) else None

            if next_token == 'SE':
                return self._parse_if()
            elif next_token == 'PARA':
                return self._parse_for()
            else:
                return self._parse_expression()
        elif current == 'EOF':
            return None
        else:
            return self._parse_expression()

    def _parse_if(self):
        """Analisa declaração if-then-else."""
        self._expect('(')
        self._expect('SE')
        condition = self._parse_term()
        self._expect('ENTAO')
        then_branch = self._parse_term()

        else_branch = None
        if self._current_token() == 'SENAO':
            self._expect('SENAO')
            else_branch = self._parse_term()

        self._expect(')')
        return IfNode(condition, then_branch, else_branch)

    def _parse_for(self):
        """Analisa declaração for."""
        self._expect('(')
        self._expect('PARA')
        var_id = self._parse_number()
        self._expect('DE')
        start_val = self._parse_number()
        self._expect('ATE')
        end_val = self._parse_number()

        step_val = None
        if self._current_token() == 'PASSO':
            self._expect('PASSO')
            step_val = self._parse_number()

        body = self._parse_term()
        self._expect(')')
        return ForNode(var_id, start_val, end_val, step_val, body)

    def _evaluate(self, node):
        """Avalia a AST."""
        if isinstance(node, NumberNode):
            return node.value
        elif isinstance(node, BinOpNode):
            left_val = self._evaluate(node.left)
            right_val = self._evaluate(node.right)
            return self._operate(left_val, right_val, node.value)
        elif isinstance(node, MemAccessNode):
            return self.memory
        elif isinstance(node, MemStoreNode):
            value = self._evaluate(node.value_node)
            self.memory = value
            return value
        elif isinstance(node, ResAccessNode):
            index = int(self._evaluate(node.index_node))
            if index < 0:
                raise ValueError("Índice para RES deve ser não-negativo.")
            if index >= len(self.results):
                raise IndexError(f"Não há {index+1} resultados anteriores.")
            return self.results[-(index + 1)]
        elif isinstance(node, IfNode):
            condition_val = self._evaluate(node.condition)
            if condition_val != 0:
                return self._evaluate(node.then_branch)
            elif node.else_branch:
                return self._evaluate(node.else_branch)
            return None
        elif isinstance(node, ForNode):
            start = int(self._evaluate(node.start_val_node))
            end = int(self._evaluate(node.end_val_node))
            step = int(self._evaluate(node.step_val_node)) if node.step_val_node else 1

            last_result = None
            for i in range(start, end + 1, step):
                last_result = self._evaluate(node.body_node)
            return last_result
        else:
            raise NotImplementedError(f"Avaliação não implementada para: {type(node)}")

    def _print_ast(self, node, level=0, prefix="Root: "):
        """Imprime a AST de forma indentada."""
        indent = "  " * level
        if node is None:
            print(f"{indent}{prefix}None")
            return

        node_info = f"{node.__class__.__name__}"
        if node.value is not None:
            node_info += f" (Value: {node.value})"

        print(f"{indent}{prefix}{node_info}")

        for i, child in enumerate(node.children):
            self._print_ast(child, level + 1, f"Child {i}: ")

    def evaluate_expression(self, expression_string):
        """Ponto de entrada principal para avaliação."""
        self.current_line_content = expression_string.strip()
        self.tokens = []
        self.token_index = 0

        if not self.current_line_content or self.current_line_content.startswith('#'):
            return None

        try:
            print(f"Expressão {self.current_line_num}: {self.current_line_content}")

            self.tokens = self._tokenize(self.current_line_content)
            self.tokens.append('EOF')
            print(f"Tokens: {self.tokens}")
            ast = self._parse_line()

            print("\n--- Árvore Sintática Abstrata (AST) ---")
            self._print_ast(ast)
            print("----------------------------------------")

            result = self._evaluate(ast)
            self.results.append(result)
            return result

        except Exception as e:
            self._generate_error_report(str(e))
            return None

    def _generate_error_report(self, error_msg):
        """Gera relatório de erro."""
        print("\n=== Relatório de Erro ===")
        print(f"Arquivo: {self.current_file}")
        print(f"Linha: {self.current_line_num}")
        print(f"Código: {self.current_line_content}")
        print(f"Erro: {error_msg}")
        print("=======================\n")

    def process_input(self, path):
        """Processa arquivos ou diretórios."""
        if os.path.isfile(path):
            if path.endswith('.txt'):
                self.process_file(path)
            else:
                print(f"Erro: '{path}' não é um arquivo .txt")
        elif os.path.isdir(path):
            for fname in sorted(os.listdir(path)):
                if fname.endswith('.txt'):
                    self.process_file(os.path.join(path, fname))
        else:
            print(f"Erro: '{path}' não encontrado.")

    def process_file(self, filename):
        """Processa um arquivo linha por linha."""
        self.current_file = os.path.basename(filename)
        print(f"\n---- Processando Arquivo: {self.current_file} ----\n")

        self.results = []
        self.memory = 0.0

        with open(filename, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            self.current_line_num = i + 1
            result = self.evaluate_expression(line)
            if result is not None:
                print(f"Resultado Final da Linha: {result}\n")
            elif line.strip() and not line.strip().startswith('#'):
                print("Avaliação da linha falhou.\n")

def main():
    """Função principal."""
    calculator = RPNCalculator()

    if len(sys.argv) > 1:
        calculator.process_input(sys.argv[1])
    else:
        print("Uso: python3 main_optimized.py <arquivo_ou_diretorio_entrada>")

if __name__ == "__main__":
    main()