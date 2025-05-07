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

def ast_to_dict(node):
    if isinstance(node, ast.AST):
        result = {'type': node.__class__.__name__}
        for field in node._fields:
            value = getattr(node, field)
            if isinstance(value, ast.AST):
                result[field] = ast_to_dict(value)
            elif isinstance(value, list):
                result[field] = [ast_to_dict(item) if isinstance(item, ast.AST) else item for item in value]
            else:
                result[field] = value
        return result
    else:
        return node


def compile_expression(code):
    try:
        tree = ast.parse(code)
        tac = []
        constants = {}

        def eval_expr(node):
            if isinstance(node, ast.BinOp):
                left = eval_expr(node.left)
                right = eval_expr(node.right)

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
        symbol_table = {}

        for line in tac:
            if '=' in line:
                parts = line.split(" = ")
                var = parts[0].strip()
                expr = parts[1].strip()

                replaced_expr = expr
                for key in sorted(symbol_table.keys(), key=lambda x: -len(x)):
                    if key in replaced_expr:
                        replaced_expr = replaced_expr.replace(key, str(symbol_table[key]))

                try:
                    value = eval(replaced_expr)
                    symbol_table[var] = value
                except:
                    if ' + 0' in replaced_expr:
                        replaced_expr = replaced_expr.replace(' + 0', '')
                    elif ' * 1' in replaced_expr:
                        replaced_expr = replaced_expr.replace(' * 1', '')
                    optimized_tac.append(f"{var} = {replaced_expr}")
            else:
                optimized_tac.append(line)

        final_result = symbol_table.get('x', None)
        if final_result is not None:
            optimized_tac = [f"x = {final_result}"]
        else:
            optimized_tac = tac.copy()

        # Build the AST for the first expression
        ast_tree = build_expr_tree(tree.body[0].value) if isinstance(tree.body[0], ast.Assign) else {}

        return {
            "tac": tac,
            "optimized_tac": optimized_tac,
            "final_result": final_result,
            "ast": ast_tree  # Make sure this is the right structure
        }
    except Exception as e:
        return {"error": str(e)} 

def build_expr_tree(node):
    # Handle the BinOp, Constant, and Name nodes
    if isinstance(node, ast.BinOp):
        return {
            "value": operator_map.get(type(node.op), '?'),
            "children": [
                build_expr_tree(node.left),
                build_expr_tree(node.right)
            ]
        }
    elif isinstance(node, ast.Constant):
        return {
            "value": str(node.value),
            "children": []
        }
    elif isinstance(node, ast.Name):
        return {
            "value": node.id,
            "children": []
        }
    else:
        return {
            "value": "?",
            "children": []
        }
