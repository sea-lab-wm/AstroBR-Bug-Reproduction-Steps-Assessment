import copy
import csv
import sys

import pandas as pd
import numpy as np
import lxml.etree as ET
import os

def write_to_csv(write_file, row):
    with open(write_file, 'a') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def write_header(write_file):
    with open(write_file, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["Bug_id", "App Names", "Bug Reports", "Labels", "Zero Shot Prompts", "Responses",
                         "#OB Sentences in Ground Truths", "#OB Sentences in Responses", "OB Sentences - TP", "OB Sentences - FP", "OB Sentences - FN", "OB Sentences - TN", "OB Sentences-Precision", "OB Sentences-Recall", "OB Sentences-F1", "OB Sentences-Accuracy",
                         "#EB Sentences in Ground Truths", "#EB Sentences in Responses", "EB Sentences - TP", "EB Sentences - FP", "EB Sentences - FN", "EB Sentences - TN", "EB Sentences-Precision", "EB Sentences-Recall", "EB Sentences-F1", "EB Sentences-Accuracy",
                         "#S2R Sentences in Ground Truths", "#S2R Sentences in Responses", "S2R Sentences - TP", "S2R Sentences - FP", "S2R Sentences - FN", "S2R Sentences - TN", "S2R Sentences-Precision", "S2R Sentences-Recall", "S2R Sentences-F1", "S2R Sentences-Accuracy",
                         "# Sentences in Bug Reports", "# Labeled Sentences", "# Unlabeled Sentences", "# Sentences in Responses",
                         "All Sentences - TP", "All Sentences - FP", "All Sentences - FN", "All Sentences - TN", "All Sentences-Precision", "All Sentences-Recall", "All Sentences-F1", "All Sentences-Accuracy"])

def get_responses(csv_file):
    df = pd.read_csv(csv_file)

    bug_ids = df['Bug_id']
    # bug_links = df['Links']
    # old_app_names = df['Old App Names']
    app_names = df['App Names']
    bug_reports = df['Bug Reports']

    ground_truths = df['Labels']
    #zero_shot_prompts = df['Zero Shot Prompts']
    zero_shot_prompts = ["" for i in range(len(ground_truths))]
    responses = df['Responses']

    return bug_ids, app_names, bug_reports, ground_truths, zero_shot_prompts, responses
    #return bug_ids, bug_links, old_app_names, app_names, bug_reports, ground_truths, zero_shot_prompts, responses

def format_comps(ground_truths):
    ground_truths = ground_truths.replace('[','')
    ground_truths = ground_truths.replace(']','')
    cur_ground_truth = ground_truths.split("\n")

    obs_ground_truth = cur_ground_truth[0].split("OBs:")
    if len(obs_ground_truth)>1:
        obs_ground_truth = obs_ground_truth[1]
    else:
        obs_ground_truth = []

    ebs_ground_truth = cur_ground_truth[1].split("EBs:")
    if len(ebs_ground_truth)>1:
        ebs_ground_truth = ebs_ground_truth[1]
    else:
        ebs_ground_truth = []

    s2rs_ground_truth = cur_ground_truth[2].split("S2Rs:")
    if len(s2rs_ground_truth)>1:
        s2rs_ground_truth = s2rs_ground_truth[1]
    else:
        s2rs_ground_truth = []

    obs_gt = []
    ebs_gt = []
    s2rs_gt = []

    if len(obs_ground_truth)>1:
        obs_gt = [x.strip() for x in obs_ground_truth.replace(',',' ').split()]
    if len(ebs_ground_truth)>1:
        ebs_gt = [x.strip() for x in ebs_ground_truth.replace(',',' ').split()]
    if len(s2rs_ground_truth)>1:
        s2rs_gt = [x.strip() for x in s2rs_ground_truth.replace(',',' ').split()]

    return obs_gt, ebs_gt, s2rs_gt

def format_responses(ground_truths):
    ground_truths = ground_truths.replace('[','')
    ground_truths = ground_truths.replace(']','')
    cur_ground_truth = ground_truths.split("\n")

    obs_ground_truth = cur_ground_truth[0].split("OB:")
    if len(obs_ground_truth)>1:
        obs_ground_truth = obs_ground_truth[1]
    else:
        obs_ground_truth = []

    ebs_ground_truth = cur_ground_truth[1].split("EB:")
    if len(ebs_ground_truth)>1:
        ebs_ground_truth = ebs_ground_truth[1]
    else:
        ebs_ground_truth = []

    s2rs_ground_truth = cur_ground_truth[2].split("S2Rs:")
    if len(s2rs_ground_truth)>1:
        s2rs_ground_truth = s2rs_ground_truth[1]
    else:
        s2rs_ground_truth = []

    obs_gt = []
    ebs_gt = []
    s2rs_gt = []

    if len(obs_ground_truth)>1:
        obs_gt = [x.strip() for x in obs_ground_truth.replace(',',' ').split()]
    if len(ebs_ground_truth)>1:
        ebs_gt = [x.strip() for x in ebs_ground_truth.replace(',',' ').split()]
    if len(s2rs_ground_truth)>1:
        s2rs_gt = [x.strip() for x in s2rs_ground_truth.replace(',',' ').split()]

    obs_gt = split_up_sentence_numbers_when_hyphen_exists(obs_gt)
    ebs_gt = split_up_sentence_numbers_when_hyphen_exists(ebs_gt)
    s2rs_gt = split_up_sentence_numbers_when_hyphen_exists(s2rs_gt)

    return obs_gt, ebs_gt, s2rs_gt

def split_up_sentence_numbers_when_hyphen_exists(br_components):
    comp_list = []
    #print("beg: " + str(br_components))
    for item in br_components:
        if "-" in item:
            comp_splits = item.split("-")
            start = comp_splits[0]
            end = comp_splits[1]

            begin_first_part = start.split(".")[0]
            begin_last_part = int(start.split(".")[1])
            end_last_part = int(end.split(".")[1])

            for i in range(begin_last_part, end_last_part+1, 1):
                val = begin_first_part + "." + str(i)
                comp_list.append(val)
        else:
            comp_list.append(item)
    #print("to: " + str(comp_list))
    return comp_list

def calc_precision(tp, fp):
    if tp==0:
        return 0
    return tp/(tp+fp)

def calc_recall(tp, fn):
    if tp==0:
        return 0
    return tp/(tp+fn)

def calc_accuracy(tp, fp, fn, tn):
    #  print("tp: " + str(tp))
    #  print("fp: " + str(fp))
    #  print("fn: " + str(fn))
    #  print("tn: " + str(tn))
    if tp+tn==0:
        return 0
    return (tp+tn)/(tp+tn+fp+fn)

def calc_f1(precision, recall):
    if precision==0 or recall==0:
        return 0
    return (2*precision*recall)/(precision+recall)

def cal_result_comps(comp_gt, comp_res, total_sentences):
    corr_res = 0
    miss_res = 0
    incorr_res = 0
    #print(comp_res)
    for each_res in comp_res:
        if (each_res[0]>='a' and each_res[0]<='z') or (each_res[0]>='A' and each_res[0]<='Z'):
            continue
        if (each_res[0]>='0' and each_res[0]<='9') is False:
            continue
        if each_res in comp_gt:
            corr_res +=1
        else:
            incorr_res +=1

    for each_gt in comp_gt:
        if each_gt not in comp_res:
            miss_res += 1

    #TP=corr_res
    #FP=incorr_res
    #FN=miss_res

    temp_tn = total_sentences - len(comp_gt)
    tn = temp_tn - incorr_res

    curr_precision = calc_precision(corr_res, incorr_res)
    curr_recall = calc_recall(corr_res, miss_res)
    curr_f1 = calc_f1(curr_precision, curr_recall)
    curr_accuracy = calc_accuracy(corr_res, incorr_res, miss_res, tn)

    return corr_res, incorr_res, miss_res, tn, curr_precision, curr_recall, curr_f1, curr_accuracy

def get_total_number_of_sentences_bl(bug_report):
    sentences = bug_report.split("\n")

    cnt = 0
    for sentence in sentences:
        if ":" in sentence:
            cnt+=1
    return cnt

def get_total_number_of_sentences_bee(app_name, bug_id, xml_dir):
    if app_name=="openmrs":
        xml_file = xml_dir + "/" + app_name + "/TRUNK-" + str(bug_id) + ".parse.xml"
    elif app_name=="pdfbox":
        xml_file = xml_dir + "/" + app_name + "/PDFBOX-" + str(bug_id) + ".parse.xml"
    else:
        xml_file = xml_dir + "/" + app_name + "/" + str(bug_id) + ".parse.xml"

    tree = ET.parse(xml_file)
    title_count = tree.xpath('count(//title)')
    st_count = tree.xpath('count(//st)')
    return int(title_count) + int(st_count)

def get_total_labeled_sentences(obs_gt, ebs_gt, s2rs_gt):
    return len(obs_gt) + len(ebs_gt) + len(s2rs_gt)

def get_unlabeled_sentence(total_sentences, labeled_sentences):
    return total_sentences-labeled_sentences


if __name__ == "__main__":
    response_folder_path = "./generated_responses/euler"
    metrics_folder_path = "./calculated_metrics/euler-data"

    prompt_versions = ["2.1.0", "3.1.0"]

    metrics_folders = os.listdir(metrics_folder_path)

    for file in os.listdir(response_folder_path):
        if not file.endswith(".csv"):
            continue
        # print(file)
        response_file_path = os.path.join(response_folder_path, file)
        prompt_version = file.split("-")[-1].replace(".csv", "")
        # print(prompt_version)
        if prompt_version in prompt_versions:
            continue

        if not prompt_version.endswith(".0"):
            continue
        prompt_version_copy = copy.deepcopy(prompt_version)
        general_prompt_version = prompt_version_copy.split(".")
        # print(general_prompt_version)
        general_prompt_version = general_prompt_version[0] + "." + general_prompt_version[1]
        # print(general_prompt_version)

        for metrics_folder in metrics_folders:
            if general_prompt_version in metrics_folder:
                current_metrics_dir = metrics_folder
                break

        calculated_metrics_file_path = os.path.join(metrics_folder_path, current_metrics_dir, "euler-metrics-" + prompt_version + ".csv")

        current_config_dir = "bl"

        write_header(calculated_metrics_file_path)

        #bug_ids, bug_links, old_app_names, app_names, bug_reports, ground_truths, zero_shot_prompts, responses = get_responses(zero_shot_file)
        bug_ids, app_names, bug_reports, ground_truths, zero_shot_prompts, responses = get_responses(response_file_path)

        s_obs_gt = 0
        s_obs_res = 0
        s_corr_obs = 0
        s_incorr_obs = 0
        s_missed_obs = 0
        s_tn_obs = 0
        s_obs_precision = 0
        s_obs_recall = 0
        s_obs_f1 = 0
        s_obs_accuracy = 0

        s_ebs_gt = 0
        s_ebs_res = 0
        s_corr_ebs = 0
        s_incorr_ebs = 0
        s_missed_ebs = 0
        s_tn_ebs = 0
        s_ebs_precision = 0
        s_ebs_recall = 0
        s_ebs_f1 = 0
        s_ebs_accuracy = 0

        s_s2rs_gt = 0
        s_s2rs_res = 0
        s_corr_s2rs = 0
        s_incorr_s2rs = 0
        s_missed_s2rs = 0
        s_tn_s2rs = 0
        s_s2rs_precision = 0
        s_s2rs_recall = 0
        s_s2rs_f1 = 0
        s_s2rs_accuracy = 0

        s_total_sentences_in_br = 0
        s_total_labeled_sentences = 0
        s_total_unlabeled_sentences = 0
        s_total_sentences_in_responses = 0

        s_tp_all = 0
        s_fp_all = 0
        s_fn_all = 0
        s_tn_all = 0

        s_precision_all = 0
        s_recall_all = 0
        s_f1_all = 0
        s_accuracy_all = 0

        br_cnt = 0
        for i in range(len(ground_truths)):
            # if int(bug_ids[i])==1481 or int(bug_ids[i])==106 or int(bug_ids[i])==1446:
            #      continue
            br_cnt+=1
            obs_gt, ebs_gt, s2rs_gt = format_comps(ground_truths[i])
            obs_res, ebs_res, s2rs_res = format_responses(responses[i])
            #print(i)

            if current_config_dir.startswith("bee"):
                total_sentences_in_br = get_total_number_of_sentences_bee(app_names[i], bug_ids[i], xml_dir)
            elif current_config_dir.startswith("bl"):
                total_sentences_in_br = get_total_number_of_sentences_bl(bug_reports[i])

            print("Bug id: " + str(bug_ids[i]))
            print("Total sentences in bug report: " + str(total_sentences_in_br))
            total_labeled_sentences = get_total_labeled_sentences(obs_gt, ebs_gt, s2rs_gt)
            total_unlabeled_sentences = get_unlabeled_sentence(total_sentences_in_br, total_labeled_sentences)

            corr_obs, incorr_obs, missed_obs, tn_obs, obs_precision, obs_recall, obs_f1, obs_accuracy = cal_result_comps(obs_gt, obs_res, total_sentences_in_br)

            corr_ebs, incorr_ebs, missed_ebs, tn_ebs, ebs_precision, ebs_recall, ebs_f1, ebs_accuracy = cal_result_comps(ebs_gt, ebs_res, total_sentences_in_br)
            corr_s2rs, incorr_s2rs, missed_s2rs, tn_s2rs, s2rs_precision, s2rs_recall, s2rs_f1, s2rs_accuracy = cal_result_comps(s2rs_gt, s2rs_res, total_sentences_in_br)
            total_sentences_in_responses = get_total_labeled_sentences(obs_res, ebs_res, s2rs_res)

            row = []
            row.append(bug_ids[i])
            #row.append(bug_links[i])
            #row.append(old_app_names[i])
            row.append(app_names[i])
            row.append(bug_reports[i])

            row.append(ground_truths[i])
            row.append(zero_shot_prompts[i])
            row.append(responses[i])

            row.append(len(obs_gt))
            s_obs_gt += len(obs_gt)
            row.append(len(obs_res))
            s_obs_res += len(obs_res)
            row.append(corr_obs)
            s_corr_obs += corr_obs
            row.append(incorr_obs)
            s_incorr_obs += incorr_obs
            row.append(missed_obs)
            s_missed_obs += missed_obs
            row.append(tn_obs)
            s_tn_obs += tn_obs
            row.append('{0:.2f}'.format(obs_precision))
            s_obs_precision += obs_precision
            row.append('{0:.2f}'.format(obs_recall))
            s_obs_recall += obs_recall
            row.append('{0:.2f}'.format(obs_f1))
            s_obs_f1 += obs_f1
            row.append('{0:.2f}'.format(obs_accuracy))
            s_obs_accuracy += obs_accuracy

            row.append(len(ebs_gt))
            s_ebs_gt += len(ebs_gt)
            row.append(len(ebs_res))
            s_ebs_res += len(ebs_res)
            row.append(corr_ebs)
            s_corr_ebs += corr_ebs
            row.append(incorr_ebs)
            s_incorr_ebs += incorr_ebs
            row.append(missed_ebs)
            s_missed_ebs += missed_ebs
            row.append(tn_ebs)
            s_tn_ebs += tn_ebs
            row.append('{0:.2f}'.format(ebs_precision))
            s_ebs_precision += ebs_precision
            row.append('{0:.2f}'.format(ebs_recall))
            s_ebs_recall += ebs_recall
            row.append('{0:.2f}'.format(ebs_f1))
            s_ebs_f1 += ebs_f1
            row.append('{0:.2f}'.format(ebs_accuracy))
            s_ebs_accuracy += ebs_accuracy

            row.append(len(s2rs_gt))
            s_s2rs_gt += len(s2rs_gt)
            row.append(len(s2rs_res))
            s_s2rs_res += len(s2rs_res)
            row.append(corr_s2rs)
            s_corr_s2rs += corr_s2rs
            row.append(incorr_s2rs)
            s_incorr_s2rs += incorr_s2rs
            row.append(missed_s2rs)
            s_missed_s2rs += missed_s2rs
            row.append(tn_s2rs)
            s_tn_s2rs += tn_s2rs
            row.append('{0:.2f}'.format(s2rs_precision))
            s_s2rs_precision += s2rs_precision
            row.append('{0:.2f}'.format(s2rs_recall))
            s_s2rs_recall += s2rs_recall
            row.append('{0:.2f}'.format(s2rs_f1))
            s_s2rs_f1 += s2rs_f1
            row.append('{0:.2f}'.format(s2rs_accuracy))
            s_s2rs_accuracy += s2rs_accuracy

            row.append(total_sentences_in_br)
            s_total_sentences_in_br += total_sentences_in_br
            row.append(total_labeled_sentences)
            s_total_labeled_sentences += total_labeled_sentences
            row.append(total_unlabeled_sentences)
            s_total_unlabeled_sentences += total_unlabeled_sentences
            row.append(total_sentences_in_responses)
            s_total_sentences_in_responses += total_sentences_in_responses


            #"All Sentences - TP", "All Sentences - FP", "All Sentences - FN", "All Sentences - TN", "All Sentences-Precision", "All Sentences-Recall", "All Sentences-F1", "All Sentences-Accuracy"
            tp_all = corr_obs + corr_ebs + corr_s2rs
            row.append(tp_all)
            s_tp_all += tp_all

            fp_all = incorr_obs + incorr_ebs + incorr_s2rs
            row.append(fp_all)
            s_fp_all += fp_all

            fn_all = missed_obs + missed_ebs + missed_s2rs
            row.append(fn_all)
            s_fn_all += fn_all

            tn_all = tn_obs + tn_ebs + tn_s2rs
            row.append(tn_all)
            s_tn_all += tn_all

            precision_all = calc_precision(tp_all, fp_all)
            row.append('{0:.2f}'.format(precision_all))
            s_precision_all += precision_all

            recall_all = calc_recall(tp_all, fn_all)
            row.append('{0:.2f}'.format(recall_all))
            s_recall_all += recall_all

            f1_all = calc_f1(precision_all, recall_all)
            row.append('{0:.2f}'.format(f1_all))
            s_f1_all += f1_all

            accuracy_all = calc_accuracy(tp_all, fp_all, fn_all, tn_all)
            row.append('{0:.2f}'.format(accuracy_all))
            s_accuracy_all += accuracy_all

            write_to_csv(calculated_metrics_file_path, row)
