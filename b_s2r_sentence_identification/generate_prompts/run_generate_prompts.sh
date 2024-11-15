#!/bin/bash

prompt_versions=("1.2.0" "2.1.0" "3.1.0")
datasets=("euler")

# Loop through the arguments and run the Python script with each one
for dataset in "${datasets[@]}"
do
  echo "Working on dataset: $dataset"
  for prompt_version in "${prompt_versions[@]}"
  do
      echo "Generating Prompt: $prompt_version"
      python3 generate_prompts.py "$dataset" "$prompt_version"
  done
done