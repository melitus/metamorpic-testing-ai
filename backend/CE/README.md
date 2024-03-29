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
2. ```config/config.py```: This script contains system configurations.
3. ```util/sys_utils.py```: This script contains utility functions.

### How to run the Cause & Effect Backend System locally:
1. Create and activate a virtual environment: ```python3 -m venv _name_of_virtual_env_```.
2. Install dependencies using: ```pip install -r requirements.txt```.
3. Create a ```.env``` file and set the following variables:
    ```Request for the environment variables from the developer in charge.```,
  
5. Run the server locally using: ```uvicorn main:app --reload```

### Endpoints:
```local server```: ```http://127.0.0.1:8000```; 
```cloud server```: ```https://causal-discovery-llm.onrender.com```

1. cd_llm (```POST```) : ```cloud server```/```cd_llm```;```NOT-TESTED```.

### Request Body Breakdown:
```request type```: ```formData```; 
```request body```:
```
var_name_desc: {  "var_1":{"var_name": "abc", "var_desc": "abc abc abc abc abc abc"}, 
                  "var_2":{"var_name": "def", "var_desc": "def def def def def def"},            
                  "var_3":{"var_name": "ghi", "var_desc": "ghi ghi ghi ghi ghi ghi"},           
                  "var_4":{"var_name": "jkl", "var_desc": "jkl jkl jkl jkl jkl jkl"},         
                  "var_5":{"var_name": "mno", "var_desc": "mno mno mno mno mno mno"}
                }
prompt: base
prompt_info: alphabets
use_stats: False
csv_file : "..."
```

#### Parameter definition:
1. ```var_name_desc```: variable name and description.
1. ```prompt```: This variable indicates if llm should use base prompt or optimized prompt. It has only two options; ```base``` or ```opt```.
2. ```prompt_info```: This variable contains a variable brief description of the dataset.
3. ```use_stats```: This boolean variable indicates if the system should used statistical information (pearson correlation)
4. ```csv_file```: Csv file of dataset (optional).

#### System Response:
```
{
    b64_result: "..."
}
```
#### System Response definition:
1. ```b64_result```: Base64 image format of the generated causal graph.
