#This code identifies the ranks the GUI components on a screen using a cosine similarity score
import xml.etree.ElementTree as ET
from xml.dom import minidom
import glob
import pandas as pd
from llms_generate_response import LLM
from write_results import WriteResults
import argparse
import re
import ast, json
from collections import defaultdict
from prompts import Prompts
from helpers import Helpers
from path import Path
from graph_visualization import GraphVisualzation

class Mapping_GUI():
	def __init__(self):
		self.writeResults = WriteResults()
		self.prompts = Prompts()
		self.helpers = Helpers()
		self.path = Path()
		self.vis = GraphVisualzation()

	def addEdge(self, u, v):
		self.graph[u].append(v)

	# def temp_node_bug_10(self, index):
	# 	node_list = [0,1,3,6,39,8,13,14]
	# 	return index in node_list
	
	# def temp_node_bug_248(self, index):
	# 	node_list = [0,1,20,21,23,2,3,4,6,7,10,9,5,8,15,16]
	# 	return index in node_list
	
	# def temp_node_bug_1568(self, index):
	# 	node_list = [0,4,6,7,8,10,2,3]
	# 	return index in node_list
	
	# def temp_node_bug_2(self, index):
	# 	node_list = [0,1,3,9,20,22,2]
	# 	return index in node_list

	# def is_ambiguous_step(self, sentence):
	# 	#conjunctions generated by ChatGPT
	# 	keywords = ["and", "both", "all", "then", "after", "before"]

	# 	for keyword in keywords:
	# 		if keyword in sentence:
	# 			return True
	# 	return False
	
	def get_interaction_correctness(self, matched_sentences, interactions, comp_id_list, s2r_sentence):
		updated_comp_id_list = []
		sim_score_list = []

		# if self.is_ambiguous_step(s2r_sentence):
		# 	return comp_id_list
		# if s2r_sentence == "Go back to Password // PIN":

		# print("S: " + s2r_sentence)
		# print(matched_sentences)
		unique_comp_list = []
		if self.helpers.comp_is_duplicate(comp_id_list, interactions):
			unique_comp_list.append(comp_id_list[0])
			return unique_comp_list

		for i in range(len(matched_sentences)):
			sim_score = self.llm.get_cosine_similarity(matched_sentences[i], s2r_sentence)
			if sim_score not in sim_score_list:
				updated_comp_id_list.append(comp_id_list[i])
			sim_score_list.append(sim_score)
		return updated_comp_id_list
	
	def rewrite_s2r_sentences(self, app_name, bug_id, s2r_sentence_list):
		updated_s2r_sentence_list = []

		for i in range(len(s2r_sentence_list)):
			_, updated_s2r = self.llm.get_updated_s2rs(app_name, bug_id, i, s2r_sentence_list)
			updated_s2r_sentence_list.append(updated_s2r)
		return updated_s2r_sentence_list
	
	def create_graph_dict_for_dfs(self, start_list, end_list, transition_list):
		screen_Dict = {}
		index = 0
		transition_Dict = {}
		transition_index = 0
		edge_list = []
		for i in range(len(start_list)):
			if start_list[i] not in screen_Dict:
				screen_Dict[start_list[i]] = index
				index = index + 1

			if end_list[i] not in screen_Dict:
				screen_Dict[end_list[i]] = index
				index = index + 1

			if transition_list[i] not in transition_Dict:
				transition_Dict[transition_list[i]] = transition_index
				transition_index = transition_index + 1

		for i in range(len(start_list)):
			start_index = screen_Dict.get(start_list[i])
			end_index = screen_Dict.get(end_list[i])

			#if self.temp_node_bug_248(start_index) or self.temp_node_bug_248(end_index):
			self.addEdge(start_index, end_index)
			edge_list.append((start_index, end_index))
				#print("agt: " + str(start_index) + " " + str(end_index))
		
		return screen_Dict, index, transition_Dict, transition_index, edge_list
	
	def temporary_prompt_step_check(self, v, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag, comp_id):
		cur_screen_id = self.helpers.get_key_from_value(screen_Dict, v)
		comp_infos = self.helpers.get_comp_values(df, cur_screen_id)
	
		comp_str = self.prompts.create_temp_comp_interactions(comp_infos, bug_id, graph_folder_path, cur_screen_id, states_df, comp_id)
		activity = self.helpers.get_activity(states_df, cur_screen_id)

		cur_prompt, response = self.llm.get_response_for_temp_match(app_name, bug_id, s2r_index, s2r_sentence_list, comp_str, cur_screen_id, activity)
		
		comp_id_list = []
		matched_comps_similarity_exist = False	
		if response == "1":
			_, comp_id_list = self.llm.get_response_for_temp_comp_ids(app_name, bug_id, s2r_index, s2r_sentence_list, comp_str, cur_screen_id, activity)       
	
		matched_ids = self.helpers.get_matched_component_ids(comp_id_list, comp_infos)
			
		return matched_ids
	
	def ambiguous_step_check(self, v, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag):
		cur_screen_id = self.helpers.get_key_from_value(screen_Dict, v)
		comp_infos = self.helpers.get_comp_values(df, cur_screen_id)
		comp_str = self.prompts.create_comp_interactions(comp_infos, bug_id, graph_folder_path, cur_screen_id, states_df)
		activity = self.helpers.get_activity(states_df, cur_screen_id)

		cur_prompt, response = self.llm.get_response_for_match(app_name, bug_id, s2r_index, s2r_sentence_list, comp_str, cur_screen_id, activity)
		#print("s2r: " + s2r_sentence_list[s2r_index])
		#print(cur_prompt)
		
		comp_id_list = []
		matched_comps_similarity_exist = False	
		if response == "1":
			_, comp_id_list = self.llm.get_response_for_comp_ids(app_name, bug_id, s2r_index, s2r_sentence_list, comp_str, cur_screen_id, activity)       
		# if response!="1" or (response=="1" and len(comp_id_list)<=1):
		# 	matched_comps_similarity_exist, comp_id_list = self.helpers.get_maximum_similar_interactions(comp_infos, bug_id, cur_screen_id, graph_folder_path, s2r_sentence_list[s2r_index], self.llm)
	
		matched_ids = self.helpers.get_matched_component_ids(comp_id_list, comp_infos)
			
		return matched_ids

	def DFSUtil(self, v, visited, cur_s2r_visited, screen_Dict, transition_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, all_responses, level, path, top_similarity_score, parent, label_count, prev_node_match, last_matched_info, bug_id, graph_folder_path, save_dp, nxG, nxPos, vis, exact_match_check_flag):
		if s2r_index >= len(s2r_sentence_list):
			return [-1, -1, -1, [], []]
		
		if (v, s2r_index) in visited:
			return save_dp[v][s2r_index]
		
		cur_screen_id = self.helpers.get_key_from_value(screen_Dict, v)
		
		if self.helpers.check_leaf_node(cur_screen_id):
			final_response = [self.helpers.get_key_from_value(screen_Dict, last_matched_info[0]), "Leaf Node", "", cur_screen_id, "", "", "", "", "", "", "", "", "VM", s2r_sentence_list[s2r_index], s2r_index, "", "", last_matched_info[1], ""]
			all_responses.append(final_response)
			save_dp[v][s2r_index] = [-1, -1, -1, [], []]
			return save_dp[v][s2r_index]
		
		visited.add((v, s2r_index))
		
		comp_infos = self.helpers.get_comp_values(df, cur_screen_id)
		comp_str = self.prompts.create_comp_interactions(comp_infos, bug_id, graph_folder_path, cur_screen_id, states_df)
		activity = self.helpers.get_activity(states_df, cur_screen_id)

		cur_prompt, response = self.llm.get_response_for_match(app_name, bug_id, s2r_index, s2r_sentence_list, comp_str, cur_screen_id, activity)
		
		comp_id_list = []
		matched_comps_similarity_exist = False	
		if response == "1":
			_, comp_id_list = self.llm.get_response_for_comp_ids(app_name, bug_id, s2r_index, s2r_sentence_list, comp_str, cur_screen_id, activity) 
		# if response!="1" or (response=="1" and len(comp_id_list)<=1):
		# 	matched_comps_similarity_exist, comp_id_list = self.helpers.get_maximum_similar_interactions(comp_infos, bug_id, cur_screen_id, graph_folder_path, s2r_sentence_list[s2r_index], self.llm)      
		# else:
		# 	comp_info_list = self.prompts.get_comp_info_list(comp_infos)
		# 	object_response = self.llm.get_objects(app_name, s2r_sentence_list[s2r_index])

		# 	if object_response!="0":
		# 		matched_comps_similarity_exist, comp_id_list = self.helpers.get_maximum_similar_comps(comp_infos, comp_info_list, object_response, s2r_sentence_list[s2r_index], self.llm)
		#print("C" + str(comp_id_list))
		if (response=="1" and len(comp_id_list)>0  and comp_id_list[0].isnumeric()) or matched_comps_similarity_exist:
		#if response=="1" and len(comp_id_list)>0:
			if exact_match_check_flag:
				return [v, 1, s2r_index, [], []]
			print("node: " + str(v) + " s2r: " + str(s2r_index) + " " + str(s2r_sentence_list[s2r_index]) + " " + str(cur_screen_id) + " Match: 1")
			#vis.current_node_visualization(v, self.graph[v], cur_screen_id, "1", str(s2r_index) + ". " + s2r_sentence_list[s2r_index], last_matched_info[0], nxG, nxPos)
			matched_ids, matched_sentences, path, path_sentences = self.helpers.get_necessary_info_before_recursion(v, parent, comp_id_list, prev_node_match, comp_infos, last_matched_info, screen_Dict, df, self.graph, bug_id, cur_screen_id, graph_folder_path)
			unique_comp_id_list = self.get_interaction_correctness(matched_sentences, comp_infos, comp_id_list, s2r_sentence_list[s2r_index])
			q_label = self.helpers.get_labels(unique_comp_id_list, prev_node_match, exact_match_check_flag)
			final_response = [self.helpers.get_key_from_value(screen_Dict, last_matched_info[0]), response, cur_prompt, cur_screen_id, comp_id_list, "", "",
			path, "", "1", level, "", q_label, s2r_sentence_list[s2r_index], s2r_index, matched_ids, matched_sentences, last_matched_info[1], path_sentences]

			all_responses.append(final_response)
			
			prev_node_match = True
			ret_match_info_list = []
			comp_id = -1
			selected_interaction_id = -1
			next_path = []
			next_path_sentences = []
			
			if len(comp_id_list)>0:
				for c_index in range(len(comp_id_list)):
					comp_id, selected_interaction_id, last_matched_info, node = self.helpers.get_next_node_info(v, comp_id_list, c_index, comp_infos, s2r_index, screen_Dict)
					# if not self.helpers.check_leaf_node_from_id(screen_Dict,node):
					# 	ambigous_step_check = self.ambiguous_step_check(node, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag)
					# 	if ambigous_step_check and "EM" in q_label:
					# 		q_label = list(map(lambda x: x.replace("EM", "AS"), q_label))
					
					# ret_screen_seq_id, ret_interaction_id, ret_s2r_index, all_next_paths, all_next_path_sentences
					ret_list = self.DFSUtil(node, visited, cur_s2r_visited, screen_Dict, transition_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index+1, all_responses, level+1, path, top_similarity_score, parent, label_count, prev_node_match, last_matched_info, bug_id, graph_folder_path, save_dp, nxG, nxPos, vis, exact_match_check_flag)
					#print(ret_list)
					
					next_path, next_path_sentences = self.helpers.get_next_path_and_sentences(v, ret_list[0], ret_list[1], comp_infos, comp_id, parent, screen_Dict, df, self.graph, bug_id, graph_folder_path, cur_screen_id)
					#print("Np: " + str(next_path))
					if ret_list[0]!=-1 and len(next_path)>0:
						ret_match_info_list.append([comp_id, next_path, next_path_sentences, ret_list[0], ret_list[1], ret_list[2], ret_list[3], ret_list[4]])

						# if node==v:
						# 	matched_interaction_ids = self.temporary_prompt_step_check(node, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag, comp_id)
						# 	matched_interaction_ids.append(selected_interaction_id)
							
						# 	matched_sentences = self.helpers.get_individual_path_sentences(matched_interaction_ids , df, bug_id, graph_folder_path, cur_screen_id)
						# 	#print("bef: " + str(matched_sentences))
						# 	#matched_sentences = self.helpers.remove_duplicate_but_not_in_popup(matched_sentences)
						# 	#print("aft: " + str(matched_sentences))
						# 	if len(matched_sentences)>1 and not self.helpers.check_leaf_node_from_id(screen_Dict,node) and "EM" in q_label:
						# 		q_label = list(map(lambda x: x.replace("EM", "AS"), q_label))
						
						
						if self.helpers.sentence_plural_check(s2r_sentence_list[s2r_index]):
							matched_interaction_ids = []
							temp_interaction_ids = self.temporary_prompt_step_check(v, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag, comp_id)
							matched_interaction_ids = self.ambiguous_step_check(node, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag)
							#matched_interaction_ids = self.temporary_prompt_step_check(node, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag, comp_id)
							matched_interaction_ids.append(selected_interaction_id)
							matched_interaction_ids.extend(temp_interaction_ids)
							filtered_matched_interaction_ids = [x for x in matched_interaction_ids if x!=ret_list[1]]
							filtered_matched_interaction_ids.append(selected_interaction_id)
							
							matched_sentences = self.helpers.get_individual_path_sentences(filtered_matched_interaction_ids, df, bug_id, graph_folder_path, cur_screen_id)
							#print("bef2: " + str(matched_sentences))
							matched_sentences = self.helpers.remove_duplicate_but_not_in_popup(matched_sentences)
							#print("aft2: " + str(matched_sentences))
							print("MST: " + str(matched_sentences))
							if len(matched_sentences)>1 and not self.helpers.check_leaf_node_from_id(screen_Dict,node) and "EM" in q_label:
								q_label = list(map(lambda x: x.replace("EM", "AS"), q_label))

						# elif ret_list[0]!=node:
						# 	matched_interaction_ids = self.ambiguous_step_check(node, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag)
						# 	#matched_interaction_ids = self.temporary_prompt_step_check(node, screen_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, bug_id, graph_folder_path, exact_match_check_flag, comp_id)
						# 	matched_interaction_ids.append(selected_interaction_id)
						
						# 	matched_sentences = self.helpers.get_individual_path_sentences(matched_interaction_ids , df, bug_id, graph_folder_path, cur_screen_id)
						# 	#print("bef: " + str(matched_sentences))
						# 	matched_sentences = self.helpers.remove_duplicate_but_not_in_popup(matched_sentences)
						# 	#print("aft: " + str(matched_sentences))
						# 	if len(matched_sentences)>1 and not self.helpers.check_leaf_node_from_id(screen_Dict,node) and "EM" in q_label:
						# 		q_label = list(map(lambda x: x.replace("EM", "AS"), q_label))
				
				#if len(ret_match_info_list)>0:
				save_dp[v][s2r_index] = self.helpers.get_selected_interaction(v, ret_match_info_list, comp_infos, s2r_index, q_label, selected_interaction_id, next_path, next_path_sentences, parent, screen_Dict, df, self.graph)
				#print("v: " + str(v) + " ind " + str(s2r_index) +  " s2r: " + str(s2r_sentence_list[s2r_index]) + " " + str(save_dp[v][s2r_index][4]) )
				return save_dp[v][s2r_index]
		elif exact_match_check_flag:
			return [-1, -1, -1, [], []]

		#self.graph[v] = self.helpers.remove_duplicate(self.graph[v])
		#vis.current_node_visualization(v, self.graph[v], cur_screen_id, "0", str(s2r_index) + ". " + s2r_sentence_list[s2r_index], last_matched_info[0], nxG, nxPos)
		#print("node: " + str(v) + " s2r: " + str(s2r_index) + " " + str(s2r_sentence_list[s2r_index]) + " " + str(cur_screen_id) + " Match: 0")
		cur_no_match_info_list = []
		
		for neighbour in self.graph[v]:
			prev_node_match = self.helpers.track_prev_node_match(v, neighbour, cur_screen_id, prev_node_match)
			# ret_screen_seq_id, ret_interaction_id, ret_s2r_index, all_next_paths, all_next_path_sentences
			#level = 0
			ret_list = self.DFSUtil(neighbour, visited, cur_s2r_visited, screen_Dict, transition_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index, all_responses, level+1, path, top_similarity_score, parent, label_count, prev_node_match, last_matched_info, bug_id, graph_folder_path, save_dp, nxG, nxPos, vis, exact_match_check_flag)

			if ret_list[0]!=-1:
				cur_no_match_info_list.append([-1, [], [], ret_list[0], ret_list[1], ret_list[2], ret_list[3], ret_list[4]])
		
		if len(cur_no_match_info_list)==0:
			for neighbour in self.graph[v]:
				# if v==neighbour:
				#     continue
				ret_list_other_s2rs = self.DFSUtil(neighbour, visited, cur_s2r_visited, screen_Dict, transition_Dict, df, states_df, app_name, s2r_sentence_list, s2r_index+1, all_responses, level+1, path, top_similarity_score, parent, label_count, prev_node_match, last_matched_info, bug_id, graph_folder_path, save_dp, nxG, nxPos, vis, exact_match_check_flag)
				if ret_list_other_s2rs[0]!=-1:
					cur_no_match_info_list.append([-1, [], [], ret_list_other_s2rs[0], ret_list_other_s2rs[1], ret_list_other_s2rs[2], ret_list_other_s2rs[3], ret_list_other_s2rs[4]])

		if len(cur_no_match_info_list)>0:
			best_cur_no_match_info_list = self.helpers.select_best_matched_interaction(cur_no_match_info_list)
			save_dp[v][s2r_index] = [best_cur_no_match_info_list[3], best_cur_no_match_info_list[4], best_cur_no_match_info_list[5], best_cur_no_match_info_list[6], best_cur_no_match_info_list[7]]
		else:
			save_dp[v][s2r_index] = [-1, -1, -1, [], []]
		return save_dp[v][s2r_index]

	def main(self):
		# euler or study
		dataset = "study"
		if dataset == "study":
			s2r_parsing_file = "../s2r_mapping_gui/inputs/BL Dataset - development-set.csv"
			cache_dir = "../s2r_mapping_gui/cache_study_bug_reports-final"
			result_file = "../s2r_mapping_gui/results/quality_labels_s2r_order-study-ZS.csv"
			individual_s2r_result_file = "../s2r_mapping_gui/results/quality_labels_execution_order-study-ZS.csv"
			quality_label_file = "../s2r_mapping_gui/results/quality_labels-study-ZS.csv"
			graph_folder_dir = "../burt/data/graphs_json_data"

			self.llm = LLM(cache_dir)

			self.writeResults.write_header_for_individual_s2r(result_file)
			self.writeResults.write_header_for_individual_s2r(individual_s2r_result_file)
			self.writeResults.write_header_for_label_and_path(quality_label_file)

			bug_ids = ["2", "10", "110", "117", "130", "135", "248", "1299", "1563", "1568"]
			#bug_ids = ["1481", "129"]
			
			trav_start_screen_ids = ["21c267ef898a5960eea0d8cc0c93ea6eb54b46d154921ccbd6255d36be1f406f"]
			
			graph_folders = ["io.github.zwieback.familyfinance.debug-1.5.5-DEBUG", "me.zhanghai.android.files-1.0.0-beta.11",
							"com.poupa.vinylmusicplayer.debug-0.24.1", "openfoodfacts.github.scrachx.openfood-2.9.8",
							"org.shadowice.flocke.andotp.dev-0.6.3.1-dev", "fr.free.nrw.commons-2.9.0-debug",
							"org.odk.collect.android-v1.20.0", "com.fieldbook.tracker-4.3.3",
							"io.lerk.lrkFM-1.8.0", "io.lerk.lrkFM-2.3.0"]

			#graph_folders = ["com.hexforhn.hex-0.1.0", "org.shadowice.flocke.andotp.dev-0.7.0-dev"]
			
		elif dataset == "euler":
			euler_data_file = "../s2r_mapping_gui/inputs/Euler Execution Data.csv"
			euler_bug_report_data_file = "../s2r_mapping_gui/inputs/euler_bug_report_data.csv"
			cache_dir = "../s2r_mapping_gui/cache_euler_2.0-ZS"
			result_file = "../s2r_mapping_gui/results/quality_labels_s2r_order-euler.csv"
			individual_s2r_result_file = "../s2r_mapping_gui/results/quality_labels_execution_order-euler.csv"
			quality_label_file = "../s2r_mapping_gui/results/quality_labels-euler.csv"
			graph_folder_dir = "../Data/graphs_json_data_EULER"

			self.llm = LLM(cache_dir)

			self.writeResults.write_header_for_individual_s2r(result_file)
			self.writeResults.write_header_for_individual_s2r(individual_s2r_result_file)
			self.writeResults.write_header_for_label_and_path(quality_label_file)

			# Euler dataset
			bug_ids, app_names, app_ver_bug_list = self.helpers.get_app_names_bug_ids_for_euler(euler_data_file)
			
			trav_start_screen_ids = ["21c267ef898a5960eea0d8cc0c93ea6eb54b46d154921ccbd6255d36be1f406f"]

			graph_folders = self.helpers.get_graph_directory(bug_ids, graph_folder_dir)


		for b_index in range(len(bug_ids)):
			self.__init__()
			self.graph = defaultdict(list)
			bug_id = bug_ids[b_index]
			print("Bug ID: " + bug_id)

			s2r_sentence_list = []
			bug_report_step_list = []
			
			if dataset=="study":
				app_name = self.helpers.get_app_names_from_s2rs(s2r_parsing_file, bug_id)
				bug_report = self.helpers.get_bug_report_study(bug_id, s2r_parsing_file)
				identification_response = self.llm.get_bug_report_identification_components(app_name, bug_report, bug_id)
				#print(identification_response)

				label_list, s2r_list =  self.helpers.get_s2rs(bug_report, identification_response)

				individual_s2r_response = self.llm.get_individual_s2rs(app_name, s2r_list, bug_id)
				s2r_sentence_list = self.helpers.get_parsed_individual_s2rs_list(individual_s2r_response)
			elif dataset=="euler":
				app_name = app_names[b_index]
				app_ver_bug = app_ver_bug_list[b_index]

				bug_report = self.helpers.get_bug_report(app_ver_bug, euler_bug_report_data_file)
				identification_response = self.llm.get_bug_report_identification_components(app_name, bug_report, app_ver_bug)
				#print(identification_response)

				label_list, s2r_list =  self.helpers.get_s2rs(bug_report, identification_response)

				individual_s2r_response = self.llm.get_individual_s2rs(app_name, s2r_list, app_ver_bug)
				s2r_sentence_list = self.helpers.get_parsed_individual_s2rs_list(individual_s2r_response)

			graph_file = graph_folder_dir + "/Bug" + bug_id + "/1-" + graph_folders[b_index] + "/1-" + graph_folders[b_index] + "-graph.txt"

			dfs_start_screen_id = trav_start_screen_ids[0]

			transition_list, start_list, end_list, action_list, type_list, id_list, text_list, desc_list, \
				interaction_id_list, execution_id_list, sequence_id_list, positionX_list, positionY_list, height_list, \
					width_list, destination_list = self.helpers.get_graph_transition_data(graph_file)
			transitions_df = self.helpers.create_comp_dataframe(start_list, end_list, transition_list, action_list, type_list, id_list, text_list, desc_list, interaction_id_list, execution_id_list, sequence_id_list, positionX_list, positionY_list, height_list, width_list, destination_list)
			states_df = self.helpers.get_graph_states_data(graph_file)

			screen_Dict, index, transition_Dict, transition_index, edge_list = self.create_graph_dict_for_dfs(start_list, end_list, transition_list)
			
			dfs_start_node = screen_Dict.get(dfs_start_screen_id)
			start_node_comp_values = self.helpers.get_comp_values(transitions_df, dfs_start_screen_id)
			start_node_interactions = self.helpers.get_node_interactions(start_node_comp_values)
			start_node_path_sentences = self.helpers.get_path_sentences(start_node_interactions, transitions_df, bug_id, graph_folders[b_index], dfs_start_screen_id)

			prev_node_match = False
			exact_match_check_flag = False

			s2r_index = 0
			install_flag = False
			if "install" in s2r_sentence_list[s2r_index].lower():
				install_flag = True
				self.writeResults.write_row_for_query_for_individual_s2r(result_file, bug_id, s2r_index, s2r_sentence_list[s2r_index], "", "", "", "1", "", "", "", "", [0], "", "0", "", "", "VM", "", "[Install App]", "")
				self.writeResults.write_row_for_query_for_individual_s2r(individual_s2r_result_file,bug_id, s2r_index, s2r_sentence_list[s2r_index], "", "", "", "1", "", "", "", "", [0], "", "0", "", "", "VM", "", "[Install App]", "")
				s2r_index += 1
			
			if ((s2r_index == 0) or (install_flag and s2r_index==1)) and \
					(("open" in s2r_sentence_list[s2r_index].lower() and "app" in s2r_sentence_list[s2r_index].lower()) \
	 				or ("open" in s2r_sentence_list[s2r_index].lower() and app_name in s2r_sentence_list[s2r_index].lower()) \
					or ("open" in s2r_sentence_list[s2r_index].lower() and self.llm.get_sentence_cosine_similarity("open " + app_name, s2r_sentence_list[s2r_index])>=0.6) \
					or ("launch" in s2r_sentence_list[s2r_index].lower())):
				self.writeResults.write_row_for_query_for_individual_s2r(result_file, bug_id, s2r_index, s2r_sentence_list[s2r_index], "", "", "", "1", "", "", "", "", [0], "", "0", "", "", "EM", start_node_interactions, "[Open app]", start_node_path_sentences)
				self.writeResults.write_row_for_query_for_individual_s2r(individual_s2r_result_file,bug_id, s2r_index, s2r_sentence_list[s2r_index], "", "", "", "1", "", "", "", "", [0], "", "0", "", "", "EM", start_node_interactions, "[Open app]", start_node_path_sentences)
				s2r_index += 1
				prev_node_match = True
			print("sr: " + str(s2r_index))

			all_responses = []

			dfs_visited = set()
			cur_s2r_visited = set()
			path = []
			top_similarity_score = 0
			parent = [-1] * len(transition_list)
			label_count = 0
			level = 0
			
			self.path.path(dfs_start_node, parent, self.graph)
			(s_rows, s_cols) = (index, len(s2r_sentence_list))
			save_dp = [[[-1,-1,-1,[],[]] for _ in range(s_cols)] for _ in range(s_rows)]

			#TODO: "open app" case double check
			dfs_match_info_list = []
			for comp_index in range(len(start_node_comp_values)):
				last_matched_info = (0, 0, start_node_comp_values[comp_index][0])
				node = self.helpers.get_value_from_key(screen_Dict, start_node_comp_values[comp_index][1])
				nxG, nxPos = self.vis.create_visualization_graph(edge_list)
				ret_list = self.DFSUtil(node, dfs_visited, cur_s2r_visited, screen_Dict, transition_Dict, transitions_df, states_df, app_name, s2r_sentence_list, s2r_index, all_responses, level, path, top_similarity_score, parent, label_count, prev_node_match, last_matched_info, bug_id, graph_folders[b_index], save_dp, nxG, nxPos, self.vis, exact_match_check_flag)
				#self.vis.graph_end()
				next_path, next_path_sentences = self.helpers.get_next_path_and_sentences(dfs_start_node, ret_list[0], ret_list[1], start_node_comp_values, int(comp_index)+1, parent, screen_Dict, transitions_df, self.graph, bug_id, graph_folders[b_index], dfs_start_screen_id)
				if ret_list[0]!=-1 and len(next_path)>0:
					dfs_match_info_list.append([int(comp_index)+1, next_path, next_path_sentences, ret_list[0], ret_list[1], ret_list[2], ret_list[3], ret_list[4]])

			all_next_paths, all_next_path_sentences = [], []
			if len(dfs_match_info_list)>0:
				best_start_match_info_list = self.helpers.select_best_matched_interaction(dfs_match_info_list)
				if s2r_index==1:
					all_next_paths, all_next_path_sentences = self.helpers.insert_match_strings(0, ["EM"], best_start_match_info_list[1], best_start_match_info_list[2], best_start_match_info_list[6], best_start_match_info_list[7], start_node_comp_values, best_start_match_info_list[0], parent, screen_Dict, transitions_df, self.graph, 0)
				elif s2r_index==2 and install_flag:
					self.writeResults.write_to_csv(quality_label_file, [bug_id, 0, "", s2r_sentence_list[0], ["VM"], "", "", "", ""])
					all_next_paths, all_next_path_sentences = self.helpers.insert_match_strings(1, ["EM"], best_start_match_info_list[1], best_start_match_info_list[2], best_start_match_info_list[6], best_start_match_info_list[7], start_node_comp_values, best_start_match_info_list[0], parent, screen_Dict, transitions_df, self.graph, 0)
				else:
					# NM: means no match. Identify steps from open app to first interaction match for an S2R
					all_next_paths, all_next_path_sentences = self.helpers.insert_match_strings(-1, ["NM"], best_start_match_info_list[1], best_start_match_info_list[2], best_start_match_info_list[6], best_start_match_info_list[7], start_node_comp_values, best_start_match_info_list[0], parent, screen_Dict, transitions_df, self.graph, 0)
					#all_next_paths, all_next_path_sentences = best_start_match_info_list[6], best_start_match_info_list[7]
			elif s2r_index==1:
				all_next_paths, all_next_path_sentences = self.helpers.insert_match_strings(0, ["EM"], [], [], [], [], start_node_comp_values, -1, parent, screen_Dict, transitions_df, self.graph, 0)
			

			#print("ab: " + str(save_dp[3][2][4]))
			# for i in range(len(dfs_match_info_list)):
			#     print(dfs_match_info_list[i])

			# for i in range(index):
			#     for j in range(len(s2r_sentence_list)):
			#         if save_dp[i][j][0]!=-1:
			#             print(str(i) + " " + str(j) + " " + str(save_dp[i][j]))

			for f_response in all_responses:
				self.writeResults.write_row_for_query_for_individual_s2r(individual_s2r_result_file, bug_id, f_response[14], f_response[13], f_response[17], f_response[0], f_response[2], f_response[1], f_response[3], f_response[4], f_response[5], f_response[6], f_response[7], f_response[8], f_response[9], f_response[10], f_response[11], f_response[12], f_response[15], f_response[16], f_response[18])

			all_responses = self.helpers.filter_responses_VM(s2r_sentence_list, all_responses)

			for f_response in all_responses:
				self.writeResults.write_row_for_query_for_individual_s2r(result_file, bug_id, f_response[14], f_response[13], f_response[17], f_response[0], f_response[2], f_response[1], f_response[3], f_response[4], f_response[5], f_response[6], f_response[7], f_response[8], f_response[9], f_response[10], f_response[11], f_response[12], f_response[15], f_response[16], f_response[18])

			self.writeResults.write_row_for_query_for_s2r_labels_and_paths(quality_label_file, bug_id, bug_report_step_list, s2r_sentence_list, all_next_paths, all_next_path_sentences, transitions_df)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	args = vars(parser.parse_args())

	parse_gui = Mapping_GUI()
	parse_gui.main()




