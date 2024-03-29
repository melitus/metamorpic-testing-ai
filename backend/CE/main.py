from typing import Annotated
from ce.utils.sys_utils import run_llm_cs_sys
from ce.components.ce_logic import cd_llm_system
from fastapi import FastAPI, Form, File, UploadFile

app = FastAPI()

@app.post("/cd_llm")
async def draw_dag(var_name_desc: Annotated[str, Form()], 
                    prompt: Annotated[str, Form()], 
                    prompt_info: Annotated[str, Form()], 
                    use_stats: Annotated[bool, Form()], 
                    csv_file: Annotated[UploadFile, File()]):
    b64_result = run_llm_cs_sys(cd_llm_system, var_name_desc, csv_file, prompt, prompt_info, use_stats)
    return {"b64_result": b64_result}
