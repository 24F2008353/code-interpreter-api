from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import traceback
import re
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
        output = traceback.format_exc()

        return {
            "success": False,
            "output": output
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

    traceback_text = result["output"]

    line_numbers = [
        int(x)
        for x in re.findall(r'line (\d+)', traceback_text)
    ]

    return {
        "error": sorted(list(set(line_numbers))),
        "result": traceback_text
    }


@app.get("/")
def root():
    return {"status": "ok"}
