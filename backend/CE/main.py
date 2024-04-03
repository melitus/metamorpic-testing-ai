from typing import Annotated
from fastapi.responses import JSONResponse
from CE.ce.utils.sys_utils import run_llm_cs_sys
from CE.ce.components.ce_logic import cd_llm_system
from fastapi import FastAPI, Form, File, UploadFile, Response
from CE.ce.components.metamorphic_logic import MetaMorphicTesting

app = FastAPI()

@app.post("/cd_llm")
async def draw_dag(var_name_desc: Annotated[str, Form()], 
                    prompt: Annotated[str, Form()], 
                    prompt_info: Annotated[str, Form()], 
                    use_stats: Annotated[bool, Form()], 
                    n_aug: Annotated[int, Form()],
                    robust_test: Annotated[str, Form()],
                    csv_file: Annotated[UploadFile, File()]) -> Response:
    b64_result = run_llm_cs_sys(cd_llm_system, MetaMorphicTesting, var_name_desc, csv_file, prompt, prompt_info, use_stats, n_aug, robust_test)
    return JSONResponse(content={"b64_result": b64_result})
