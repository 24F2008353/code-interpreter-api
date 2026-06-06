from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import traceback
from io import StringIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code, {})
        output = sys.stdout.getvalue()

        return {
            "success": True,
            "output": output
        }

    except Exception:
        tb = traceback.extract_tb(sys.exc_info()[2])

        line_numbers = []

        for frame in tb:
            if frame.filename == "<string>":
                line_numbers = [frame.lineno]

        output = traceback.format_exc()

        return {
            "success": False,
            "output": output,
            "line_numbers": line_numbers
        }

    finally:
        sys.stdout = old_stdout


@app.post("/code-interpreter")
def code_interpreter(req: CodeRequest):

    result = execute_python_code(req.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    return {
        "error": result.get("line_numbers", []),
        "result": result["output"]
    }


@app.get("/")
def root():
    return {"status": "ok"}
