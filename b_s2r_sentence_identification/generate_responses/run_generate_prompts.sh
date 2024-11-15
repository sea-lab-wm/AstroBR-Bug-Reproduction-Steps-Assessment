#!/bin/bash

prompt_versions=("1.0.0" "1.0.1" "1.0.2" "1.0.3" "1.1.0" "1.1.1" "1.1.2" "1.1.3" "1.2.0" "1.2.1" "1.2.2" "1.2.3" "1.4.0" "1.4.1" "1.4.2" "1.4.3" "2.1.0" "3.1.0")
#prompt_versions=("2.1.0" "3.1.0")
#datasets=("bee-applications" "bee-android" "bl-test")
datasets=("euler")

# Loop through the arguments and run the Python script with each one
for dataset in "${datasets[@]}"
do
  echo "Working on dataset: $dataset"
  for prompt_version in "${prompt_versions[@]}"
  do
      echo "Generating Responses for Prompt: $prompt_version"
      python3 generate_responses.py "$dataset" "$prompt_version"
  done
done