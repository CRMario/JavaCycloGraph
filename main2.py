import os
from Lexer import JavaLexer
from Parser import JavaParser
from CFG import CFGBuilder
from Visualizer import visualize_all
from Scope import SemanticException

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_lexer_tests():
    DIR = os.path.join(BASE_DIR, "tests", "01")
    if not os.path.exists(DIR):
        return
    print("=== 01: LEXER ===")
    for fich in sorted(f for f in os.listdir(DIR) if f.endswith('.java')):
        lexer = JavaLexer()
        with open(os.path.join(DIR, fich), 'r', newline='') as f:
            source = f.read()

        tokens = list(lexer.tokenize(source))
        output = '\n'.join(f'#{tok.lineno} {tok.type}' for tok in tokens)

        expected_path = os.path.join(DIR, os.path.splitext(fich)[0] + '.expected')
        if os.path.exists(expected_path):
            with open(expected_path, 'r') as f:
                expected = f.read().strip()
            status = 'OK' if output.strip() == expected else 'FAIL'
        else:
            status = 'NO_EXPECTED'

        out_path = os.path.join(DIR, os.path.splitext(fich)[0] + '.out')
        with open(out_path, 'w') as f:
            f.write(output)

        print(f'  [{status}] {fich}')


def run_parser_tests():
    DIR = os.path.join(BASE_DIR, "tests", "02")
    if not os.path.exists(DIR):
        return
    print("=== 02: PARSER ===")
    for fich in sorted(f for f in os.listdir(DIR) if f.endswith('.java')):
        lexer = JavaLexer()
        with open(os.path.join(DIR, fich), 'r', newline='') as f:
            source = f.read()

        tokens = lexer.tokenize(source)
        parser = JavaParser(filename=fich)
        program = parser.parse(tokens)

        out_path = os.path.join(DIR, os.path.splitext(fich)[0] + '.out')
        if parser.errors:
            with open(out_path, 'w') as f:
                f.write('\n'.join(parser.errors))
            print(f'  [ERRORS] {fich}')
            for e in parser.errors:
                print(f'    {e}')
        else:
            with open(out_path, 'w') as f:
                f.write('OK')
            print(f'  [OK] {fich}')


def run_cfg_tests():
    DIR = os.path.join(BASE_DIR, "tests", "03")
    if not os.path.exists(DIR):
        return
    print("=== 03: CFG ===")
    OUTPUT_DIR = os.path.join(BASE_DIR, "cfg_output")

    for fich in sorted(f for f in os.listdir(DIR) if f.endswith('.java')):
        print(f'\n  {fich}')
        with open(os.path.join(DIR, fich), 'r', newline='') as f:
            source = f.read()

        # lex
        lexer = JavaLexer()
        tokens = lexer.tokenize(source)

        # parse
        parser = JavaParser(filename=fich)
        program = parser.parse(tokens)

        if parser.errors:
            print('    [PARSE ERRORS]')
            for e in parser.errors:
                print(f'      {e}')
            out_path = os.path.join(DIR, os.path.splitext(fich)[0] + '.out')
            with open(out_path, 'w') as f:
                f.write('\n'.join(parser.errors))
            continue

        # build CFG
        builder = CFGBuilder()
        graphs = builder.build(program)

        # write .out if there are semantic errors
        out_path = os.path.join(DIR, os.path.splitext(fich)[0] + '.out')
        if builder.errors:
            print('    [SEMANTIC ERRORS]')
            for e in builder.errors:
                print(f'      {e}')
            with open(out_path, 'w') as f:
                f.write('\n'.join(builder.errors))
        else:
            with open(out_path, 'w') as f:
                f.write('OK')

        # cyclomatic complexity summary
        for method_name, gdata in graphs.items():
            g = gdata['graph']
            cc = g.number_of_edges() - g.number_of_nodes() + 2
            print(f'    {method_name}: CC={cc}')

        # visualize
        method_output_dir = os.path.join(OUTPUT_DIR, os.path.splitext(fich)[0])
        visualize_all(graphs, output_dir=method_output_dir, errors=builder.errors)


if __name__ == '__main__':
    run_lexer_tests()
    run_parser_tests()
    run_cfg_tests()