import random
from ..config.config import CEConfig

class Robustness:
  def __init__(self,n=1):
    self.n = n #number of perturbs (character level)
    self.hold_n = None

  def set_n(self,n):
    self.n = n

  def compare_text_len_with_n(self, text):
    if len(text) < self.n:
      print("Number of perturb iterations is equal to the length of text.\nResetting perturb iterations to length of (text-1) to perform MT.")
      self.hold_n = self.n
      self.n =  len(text) - 1

  def reset_n(self):
    if self.hold_n is not None:
      print("Resetting perturb iterations back to original value.")
      self.n = self.hold_n

  def _get_random_id(self, start, end):
    vals = [random.randint(start,end) for _ in range(self.n)]
    return vals

  def get_text_info(self, text):
    start_ = 0
    end_ = len(text) - 1
    random_ids = self._get_random_id(start_, end_)
    return start_, end_, random_ids

  def swap(self, text):
    self.compare_text_len_with_n(text)
    start_, end_, random_ids = self.get_text_info(text)

    text_list = list(text)
    for i in range(len(random_ids)):
      val = random_ids[i]
      nxv_val = val + 1
      if nxv_val > end_ :
        pre_val = val-1
        text_list[val], text_list[pre_val] = text_list[pre_val], text_list[val]
      else:
        text_list[val], text_list[nxv_val] = text_list[nxv_val], text_list[val]

    swapped_text = "".join(text_list)
    self.reset_n()
    return swapped_text

  def char_delete(self, text):
    self.compare_text_len_with_n(text)
    start_, end_, random_ids = self.get_text_info(text)
    text_list = list(text)
    for id in random_ids:
      text_list[id] = ""
    char_delete_text = "".join(text_list)
    self.reset_n()
    return char_delete_text

  def add_char(self,text):
    self.compare_text_len_with_n(text)
    start_, end_, random_ids = self.get_text_info(text)
    random_ids_values = [text[id] for id in random_ids]
    abc_list = ["a", "b", "c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    exra_char_text = text
    for riv in random_ids_values:
      rand_char = random.choice(abc_list)
      exra_char_text = exra_char_text.replace(riv, f"{rand_char}{riv}",1)
    return exra_char_text


  def add_space(self, text):
    self.compare_text_len_with_n(text)
    start_, end_, random_ids = self.get_text_info(text)
    random_ids_values = [text[id] for id in random_ids]
    spaced_text = text
    for riv in random_ids_values:
      spaced_text = spaced_text.replace(riv, f"  {riv}",1)
    self.reset_n()
    return spaced_text

  def add_number(self, text):
    self.compare_text_len_with_n(text)
    start_, end_, random_ids = self.get_text_info(text)
    random_ids_values = [text[id] for id in random_ids]
    numbered_text = text
    for riv in random_ids_values:
      rand_val = random.randint(0,9)
      numbered_text = numbered_text.replace(riv, f"{rand_val}{riv}",1)
    self.reset_n()
    return numbered_text

  def swap_with_number(self, text):
    self.compare_text_len_with_n(text)
    start_, end_, random_ids = self.get_text_info(text)
    random_ids_values = [text[id] for id in random_ids]
    mapper = {t:i for i,t in enumerate(text)}
    number_swapped_text = text
    for riv in random_ids_values:
      number_swapped_text  = number_swapped_text.replace(riv, str(mapper[riv]),1)
    self.reset_n()
    return number_swapped_text

  def synonym_sub(self, text):
      prompt_base=[
      {
        "role": "system",
        "content": """You synonym assitant, convert  the provided word with its synonym.
                    If it is a sentence rephrase, the sentence entirely but make sure to retain the original meaning.
                    If you don't know what to do return the original text."""
      },
      {
        "role": "user",
        "content": f"You are a helpful assistant, kindly help me with this text: {text}.\nProvide your final answer within the tags <Answer>...</Answer>"
      }
      ]
      client = OpenAI(api_key=CEConfig.openai_api)
      model = CEConfig.openai_model_ver
      temperature = 0.2
      response = client.chat.completions.create(
                        model=model,
                        messages=prompt_base,
                        temperature=temperature,
                        max_tokens=4095,
                        frequency_penalty=0,
                        presence_penalty=0)

      answer = response.choices[0].message.content
      answer = answer.split('<Answer>')[1].split('</Answer>')[0].split(', ')
      return answer[0]

  def run(self, text, type_):
    if type_ == "swap":
      return self.swap(text)
    elif type_ == "char_delete":
      return self.char_delete(text)
    elif type_ == "add_char":
      return self.add_char(text)
    elif type_ == "add_space":
      return self.add_space(text)
    elif type_ == "add_number":
      return self.add_number(text)
    elif type_ == "swap_with_number":
      return self.swap_with_number(text)
    elif type_ == "synonym_sub":
      return self.synonym_sub(text)

class MetaMorphicTesting:
  def __init__(self, cd_llm_sys, tests, n_aug, robust_tests):
    self.cd_llm_sys = cd_llm_sys
    self.robustness = Robustness()
    self.tests = tests
    self.pipeline = self.setup_test_process(n_aug, robust_tests)
    self.mtv_nhd_ratio = .35
    self.mtv_f1 = .65


  def setup_test_process(self, n_aug, robust_tests):
    pipeline = []
    for test in self.tests:
      mt_dict_info = {}
      if test == "robustness":
        mt_dict_info["robustness"] = {}
        mt_dict_info["robustness"]["n_peturbs"] = n_aug
        mt_dict_info["robustness"]["peturb_type"] = robust_tests
      pipeline.append(mt_dict_info)
    print(pipeline)
    return pipeline

  def _calculate_mt_robustness(self, metrics):
    f1 = metrics["F1_score"]
    nhd_rat = metrics["NHD_RATIO"]

    if f1 >= self.mtv_f1 and nhd_rat <= self.mtv_nhd_ratio:
      return True
    else:
      return False

  def _calculate_mt_non_determinism(self, metrics_list):
    f1_sum = 0
    nhd_rat_sum = 0
    no_iter = len(metrics_list)

    for val in metrics_list:
       nhd_rat_sum += val["NHD_RATIO"]

    for val in metrics_list:
      f1_sum += val['F1_score']

    f1_mean = f1_sum/ no_iter
    nhd_rat_mean =  nhd_rat_sum/ no_iter

    if f1_mean >= self.mtv_f1 and nhd_rat_mean <= self.mtv_nhd_ratio:
      return True
    else:
      return False

  def _calculate_mt_relation_result(self, metrics, type_):
    if type_ == "robustness":
      return self._calculate_mt_robustness(metrics)
    elif type_ == "non_determinism":
      return self._calculate_mt_non_determinism(metrics)

  def _handle_description(self, description, object, pertub_type):
    if pertub_type != "synonym_sub":
      desc_list = description.split()
      for i, desc in enumerate(desc_list):
        desc_list[i] = object.run(desc, pertub_type)
      desc = " ".join(desc_list)
      return desc
    else:
      result = object.run(description, pertub_type)
      return result
  def _handle_name(self, name, object, pertub_type):
    name_list = name.split()
    for i, tmp_name in enumerate(name_list):
      name_list[i] = object.run(tmp_name, pertub_type)
    name = " ".join(name_list)
    return name


  def run_test(self, var_name_desc_dict, csv_data_path, prmpt_type, prmpt_info, use_stat, temp_dir):
    total_result = []
    for mt in self.pipeline:
      if "robustness" in mt:
        for n in mt["robustness"]["n_peturbs"]:
          self.robustness.set_n(n=n)
          for pertub_type in mt["robustness"]["peturb_type"]:
            name_desc = [var for var in var_name_desc_dict]
            tmp_aug_map = {}
            for var in name_desc:
              orig_var = var_name_desc_dict[var]["var_name"]
              orig_desc = var_name_desc_dict[var]["var_desc"]
              var_name_desc_dict[var]["var_name"] = self. _handle_name(orig_var, self.robustness, pertub_type) #self.robustness.run(orig_var, pertub_type)
              var_name_desc_dict[var]["var_desc"]  = self._handle_description(orig_desc, self.robustness, pertub_type)
              tmp_aug_map[var_name_desc_dict[var]["var_name"]] = orig_var
            mt_result = self.cd_llm_sys(var_name_desc_dict=var_name_desc_dict, data_path=csv_data_path, prompt_type=prmpt_type, prompt_info=prmpt_info,aug_map=tmp_aug_map,include_statistics=use_stat, tmp_dir=temp_dir)
        total_result.append(mt_result)
    return total_result[0]