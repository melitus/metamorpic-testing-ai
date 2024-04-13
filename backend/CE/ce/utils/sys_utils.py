import json
import base64
import tempfile
from ..config.config import CEConfig

def b64_encode(obj_path):
    enc_byte = base64.b64encode(open(obj_path, "rb").read())
    b64_result = str(enc_byte, encoding='utf-8')
    return b64_result

def run_llm_cs_sys(cd_llm_sys_obj, metamorphic_obj, var_name_desc, csv_file_obj, prmpt_type, prmpt_info, use_stat, n_aug, robust_test):
    csv_data_path = None
    with tempfile.TemporaryDirectory(dir=CEConfig.tmp_dir) as temp_dir:
        if csv_file_obj != None:
            csv_data_path = f"{temp_dir}/{csv_file_obj.filename}"
            with open(csv_data_path, "wb+") as file_object:
                file_object.write(csv_file_obj.file.read())

        variable_dict = json.loads(var_name_desc)

        if "metamorphic" in prmpt_type:
            n_aug = [n_aug]
            robust_tests = [robust_test]
            mt_tester = metamorphic_obj(cd_llm_sys_obj,tests=["robustness"], n_aug=n_aug, robust_tests=robust_tests)
            result = mt_tester.run_test(var_name_desc_dict=variable_dict, csv_data_path=csv_data_path, prmpt_type=prmpt_type, prmpt_info=prmpt_info, use_stat=use_stat, temp_dir=temp_dir)
        else:
            result = cd_llm_sys_obj(var_name_desc_dict=variable_dict, data_path=csv_data_path, prompt_type= prmpt_type, prompt_info=prmpt_info,  include_statistics= use_stat, tmp_dir=temp_dir)
        # convert to base64
        return b64_encode(result)
        
