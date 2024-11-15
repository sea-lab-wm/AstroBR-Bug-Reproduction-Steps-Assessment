This is the replication package for the paper entitled "Combining Language and App UI Analysis for the Automated Assessment of Bug Reproduction Steps".

This package contains the following files/folders:
1. `a_dataset`: a folder containing the required dataset to replicate the results of the paper
    * `bug_reports`: this folder contains the bug reports used in the study. The bug reports are divided into two sets: development and test sets. The development set contains 54 bug reports, while the test set contains 21 bug reports.
    * `execution_model_test_set`: this folder contains the application execution models for the 21 bug reports in the test set.
    * `execution_model_development_set`: this folder contains the application execution models for the 10 bug reports in the development set.
    * `QAs`: this folder contains quality annotation data
2. `b_s2r_sentence_identification`: a folder containing the necessary scripts to run the S2R sentence identification phase of AstroBR. This folder has the following sub-folders:
    * `generate_prompts`: this folder contains the necessary scripts to generate prompts for the S2R sentence identification task.
    * `generate_responses`: this folder contains the necessary scripts to generate GPT-4 responses for the S2R sentence identification task.
    * `result_generation`: this folder contains the necessary scripts to generate the results of the S2R sentence identification task. We already provided the necessary result files.
3. `c_individual_s2r_extraction`: a folder containing the necessary scripts to run the individual S2R extraction phase of AstroBR. This folder has the following sub-folders:
4. `d_quality_assessment`: a folder containing the necessary scripts to run the quality assessment phase of AstroBR.
    * `mapping_gui_response_quality_labels.py`: this file will generate annotations for individual S2Rs.
5. `e_prompt_templates`: a folder containing the prompt templates used in the S2R sentence identification, individual S2R identification, and individual S2R mapping tasks.