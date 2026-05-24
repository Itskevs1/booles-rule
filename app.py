from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def booles_rule(f_values, h):
    """
    Boole's Rule numerical integration.
    Requires exactly 5 equally-spaced points (4 intervals).
    Formula: (2h/45) * [7f0 + 32f1 + 12f2 + 32f3 + 7f4]
    """
    if len(f_values) != 5:
        raise ValueError("Boole's Rule requires exactly 5 function values.")
    
    f0, f1, f2, f3, f4 = f_values
    result = (2 * h / 45) * (7*f0 + 32*f1 + 12*f2 + 32*f3 + 7*f4)
    return result

def compute_f_values(func_str, a, b):
    """Compute 5 equally spaced f(x) values from a to b."""
    import math
    h = (b - a) / 4
    x_values = [a + i * h for i in range(5)]
    
    safe_dict = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
        "pi": math.pi, "e": math.e, "abs": abs,
        "log10": math.log10, "log2": math.log2,
        "sinh": math.sinh, "cosh": math.cosh,
        "asin": math.asin, "acos": math.acos, "atan": math.atan,
    }
    
    f_values = []
    for x in x_values:
        safe_dict["x"] = x
        f_values.append(eval(func_str, {"__builtins__": {}}, safe_dict))
    
    return x_values, f_values, h

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()
        mode = data.get("mode")  # "function" or "manual"
        
        if mode == "function":
            func_str = data.get("function", "").strip()
            a = float(data.get("a"))
            b = float(data.get("b"))
            
            x_values, f_values, h = compute_f_values(func_str, a, b)
            result = booles_rule(f_values, h)
            
            steps = []
            steps.append(f"h = (b - a) / 4 = ({b} - {a}) / 4 = {h:.6f}")
            for i, (x, f) in enumerate(zip(x_values, f_values)):
                steps.append(f"f(x{i}) = f({x:.6f}) = {f:.8f}")
            
            coeffs = [7, 32, 12, 32, 7]
            weighted = [f"({coeffs[i]} × {f_values[i]:.6f})" for i in range(5)]
            steps.append(f"Weighted sum = {' + '.join(weighted)}")
            wsum = sum(coeffs[i] * f_values[i] for i in range(5))
            steps.append(f"Weighted sum = {wsum:.8f}")
            steps.append(f"Result = (2 × {h:.6f} / 45) × {wsum:.8f} = {result:.10f}")
            
            return jsonify({
                "success": True,
                "result": result,
                "steps": steps,
                "x_values": x_values,
                "f_values": f_values,
                "h": h
            })
        
        elif mode == "manual":
            f_values = [float(data.get(f"f{i}")) for i in range(5)]
            h = float(data.get("h"))
            
            result = booles_rule(f_values, h)
            
            steps = []
            steps.append(f"Given h = {h}")
            for i, f in enumerate(f_values):
                steps.append(f"f{i} = {f}")
            coeffs = [7, 32, 12, 32, 7]
            wsum = sum(coeffs[i] * f_values[i] for i in range(5))
            steps.append(f"Weighted sum = 7({f_values[0]}) + 32({f_values[1]}) + 12({f_values[2]}) + 32({f_values[3]}) + 7({f_values[4]}) = {wsum:.8f}")
            steps.append(f"Result = (2 × {h} / 45) × {wsum:.8f} = {result:.10f}")
            
            return jsonify({
                "success": True,
                "result": result,
                "steps": steps,
                "f_values": f_values,
                "h": h
            })
        
        else:
            return jsonify({"success": False, "error": "Invalid mode."})
    
    except ZeroDivisionError:
        return jsonify({"success": False, "error": "Division by zero encountered."})
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)})

if __name__ == "__main__":
    app.run(debug=True, port=8080)
