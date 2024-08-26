from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess
import os
import black

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/problem/<int:problem_id>')
def problem(problem_id):
    return render_template('problem.html', problem_id=problem_id)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/execute', methods=['POST'])
def execute():
    code = request.json.get('code')
    inputs = request.json.get('inputs', "")  # Get the input data
    
    result = {"stdout": "", "stderr": ""}
    script_path = 'temp_script.py'

    try:
        # Auto-format the code using black
        formatted_code = black.format_str(code, mode=black.Mode())

        # Save the formatted code to a temporary file
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(formatted_code)
        
        # Run the formatted code with input
        process_result = subprocess.run(
            ['python', script_path],
            input=inputs,  # Directly pass inputs as str
            capture_output=True,
            text=True,     # Ensure stdout and stderr are handled as str
            timeout=10     # Increased timeout to 10 seconds
        )
        
        result["stdout"] = process_result.stdout
        result["stderr"] = process_result.stderr

    except subprocess.TimeoutExpired:
        result["stderr"] = 'Execution timed out'
    except Exception as e:
        result["stderr"] = str(e)
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
    
    return jsonify({
        'stdout': result['stdout'],
        'stderr': result['stderr'],
        'formatted_code': formatted_code  # Return the formatted code to the frontend
    })

if __name__ == '__main__':
    app.run(debug=True)
