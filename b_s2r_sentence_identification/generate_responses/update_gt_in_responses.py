import pandas as pd
import os

if __name__ == "__main__":
    # BL Development data
    # data_path = '../../Data/BL-Data/BL-data-development.csv'
    # response_folder_path = 'generated_responses/bl-development'

    # EULER Data
    data_path = '../../Data/EULER-Repl-Package/1_data/euler_predictions_21_bugs.csv'
    response_folder_path = './generated_responses/euler'

    bug_ids_not_euler = [1, 81, 104]

    data_df = pd.read_csv(data_path)
    data_df = data_df.sort_values(by=['Bug_id']).reset_index(drop=True)

    # Column names
    column_name_to_take = 'Labels'  # Name of the column to take from the first file
    column_name_to_replace = 'Labels'  # Name of the column to replace in the second file

    for file in os.listdir(response_folder_path):
        if not file.endswith(".csv"):
            continue
        response_path = os.path.join(response_folder_path, file)
        response_df = pd.read_csv(response_path)

        if response_folder_path.__contains__("euler"):
            # Drop the rows with bug ids that are not in the euler dataset
            response_df = response_df[~response_df['Bug_id'].isin(bug_ids_not_euler)]

            # Update the bug ids to match the euler dataset
            response_df.loc[(response_df['Bug_id'] == 25) & (response_df['App Names'] == 'atimetracker'), 'Bug_id'] = 251
            response_df.loc[(response_df['Bug_id'] == 25) & (response_df['App Names'] == 'droidweight'), 'Bug_id'] = 252

            # Sort the DataFrame by Bug_id
            response_df = response_df.sort_values(by=['Bug_id']).reset_index(drop=True)

        # Check if the column to take exists in the first DataFrame
        if column_name_to_take not in data_df:
            raise ValueError(f"Column '{column_name_to_take}' not found in {data_path}")

        # Check if the length of both columns is the same
        if len(data_df[column_name_to_take]) != len(response_df[column_name_to_replace]):
            raise ValueError("The lengths of the columns do not match.")

        # Replace the target column in the second DataFrame with the column from the first DataFrame
        response_df[column_name_to_replace] = data_df[column_name_to_take]

        # Save the modified DataFrame to a new CSV file
        response_df.to_csv(response_path, index=False)
