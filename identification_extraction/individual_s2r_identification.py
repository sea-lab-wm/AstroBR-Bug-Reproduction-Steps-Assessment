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

class Mapping_GUI():
	def __init__(self):
		self.writeResults = WriteResults()
		self.prompts = Prompts()
		self.helpers = Helpers()

	def addEdge(self, u, v):
		self.graph[u].append(v)
	
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

	def main(self):
		dataset = "euler"
		if dataset == "study":
			s2r_parsing_file = "gpt4br/individual_s2r_identification/inputs/BL Dataset - development-set.csv"
			cache_dir = "gpt4br/individual_s2r_identification/cache_study_individual_s2r-ZS"
			result_file = "gpt4br/individual_s2r_identification/quality_labels_s2r_order-study-ZS.csv"
			individual_s2r_identification_result_file = "gpt4br/individual_s2r_identification/results-indv_s2r/individual_s2r-study.csv"
			
			self.llm = LLM(cache_dir)

			self.writeResults.write_header_for_individual_s2r(result_file)
			self.writeResults.write_individual_s2r_header(individual_s2r_identification_result_file)

			#bug_ids = ["2", "10", "110", "117", "130", "135", "248", "1299", "1563", "1568"]
			bug_ids = ["2", "10", "110", "117", "130", "135", "248", "1299", "1563", "1568", "8", "18", "19",
			  "44", "45", "53", "54", "71", "76", "92", "128", "129", "158", "160",
			  "162", "168", "191", "192", "199", "200", "201", "209", "256", "1073", "1096", "1146",
			  "1147", "1150", "1151", "1198", "1202", "1205", "1207", "1214", "1215", "1389", "1399",
			  "1406", "1425", "1430", "1441", "1445", "1641", "1645"]
		elif dataset=="euler":
			euler_data_file = "gpt4br/s2r_mapping_gui/inputs/Euler Execution Data.csv"
			euler_bug_report_data_file = "gpt4br/s2r_mapping_gui/inputs/euler_bug_report_data.csv"
			cache_dir = "gpt4br/individual_s2r_identification/cache_euler_2.0_individual_s2r-ZS"
			result_file = "gpt4br/individual_s2r_identification/quality_labels_s2r_order-euler.csv"
			individual_s2r_identification_result_file = "gpt4br/individual_s2r_identification/results-indv_s2r/individual_s2r-zero-shot-euler.csv"

			self.llm = LLM(cache_dir)

			self.writeResults.write_header_for_individual_s2r(result_file)
			self.writeResults.write_individual_s2r_header(individual_s2r_identification_result_file)

			# Euler dataset
			bug_ids, app_names, app_ver_bug_list = self.helpers.get_app_names_bug_ids_for_euler(euler_data_file)

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

			self.writeResults.write_row_for_individual_s2rs(individual_s2r_identification_result_file, bug_id, s2r_sentence_list)
			
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	args = vars(parser.parse_args())

	parse_gui = Mapping_GUI()
	parse_gui.main()




