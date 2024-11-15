import csv
import ast
from helpers import Helpers

class WriteResults:
	def __init__(self):
		self.helpers = Helpers()

	def write_to_csv(self, write_file, row):
		with open(write_file, 'a') as file:
			writer = csv.writer(file)
			writer.writerow(row)

	def write_header_for_similarity(self, filename):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Text", "Embedding"])

	def write_header_for_query(self, filename):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Bug_id", "S2R Actions", "S2R Objects", "Prompts", "Response", "Screen ID", "Prompt for Component", "Component Info"])

	def write_header_for_individual_s2r(self, filename):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Bug_id", "S2R Index", "S2R Sentence", "Last Matched S2R", "Last Matched Node", "Prompts", "Response", "Current Screen ID", "Component IDs", "Transition ID", "End ID", "Path", "Component Info", "Checkpoint", "Path Length", "Similarity Score", "Quality Labels", "Matched Transition IDs", "Matched Sentences", "Path Sentences"])

	def write_header_for_label_and_path(self, filename):
		with open(filename, 'w') as file:
			writer = csv.writer(file)
			writer.writerow(["Bug_id", "S2R Index", "Bug Report S2Rs", "Individual Step", "Quality Labels", "Paths", "Source", "Destination", "Path Sentences"])
	
	def write_row_for_similarity(self, filename, text, embedding):
		result_row = []
		result_row.append(text)
		result_row.append(embedding)
		self.write_to_csv(filename, result_row)

	def write_row_for_query(self, filename, bug_id, s2r_action, s2r_object, prompts, response, screen_id, comp_prompt, comp_info):
		result_row=[]
		result_row.append(bug_id)
		result_row.append(s2r_action)
		result_row.append(s2r_object)
		result_row.append(prompts)
		result_row.append(response)
		result_row.append(screen_id)
		result_row.append(comp_prompt)
		result_row.append(comp_info)
		self.write_to_csv(filename, result_row)

	def write_row_for_query_for_individual_s2r(self, filename, bug_id, s2r_index, s2r_sentence, last_matched_s2r, node, prompts, response, screen_id, comp_id, transition_id, end_id, path, identified_comp_info, checkpoint, length, sim_score, quality_labels, matched_ids, matched_sentences, path_sentences):
		result_row=[]
		result_row.append(bug_id)
		result_row.append(s2r_index)
		result_row.append(s2r_sentence)
		result_row.append(last_matched_s2r)
		result_row.append(node)
		result_row.append(prompts)
		result_row.append(response)
		result_row.append(screen_id)
		result_row.append(comp_id)
		result_row.append(transition_id)
		result_row.append(end_id)
		result_row.append(path)
		result_row.append(identified_comp_info)
		result_row.append(checkpoint)
		result_row.append(length)
		result_row.append(sim_score)
		result_row.append(quality_labels)
		result_row.append(matched_ids)
		result_row.append(matched_sentences)
		result_row.append(path_sentences)
		self.write_to_csv(filename, result_row)

	# def write_row_for_query_for_s2r_labels_and_paths(self, filename, bug_id, bug_report_step_list, s2r_sentence_list, path_strings, path_sentence_strings, transitions_df):
	# 	s2r_found_list = set()
	# 	result_row_list = []
	# 	for i in range(len(path_strings)):
	# 		path_splits = path_strings[i].split("#")
	# 		path_sentence_splits = path_sentence_strings[i].split("#")

	# 		if len(path_splits)==3:
	# 			s2r_index = int(path_splits[0])
	# 			#print("s2r: " + str(s2r_index))
	# 			if s2r_index!=-1:
	# 				s2r_found_list.add(s2r_index)
	# 				s2r_sentence = s2r_sentence_list[s2r_index]
	# 			label = path_splits[1]
	# 			path = ast.literal_eval(path_splits[2])
	# 			path_string = ast.literal_eval(path_sentence_splits[2])

	# 			for j in range(len(path)):
	# 				if len(path)>=2 and j==len(path)-1:
	# 					continue
	# 				transition_info = self.helpers.get_interaction_values(transitions_df, path[j])
	# 				if j==0 and s2r_index!=-1:
	# 					row = [bug_id, s2r_index+1, "", s2r_sentence, label, path[j], transition_info[0], transition_info[1], path_string[j]]
	# 					result_row_list.append(row)
	# 				else: 
	# 					row = [bug_id, s2r_index+1, "", "", "", path[j], transition_info[0], transition_info[1], path_string[j]]
	# 					result_row_list.append(row)

	# 	# for j in range(len(result_row_list)):
	# 	# 	if abs(int(result_row_list[j][1])-int(result_row_list[j-1][1]))>1:
	# 	# 		self.write_to_csv(filename, result_row_list[j])
	# 	# 	else:



	# 	for i in range(len(s2r_sentence_list)):
	# 		if i not in s2r_found_list:
	# 			self.write_to_csv(filename, [bug_id, i+1, "", s2r_sentence_list[i], ["VM"], "", "", "", ""])
	# 		else:
	# 			for j in range(len(result_row_list)):
	# 				if int(result_row_list[j][1])-1==i:
	# 					self.write_to_csv(filename, result_row_list[j])

	# 	# for row in result_row_list:
	# 	# 	self.write_to_csv(filename, row)
	# 	self.write_to_csv(filename, ["", "", "", "", "", "", "", "", ""])

	def write_row_for_query_for_s2r_labels_and_paths(self, filename, bug_id, bug_report_step_list, s2r_sentence_list, path_strings, path_sentence_strings, transitions_df):
		s2r_found_list = set()
		result_row_list = []
		for i in range(len(path_strings)):
			#print(path_strings[i])
			path_splits = path_strings[i].split("#")
			path_sentence_splits = path_sentence_strings[i].split("#")

			if len(path_splits)==3:
				s2r_index = int(path_splits[0])
				#print("s2r: " + str(s2r_index))
				if s2r_index!=-1:
					s2r_found_list.add(s2r_index)
					s2r_sentence = s2r_sentence_list[s2r_index]
				label = path_splits[1]
				path = ast.literal_eval(path_splits[2])
				path_string = ast.literal_eval(path_sentence_splits[2])

				for j in range(len(path)):
					if len(path)>=2 and j==len(path)-1:
						continue
					transition_info = self.helpers.get_interaction_values(transitions_df, path[j])
					if j==0 and s2r_index!=-1:
						row = [bug_id, s2r_index+1, "", s2r_sentence, label, path[j], transition_info[0], transition_info[1], path_string[j]]
						result_row_list.append(row)
					else: 
						row = [bug_id, s2r_index+1, "", "", "", path[j], transition_info[0], transition_info[1], path_string[j]]
						result_row_list.append(row)

		# for j in range(len(result_row_list)):
		# 	if abs(int(result_row_list[j][1])-int(result_row_list[j-1][1]))>1:
		# 		self.write_to_csv(filename, result_row_list[j])
		# 	else:

		#print(result_row_list)



		# for i in range(len(s2r_sentence_list)):
		# 	if i not in s2r_found_list:
		# 		self.write_to_csv(filename, [bug_id, i+1, "", s2r_sentence_list[i], ["VM"], "", "", "", ""])
		# 	else:
		# 		for j in range(len(result_row_list)):
		# 			if int(result_row_list[j][1])-1==i or int(result_row_list[j][1])==0:
		# 				self.write_to_csv(filename, result_row_list[j])
		
		cur_index = 0
		for j in range(len(result_row_list)):
			if j>0 and int(result_row_list[j][1])-int(result_row_list[j-1][1])>1:
				for k in range(int(result_row_list[j-1][1])+1,int(result_row_list[j][1])):
					self.write_to_csv(filename, [bug_id, k, "", s2r_sentence_list[k-1], ["VM"], "", "", "", ""])
			cur_index = result_row_list[j][1]
			self.write_to_csv(filename, result_row_list[j])
		
		for j in range(cur_index+1, len(s2r_sentence_list)+1):
			self.write_to_csv(filename, [bug_id, j, "", s2r_sentence_list[j-1], ["VM"], "", "", "", ""])


		# for row in result_row_list:
		# 	self.write_to_csv(filename, row)
		self.write_to_csv(filename, ["", "", "", "", "", "", "", "", ""])





