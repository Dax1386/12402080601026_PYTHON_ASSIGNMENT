class FormulaError(Exception): pass
class UnknownVariableError(FormulaError): pass
class UnsupportedOperatorError(FormulaError): pass
class DivisionByZeroError(FormulaError): pass

def run_calculator():
    variables = {}
    
    while True:
        try:
            line = input().strip()
            if not line or line == "quit":
                break

            if "=" in line:
                var_name, expr = line.split("=", 1)
                var_name, expr = var_name.strip(), expr.strip()
                val = eval_operand(expr, variables)
                variables[var_name] = val
                continue
                
            tokens = line.split()
            if len(tokens) != 3:
                raise FormulaError("Invalid format")

            op1_str, op, op2_str = tokens
            
            if op not in ('+', '-', '*', '/', '%'):
                raise UnsupportedOperatorError("Unsupported OperatorError")
                
            v1 = eval_operand(op1_str, variables)
            v2 = eval_operand(op2_str, variables)
            
            if op in ('/', '%') and v2 == 0:
                raise DivisionByZeroError("DivisionByZeroError")
                
            if op == '+': res = v1 + v2
            elif op == '-': res = v1 - v2
            elif op == '*': res = v1 * v2
            elif op == '/': res = v1 / v2
            elif op == '%': res = v1 % v2

            print(int(res) if isinstance(res, float) and res.is_integer() else res)

        except FormulaError as fe:
            print(fe.__class__.__name__)
        except Exception as e:
            print("FormulaError")

def eval_operand(token, variables):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            if token in variables:
                return variables[token]
            raise UnknownVariableError(f"Unknown variable '{token}'")

if __name__ == "__main__":
    run_calculator()