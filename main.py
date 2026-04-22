import os
from Lexer import JavaLexer

TESTS = "01"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(BASE_DIR, "tests", TESTS)

FICHEROS = [f for f in os.listdir(DIR) if f.endswith('.java')]

for fich in FICHEROS:
    lexer = JavaLexer()
    with open(os.path.join(DIR, fich), 'r', newline='') as f:
        entrada = f.read()
    
    tokens = list(lexer.tokenize(entrada))
    
    # format output as #lineno TYPE
    output = '\n'.join([f'#{tok.lineno} {tok.type}' for tok in tokens])
    
    # read expected output
    expected_path = os.path.join(DIR, os.path.splitext(fich)[0] + '.expected')
    with open(expected_path, 'r') as f:
        esperado = f.read().strip()

    # write actual output
    out_path = os.path.join(DIR, os.path.splitext(fich)[0] + '.out')
    with open(out_path, 'w') as f:
        f.write(output)

    # compare outputs
    if output.strip() != esperado.strip():
        print(f"FAIL: {fich}")
    else:
        print(f"OK: {fich}")