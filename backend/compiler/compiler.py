import ast
import operator
import re
import random

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

def preprocess_expression(code):
    """Preprocess the expression to handle implicit multiplication and exponents."""
    # Handle superscript ² (convert to **2)
    code = code.replace('²', '**2')
    
    # Handle exponents with ^ notation (convert to **)
    code = re.sub(r'(\w+)\^(\d+)', r'\1**\2', code)
    
    # Handle implicit multiplication (e.g., 3x -> 3*x)
    code = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', code)
    
    # Handle parenthesized expressions like (x+3)(x-2) -> (x+3)*(x-2)
    code = re.sub(r'\)(\()', r')*(', code)
    
    # If the expression doesn't have an assignment, add x = to the beginning
    if '=' not in code:
        code = f"x = {code}"
        
    return code

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
        # Preprocess the expression
        processed_code = preprocess_expression(code)
        
        tree = ast.parse(processed_code)
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
            elif isinstance(node, ast.UnaryOp):
                operand = eval_expr(node.operand)
                if isinstance(node.op, ast.USub):
                    if isinstance(operand, (int, float)):
                        return -operand
                    tmp = f"t{len(tac)}"
                    tac.append(f"{tmp} = -{operand}")
                    return tmp
                elif isinstance(node.op, ast.UAdd):
                    return operand
                else:
                    return "?"
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
                    # Only evaluate if all variables are numbers
                    if not any(c.isalpha() for c in replaced_expr if c not in ('e', 'j')):
                        value = eval(replaced_expr)
                        symbol_table[var] = value
                    else:
                        raise Exception("Contains variables")
                except:
                    if ' + 0' in replaced_expr:
                        replaced_expr = replaced_expr.replace(' + 0', '')
                    elif ' * 1' in replaced_expr:
                        replaced_expr = replaced_expr.replace(' * 1', '')
                    optimized_tac.append(f"{var} = {replaced_expr}")
            else:
                optimized_tac.append(line)

        # Build the AST for the first expression
        ast_tree = build_expr_tree(tree.body[0].value) if isinstance(tree.body[0], ast.Assign) else {}

        return {
            "tac": tac,
            "optimized_tac": optimized_tac,
            "original_expr": code,
            "processed_expr": processed_code,
            "ast": ast_tree
        }
    except Exception as e:
        return {"error": str(e), "original_expr": code}

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

# Add this new function to generate random expressions
def generate_random_expression():
    """Generate a random algebraic expression for testing."""
    expression_types = [
        "simple", "quadratic", "linear_multi_var", "factored", "fraction"
    ]
    expr_type = random.choice(expression_types)
    
    variables = ['x', 'y', 'z', 'a', 'b']
    
    if expr_type == "simple":
        # Simple expressions like 3x + 5
        var = random.choice(variables[:3])
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        op = random.choice(['+', '-'])
        return f"{a}{var} {op} {b}"
    
    elif expr_type == "quadratic":
        # Quadratic expressions like x² + 5x - 6
        var = random.choice(variables[:2])
        a = random.randint(1, 5)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        if a == 1:
            return f"{var}² {'+' if b >= 0 else ''} {b}{var} {'+' if c >= 0 else ''} {c}"
        else:
            return f"{a}{var}² {'+' if b >= 0 else ''} {b}{var} {'+' if c >= 0 else ''} {c}"
    
    elif expr_type == "linear_multi_var":
        # Multi-variable expressions like 4a - 7b + 2
        var1, var2 = random.sample(variables, 2)
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        c = random.randint(0, 10)
        return f"{a}{var1} - {b}{var2} {'+' if c > 0 else ''} {c if c > 0 else ''}"
    
    elif expr_type == "factored":
        # Factored expressions like (x + 3)(x - 2)
        var = random.choice(variables[:2])
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)
        return f"({var} {'+' if a >= 0 else ''} {a})({var} {'+' if b >= 0 else ''} {b})"
    
    elif expr_type == "fraction":
        # Fractions like (3x/2) + (7y/4)
        var1, var2 = random.sample(variables[:3], 2)
        a = random.randint(1, 10)
        b = random.randint(2, 6)
        c = random.randint(1, 10)
        d = random.randint(2, 6)
        return f"({a}{var1}/{b}) + ({c}{var2}/{d})"
    
    return "x + 1"  # Default fallback
