# Calculadora RPN - Analisador Léxico e Sintático

## Visão Geral

Este projeto implementa uma calculadora para **Notação Polonesa Reversa (RPN)** com análise léxica e sintática completa. A versão otimizada reduz significativamente a complexidade do código original mantendo toda a funcionalidade.

## Principais Otimizações Realizadas

### 1. **Redução de Código**
- **Original**: 589 linhas
- **Otimizado**: 450 linhas
- **Redução**: ~24% menos código

### 2. **Simplificações Implementadas**

#### **Remoção de Código Não Utilizado**
- Removidas funções de conversão IEEE 754 (`convertFloatToHalf`, `convertHalfToFloat`)
- Eliminada classe `ProgramNode` desnecessária

#### **Otimização das Classes AST**
- Simplificação dos construtores usando atribuição múltipla
- Consolidação da lógica de adição de filhos no `ForNode`

#### **Melhoria do Tokenizador**
- Uso de string literal para operadores: `'+-*|/%^()'`
- Lógica mais direta e legível

#### **Refatoração das Operações Matemáticas**
- Uso de dicionário com lambdas para operações
- Métodos auxiliares para tratamento de erros
- Eliminação de repetição de código

#### **Simplificação dos Métodos do Parser**
- Nomes de métodos mais concisos (`_current_token`, `_advance`, `_evaluate`)
- Consolidação de verificações de tipo
- Redução de duplicação de lógica

## Arquitetura do Sistema

### **Componentes Principais**

```
RPNCalculator
├── Análise Léxica (_tokenize)
├── Análise Sintática (_parse_*)
├── Construção da AST (ASTNode classes)
├── Avaliação (_evaluate)
└── Processamento de Arquivos
```

## Classes da AST (Árvore de Sintaxe Abstrata)

### **Hierarquia de Classes**

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

### **Funcionalidades de Cada Classe**

#### **ASTNode**
- Classe base para todos os nós
- Gerencia filhos e valor do nó
- Fornece representação string para debug

#### **NumberNode**
- Representa números literais (inteiros e decimais)
- Suporta números negativos

#### **BinOpNode**
- Operações aritméticas: `+`, `-`, `*`, `|`, `/`, `%`, `^`
- `|` = divisão real
- `/` = divisão inteira
- `%` = módulo
- `^` = potenciação

#### **MemAccessNode / MemStoreNode**
- `(MEM)` - acessa valor da memória
- `(V MEM)` - armazena valor V na memória

#### **ResAccessNode**
- `(N RES)` - acessa o N-ésimo resultado anterior
- N=0 = último resultado, N=1 = penúltimo, etc.

#### **IfNode**
- `(SE condição ENTAO expressão SENAO expressão)`
- SENAO é opcional
- Condição ≠ 0 = verdadeiro

#### **ForNode**
- `(PARA var DE início ATE fim PASSO incremento expressão)`
- PASSO é opcional (padrão = 1)
- Executa expressão para cada valor da variável

## Análise Léxica (Tokenização)

### **Processo de Tokenização**

1. **Espaços em branco**: Ignorados
2. **Operadores**: `+`, `-`, `*`, `|`, `/`, `%`, `^`, `(`, `)`
3. **Números**: Inteiros, decimais e negativos
4. **Palavras-chave**: `MEM`, `RES`, `SE`, `ENTAO`, `SENAO`, `PARA`, `DE`, `ATE`, `PASSO`

### **Exemplo de Tokenização**

```
Entrada: "(3 4 +)"
Tokens: ['(', '3', '4', '+', ')', 'EOF']
```

## Análise Sintática (Parser LL(1))

### **Gramática Suportada**

```
Linha ::= Expressao | IfDeclaracao | ForDeclaracao
Expressao ::= '(' Termo Termo OP_ARITMETICA ')'
            | ComandoEspecial
            | NUMERO
Termo ::= Expressao | NUMERO
ComandoEspecial ::= '(' 'MEM' ')'
                  | '(' NUMERO 'MEM' ')'
                  | '(' NUMERO 'RES' ')'
IfDeclaracao ::= '(' 'SE' Expressao 'ENTAO' Expressao ('SENAO' Expressao)? ')'
ForDeclaracao ::= '(' 'PARA' NUMERO 'DE' NUMERO 'ATE' NUMERO ('PASSO' NUMERO)? Expressao ')'
```

### **Métodos do Parser**

- `_parse_line()`: Ponto de entrada, decide o tipo de declaração
- `_parse_expression()`: Analisa expressões RPN e comandos especiais
- `_parse_term()`: Analisa termos (números ou sub-expressões)
- `_parse_if()`: Analisa estruturas condicionais
- `_parse_for()`: Analisa estruturas de repetição
- `_parse_number()`: Cria nós de números

## Avaliação da AST

### **Processo de Avaliação**

O método `_evaluate()` percorre a AST recursivamente:

1. **NumberNode**: Retorna o valor numérico
2. **BinOpNode**: Avalia operandos e aplica operação
3. **MemAccessNode**: Retorna valor da memória
4. **MemStoreNode**: Armazena valor na memória
5. **ResAccessNode**: Acessa resultado anterior
6. **IfNode**: Avalia condição e executa branch apropriado
7. **ForNode**: Executa loop com variável de controle

### **Tratamento de Erros**

- **ZeroDivisionError**: Divisão por zero
- **TypeError**: Tipos incompatíveis para operação
- **ValueError**: Valores inválidos (ex: índice negativo para RES)
- **IndexError**: Acesso a resultado inexistente
- **SyntaxError**: Erro de sintaxe na expressão

## Exemplos de Uso

### **Operações Básicas**
```
(3 4 +)          → 7
(10 3 -)         → 7
(5 2 *)          → 10
(8 2 |)          → 4.0 (divisão real)
(8 3 /)          → 2 (divisão inteira)
(8 3 %)          → 2 (módulo)
(2 3 ^)          → 8 (potenciação)
```

### **Comandos de Memória**
```
(5 MEM)          → Armazena 5 na memória
(MEM)            → Acessa valor da memória (5)
```

### **Acesso a Resultados**
```
(3 4 +)          → 7 (resultado 0)
(2 3 *)          → 6 (resultado 1)
(0 RES)          → 6 (último resultado)
(1 RES)          → 7 (penúltimo resultado)
```

### **Estruturas Condicionais**
```
(SE (5 3 -) ENTAO 10 SENAO 20)     → 10 (condição = 2 ≠ 0)
(SE (3 3 -) ENTAO 10 SENAO 20)     → 20 (condição = 0)
```

### **Estruturas de Repetição**
```
(PARA 1 DE 1 ATE 3 (1 2 +))        → Executa (1 2 +) 3 vezes, retorna 3
(PARA 1 DE 1 ATE 5 PASSO 2 (1 1 +)) → Executa para i=1,3,5, retorna 2
```

## Processamento de Arquivos

### **Funcionalidades**

- **Arquivo único**: Processa arquivo .txt especificado
- **Diretório**: Processa todos os arquivos .txt do diretório
- **Escopo por arquivo**: Memória e resultados são limpos entre arquivos
- **Comentários**: Linhas iniciadas com `#` são ignoradas
- **Linhas vazias**: Ignoradas automaticamente

### **Formato de Saída**

Para cada linha processada:
```
Expressão 1: (3 4 +)
Tokens: ['(', '3', '4', '+', ')', 'EOF']

--- Árvore Sintática Abstrata (AST) ---
Root: BinOpNode (Value: +)
  Child 0: NumberNode (Value: 3.0)
  Child 1: NumberNode (Value: 4.0)
----------------------------------------
Resultado Final da Linha: 7.0
```

## Como Executar

### **Linha de Comando**
```bash
python3 main_optimized.py arquivo.txt
python3 main_optimized.py diretorio/
```

### **Estrutura de Arquivo de Teste**
```
# Comentário - ignorado
(3 4 +)
(5 MEM)
(MEM)
(0 RES 2 *)
```

## Melhorias da Versão Otimizada

### **Performance**
- Menos overhead de métodos
- Estruturas de dados mais eficientes
- Menos verificações redundantes

### **Manutenibilidade**
- Código mais limpo e legível
- Métodos com responsabilidades bem definidas
- Nomes mais descritivos e concisos

### **Robustez**
- Tratamento de erro mais consistente
- Validações consolidadas
- Mensagens de erro mais claras

## Limitações e Considerações

### **Limitações Atuais**
- Números de ponto flutuante seguem precisão padrão do Python
- Variáveis de loop em FOR não são utilizadas na expressão
- Escopo de memória e resultados é por arquivo

### **Possíveis Extensões**
- Suporte a variáveis nomeadas
- Funções definidas pelo usuário
- Operações com strings
- Estruturas de dados mais complexas

## Conclusão

A versão otimizada mantém toda a funcionalidade do código original enquanto oferece:
- **24% menos código**
- **Melhor legibilidade**
- **Estrutura mais organizada**
- **Manutenção mais fácil**
- **Performance equivalente**

O sistema implementa com sucesso um analisador léxico e sintático completo para RPN, demonstrando conceitos fundamentais de compiladores de forma prática e educativa.