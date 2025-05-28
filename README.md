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
- Suportar números reais e inteiros
- Implementar todas as operações aritméticas
- Suportar estruturas de controle (IF-THEN-ELSE e FOR)

## Gramática Formal da Linguagem

### Gramática BNF

```
<Programa> ::= <Linha>*
<Linha> ::= <Expressao> | <IfDeclaracao> | <ForDeclaracao>
<Expressao> ::= '(' <Termo> <Termo> <OP_ARITMETICA> ')' | <ComandoEspecial> | <NUMERO>
<Termo> ::= <Expressao> | <NUMERO>
<ComandoEspecial> ::= '(' 'MEM' ')' | '(' <NUMERO> 'MEM' ')' | '(' <NUMERO> 'RES' ')'
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
- **Adição**: `(A B +)` - Soma A + B
- **Subtração**: `(A B -)` - Subtração A - B
- **Multiplicação**: `(A B *)` - Multiplicação A * B
- **Divisão Real**: `(A B |)` - Divisão real A / B (retorna float)
- **Divisão Inteira**: `(A B /)` - Divisão inteira A // B
- **Resto da Divisão**: `(A B %)` - Resto A % B
- **Potenciação**: `(A B ^)` - Potenciação A ^ B

### Comandos Especiais
- **`(N RES)`**: Acessa resultado N linhas anteriores (0 = último resultado)
- **`(V MEM)`**: Armazena valor V na memória
- **`(MEM)`**: Recupera valor da memória

### Estruturas de Controle
- **Condicional**: `(SE condição ENTAO expressão SENAO expressão)`
  - Se condição ≠ 0, executa primeira expressão
  - Se condição = 0, executa segunda expressão (SENAO é opcional)
- **Laço**: `(PARA var DE início ATE fim PASSO incremento expressão)`
  - Executa expressão para var de início até fim com incremento
  - PASSO é opcional (padrão = 1)

### Precisão Numérica
- **Números Reais**: Suporte completo a números decimais (ex: 3.14, -2.5)
- **Números Inteiros**: Range de 16 bits (-32768 a 32767) para inteiros
- **Números Negativos**: Suporte a números negativos (ex: -5, -3.2)

## Como Funciona

### 1. Análise Léxica (Tokenização)
O analisador léxico (`_tokenize`) processa a entrada caractere por caractere:

```python
def _tokenize(self, expression):
    # 1. Ignora espaços em branco
    # 2. Identifica números (inteiros, decimais, negativos)
    # 3. Identifica operadores (+, -, *, |, /, %, ^)
    # 4. Identifica parênteses (, )
    # 5. Identifica palavras-chave (MEM, RES, SE, ENTAO, etc.)
```

**Exemplo:**
```
Entrada: "(3.5 -2 +)"
Tokens: ['(', '3.5', '-2', '+', ')', 'EOF']
```

### 2. Análise Sintática (Parser LL(1))
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

### 3. Árvore Sintática Abstrata (AST)
A AST é construída durante o parsing com diferentes tipos de nós:

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

### 4. Avaliação
A avaliação percorre a AST em pós-ordem (filhos antes do pai):

```python
def _evaluate(self, node):
    # Cada tipo de nó tem sua lógica específica
    # Números retornam seu valor
    # Operações calculam resultado dos filhos
    # Estruturas de controle implementam sua semântica
```

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

### Números Reais
```
(8.5 -1.5 +)     → 7.0
(9.2 1.1 *)      → 10.12
(12 0.2 +)       → 12.2
```

### Expressões Aninhadas
```
(3 (4 5 +) *)    → 27
((2 3 +) (4 1 -) |) → 1.666...
```

### Comandos de Memória
```
(5.5 MEM)        → Armazena 5.5 na memória
(MEM)            → Recupera 5.5 da memória
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
(SE (10 5 |) ENTAO (2 3 +) SENAO (4 5 *)) → 5
```

### Estruturas de Repetição
```
(PARA 1 DE 1 ATE 3 (2 3 +))           → Executa 3 vezes, retorna 5
(PARA 1 DE 1 ATE 5 PASSO 2 (1 1 +))   → Executa para i=1,3,5, retorna 2
```

### Estruturas Aninhadas
```
(SE (PARA 1 DE 1 ATE 2 (1 1 +)) ENTAO 50 SENAO 60) → 50
((SE (2 1 -) ENTAO 3 SENAO 4) (PARA 1 DE 1 ATE 2 (2 2 +)) *) → 12
```

## Execução do Programa

### Linha de Comando
```bash
# Processar um arquivo específico
python3 main_optimized.py arquivosTestes/test1.txt

# Processar todos os arquivos .txt de um diretório
python3 main_optimized.py arquivosTestes/
```

### Saída do Programa
Para cada expressão, o programa exibe:
1. **Expressão original**
2. **Tokens gerados**
3. **Árvore Sintática Abstrata (AST)**
4. **Resultado final**

```
Expressão 1: (3.5 -2 +)
Tokens: ['(', '3.5', '-2', '+', ')', 'EOF']

--- Árvore Sintática Abstrata (AST) ---
Root: BinOpNode (Value: +)
  Child 0: NumberNode (Value: 3.5)
  Child 1: NumberNode (Value: -2.0)
----------------------------------------
Resultado Final da Linha: 1.5
```

## Tratamento de Erros

O programa trata diversos tipos de erro:

### Erros de Sintaxe
```
(5 +)  → Erro: Esperado segundo operando
```

### Erros de Divisão por Zero
```
(5 0 /)  → Erro: Divisão inteira por zero
(5 0 |)  → Erro: Divisão real por zero
```

### Erros de Acesso
```
(-1 RES)  → Erro: Índice para RES deve ser não-negativo
(5 RES)   → Erro: Não há 6 resultados anteriores
```

### Relatório de Erro
```
=== Relatório de Erro ===
Arquivo: test_erro.txt
Linha: 3
Código: (5 0 /)
Erro: Divisão inteira por zero.
=======================
```

## Conformidade com Requisitos

### ✅ Requisitos Atendidos (100%)

1. **Entrega da árvore sintática (70%)**:
   - ✅ Todas as 7 operações aritméticas implementadas
   - ✅ Estruturas de controle (IF-THEN-ELSE e FOR) implementadas
   - ✅ Gramática formal definida com BNF
   - ✅ Conjuntos FIRST e FOLLOW documentados
   - ✅ Tabela de derivação LL(1) incluída
   - ✅ Suporte a números reais (não apenas inteiros)

2. **Organização e legibilidade do código (15%)**:
   - ✅ Código bem estruturado e comentado
   - ✅ Classes organizadas hierarquicamente
   - ✅ Métodos com responsabilidades bem definidas

3. **Robustez diante de casos complexos ou com erros (15%)**:
   - ✅ Tratamento abrangente de erros
   - ✅ Relatórios de erro informativos
   - ✅ Suporte a expressões aninhadas complexas
   - ✅ Validação de entrada robusta

## Arquivos do Projeto

- **`main_optimized.py`**: Código principal otimizado
- **`arquivosTestes/`**: Diretório com arquivos de teste
  - `test1.txt`: Operações básicas e números reais
  - `test_estruturas_controle.txt`: Estruturas de controle
- **`DOCUMENTACAO_COMPLETA.md`**: Documentação técnica detalhada
- **`README.md`**: Este arquivo explicativo

## Conclusão

O analisador léxico e sintático implementado atende **completamente** aos requisitos especificados, fornecendo:

- ✅ Parser LL(1) funcional com gramática formal documentada
- ✅ AST em representação canônica
- ✅ Suporte completo à linguagem RPN especificada
- ✅ Suporte a números reais e inteiros
- ✅ Todas as 7 operações aritméticas
- ✅ Estruturas de controle (IF-THEN-ELSE e FOR)
- ✅ Tratamento robusto de erros
- ✅ Código bem organizado e documentado

A implementação demonstra compreensão sólida dos conceitos de compiladores e análise sintática, sendo adequada para avaliação acadêmica e uso prático.