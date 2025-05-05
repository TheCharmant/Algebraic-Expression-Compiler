import ast
import operator

# Operator mapping for Binary Operations
operator_map = {
    ast.Add: '+',
    ast.Sub: '-',
    ast.Mult: '*',
    ast.Div: '/',
    ast.Mod: '%',
    ast.Pow: '**',
    ast.BitAnd: '&',
    ast.BitOr: '|',
    ast.BitXor: '^',
    ast.LShift: '<<',
    ast.RShift: '>>'
}

def compile_expression(code):
    try:
        tree = ast.parse(code)
        tac = []
        constants = {}

        def eval_expr(node):
            if isinstance(node, ast.BinOp):
                left = eval_expr(node.left)
                right = eval_expr(node.right)

                # If left or right is a raw constant, create a temporary
                if isinstance(left, (int, float)):
                    tmp_left = f"t{len(tac)}"
                    tac.append(f"{tmp_left} = {left}")
                    left = tmp_left

                if isinstance(right, (int, float)):
                    tmp_right = f"t{len(tac)}"
                    tac.append(f"{tmp_right} = {right}")
                    right = tmp_right

                op = operator_map[type(node.op)]
                tmp = f"t{len(tac)}"
                tac.append(f"{tmp} = {left} {op} {right}")
                return tmp
            elif isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.Name):
                return node.id
            else:
                return "?"

        # Generate TAC from AST
        for stmt in tree.body:
            if isinstance(stmt, ast.Assign):
                target = stmt.targets[0].id
                val = eval_expr(stmt.value)
                tac.append(f"{target} = {val}")
            else:
                tac.append("# Unsupported statement")

        # Optimization: Constant folding and propagation
        optimized_tac = []
        symbol_table = {}  # Tracks variable values

        for line in tac:
            if '=' in line:
                parts = line.split(" = ")
                var = parts[0].strip()
                expr = parts[1].strip()

                # Replace known variables in the expression
                replaced_expr = expr
                for key in sorted(symbol_table.keys(), key=lambda x: -len(x)):
                    if key in replaced_expr:
                        replaced_expr = replaced_expr.replace(key, str(symbol_table[key]))

                # Try to evaluate the replaced expression
                try:
                    value = eval(replaced_expr)
                    symbol_table[var] = value
                    # Skip adding this line since it's a constant now
                except:
                    # If evaluation fails, check for identity simplifications
                    if ' + 0' in replaced_expr:
                        replaced_expr = replaced_expr.replace(' + 0', '')
                    elif ' * 1' in replaced_expr:
                        replaced_expr = replaced_expr.replace(' * 1', '')
                    optimized_tac.append(f"{var} = {replaced_expr}")
            else:
                optimized_tac.append(line)

        # Check if the target variable (x) was optimized to a constant
        final_result = symbol_table.get('x', None)
        if final_result is not None:
            optimized_tac = [f"x = {final_result}"]
        else:
            # Fallback to original TAC if optimization didn't find a result
            optimized_tac = tac.copy()

        return {
            "tac": tac,
            "optimized_tac": optimized_tac,
            "final_result": final_result,
            "ast": ast.dump(tree, indent=4)
        }
    except Exception as e:
        return {"error": str(e)}