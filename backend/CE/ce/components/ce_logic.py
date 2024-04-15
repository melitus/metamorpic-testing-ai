import numpy as np
import pandas as pd
import igraph as ig
import bnlearn as bn
import networkx as nx
from openai import OpenAI
import matplotlib.pyplot as plt
from ..config.config import CEConfig



def set_prompt(prompt_type, prompt_info):
    if "metamorphic" in prompt_type:
      prompt_type =  prompt_type.split("_")[1].strip()

    if prompt_type == "base" or prompt_type == "opt":
        prompt_ =[
            {
            "role": "system",
            "content": prompt_info
            },
            {
            "role": "user",
            "content": f"Our goal is to construct a causal graph between the following variables.\n"
            }
        ]
        return prompt_


class DrawDAG:

  "Causal Discovery diagram drawer."

  def __init__(self):
    self.graph = nx.DiGraph()
    
  def create_clean_DAgraph(self, dag):
    clean_dict = {}
    for d in dag:
      if len(dag[d]) == 0:
        continue
      clean_dict[d] = dag[d]
    return clean_dict

  def created_dag_list(self, da_g):
    new_list = []
    for key,val in da_g.items():
      if len(val) == 1:
        new_list.append((key, val[0]))
      else:
        for vl in val:
          new_list.append((key, vl))
    final_list = [("root", new_list[0][0])]
    final_list.extend(new_list)
    return final_list

  def draw(self, dag, tmp, save=True):
    da_g = self.create_clean_DAgraph(dag)
    graph_list = self.created_dag_list(da_g)
    self.graph.add_edges_from(graph_list)
    plt.tight_layout()
    nx.draw_networkx(self.graph, arrows=True)

    image_path = f"{tmp}/graph.png"
    if save:
      plt.savefig(image_path, format="PNG")
    plt.clf()
    return image_path


class CDExpert:
  "LLM based causal discovery expert class."
  def __init__(self, df, prompt_type, prompt_info, include_statistics, aug_map):
    self.gpt = self.gpt4_client
    self.df = df
    self.corr = None
    self.include_statistics=include_statistics
    self.prompt_init = 'Now you are going to use the data to construct a causal graph. You will start with identifying the variable(s) that are unaffected by any other variables.\n'
    self.prompt_format = 'Think step by step. Then, provide your final answer (variable names only) within the tags <Answer>...</Answer>, seperated by ", ". '
    self.prompt_init += self.prompt_format
    self.predict_graph = dict()
    self.message_history = set_prompt(prompt_type, prompt_info)
    self.aug_map = aug_map
    self.rev_aug_map = {v:k for k, v in self.aug_map.items()} if self.aug_map != None else None
    
  def get_data_prompt(self, to_visit):
    prompt = f'Addtionally, the Pearson correlation coefficient between {to_visit} and other variables are as follows:\n'
    for var in self.corr:
        if var == to_visit:
            continue
        prompt += f'{var}: {self.corr[var][to_visit]:.2f}\n'
    return prompt

  def gpt4_client(self):
    client = OpenAI(api_key=CEConfig.openai_api)
    model = CEConfig.openai_model_ver
    temperature = 0.2
    response = client.chat.completions.create(
                      model=model,
                      messages=self.message_history,
                      temperature=temperature,
                      max_tokens=4095,
                      frequency_penalty=0,
                      presence_penalty=0)
    answer = response.choices[0].message.content
    self.message_history.append({
        "role": "assistant",
        "content": answer
    })
    answer = answer.split('<Answer>')[1].split('</Answer>')[0].split(', ')
    return answer

  def clean_answer(self, answer, independent_nodes, nodes):
    for node in answer:
      if node in independent_nodes:
          answer.remove(node)
      elif len(node) == 0:
          answer.remove(node)
      elif node not in nodes:
          answer.remove(node)
    return answer

  def insert_var_and_desc(self, var_names_and_desc):
    var_count_keys = [var for var in var_names_and_desc.keys()]
    new_nodes = []
    for var in var_count_keys:
        var_name = var_names_and_desc[var]["var_name"]
        var_desc = var_names_and_desc[var]["var_desc"]
        self.message_history[1]['content'] += f'''{var_name}: {var_desc}\n'''
        new_nodes.append(var_name)
    self.message_history[1]['content'] += self.prompt_init
    return new_nodes

  def get_frontier(self, independent_nodes, unvisited_nodes, nodes):
    frontier = []

    for to_visit in independent_nodes:
        prompt = 'Given ' + ', '.join(independent_nodes) + ' is(are) not affected by any other variable'
        if len(self.predict_graph) == 0:
            prompt += '.\n'
        else:
            prompt += ' and the following causal relationships.\n'
            for head,tails in self.predict_graph.items():
                if len(tails) > 0:
                    prompt += f'{head} causes ' + ', '.join(tails) + '\n'

        prompt += f'Select variables that are caused by {to_visit}.\n'

        if self.include_statistics:
            prompt += self.get_data_prompt(to_visit)

        prompt += self.prompt_format

        self.message_history.append({
                "role": "user",
                "content": prompt
            })

        answer = self.gpt()
        answer = self.clean_answer(answer, independent_nodes, nodes)
        self.predict_graph[to_visit] = answer

        for node in answer:
            if node in unvisited_nodes and node not in frontier:
                frontier.append(node)
        return frontier

  def construct_adjency_matrix(self):
      df_order = [var for var in self.df.columns]
      n = len(df_order)
      adj_matrix = np.zeros((n, n))
      for i, var in enumerate(df_order):
          if self.rev_aug_map:
            var = self.rev_aug_map[var]
          if var in self.predict_graph:
              for node in self.predict_graph[var]:
                  if self.aug_map:
                    if node in self.rev_aug_map.keys():
                      pass
                    elif node in self.aug_map.keys():
                      node = self.aug_map[node]
                  j = df_order.index(node)
                  adj_matrix[i][j] = 1
      return adj_matrix

  def run_llm_bfs(self, var_names_and_desc):

    if self.include_statistics:
        self.corr = self.df.corr()

    nodes = self.insert_var_and_desc(var_names_and_desc)
    answer = self.gpt()
    independent_nodes = answer.copy()
    unvisited_nodes = nodes.copy()

    for node in answer:
      if node in unvisited_nodes:
        unvisited_nodes.remove(node)

    frontier = self.get_frontier(independent_nodes, unvisited_nodes, nodes)

    while len(frontier) > 0:
        to_visit = frontier.pop(0)

        if to_visit in unvisited_nodes:
          unvisited_nodes.remove(to_visit)

        prompt = 'Given ' + ', '.join(independent_nodes) + ' is(are) not affected by any other variable and the following causal relationships.\n'
        for head,tails in self.predict_graph.items():
            if len(tails) > 0:
                prompt += f'{head} causes ' + ', '.join(tails) + '\n'
        prompt += f'Select variables that are caused by {to_visit}.\n'
        if self.include_statistics:
            prompt += self.get_data_prompt(to_visit)

        prompt += self.prompt_format

        self.message_history.append({
            "role": "user",
            "content": prompt
        })

        answer = self.gpt()
        answer = self.clean_answer(answer, independent_nodes, nodes)
        self.predict_graph[to_visit] = answer

        for node in answer:
            if node in unvisited_nodes and node not in frontier:
              frontier.append(node)

    # adj_matrix = self.construct_adjency_matrix()
    # adj_matrix
    return self.predict_graph

def cd_llm_system(var_name_desc_dict, data_path, n_samples=100, prompt_type = "base", prompt_info=None, include_statistics=False, aug_map=None, tmp_dir=None):
  df = None
  if data_path != None:
    df = pd.read_csv(data_path)
  dag_drawer = DrawDAG()
  llm_expert = CDExpert(df=df, prompt_type=prompt_type, prompt_info=prompt_info, include_statistics=include_statistics, aug_map=aug_map)
  DAgraph = llm_expert.run_llm_bfs(var_name_desc_dict)
  path = dag_drawer.draw(dag=DAgraph, tmp=tmp_dir)
  return path