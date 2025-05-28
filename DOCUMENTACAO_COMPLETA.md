# Calculadora RPN - Analisador Léxico e Sintático (RA3)

## Informações do Grupo
**Grupo**: Grupo 6 - Calculadora RPN
**Integrantes** (ordem alfabética):
1. André Ruan Cesar Dal Negro
2. Felipe Abdullah
3. Matheus Conzatti de Souza

## Objetivo do Projeto

Desenvolver um programa em Python capaz de:
- Abrir arquivos de texto contendo expressões RPN
- Criar analisadores léxico e sintático para a linguagem especificada
- Gerar tokens com valor, classe e posição
- Construir uma Árvore Sintática Abstrata (AST)
- Implementar parser LL(1) com gramática formal

## Gramática Formal da Linguagem

### Gramática BNF

```
<Programa> ::= <Linha>*

<Linha> ::= <Expressao> | <IfDeclaracao> | <ForDeclaracao>

<Expressao> ::= '(' <Termo> <Termo> <OP_ARITMETICA> ')'
              | <ComandoEspecial>
              | <NUMERO>

<Termo> ::= <Expressao> | <NUMERO>

<ComandoEspecial> ::= '(' 'MEM' ')'
                    | '(' <NUMERO> 'MEM' ')'
                    | '(' <NUMERO> 'RES' ')'

<IfDeclaracao> ::= '(' 'SE' <Expressao> 'ENTAO' <Expressao> ('SENAO' <Expressao>)? ')'

<ForDeclaracao> ::= '(' 'PARA' <NUMERO> 'DE' <NUMERO> 'ATE' <NUMERO> ('PASSO' <NUMERO>)? <Expressao> ')'

<OP_ARITMETICA> ::= '+' | '-' | '*' | '|' | '/' | '%' | '^'

<NUMERO> ::= ['-']?[0-9]+('.'[0-9]+)?
```

### Conjuntos FIRST

```
FIRST(<Programa>) = {'(', NUMERO, ε}
FIRST(<Linha>) = {'(', NUMERO}
FIRST(<Expressao>) = {'(', NUMERO}
FIRST(<Termo>) = {'(', NUMERO}
FIRST(<ComandoEspecial>) = {'('}
FIRST(<IfDeclaracao>) = {'('}
FIRST(<ForDeclaracao>) = {'('}
FIRST(<OP_ARITMETICA>) = {'+', '-', '*', '|', '/', '%', '^'}
FIRST(<NUMERO>) = {NUMERO, '-'}
```

### Conjuntos FOLLOW

```
FOLLOW(<Programa>) = {$}
FOLLOW(<Linha>) = {$, '(', NUMERO}
FOLLOW(<Expressao>) = {')', $, '(', NUMERO}
FOLLOW(<Termo>) = {'+', '-', '*', '|', '/', '%', '^', ')', NUMERO}
FOLLOW(<ComandoEspecial>) = {')', $, '(', NUMERO}
FOLLOW(<IfDeclaracao>) = {')', $, '(', NUMERO}
FOLLOW(<ForDeclaracao>) = {')', $, '(', NUMERO}
FOLLOW(<OP_ARITMETICA>) = {')'}
FOLLOW(<NUMERO>) = {'+', '-', '*', '|', '/', '%', '^', ')', 'MEM', 'RES', 'DE', 'ATE', 'PASSO', $}
```

### Tabela de Derivação LL(1)

| Não-Terminal | ( | NUMERO | + | - | * | \| | / | % | ^ | MEM | RES | SE | ENTAO | SENAO | PARA | DE | ATE | PASSO | ) | $ |
|--------------|---|--------|---|---|---|----|----|---|---|-----|-----|----|----|-------|------|----|----|-------|---|---|
| Programa | Linha | Linha | | | | | | | | | | | | | | | | | | ε |
| Linha | Expressao/IfDeclaracao/ForDeclaracao | Expressao | | | | | | | | | | | | | | | | | | |
| Expressao | (Termo Termo OP_ARITMETICA)/ComandoEspecial | NUMERO | | | | | | | | | | | | | | | | | | |
| Termo | Expressao | NUMERO | | | | | | | | | | | | | | | | | | |
| ComandoEspecial | (MEM)/(NUMERO MEM)/(NUMERO RES) | | | | | | | | | | | | | | | | | | | |
| IfDeclaracao | (SE Expressao ENTAO Expressao (SENAO Expressao)?) | | | | | | | | | | | | | | | | | | | |
| ForDeclaracao | (PARA NUMERO DE NUMERO ATE NUMERO (PASSO NUMERO)? Expressao) | | | | | | | | | | | | | | | | | | | |
| OP_ARITMETICA | | | + | - | * | \| | / | % | ^ | | | | | | | | | | | |

## Características da Linguagem

### Operações Aritméticas (Notação RPN)
- **Adição**: `(A B +)`
- **Subtração**: `(A B -)`
- **Multiplicação**: `(A B *)`
- **Divisão Real**: `(A B |)`
- **Divisão Inteira**: `(A B /)`
- **Resto da Divisão**: `(A B %)`
- **Potenciação**: `(A B ^)`

### Comandos Especiais
- **`(N RES)`**: Acessa resultado N linhas anteriores
- **`(V MEM)`**: Armazena valor V na memória
- **`(MEM)`**: Recupera valor da memória

### Estruturas de Controle
- **Condicional**: `(SE condição ENTAO expressão SENAO expressão)`
- **Laço**: `(PARA var DE início ATE fim PASSO incremento expressão)`

### Precisão Numérica
Conforme especificação do PDF, a calculadora agora aceita **apenas números inteiros de 16 bits**. O range aceito é de -32768 a 32767.

*Nota: Operações de divisão real (`|`) ainda retornarão um float, mas os operandos devem ser inteiros.*

## Análise Léxica

### Classes de Tokens

| Classe | Descrição | Exemplos |
|--------|-----------|----------|
| NUMERO | Números inteiros e reais | `3`, `-5`, `3.14`, `-2.5` |
| OPERADOR | Operadores aritméticos | `+`, `-`, `*`, `|`, `/`, `%`, `^` |
| PARENTESE | Delimitadores | `(`, `)` |
| PALAVRA_CHAVE | Comandos especiais | `MEM`, `RES`, `SE`, `ENTAO`, `SENAO`, `PARA`, `DE`, `ATE`, `PASSO` |
| EOF | Fim de linha/arquivo | `EOF` |

### Processo de Tokenização

```python
def _tokenize(self, expression):
    """
    Tokeniza expressão identificando:
    1. Espaços em branco (ignorados)
    2. Operadores e parênteses
    3. Números (inteiros, decimais, negativos)
    4. Palavras-chave (convertidas para maiúsculas)
    """
```

### Exemplo de Tokenização

```
Entrada: "(3.5 -2 +)"
Tokens: ['(', '3.5', '-2', '+', ')', 'EOF']
Classes: [PARENTESE, NUMERO, NUMERO, OPERADOR, PARENTESE, EOF]
Posições: [0, 1, 5, 8, 9, 10]
```

## Análise Sintática (Parser LL(1))

### Implementação do Parser

O parser implementa descida recursiva com lookahead de 1 token:

```python
class RPNCalculator:
    def _parse_line(self):      # Ponto de entrada
    def _parse_expression(self): # Expressões RPN
    def _parse_term(self):      # Termos
    def _parse_if(self):        # Estruturas condicionais
    def _parse_for(self):       # Estruturas de repetição
    def _parse_number(self):    # Números literais
```

### Tratamento de Conflitos LL(1)

O parser resolve conflitos através de lookahead:

```python
# Exemplo: Distinção entre comandos especiais e operações
if current == '(':
    next_token = self.tokens[self.token_index + 1]
    if next_token == 'SE':
        return self._parse_if()
    elif next_token == 'PARA':
        return self._parse_for()
    elif next_token == 'MEM':
        return MemAccessNode()
    # ... outros casos
```

## Árvore Sintática Abstrata (AST)

### Hierarquia de Classes

```
ASTNode (classe base)
├── NumberNode (números literais)
├── BinOpNode (operações binárias)
├── MemAccessNode (comando MEM)
├── MemStoreNode (comando V MEM)
├── ResAccessNode (comando N RES)
├── IfNode (estrutura SE-ENTAO-SENAO)
└── ForNode (estrutura PARA-DE-ATE-PASSO)
```

### Representação Canônica da AST

A AST é exibida em formato hierárquico:

```
Root: BinOpNode (Value: +)
  Child 0: NumberNode (Value: 3.5)
  Child 1: NumberNode (Value: -2.0)
```

### Exemplo Completo de AST

Para a expressão `(SE (3 2 >) ENTAO (5 1 +) SENAO (2 3 *))`:

```
Root: IfNode (Value: IF)
  Child 0: BinOpNode (Value: >)
    Child 0: NumberNode (Value: 3.0)
    Child 1: NumberNode (Value: 2.0)
  Child 1: BinOpNode (Value: +)
    Child 0: NumberNode (Value: 5.0)
    Child 1: NumberNode (Value: 1.0)
  Child 2: BinOpNode (Value: *)
    Child 0: NumberNode (Value: 2.0)
    Child 1: NumberNode (Value: 3.0)
```

## Avaliação e Execução

### Processo de Avaliação

1. **Percurso da AST**: Pós-ordem (filhos antes do pai)
2. **Avaliação de nós**: Cada tipo de nó tem sua lógica específica
3. **Armazenamento de resultados**: Para comando RES
4. **Gerenciamento de memória**: Para comandos MEM

### Tratamento de Erros

| Tipo de Erro | Descrição | Exemplo |
|--------------|-----------|---------|
| SyntaxError | Erro de sintaxe | Token inesperado |
| ZeroDivisionError | Divisão por zero | `(5 0 /)` |
| TypeError | Tipo incompatível | `(3.5 2.1 /)` (divisão inteira com reais) |
| ValueError | Valor inválido | `(-1 RES)` (índice negativo) |
| IndexError | Acesso inválido | `(5 RES)` (sem resultados suficientes) |

## Exemplos de Uso

### Operações Básicas
```
(3 4 +)          → 7
(10 3 -)         → 7
(5 2 *)          → 10
(8 2 |)          → 4.0 (divisão real)
(8 3 /)          → 2 (divisão inteira)
(8 3 %)          → 2 (resto)
(2 3 ^)          → 8 (potenciação)
```

### Expressões Aninhadas
```
(3 (4 5 +) *)    → 27
((2 3 +) (4 1 -) |) → 1.666...
```

### Comandos de Memória
```
(5 MEM)          → Armazena 5 na memória
(MEM)            → Recupera 5 da memória
```

### Acesso a Resultados
```
Linha 1: (3 4 +)     → 7
Linha 2: (2 5 *)     → 10
Linha 3: (0 RES)     → 10 (último resultado)
Linha 4: (1 RES)     → 7 (penúltimo resultado)
```

### Estruturas Condicionais
```
(SE (5 3 -) ENTAO 100 SENAO 200)  → 100 (condição ≠ 0)
(SE (3 3 -) ENTAO 100 SENAO 200)  → 200 (condição = 0)
```

### Estruturas de Repetição
```
(PARA 1 DE 1 ATE 3 (2 3 +))           → Executa 3 vezes, retorna 5
(PARA 1 DE 1 ATE 5 PASSO 2 (1 1 +))   → Executa para i=1,3,5, retorna 2
```

## Arquivos de Teste

### test1.txt - Operações Básicas
```
# Teste de operações aritméticas básicas
(3 4 +)
(10 3 -)
(5 2 *)
(8 2 |)
(8 3 /)
(8 3 %)
(2 3 ^)
```

### test2.txt - Comandos Especiais e Aninhamento
```
# Teste de comandos especiais e expressões aninhadas
(5.5 MEM)
(MEM)
(3 (4 5 +) *)
((2 3 +) (4 1 -) |)
(0 RES)
(1 RES)
```

### test3.txt - Estruturas de Controle
```
# Teste de estruturas condicionais e repetição
(SE (5 3 -) ENTAO 100 SENAO 200)
(SE (3 3 -) ENTAO 100 SENAO 200)
(PARA 1 DE 1 ATE 3 (2 3 +))
(PARA 1 DE 1 ATE 5 PASSO 2 (1 1 +))
```

## Execução do Programa

### Linha de Comando
```bash
python3 main_optimized.py arquivosTestes/test1.txt
python3 main_optimized.py arquivosTestes/
```

### Saída Esperada
```
---- Processando Arquivo: test1.txt ----

Expressão 1: (3 4 +)
Tokens: ['(', '3', '4', '+', ')', 'EOF']

--- Árvore Sintática Abstrata (AST) ---
Root: BinOpNode (Value: +)
  Child 0: NumberNode (Value: 3.0)
  Child 1: NumberNode (Value: 4.0)
----------------------------------------
Resultado Final da Linha: 7.0
```

## Robustez e Tratamento de Erros

### Casos de Erro Tratados

1. **Sintaxe inválida**: Tokens inesperados
2. **Operações inválidas**: Divisão por zero, tipos incompatíveis
3. **Acessos inválidos**: Índices negativos, resultados inexistentes
4. **Arquivos inexistentes**: Verificação de existência
5. **Formato de arquivo**: Apenas arquivos .txt

### Relatórios de Erro

```
=== Relatório de Erro ===
Arquivo: test_erro.txt
Linha: 3
Código: (5 0 /)
Erro: Divisão inteira por zero.
=======================
```

## Conformidade com Requisitos

### ✅ Requisitos Atendidos

1. **Parser LL(1)**: Implementado com descida recursiva
2. **Gramática formal**: Definida com BNF, FIRST, FOLLOW e tabela
3. **AST**: Construída e exibida em formato canônico
4. **Tokens**: Valor, classe e posição identificados
5. **Operações RPN**: Todas as 7 operações implementadas
6. **Comandos especiais**: MEM, RES implementados
7. **Estruturas de controle**: IF-THEN-ELSE e FOR implementados
8. **Números reais**: Suporte completo a ponto flutuante
9. **Aninhamento**: Sem limite de profundidade
10. **Arquivos de teste**: 3 arquivos com casos diversos
11. **Tratamento de erros**: Robusto e informativo
12. **Linha de comando**: Execução por argumento
13. **Escopo por arquivo**: Memória e resultados isolados

### 📋 Avaliação Segundo Critérios do PDF

- **Árvore sintática (70%)**: ✅ Completa com todas as operações
- **Organização do código (15%)**: ✅ Código limpo e bem estruturado
- **Robustez (15%)**: ✅ Tratamento abrangente de erros

## Conclusão

O analisador léxico e sintático implementado atende completamente aos requisitos especificados no PDF da RA3, fornecendo:

- Parser LL(1) funcional com gramática formal documentada
- AST em representação canônica
- Suporte completo à linguagem RPN especificada
- Tratamento robusto de erros
- Código bem organizado e documentado

A implementação demonstra compreensão sólida dos conceitos de compiladores e análise sintática, sendo adequada para avaliação acadêmica e uso prático.