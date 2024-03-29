import json
import base64
import tempfile
from ..config.config import CEConfig

def b64_encode(obj_path):
    enc_byte = base64.b64encode(open(obj_path, "rb").read())
    b64_result = str(enc_byte, encoding='utf-8')
    return b64_result

def run_llm_cs_sys(cd_llm_sys_obj, var_name_desc, csv_file_obj, prmpt_type, prmpt_info, use_stat):
    csv_data_path = None
    with tempfile.TemporaryDirectory(dir=CEConfig.tmp_dir) as temp_dir:
        if csv_file_obj.filename != "":
            csv_data_path = f"{temp_dir}/{csv_file_obj.filename}"
            with open(csv_data_path, "wb+") as file_object:
                file_object.write(csv_file_obj.file.read())
        variable_dict = json.loads(var_name_desc)
        result = cd_llm_sys_obj(var_name_desc_dict=variable_dict, data_path=csv_data_path, prompt_type= prmpt_type, prompt_info=prmpt_info,  include_statistics= use_stat, tmp_dir=temp_dir)
        # convert to base64
        return b64_encode(result)
        
