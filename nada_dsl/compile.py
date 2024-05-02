"""
Compilation functions.
"""
import sys
import os.path
import base64
import json
from dataclasses import dataclass
import traceback
import importlib.util
import nada_dsl
from nada_dsl.compiler_frontend import nada_compile


@dataclass
class CompilerOutput:
    """ Compiler Output
    """
    mir: str

def compile(script_path: str) -> CompilerOutput:
    """Compiles a NADA program

    Args:
        script_path (str): The nada program path

    Returns:
        CompilerOutput: The Compiler Output
    """
    script_dir = os.path.dirname(script_path)
    sys.path.insert(0, script_dir)
    script_name = os.path.basename(script_path)
    if script_name.endswith(".py"):
        script_name = script_name[:-3]

    script = __import__(script_name)

    try:
        main = getattr(script, "nada_main")
    except:
        raise Exception("'nada_dsl' entrypoint function is missing in program " + script_name)
    outputs = main()
    compile_output = nada_compile(outputs)
    return CompilerOutput(compile_output)


def compile_string(script: str) -> CompilerOutput:
    """Compiles a NADA program from a string

    Args:
        script (str): The nada program as a base64 encoded string (UTF-8)

    Returns:
        CompilerOutput: The Compiler Output
    """
    decoded_program = base64.b64decode(script).decode('utf-8')
    temp_name = 'temp_program'
    spec = importlib.util.spec_from_loader(temp_name, loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(decoded_program, module.__dict__)
    sys.modules[temp_name] = module
    globals()[temp_name] = module

    outputs = module.nada_main()
    compile_output = nada_compile(outputs)
    return CompilerOutput(compile_output)


def print_output(output: CompilerOutput):
    """Prints compiler output

    Args:
        output (CompilerOutput): Output of the compiler
    """
    output_json = {
        "result": "Success",
        "mir": output.mir,
    }
    print(json.dumps(output_json))


if __name__ == "__main__":
    try:
        args_length = len(sys.argv)
        if args_length < 2:
            raise Exception("expected program as argument")
        if args_length == 2:
            output = compile(sys.argv[1])
            print_output(output)
        if args_length == 3 and sys.argv[1] == '-s':
            output = compile_string(sys.argv[2])
            print_output(output)

    except Exception as ex:
        tb = traceback.format_exc()
        output = {"result": "Failure", "reason": str(ex), "traceback": str(tb)}
        print(json.dumps(output))
