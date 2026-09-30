import sys

def solve_expression():
    lines = sys.stdin.read().splitlines()
    if not lines:
        return
    
    num_vars = int(lines[0].strip())
    var_map = {}
    
    for i in range(1, num_vars + 1):
        name, expr = lines[i].split('=', 1)
        var_map[name.strip()] = expr.strip()
        
    target_expr = lines[num_vars + 1].strip()
    
    memo = {}
    visiting = set()
    
    def tokenize(expr):
        tokens = []
        i = 0
        while i < len(expr):
            if expr[i].isspace():
                i += 1
            elif expr[i] in '+-*()':
                tokens.append(expr[i])
                i += 1
            elif expr[i].isalnum():
                val = ""
                while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                    val += expr[i]
                    i += 1
                tokens.append(val)
            else:
                raise ValueError("INVALID")
        return tokens

    def parse_eval(tokens):
        # Standard Shunting-yard or recursive descent parser for +, -, *
        def parse_tokens(toks):
            def parse_expr(i):
                val, i = parse_term(i)
                while i < len(toks) and toks[i] in ('+', '-'):
                    op = toks[i]
                    right, i = parse_term(i + 1)
                    val = val + right if op == '+' else val - right
                return val, i

            def parse_term(i):
                val, i = parse_factor(i)
                while i < len(toks) and toks[i] == '*':
                    right, i = parse_factor(i + 1)
                    val = val * right
                return val, i

            def parse_factor(i):
                if toks[i] == '(':
                    val, i = parse_expr(i + 1)
                    if i >= len(toks) or toks[i] != ')':
                        raise ValueError("INVALID")
                    return val, i + 1
                elif toks[i].isdigit():
                    return int(toks[i]), i + 1
                elif toks[i].isidentifier():
                    return eval_var(toks[i]), i + 1
                else:
                    raise ValueError("INVALID")
            
            res, next_i = parse_expr(0)
            if next_i != len(toks):
                raise ValueError("INVALID")
            return res

        return parse_tokens(tokens)

    def eval_var(var):
        if var in memo:
            return memo[var]
        if var in visiting:
            raise RecursionError("CYCLE")
        if var not in var_map:
            raise ValueError("INVALID")
            
        visiting.add(var)
        val = parse_eval(tokenize(var_map[var]))
        visiting.remove(var)
        memo[var] = val
        return val

    try:
        ans = parse_eval(tokenize(target_expr))
        print(ans)
    except RecursionError:
        print("CYCLE")
    except Exception:
        print("INVALID")

if __name__ == "__main__":
    solve_expression()