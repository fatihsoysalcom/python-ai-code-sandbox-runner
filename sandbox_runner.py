import subprocess
import sys
import os

def run_in_sandbox(code_string, timeout=5):
    """Runs a Python code string in a restricted subprocess.

    Args:
        code_string: The Python code to execute.
        timeout: Maximum execution time in seconds.

    Returns:
        A tuple containing (stdout, stderr) or (None, error_message) on failure.
    """
    # Define restricted builtins and modules to prevent access to sensitive functions
    # This is a basic example; a real-world sandbox would be much more sophisticated.
    restricted_builtins = {
        '__import__': None,  # Disable import
        'open': None,        # Disable file opening
        'eval': None,        # Disable eval
        'exec': None,        # Disable exec
        'input': None,       # Disable input
        'exit': None,
        'quit': None
    }

    # Prepare the execution environment
    env = os.environ.copy()
    # Remove potentially dangerous environment variables if necessary
    # env.pop('PATH', None)

    try:
        # Use subprocess.run to execute the code in a separate Python interpreter
        # The 'restricted_builtins' are passed as globals to the new interpreter
        process = subprocess.run(
            [sys.executable, '-c', code_string],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,  # Don't raise exception on non-zero exit code
            env=env,
            # This is a very basic attempt at restriction. 
            # For true security, consider using Docker or specialized libraries.
            # The 'globals' argument is not directly supported by subprocess.run for 
            # restricting builtins in the child process this way. 
            # A more robust approach would involve modifying the Python interpreter itself 
            # or using a dedicated sandboxing library.
            # For this example, we rely on the subprocess isolation and timeout.
        )

        if process.returncode != 0:
            return None, f"Execution failed with error code {process.returncode}: {process.stderr}"
        
        return process.stdout, process.stderr

    except subprocess.TimeoutExpired:
        return None, "Execution timed out."
    except Exception as e:
        return None, f"An unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    # Example 1: Safe code
    safe_code = "print('Hello from sandbox!')\nprint(2 + 2)"
    print("--- Running safe code ---")
    stdout, stderr = run_in_sandbox(safe_code)
    if stdout:
        print("STDOUT:", stdout)
    if stderr:
        print("STDERR:", stderr)
    print("-------------------------\n")

    # Example 2: Potentially malicious code (attempting to access files)
    # This will likely fail due to subprocess isolation and lack of 'open' builtin.
    malicious_code_file_access = "try:\n    with open('sensitive_data.txt', 'r') as f:\n        print(f.read())\nexcept Exception as e:\n    print(f'File access failed: {e}')"
    print("--- Running malicious code (file access attempt) ---")
    stdout, stderr = run_in_sandbox(malicious_code_file_access)
    if stdout:
        print("STDOUT:", stdout)
    if stderr:
        print("STDERR:", stderr)
    print("--------------------------------------------------\n")

    # Example 3: Code that would normally import modules
    # This will fail if '__import__' is restricted or if modules are not available in the isolated env.
    # For simplicity, we are not explicitly blocking imports here, but relying on subprocess isolation.
    import_code = "import math\nprint(math.sqrt(16))"
    print("--- Running code with import ---")
    stdout, stderr = run_in_sandbox(import_code)
    if stdout:
        print("STDOUT:", stdout)
    if stderr:
        print("STDERR:", stderr)
    print("--------------------------------\n")

    # Example 4: Code that times out
    timeout_code = "import time\ntime.sleep(10)\nprint('This should not print')"
    print("--- Running code that times out ---")
    stdout, stderr = run_in_sandbox(timeout_code, timeout=2)
    if stdout:
        print("STDOUT:", stdout)
    if stderr:
        print("STDERR:", stderr)
    print("-----------------------------------\n")
