import json
import os
import torch
import pandas as pd
from tqdm import tqdm
from datasets import Dataset

from new_llm_managers import HuggingFaceLlmManager
from credentials import HF_API_TOKEN

# Check if CUDA is available
if torch.cuda.is_available():
    print("CUDA is available")
else:
    print("CUDA is not available")

manager = HuggingFaceLlmManager("mistralai/Mistral-7B-Instruct-v0.2", quantization="4bit")

with open('prompt_tests.txt', 'r') as f:
        prompt_primer = f.read()


def argument_relation(parent_arg, child_arg, nr=False, support_label="Support", attack_label="Attack", no_label="No"):
    prompt = f"""{prompt_primer}

    Arg1: {parent_arg}
    Arg2: {child_arg}
    Relation:"""

    constraints = {
        "constraint_prefix": "",
        "constraint_options": [support_label, attack_label] + ([no_label] if nr else []),
        "constraint_end_after_options": True,
    }

    response = manager.chat_completion(
        prompt,
        print_result=False,
        trim_response=True,
        apply_template=False,
        **constraints,
    )

    return response

def set_relations_from(parent_id, child, relations):
    pair_id = f"{parent_id}_{child['id']}"
    child['relation'] = str(relations.loc[relations['pair_id'] == pair_id, 'relation'].values[0])
    for com in child['comments']:
        set_relations_from(child['id'], com, relations)

def gather_parent_child_from(parent, relations_dict):
    for com in parent['comments']:
        relations_dict['pair_id'].append(f"{parent['id']}_{com['id']}")
        relations_dict['parent'].append(parent['content'])
        relations_dict['child'].append(com['content'])
        gather_parent_child_from(com, relations_dict)


def gather_parent_child(thread):
    relations_dict = {'pair_id': [], 'parent': [], 'child': []}

    for com in thread['comments']:
        relations_dict['pair_id'].append(f"{thread['id']}_{com['id']}")
        relations_dict['parent'].append(thread['post content'])
        relations_dict['child'].append(com['content'])
        gather_parent_child_from(com, relations_dict)

    relations_df = pd.DataFrame(relations_dict)

    return relations_df

def arg_mine_reddit():
    directory = '../reddit_data/aita_posts/'
    filenames = os.listdir(directory)
    progress_bar = tqdm(total=len(filenames), initial=0)

    for fn in filenames:
        with open(directory + fn, 'r') as f:
            thread = json.load(f)

        relations_df = gather_parent_child(thread)
        relations_dataset = Dataset.from_pandas(relations_df)

        relations_dataset = relations_dataset.map(lambda r: {'relation': argument_relation(r['parent'], r['child'], nr=True)})
        relations_df = relations_dataset.to_pandas()

        for com in thread['comments']:
            set_relations_from(thread['id'], com, relations_df)

        with open(directory + fn, 'w') as thread_file:
            json.dump(thread, thread_file, indent=2)

        progress_bar.update(1)

    progress_bar.close()


def test_argument_relation():
    test_df = pd.read_csv('arg_relation_test.tsv', sep='\t', encoding='utf-16')

    # apply argument_relation to each row in the dataframe
    responses = test_df.apply(lambda r: argument_relation(r['parent'], r['child'], nr=True), axis=1)
    test_df['prediction'] = responses

    test_df.to_csv('arg_relation_test.tsv', sep='\t', index=False)


if __name__ == '__main__':
    arg_mine_reddit()
    # test_argument_relation()
