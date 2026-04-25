import os
import networkx as nx
from Lexer import JavaLexer
from Parser import JavaParser
from CFG import CFGBuilder

TESTS = "03" 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(BASE_DIR, "tests", TESTS)

FICHEROS = [f for f in os.listdir(DIR) if f.endswith('.java')]

for fich in FICHEROS:
    print(f'\n=== Processing: {fich} ===')
    filepath = os.path.join(DIR, fich)
    with open(filepath, 'r') as f:
        source = f.read()

    lexer = JavaLexer()
    tokens = list(lexer.tokenize(source))
    
    parser = JavaParser(filename=fich)
    program = parser.parse(iter(tokens))
    if parser.errors:
        print(f"  [!] Parse Errors: {parser.errors}")
        continue

    builder = CFGBuilder()
    builder.scope.filename = fich
    # build() returns a dict of graphs (one per method)
    graphs = builder.build(program)

    if builder.errors:
        print(f"  [!] Semantic Errors: {builder.errors}")

    # temporally here to start trying out some tests
    print(f"  Results for folder {TESTS}:")
    for method_full_name, data in graphs.items():
        g = data['graph']
        nodes = g.number_of_nodes()
        edges = g.number_of_edges()
        
        # M = E - N + 2P (P=1 for a single method)
        complexity = edges - nodes + 2
        
        print(f"    Method: {method_full_name}")
        print(f"    Nodes: {nodes}, Edges: {edges}")
        print(f"    Cyclomatic Complexity: {complexity}")
        
        # Verify the execution path was tracked
        path_len = len(data['execution_path'])
        print(f"    Nodes in highlighted path: {path_len}")