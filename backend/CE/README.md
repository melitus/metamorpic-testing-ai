# Cause & Effect Backend System

### INTRODUCTION & AIM:
The cause & effect backend system is an ML system that utilize large language model's (GPT4) pre-trained knowledge for the purpose of causal discovery.

### Repository Breakdown:

##### INDSIDE ```backend/CE``` FOLDER:
1. ```ce```: This module contains causal disovery scripts and configuration.
2. ```main.py```: This script runs the application as a fastapi server.
3. ```requirements.txt```: this contains the requirements configuration.

##### INDSIDE ```ce``` FOLDER:
1. ```components/ce_logic.py```: This script contains the caual discovery using llms logic.
2. ```components/metamorphic_logic.py```: This script contais the metamorphic testing logic.
3. ```config/config.py```: This script contains system configurations.
4. ```util/sys_utils.py```: This script contains utility functions.

### How to run the Cause & Effect Backend System locally:
1. Create and activate a virtual environment: ```python3 -m venv _name_of_virtual_env_```.
2. Install dependencies using: ```pip install -r requirements.txt```.
3. Create a ```.env``` file and set the following variables:
    ```Request for the environment variables from the developer in charge.```,
  
5. Run the server locally using: ```uvicorn main:app --reload```

### Endpoints:
```local server```: ```http://127.0.0.1:8000```; 
```cloud server```: ```https://causal-discovery-llm.onrender.com```

1. cd_llm (```POST```) : ```cloud server```/```cd_llm```;```TESTED```.

### Request Body Breakdown:
```request type```: ```formData```; 
```request body```:
```
var_name_desc: "var_name_desc":{
                                 "var_1":{"var_name": "dyspnoea", "var_desc": "whether or not the patient has dyspnoea, also known as shortness of breath"},
                                 "var_2":{"var_name": "tuberculosis", "var_desc": "whether or not the patient has tuberculosis"},
                                 "var_3":{"var_name": "lung cancer", "var_desc": "whether or not the patient has lung cancer"},
                                 "var_4":{"var_name": "bronchitis", "var_desc": "whether or not the patient has either tuberculosis or lung cancer"},
                                 "var_5":{"var_name": "either tuberculosis or lung cancer", "var_desc": "whether or not the patient is a smoker"},
                                 "var_6":{"var_name": "smoking", "var_desc": "whether or not the patient is a smoker"},
                                 "var_7":{"var_name": "recent visit to asia", "var_desc": "whether or not the patient has recently visited asia"},
                                 "var_8":{"var_name": "positive chest xray", "var_desc": "whether or not the patient has had a positive chest xray"}
                                }
prompt: base
prompt_info: lung disease
use_stats: False
csv_file : "..."
n_aug: 1
robust_test: swap
```

#### Parameter definition:
1. ```var_name_desc```: variable name and description.
1. ```prompt```: This variable indicates if llm should use base prompt or optimized prompt. It has four options; ```base```, ```opt```, ```metamorphic_base```, and ```metamorphic_opt```.
2. ```prompt_info```: This variable gives a brief description of the dataset.
3. ```use_stats```: This boolean variable indicates if the system should used statistical information (pearson correlation coefficient between current variable and other variables)
4. ```csv_file```: Csv file of dataset (optional).
5. ```n_aug```: Number of characters to alter for metamorphic testing(```robustness```).
6. ```robust_test```: Specfies what type of altering should be done to the word or text. (Only one should be selected at a time)

#### Types of ```robust_test``` :
1. ```swap```: randomly swap character(s) in a word. 
2. ```char_delete```: randomly delete character(s) in a word.
3. ```add_char```: randomly add character(s) in a word.
4. ```add_space```: randomly add space(s) in a word.
5. ```add_number```: randomly add number(s) in a word.
6. ```swap_with_number```: randomly replace character(s) with number in a word.
7. ```synonym_sub```: rephrase a word or sentence.

#### System Response:
```response type```: ```Json```; 
```response body```:
```
{
    b64_result: "..."
}
```
#### System Response definition:
1. ```b64_result```: Base64 image format of the generated causal graph.
