import pandas as pd
import csv
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate responses for a given prompt file')
    parser.add_argument('dataset', type=str, help='Dataset to use: bee-applications/bee-android/bl-development/bl-test/euler')
    parser.add_argument('prompt_version', type=str, help='Prompt version to use')
    args = parser.parse_args()

    dataset = args.dataset
    prompt_version = args.prompt_version

    if dataset == "bee-applications":
        bug_reports_path = '../../Data/BEE-Data/bee_data_applications.csv'
    elif dataset == "bee-android":
        bug_reports_path = '../../Data/BEE-Data/bee_data_android.csv'
    elif dataset == "bl-development":
        bug_reports_path = '../../Data/BL-Data/BL-data-development.csv'
    elif dataset == "bl-test":
        bug_reports_path = '../../Data/BL-Data/BL-data-test.csv'
    elif dataset == "euler":
        bug_reports_path = '../../Data/Euler-Data/euler_data_21_bugs.csv'

    # Paths to the CSV files containing the templates and bug reports
    prompt_templates_path = 'prompt_templates.csv'
    generated_prompts_file_path = f'./generated_prompts/{dataset}/{dataset}-prompts-{prompt_version}.csv'

    # Read the templates and bug reports CSV files
    templates_df = pd.read_csv(prompt_templates_path)
    bug_reports_df = pd.read_csv(bug_reports_path)

    # Prepare a list to hold all the prompts
    prompts = []

    # Iterate over all the prompt templates and get the desired template
    for _, template_row in templates_df.iterrows():
        if template_row['Version'] == prompt_version:
            template_text = template_row['Template']
            break
    # Iterate over all the bug reports and generate the prompts
    for _, bug_report_row in bug_reports_df.iterrows():
        system_name = bug_report_row['App Names']
        # bug_id = bug_report_row['Bug-Id']
        bug_report = bug_report_row['Bug Reports']
        # label = bug_report_row['Label']
        # Replace the placeholders in the template with the actual values
        prompt = template_text.replace('<system-name>', system_name).replace('<bug-report>', bug_report)
        prompts.append(prompt)

    # Convert the prompts list to a DataFrame
    # prompts_df = pd.DataFrame(prompts, columns=['Bug_id', "App Names", 'Bug Reports', 'Labels', 'Zero Shot Prompts'])
    bug_reports_df['Zero Shot Prompts'] = prompts
    # Save the prompts DataFrame to a CSV file
    bug_reports_df.to_csv(generated_prompts_file_path, index=False, quoting=csv.QUOTE_ALL)

    print(f"Prompts have been saved to {generated_prompts_file_path}\n\n")
