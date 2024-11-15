import os
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
import pandas as pd
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate responses for a given prompt file')
    parser.add_argument('dataset', type=str, help='Dataset to use: bee/bl-development/bl-test')
    parser.add_argument('prompt_version', type=str, help='Prompt version to use')
    args = parser.parse_args()

    api_key = ""  # TODO: Add your OpenAI API key here
    os.environ["OPENAI_API_KEY"] = api_key

    dataset = args.dataset
    prompt_version = args.prompt_version

    prompt_file_path = f'../generate_prompts/generated_prompts/{dataset}/{dataset}-prompts-{prompt_version}.csv'
    response_file_path = f'./generated_responses/{dataset}/{dataset}-responses-{prompt_version}.csv'

    template = """
        {question}
        """

    QA_CHAIN_PROMPT = PromptTemplate(input_variables=["question"], template=template, )
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    # ask the defined LLM
    llm_chain = LLMChain(llm=llm, prompt=QA_CHAIN_PROMPT)

    prompts_df = pd.read_csv(prompt_file_path)
    responses = []

    for i, prompt_row in prompts_df.iterrows():
        prompt = prompt_row['Zero Shot Prompts']
        response = str(llm_chain.run(prompt))
        # print(response)
        responses.append(response)

        if i % 20 == 0:
            print(f"Processed {i} prompts")

    prompts_df['Responses'] = responses
    prompts_df.to_csv(response_file_path, index=False)
    print(f"Responses have been saved to {response_file_path}\n\n")
