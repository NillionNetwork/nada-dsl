import sys
import os.path
import json
from dataclasses import dataclass
import traceback


@dataclass
class CompileOutput:
    mir: str
    nada_dsl_path: str


def transform_program(script_path: str) -> CompileOutput:
    script_dir = os.path.dirname(script_path)
    sys.path.insert(0, script_dir)
    script_name = os.path.basename(script_path)
    if script_name.endswith(".py"):
        script_name = script_name[:-3]

    script = __import__(script_name)

    import nada_dsl
    from nada_dsl.compiler_frontend import nada_compile

    try:
        main = getattr(script, "nada_main")
    except:
        raise Exception("'nada_dsl' entrypoint function is missing in program " + script_name)
    outputs = main()
    compile_output = nada_compile(outputs)
    nada_dsl_path = nada_dsl.__path__[0]
    return CompileOutput(compile_output, nada_dsl_path)


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise Exception("expected program as argument")
        output = transform_program(sys.argv[1])
        output = {
            "result": "Success",
            "mir": output.mir,
            "nada_dsl_path": output.nada_dsl_path,
        }
        print(json.dumps(output))
    except Exception as ex:
        tb = traceback.format_exc()
        output = {"result": "Failure", "reason": str(ex), "traceback": str(tb)}
        print(json.dumps(output))
