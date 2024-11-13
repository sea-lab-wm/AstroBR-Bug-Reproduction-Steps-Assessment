import pandas as pd
from bs4 import BeautifulSoup
import os
import itertools
import json
import re
from bfs import BFS
import ast

class Helpers:
	def __init__(self):
		self.bfs = BFS()

	def get_actions_from_s2rs(self, filename, bug_id):
		df = pd.read_csv(filename)
		if not df['Bug_id'].isin([int(bug_id)]).any():
			print(f'Bug Id: {bug_id} does not exist in {filename}')
		actions = df.loc[df['Bug_id']==int(bug_id), "Event (Final)"].values.tolist()
		return actions[0]
	
	def get_ground_truth_screen_and_interaction(self, filename, s2r_index, s2r_sentence_list, bug_id, src_screen_id):
		df = pd.read_csv(filename)
		if not df['Bug ID'].isin([int(bug_id)]).any():
			print(f'Bug Id: {bug_id} does not exist in {filename}')
		if not df['S2R Indices'].isin([int(s2r_index)+1]).any():
			print(f'S2R Indices: {int(s2r_index)+1} does not exist in {filename}')
		if not df['Interaction in Natural Language Not Unique'].isin([s2r_sentence_list[s2r_index]]).any():
			print(f'S2R Sentence: {s2r_sentence_list[s2r_index]} does not exist in {filename}')
		interaction_id_list = df.loc[(df['Bug ID']==int(bug_id)) & (df['S2R Indices']==int(s2r_index)+1) & (df['Interaction in Natural Language Not Unique']==s2r_sentence_list[s2r_index]) & (df['Source_Screen_Id']==src_screen_id), "Interaction_Id"].values.tolist()
		target_screen_id_list = df.loc[(df['Bug ID']==int(bug_id)) & (df['S2R Indices']==int(s2r_index)+1) & (df['Interaction in Natural Language Not Unique']==s2r_sentence_list[s2r_index]) & (df['Source_Screen_Id']==src_screen_id), "Target_Screen_Id"].values.tolist()
		return interaction_id_list, target_screen_id_list
	
	def get_objects_from_s2rs(self, filename, bug_id):
		df = pd.read_csv(filename)
		if not df['Bug_id'].isin([int(bug_id)]).any():
			print(f'Bug Id: {bug_id} does not exist in {filename}')
		objects = df.loc[df['Bug_id']==int(bug_id), "Object (Final)"].values.tolist()
		return objects[0]
	
	# def get_app_names_from_s2rs(self, filename, bug_id):
	# 	df = pd.read_csv(filename)
	# 	if not df['Bug_id'].isin([int(bug_id)]).any():
	# 		print(f'Bug Id: {bug_id} does not exist in {filename}')
	# 	app_names = df.loc[df['Bug_id']==int(bug_id), "App Names"].values.tolist()
	# 	return  app_names[0]

	def get_app_names_from_s2rs(self, filename, bug_id):
		df = pd.read_csv(filename)
		if not df['Bug_id'].astype(str).isin([bug_id]).any():
			print(f'Bug Id: {bug_id} does not exist in {filename}')
		app_names = df.loc[df['Bug_id'].astype(str)==bug_id, "App Names"].values.tolist()
		return  app_names[0]
	
	def get_app_names_bug_ids_for_euler(self, filename):
		df = pd.read_csv(filename)
		bug_id_list = []
		app_name_list = []
		app_ver_bug_list = []

		for _,row in df.iterrows():
			bug_id_list.append(str(row["unique_bg_id"]))
			app_name_list.append(row["app"])
			app_ver_bug_list.append(row["app_ver_bug"])

		return bug_id_list, app_name_list, app_ver_bug_list
	
	def get_bug_report(self, app_ver_bug, filename):
		app_ver_bug += ".xml"
		df = pd.read_csv(filename)
		if not df['Bug_id'].isin([app_ver_bug]).any():
			print(f'Bug Id: {app_ver_bug} does not exist in {filename}')
		bug_report = df.loc[df['Bug_id']==app_ver_bug, "Bug Reports"].values.tolist()
		return bug_report[0]
	
	def get_bug_report_study(self, bug_id, filename):
		df = pd.read_csv(filename)
		if not df['Bug_id'].astype(str).isin([bug_id]).any():
			print(f'Bug Id: {bug_id} does not exist in {filename}')
		bug_report = df.loc[df['Bug_id'].astype(str)==bug_id, "Bug Reports"].values.tolist()
		return bug_report[0]
	
	def get_atomic_and_bug_report_steps(self, filename):
		df = pd.read_excel(filename, index_col=0)

		atomic_step_list = []
		bug_report_step_list = []
		for _, row in df.iterrows():
			if (type(row["Atomic step"])==float and self.isNan(row["Atomic step"])) or row["Atomic step"]=="Did you reproduce the bug? (Yes/No)":
				continue
			atomic_step_list.append(row["Atomic step"])
			if type(row["Step from the bug report (BR)"])==float and self.isNan(row["Atomic step"]):
				bug_report_step_list.append("")
			else:
				bug_report_step_list.append(row["Step from the bug report (BR)"])
		return atomic_step_list, bug_report_step_list
	
	def get_s2r_contents(self, filename, bug_id):
		df = pd.read_csv(filename)
		if not df['Bug_id'].isin([int(bug_id)]).any():
			print(f'Bug Id: {bug_id} does not exist in {filename}')
		s2r_sentences = df.loc[df['Bug_id']==int(bug_id), "Parsed S2R Sentences"].values.tolist()
		return s2r_sentences[0]
	
	def get_s2r_sentences_from_bug_ids(self, filename, bug_id):
		df = pd.read_csv(filename)
		if not df['Bug_id'].isin([int(bug_id)]).any():
			print(f'Bug Id: {bug_id} does not exist in {filename}')
		s2r_sentences = df.loc[df['Bug_id']==int(bug_id), "Individual Step"].values.tolist()
		bug_report_steps = df.loc[df['Bug_id']==int(bug_id), "S2Rs"].values.tolist()
		return s2r_sentences, bug_report_steps
	
	def remove_vocabulary_mismatch_labels(self, s2r_sentence, all_responses):
	   return list(itertools.filterfalse(lambda x: (x[13] == s2r_sentence and x[12] == "VM"), all_responses))
	
	def filter_responses_VM(self, s2r_sentence_list, all_responses):
		temp_responses = []
		for i in range(len(s2r_sentence_list)):
			cur_responses = list(filter(lambda x: x[13]==s2r_sentence_list[i] and x[14]==i and x[12]!="VM",all_responses))
			if len(cur_responses)>0:
				temp_responses.extend(cur_responses)
			else:
				cur_responses = list(filter(lambda x: x[13]==s2r_sentence_list[i] and x[14]==i and x[12]=="VM",all_responses))
				if len(cur_responses)>0:
					temp_responses.append(cur_responses[0])
		return temp_responses

	def get_comp_id(self, res_id):
		if res_id is None or len(res_id)<=0 or "/" not in res_id:
			return ""
		id = res_id.split("/")[1]
		return id
	
	def get_comp_id_parsed(self, res_id):
		comp_id = self.get_comp_id(res_id)
		split_comp_id = re.split(r'[^a-zA-Z]', comp_id)
		return " ".join(split_comp_id)

	def get_comp_type(self, comp_class):
		if comp_class is None or len(comp_class)<=0:
			return ""
		type = comp_class.split(".")
		return type[len(type)-1]

	def get_execution_info(self, states_file, screen_id):
		states_df = pd.read_csv(states_file)
		states_row = states_df[states_df['screen_id']==screen_id].values.tolist()
		if len(states_row)<=0:
			print("screen not found")
			return [], [], []
		row = states_row[0]
		return row[1], row[2], row[3]

	def get_execution_data_filepath(self, tr_src, cs_src, source, exec_id):
		if source == 'CS':
			if exec_id==0:
				json_filepath = cs_src + "/Execution-1.json"
			elif exec_id==1:
				json_filepath = cs_src + "/Execution-2.json"
		elif source == 'TR':
			json_filepath = tr_src + "/Execution-1.json"
		return json_filepath

	def get_xml_filepath(self, tr_src, cs_src, seq_id, source, exec_id, graph_path):
		#print(seq_id)
		seq_id = int(seq_id)-1
		if source == 'CS':
			if exec_id==0:
				xml_filepath = cs_src + "/" + graph_path + "-1-Expected-Top_Down-" + str(seq_id) + ".xml"
			elif exec_id==1:
				xml_filepath = cs_src + "/" + graph_path + "-1-Expected-Bottom_Up-" + str(seq_id) + ".xml"
		elif source == 'TR':
			xml_filepath = tr_src + "/" + graph_path + "-1-User-Trace-" + str(seq_id) + ".xml"
		return xml_filepath
	
	def create_graph_dict(self, start_list, end_list):
		Dict = {}
		index = 0
		for i in range(len(start_list)):
			if start_list[i] not in Dict:
				Dict[start_list[i]] = index
				index = index + 1

			if end_list[i] not in Dict:
				Dict[end_list[i]] = index
				index = index + 1

		adjList = [[] for _ in range(index)]
		for i in range(len(start_list)):
			start_index = Dict.get(start_list[i])
			end_index = Dict.get(end_list[i])

			self.bfs.addEdge(adjList, start_index, end_index)
		
		return Dict, adjList, index

	def isNan(self, x):
		if x==None:
			return True
		if x=="":
			return True
		if type(x)==float:
			return x != x
		return False

	def get_graph_transition_data(self, filename):
		transition_list = []
		start_list = []
		end_list = []
		action_list = []
		type_list = []
		id_list = []
		text_list = []
		desc_list = []

		interaction_id_list = []
		execution_id_list = []
		sequence_id_list = []
		positionX_list = []
		positionY_list = []
		height_list = []
		width_list = []
		destination_list = []

		with open(filename, "r") as f:
			content = f.read()
		content_splits = content.split("\n")

		transition_flag = False
		for each_content in content_splits:
			if len(each_content)<=0:
				continue
			elif "Transitions (" in each_content:
				transition_flag = True
			elif "States (" in each_content:
				transition_flag = False
				break
			elif transition_flag:
				if "s:" not in each_content or "t:" not in each_content:
					continue
				#print("each: "  + str(each_content))
				route_splits = each_content.split(":")
				transition = route_splits[0]
				start = route_splits[2].split(",")[0]
				end = route_splits[3].split(")")[0] 

				action = ""
				if "act=" in route_splits[4]:
					action_split = route_splits[4].split("act=")[1]
					action = action_split[4:action_split.find(",")]
				action_list.append(action)

				type = ""
				if "ty=" in route_splits[4]:
					type_split = route_splits[4].split("ty=")[1]
					type = type_split[0:type_split.find(",")]
				type_list.append(type)

				id = ""
				if "idx=" in route_splits[4]:
					id_split = route_splits[4].split("idx=")[1]
					id = id_split[0:id_split.find(",")]
				id_list.append(id)

				text = ""
				if "tx=" in route_splits[4]:
					text_split = route_splits[4].split("tx=")[1]
					text = text_split[0:text_split.find(",")]
				text_list.append(text)

				desc = ""
				if "dsc=" in route_splits[4]:
					desc_split = route_splits[4].split("dsc=")[1]
					desc = desc_split[0:desc_split.find("]")]
				desc_list.append(desc)

				interaction_id = ""
				if "id=" in route_splits[4]:
					interaction_id_split = route_splits[4].split("id=")[1]
					interaction_id = interaction_id_split[0:interaction_id_split.find(",")]
				interaction_id_list.append(interaction_id)

				execution_id = ""
				if "ex=" in route_splits[4]:
					execution_id_split = route_splits[4].split("ex=")[1]
					execution_id = execution_id_split[0:execution_id_split.find(",")]
				execution_id_list.append(execution_id)

				sequence_id = ""
				if "sq=" in route_splits[4]:
					sequence_id_split = route_splits[4].split("sq=")[1]
					sequence_id = sequence_id_split[0:sequence_id_split.find(",")]
				sequence_id_list.append(sequence_id)

				positionX = ""
				if ", x=" in route_splits[4]:
					positionX_split = route_splits[4].split(", x=")[1]
					positionX = positionX_split[0:positionX_split.find(",")]
				positionX_list.append(positionX)

				positionY = ""
				if ", y=" in route_splits[4]:
					positionY_split = route_splits[4].split(", y=")[1]
					positionY = positionY_split[0:positionY_split.find(",")]
				positionY_list.append(positionY)

				height = ""
				if ", h=" in route_splits[4]:
					height_split = route_splits[4].split(", h=")[1]
					height = height_split[0:height_split.find(",")]
				height_list.append(height)

				width = ""
				if ", w=" in route_splits[4]:
					width_split = route_splits[4].split(", w=")[1]
					width = width_split[0:width_split.find(",")]
				width_list.append(width)

				destination = ""
				if "ds=" in route_splits[4]:
					destination_split = route_splits[4].split("ds=")[1]
					destination = destination_split[0:destination_split.find(" ")]
				destination_list.append(destination)

				transition_list.append(transition)
				start_list.append(start)
				end_list.append(end)
			
		f.close()
		return transition_list, start_list, end_list, action_list, type_list, id_list, text_list, desc_list, \
			interaction_id_list, execution_id_list, sequence_id_list, positionX_list, positionY_list, height_list, width_list, destination_list
	
	def get_graph_states_data(self, filename):
		state_list = []
		state_comp_list = []
		state_activity_list = []
		state_comp_dict = {}

		with open(filename, "r") as f:
			content = f.read()
		content_splits = content.split("\n")

		states_flag = False
		for each_content in content_splits:
			if len(each_content)<=0:
				continue
			elif "States (" in each_content:
				states_flag = True
			elif states_flag:
				if "," not in each_content or "\"dynGuiComponents\"" not in each_content:
					continue
				# print(each_content)
				# print("\n")
				screen_splits = each_content.split(",")
				state = screen_splits[0]
				activity = screen_splits[1]

				comps_list = []

				if "\"dynGuiComponents\"" in each_content:
					comps_splits = each_content.split("\"dynGuiComponents\"")
					all_comps = comps_splits[1]

					if "}" in all_comps:
						all_comps_splits = all_comps.split("}")

						for each_comp in all_comps_splits:
							if "comp" not in each_comp:
								continue
							if "t=" in each_comp:
								text_splits = each_comp.split("t='")
								# print("rt")
								# print(text_splits)
								if len(text_splits)>0 and len(text_splits[1])>1:
									redundant_text = text_splits[1]
									redundant_text_splits = redundant_text.split("'")
									text = redundant_text_splits[0]
									if len(text)>0 and text!="null":
										comps_list.append(text)
							elif "ix=" in each_comp:
								id_splits = each_comp.split("ix='")
								if len(id_splits)>0 and len(id_splits[1])>1:
									redundant_id = id_splits[1]
									redundant_id_splits = redundant_id.split("'")
									id = redundant_id_splits[0]
									if "/" in id:
										clean_id_splits = id.split("/")
										clean_id = clean_id_splits[1]
										if len(clean_id)>0 and clean_id!="null":
											comps_list.append(clean_id)
				#if len(comps_list)>0:
				state_list.append(state)
				state_activity_list.append(activity)
				state_comp_list.append(comps_list)

		state_comp_dict = {'state': state_list, 'state_comp_list': state_comp_list, 'activity': state_activity_list}
		state_comp_df = pd.DataFrame(state_comp_dict)
			
		f.close()
		return state_comp_df
	
	def create_comp_dict(self, start_list, end_list, action_list, type_list, id_list, text_list):
		comp_dict = {}
		for i in range(len(start_list)):
			comp_dict[start_list[i], end_list[i]] = [action_list[i], type_list[i], id_list[i], text_list[i]]    
		
		return comp_dict
	
	def create_comp_dataframe(self, start_list, end_list, transition_list, action_list, type_list, id_list, text_list, desc_list, interaction_id_list, execution_id_list, sequence_id_list, positionX_list, positionY_list, height_list, width_list, destination_list):
		dict = {'start': start_list, 'end': end_list, 'transition': transition_list,  'action': action_list, 'type': type_list, 'id': id_list, 'text': text_list, 'desc': desc_list, \
				'interaction_id': interaction_id_list, 'execution_id': execution_id_list, 'sequence_id': sequence_id_list, 'positionX': positionX_list, 'positionY': positionY_list, \
				'height': height_list, 'width': width_list, 'destination': destination_list}
		df = pd.DataFrame(dict)
		return df
	
	def get_comp_values(self, df, start):
		if not df['start'].isin([start]).any():
			print(f'Comp Start: {start} does not exist in dataframe')
		comp_info = df.loc[df['start']==start, ["transition", "end", "action", "type", "id", "text", "desc", "interaction_id", "execution_id", "sequence_id", "positionX", "positionY", "height", "width", "destination"]].values.tolist()
		return comp_info
	
	def get_interaction_values(self, df, transition):
		if not df['transition'].isin([transition]).any():
			print(f'Transition Interaction: {transition} does not exist in dataframe')
		comp_info = df.loc[df['transition']==transition, ["start", "end", "action", "type", "id", "text", "desc", "interaction_id", "execution_id", "sequence_id", "positionX", "positionY", "height", "width", "destination"]].values.tolist()
		return comp_info[0]
	
	def get_node_interactions(self, comp_values):
		interaction_ids = []
		for i in range(len(comp_values)):
			interaction_ids.append([comp_values[i][0]])
		return interaction_ids
	
	def get_state_comp_values(self, df, state):
		if not df['state'].isin([state]).any():
			print(f'State: {state} does not exist in dataframe')
		state_comp_info = df.loc[df['state']==state, "state_comp_list"].values.tolist()
		return state_comp_info
	
	def get_activity(self, df, state):
		if not df['state'].isin([state]).any():
			print(f'State: {state} does not exist in dataframe')
		state_activity = df.loc[df['state']==state, "activity"].values.tolist()
		screen = self.get_activity_screen(state_activity[0])
		return screen
	
	def get_all_comps_list(self, xml_file):
		if not os.path.exists(xml_file):
			return 0
		with open(xml_file, 'r') as f:
			xml_code = f.read()

		Bs_data = BeautifulSoup(xml_code, "xml")
		b_unique = Bs_data.find_all('node')

		all_comps = ""
		comp_idx = 1
		for item in b_unique:
			comp_text = item.get('text')
			comp_desc = item.get('content-desc')
			comp_id = self.get_comp_id(item.get('resource-id'))
			comp_type = self.get_comp_type(item.get('class'))
			comp_str = str(comp_idx) + ": " + comp_id + ", " + comp_text + ", " + comp_type + ", " + comp_desc  +  "\n"
			comp_idx += 1
			all_comps += comp_str
		return all_comps
	
	def get_all_comps_in_details_with_action(self, xml_file):
		if not os.path.exists(xml_file):
			return 0
		with open(xml_file, 'r') as f:
			xml_code = f.read()

		Bs_data = BeautifulSoup(xml_code, "xml")
		b_unique = Bs_data.find_all('node')

		all_comps = ""
		comp_idx = 1
		for item in b_unique:
			if comp_idx == 100:
				break
			comp_str = ""
			comp_text = item.get('text')
			comp_desc = item.get('content-desc')
			comp_id = self.get_comp_id_parsed(item.get('resource-id'))
			comp_type = self.get_comp_type(item.get('class'))

			comp_flag = False
			if len(comp_text)>0:
				comp_str = str(comp_idx) + ": " + comp_text
				comp_flag = True
			elif len(comp_id)>0:
				comp_str = str(comp_idx) + ": " + comp_id
				comp_flag = True
			elif len(comp_desc)>0:
				comp_str = str(comp_idx) + ": " + comp_desc
				comp_flag = True

			if comp_flag == False:
				continue

			if len(comp_type)>0:
				comp_str += " which has the category of " + comp_type
			
			action_flag = False
			click_flag = False
			long_click_flag = False
			scroll_flag = False
			input_flag = False

			if item.get('clickable') == "true":
				click_flag = True
				action_flag = True
			if item.get('long-clickable') == "true":
				long_click_flag = True
				action_flag = True
			if item.get('scrollable') == "true":
				scroll_flag = True
				action_flag = True
			if comp_type == "EditText":
				input_flag = True
				action_flag = True

			if action_flag == True:
				if len(comp_type)>0:
					comp_str += " and where we can perform the following actions:"
				else:
					comp_str += " where we can perform the following actions:"

				if click_flag == True:
					comp_str += " click"
				if long_click_flag == True:
					comp_str += " long-click"
				if scroll_flag == True:
					comp_str += " scroll"
				if input_flag == True:
					comp_str += " input"
			comp_str = comp_str.lower()
			comp_str += "\n"

			comp_idx += 1
			all_comps += comp_str
		
		return all_comps
	
	def get_comps_as_xmls(self, xml_file):
		with open(xml_file, 'r') as f:
			xml_code = f.read()

		return xml_code
	
	def get_comp_strs(self, comps_from_s2rs):
		s2r_list = comps_from_s2rs.split("\n")
		s2rs = []
		for i in range(len(s2r_list)):
			s2r_flawed = s2r_list[i]
			if s2r_flawed is None or len(s2r_flawed)<=0:
				continue
			cur_s2r_splits = [s.strip() for s in s2r_flawed.split(".")]
			s2r_clean = cur_s2r_splits[1]
			s2rs.append(s2r_clean)
		return s2rs
	
	def get_activity_screen(self, activity):
		if "Activity" in activity:
			activity_splits = [s.strip() for s in activity.split("Activity")]
			screen_name = activity_splits[0]
			screen_name = self.camel_case_split(screen_name)
			return screen_name
		return ""
	
	def get_s2r_sentences(self, all_s2r_contents):
		s2r_list = all_s2r_contents.split("\n")
		s2rs = []
		for i in range(len(s2r_list)):
			s2r_flawed = s2r_list[i]
			if s2r_flawed is None or len(s2r_flawed)<=0:
				continue
			cur_s2r_splits = [s.strip() for s in s2r_flawed.split(":")]
			s2r_clean = ' '.join(cur_s2r_splits[1:])
			s2rs.append(s2r_clean)
		return s2rs
	
	def get_key_from_value(self, dict, value):
		key = list(filter(lambda x: dict[x]==value, dict))[0]
		return key
	
	def get_value_from_key(self, dict, key):
		return dict[key]
	
	def check_int(self, str):
		try: 
			int(str)
			return True
		except:
			return False
	
	def pop_up_keyword(self, sentence):
		keywords = ["allow", "yes", "no", "skip", "ok", "cancel"]

		for word in keywords:
			if word in sentence.lower():
				return True
		return False
	
	def s2r_keyword(self, sentence):
		keywords = ["icon", "button", "imagebutton"]
		for word in keywords:
			if word in sentence.lower():
				return True 
		return False
	
	def filter_prompt_response(self, response):
		if "Reasoning" in response:
			response_splits = response.split("\n")
			if len(response_splits)>1:
				response = response_splits[0]
		if "Expected Response" in response and "S2R Sentence" in response:
			response_splits = response.split("\n")
			response = response_splits[len(response_splits)-1]
		if "Response" in response or "Output" in response:
			response = [r.strip() for r in response.split(":")][1]
		if "[" in response:
			response = response[1:len(response)-1]
		return response
	
	def filter_comp_id_response(self, comp_id_response):
		comp_id_list = []
		comp_id_response = self.filter_prompt_response(comp_id_response)
		if "[" in comp_id_response and "]" in comp_id_response:
			comp_id_response = comp_id_response[1:len(comp_id_response)-1]
		print("Comp: " + str(comp_id_response))
		if "No matched interaction id" in comp_id_response:
			return []
		
		if "\n" in comp_id_response:
			comp_id_list= [r.strip() for r in comp_id_response.split("\n")]
			temp_id_list = []
			for comps in comp_id_list:
				if "," in comps:
					comp_list = [r.strip() for r in comps.split(",")]
					temp_id_list.extend(comp_list)
				else:
					temp_id_list.append(comps)
			comp_id_list = temp_id_list
		if "," in comp_id_response:
			comp_id_list = [r.strip() for r in comp_id_response.split(",")]
		if self.check_int(comp_id_response) is True:
			comp_id_list = [comp_id_response]

		return comp_id_list
	
	def filter_nodes(self, comp_row, s2r_sentence):
		# if len(comp_row[3])==0 and len(comp_row[4])==0 and len(comp_row[5])==0 and len(comp_row[6])==0:
		#     return False
		# if ("scroll" in s2r_sentence.lower() or "swipe" in s2r_sentence.lower()) and "swipe" not in comp_row[2].lower():
		#     return False 
		if ("click" in s2r_sentence.lower() or "tap" in s2r_sentence.lower()) and "click" not in comp_row[2].lower():
			return False
		if "checkbox" in s2r_sentence.lower() and "checkbox" not in comp_row[3].lower():
			return False
		if "toggle" in s2r_sentence.lower() and "switch" not in comp_row[3].lower():
			return False
		if "type" in s2r_sentence.lower() and "edittext" not in comp_row[3].lower():
			return False
		if "button" in s2r_sentence.lower() and "button" not in comp_row[3].lower():
			return False
		
		return True
	
	def get_seq_id(self, screen_id, filename):
		df = pd.read_csv(filename)
		if not df['screen_id'].isin([screen_id]).any():
			print(f'Bug Id: {screen_id} does not exist in {filename}')
		execution_info = df.loc[df['screen_id']==screen_id, ["sequence_id", "source", "execution_id"]].values.tolist()
		return execution_info
	
	def check_if_path_exists(self,file):
		if not os.path.exists(file):
			return False
		return True
	
	def get_comp_id_text(self, component):
		comp = ""
		if "text" in component:
			comp = component["text"]
		elif 'idXml' in component and len(component['idXml'])>0:
			component_idxml = component['idXml'].split("/")
			comp = component_idxml[len(component_idxml)-1]
		#comp = self.preprocess_text(comp)
		return comp
	
	def check_real_value(self, val):
		if self.isNan(val) or len(val)==0:
			return False
		return True

	def get_all_component_infos(self, gui_components, positionX, positionY, height, width):
		nearby_components = []
		if not self.check_real_value(positionX) or not self.check_real_value(positionY) or not self.check_real_value(height) or not self.check_real_value(width):
			return nearby_components
		
		threshold = 100
		for component in gui_components:
			if "positionX" in component and "positionY" in component and "height" in component and "width" in component:
				if (component["positionY"] - component["height"] >= int(positionY) - int(height) - threshold) \
					and (component["positionY"] <= int(positionY) + threshold) \
					and (component["positionX"] + component["width"] <= int(positionX) \
						 or component["positionX"]>=int(positionX)+int(width)):
					comp_id_text = self.get_comp_id_text(component)
					if len(comp_id_text)>0 and comp_id_text!="null" and comp_id_text!="NO_ID":
						nearby_components.append(comp_id_text)
		return nearby_components

	def get_nearby_components(self, bug_id, graph_folder_path, screen_id, positionX, positionY, height, width, execution, destination, seq_id):
		execution_file = ""
		if destination=="TR":
			execution_file = "../data/TraceReplayer-Data/TR" + bug_id +"/Execution-" + str(int(execution)+1) + ".json"
		elif destination=="CS":
			if execution=="0":
				execution_file = "../data/CrashScope-Data/CS" + bug_id + "/" + graph_folder_path + "/Execution-Bottom_Up-Expected-1.json"
				if self.check_if_path_exists(execution_file) is False:
					execution_file = "../data/CrashScope-Data/CS" + bug_id + "/" + graph_folder_path + "/Execution-2.json"
			elif execution=="1":
				execution_file = "../data/CrashScope-Data/CS" + bug_id + "/" + graph_folder_path + "/Execution-Top_Down-Expected-1.json"
				if self.check_if_path_exists(execution_file) is False:
					execution_file = "../data/CrashScope-Data/CS" + bug_id + "/" + graph_folder_path + "/Execution-1.json"

		nearby_components = []
		if self.check_if_path_exists(execution_file) is True:
			json_file = open(execution_file)
			data = json.load(json_file)

			for step in data['steps']:
				if step['sequenceStep']==int(seq_id):
					nearby_components = self.get_all_component_infos(step['screen']['dynGuiComponents'], positionX, positionY, height, width)

		return nearby_components
	
	def get_labels(self, comp_id_list, prev_node_match, prev_exact_match_check_flag):
		q_label = []
		if len(comp_id_list)>1:
			q_label.append("AS")
		else:
			q_label.append("EM")

		if not prev_node_match:
			q_label.append("MS")
		
		return list(set(q_label))
	
	def get_labels_ground_truth(self, interaction_id_list, prev_node_match, transition_df):
		q_label = ""
		if prev_node_match:
			if len(interaction_id_list)>1:
				sentence_set = set()
				for interaction_id in interaction_id_list:
					interaction_info = self.get_interaction_values(transition_df, interaction_id)
					print("int: " + str(interaction_info))
					interaction_info_sentence  = self.get_interaction_info_sentence_from_interaction_id(interaction_info)
					sentence_set.add(interaction_info_sentence)
				if len(sentence_set)>1:
					print("sent: " + str(sentence_set))
					q_label = "AS"
				else: 
					q_label = "EM"
			else:
				q_label = "EM"
		if not prev_node_match:
			q_label = "MS"
		return q_label
	
	def check_cur_node(self, path):
		if len(path)>=1 and len(path)<=2:
			return True
		return False
	
	def track_prev_node_match(self, v, neighbor, cur_screen_id, prev_node_match):
		if v==neighbor and prev_node_match==True:
			prev_node_match = True
		elif cur_screen_id != "21c267ef898a5960eea0d8cc0c93ea6eb54b46d154921ccbd6255d36be1f406f":
			prev_node_match = False
		return prev_node_match
	
	def get_matched_component_ids(self, comp_id_list, comp_infos):
		matched_ids = []
		for comp_id in comp_id_list:
			transition_id = comp_infos[int(comp_id)-1][0]
			matched_ids.append(transition_id)
		return matched_ids
	
	def get_matched_component_sentences(self, comp_id_list, comp_infos, bug_id, cur_screen_id, graph_folder_path):
		matched_sentences = []
		for comp_id in comp_id_list:
			matched_sentences.append(self.get_interaction_info_sentence(comp_infos, int(comp_id)-1, bug_id, cur_screen_id, graph_folder_path))
		return matched_sentences
	
	def get_path_sentences(self, paths, transition_df, bug_id, graph_folder_path, screen_id):
		path_sentence_list = []
		for path in paths:
			cur_path_sentences = []
			for interaction_id in path:
				interaction_info = self.get_interaction_values(transition_df, interaction_id)
				interaction_info_sentence  = self.get_interaction_info_sentence_from_interaction_id(interaction_info, bug_id, graph_folder_path, screen_id)
				cur_path_sentences.append(interaction_info_sentence)
			path_sentence_list.append(cur_path_sentences)
		return path_sentence_list
	
	def get_individual_path_sentences(self, path, transition_df, bug_id, graph_folder_path, screen_id):
		cur_path_sentences = []
		for interaction_id in path:
			interaction_info = self.get_interaction_values(transition_df, interaction_id)
			interaction_info_sentence  = self.get_interaction_info_sentence_from_interaction_id(interaction_info, bug_id, graph_folder_path, screen_id)
			cur_path_sentences.append(interaction_info_sentence)
		return cur_path_sentences
	
	def get_interaction_info_sentence_from_interaction_id(self, interaction_info, bug_id, graph_folder_path, screen_id):
		comp_str = ""
		if len(interaction_info[2])>0:
			comp_str += self.preprocess_text(interaction_info[2])

		comp_text = "" 
		if len(interaction_info[5])>0:
			comp_text = interaction_info[5]
		elif len(interaction_info[4])>0:
			comp_text = interaction_info[4]
		elif len(interaction_info[6])>0:
			comp_text = interaction_info[6]

		if len(comp_text)>0:
			comp_str += " the \"" + self.preprocess_text(comp_text) + "\""

		if len(interaction_info[3])>0:
			comp_str += " " + self.preprocess_text(interaction_info[3])

		if interaction_info[3]=="CheckBox" or interaction_info[3]=="Switch":
			nearby_comps = self.get_nearby_components(bug_id, graph_folder_path, screen_id, interaction_info[10], interaction_info[11], interaction_info[12], interaction_info[13], interaction_info[8], interaction_info[14], interaction_info[9])
			if len(nearby_comps)>0:
				nearby_comps_str = ""
				for j in range(len(nearby_comps)):
					if j==0:
						nearby_comps_str += nearby_comps[j]
					else:
						nearby_comps_str += ", " + nearby_comps[j]
				comp_str += ", Nearby Components: [" + nearby_comps_str + "]"

		return comp_str
	
	def get_interaction_info_sentence(self, interactions, i, bug_id, screen_id, graph_folder_path):
		comp_str = ""
		if len(interactions[i][2])>0:
			comp_str += self.preprocess_text(interactions[i][2])

		comp_text = "" 
		if len(interactions[i][5])>0:
			comp_text = interactions[i][5]
		elif len(interactions[i][4])>0:
			comp_text = interactions[i][4]
		elif len(interactions[i][6])>0:
			comp_text = interactions[i][6]

		if len(comp_text)>0:
			comp_str += " the \"" + self.preprocess_text(comp_text) + "\""

		if len(interactions[i][3])>0:
			comp_str += " " + self.preprocess_text(interactions[i][3])

		if interactions[i][3]=="CheckBox" or interactions[i][3]=="Switch":
			nearby_comps = self.get_nearby_components(bug_id, graph_folder_path, screen_id, interactions[i][10], interactions[i][11], interactions[i][12], interactions[i][13], interactions[i][8], interactions[i][14], interactions[i][9])
			if len(nearby_comps)>0:
				nearby_comps_str = ""
				for j in range(len(nearby_comps)):
					if j==0:
						nearby_comps_str += nearby_comps[j]
					else:
						nearby_comps_str += ", " + nearby_comps[j]
				comp_str += ", Nearby Components: [" + nearby_comps_str + "]"

		return comp_str
	
	def get_all_interaction_sentences(self, interactions, bug_id, screen_id, graph_folder_path):
		interaction_sentence_list = []
		for i in range(len(interactions)):
			cur_sentence = self.get_interaction_info_sentence(interactions, i, bug_id, screen_id, graph_folder_path)
			interaction_sentence_list.append(cur_sentence)
		return interaction_sentence_list

	# https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python
	def camel_case_split(self, identifier):
		matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
		words = [m.group(0) for m in matches]
		word_lower = [text.lower() for text in words]
		word_str = " ".join(word_lower)
		return word_str
		
	def snake_case_split(self, identifier):
		identifier = identifier.lower()
		return identifier.replace("_", " ")
	
	def preprocess_text(self, text):
		if "_" in text:
			return self.snake_case_split(text)
		return self.camel_case_split(text)
	
	def check_leaf_node(self, screen_id):
		return screen_id == "eb11e43fb68de36fde35b98680b866cdc44aca80736896e3c983dde1de1c1c87"
	
	def check_leaf_node_from_id(self, screen_Dict, v):
		screen_id = self.get_key_from_value(screen_Dict, v)
		return screen_id == "eb11e43fb68de36fde35b98680b866cdc44aca80736896e3c983dde1de1c1c87"
	
	def select_best_matched_interaction(self, ret_match_info_list):
		#6 = number of matches
		#1 = distance
		#5 = s2r index
		sorted_ret_match_info_list = sorted(ret_match_info_list, key=lambda item: (-len(item[6]), len(item[1]), item[5]))
		# sorted_ret_match_info_list = sorted(ret_match_info_list, key=lambda item: len(item[1]))

		#sorted_ret_match_info_list = sorted(ret_match_info_list, key=lambda item: (len(item[1]), item[5], -len(item[6])))
		return sorted_ret_match_info_list[0]

	def get_next_path_and_sentences(self, v, ret_screen_seq_id, ret_interaction_id, comp_infos, comp_id, parent, screen_Dict, df, graph, bug_id, graph_folder_path, screen_id):
		# TODO: next path need to be fixed if case existing node deleted
		#print("ab: " + str(v) + " " + str(comp_infos[int(comp_id)-1][0]) + " " + str(ret_screen_seq_id) + " " + str(ret_interaction_id))
		next_path = []
		if ret_screen_seq_id==-1:
			#next_path = self.bfs.get_shortest_path(v, comp_infos[int(comp_id)-1][0], v, comp_infos[int(comp_id)-1][0], parent, screen_Dict, df, graph)
			next_path =  [comp_infos[int(comp_id)-1][0]]
		else: 
			next_path = self.bfs.get_shortest_path(v, comp_infos[int(comp_id)-1][0], ret_screen_seq_id, ret_interaction_id, parent, screen_Dict, df, graph)
			#next_path = next_path[:len(next_path)-1]
		#print("cur: " + str(next_path))
		next_path_sentences = self.get_individual_path_sentences(next_path, df, bug_id, graph_folder_path, screen_id)
		return next_path, next_path_sentences
	
	def get_next_path_and_sentences_ground_truth(self, v, ret_screen_seq_id, ret_interaction_id, interaction_id, parent, screen_Dict, df, graph):
		next_path = []
		if ret_screen_seq_id==-1:
			next_path =  [interaction_id]
		else: 
			next_path = self.bfs.get_shortest_path(v, interaction_id, ret_screen_seq_id, ret_interaction_id, parent, screen_Dict, df, graph)
		next_path_sentences = self.get_individual_path_sentences(next_path, df)
		return next_path, next_path_sentences
	
	def get_next_path_and_sentences_for_unmatched_node(self, v, ret_screen_seq_id, ret_interaction_id, transition_id, parent, screen_Dict, df, graph):
		next_path = self.bfs.get_shortest_path(v, transition_id, ret_screen_seq_id, ret_interaction_id, parent, screen_Dict, df, graph)
		next_path_sentences = self.get_individual_path_sentences(next_path, df)
		return next_path, next_path_sentences
	
	def filter_duplicate_s2r_index(self, all_next_paths, all_next_path_sentences, s2r_index, next_path, next_path_string, next_path_sentences_string, q_label):
		# if next_path_string.startswith("9"):
		#     print("AB")
		# print("path")
		# print(s2r_index)
		# print(all_next_paths)
		# print(all_next_path_sentences)

		# filtered_next_paths = all_next_paths
		# filtered_next_path_sentences = all_next_path_sentences

		# filtered_next_paths = []
		# filtered_next_path_sentences = []
		# duplicate_remove_flag = False
		# for i in range(len(all_next_paths)):
		#     individual_path_splits = all_next_paths[i].split("#")
		#     cur_s2r_index = individual_path_splits[0]
		#     cur_path = ast.literal_eval(individual_path_splits[2])
		#     if cur_s2r_index == s2r_index and len(cur_path) > len(next_path):
		#         duplicate_remove_flag = True
		#     else:
		#         filtered_next_paths.append(all_next_paths[i])
		#         filtered_next_path_sentences.append(all_next_path_sentences[i])

		# if not duplicate_remove_flag:
		#     filtered_next_paths.insert(0, next_path_string) 
		#     filtered_next_path_sentences.insert(0, next_path_sentences_string)

		# print("filtered")
		# print(filtered_next_paths)
		# print(filtered_next_path_sentences)

		#Check without filering
		#print("next : " + next_path_string)

		# next_path_string = str(s2r_index) + "#" + str(q_label) + "#" + str(next_path)
		#     next_path_sentences_string = str(s2r_index) + "#" + str(q_label) + "#" + str(next_path_sentences) 
		#print("tr " + str(all_next_paths))
		if len(all_next_paths)>0 and "NM" not in q_label:
			first_node_splits = all_next_paths[0].split("#")
			first_node_sentence_splits = all_next_path_sentences[0].split("#")
			#print("av: " + str(first_node_splits))
			if len(next_path)>=1 and len(next_path)<=2:
			#if len(next_path)==1:
				if next_path[len(next_path)-1]==ast.literal_eval(first_node_splits[2])[0] and ("MS" in first_node_splits[1]):
					all_next_paths[0] = first_node_splits[0] + "#" + str(["EM"]) + "#" + first_node_splits[2]
					all_next_path_sentences[0] = first_node_sentence_splits[0] + "#" + str(["EM"]) + "#" + first_node_sentence_splits[2]
			elif len(next_path)>2:
				if next_path[len(next_path)-1]==ast.literal_eval(first_node_splits[2])[0] and ("EM" in first_node_splits[1] or "AS" in first_node_splits[1]):
					#print("str: "+ str(first_node_splits[1]))
					temp_labels = ast.literal_eval(first_node_splits[1])
					if "MS" not in temp_labels:
						temp_labels.append("MS")
					all_next_paths[0] = first_node_splits[0] + "#" + str(temp_labels) + "#" + first_node_splits[2]
					all_next_path_sentences[0] = first_node_sentence_splits[0] + "#" + str(temp_labels) + "#" + first_node_sentence_splits[2]

		updated_paths = all_next_paths.copy()
		updated_paths.insert(0, next_path_string) 

		updated_path_sentences = all_next_path_sentences.copy()
		updated_path_sentences.insert(0, next_path_sentences_string)

		return updated_paths, updated_path_sentences

	def insert_match_strings(self, s2r_index, q_label, next_path, next_path_sentences, all_next_paths, all_next_path_sentences, comp_infos, comp_id, parent, screen_Dict, df, graph, v):
		#TODO: may need to check path
		#if len(all_next_paths)==0 and len(next_path)>0:
		if len(next_path)>0:
			next_path_string = str(s2r_index) + "#" + str(q_label) + "#" + str(next_path)
			next_path_sentences_string = str(s2r_index) + "#" + str(q_label) + "#" + str(next_path_sentences)   

			all_next_paths, all_next_path_sentences = self.filter_duplicate_s2r_index(all_next_paths, all_next_path_sentences, s2r_index, next_path, next_path_string, next_path_sentences_string, q_label)
		
		# elif len(all_next_paths)>0:
		#     start_node = all_next_paths[0].split("#")[0]
		#     # print("or " + str(all_next_paths[0]))
		#     start_node_interaction = ast.literal_eval(all_next_paths[0].split("#")[2])[0]
		#     if int(start_node)!=int(s2r_index):
		#         path_to_next_node, path_sentence_to_next_node = self.get_next_path_and_sentences(v, int(start_node), start_node_interaction, comp_infos, comp_id, parent, screen_Dict, df, graph)
		#         if len(path_to_next_node)>0:
		#             next_path_string = str(s2r_index) + "#" + str(q_label) + "#" + str(path_to_next_node)
		#             next_path_sentences_string = str(s2r_index) + "#" + str(q_label) + "#" + str(path_sentence_to_next_node)   

		#             all_next_paths, all_next_path_sentences = self.filter_duplicate_s2r_index(all_next_paths, all_next_path_sentences, s2r_index, next_path, next_path_string, next_path_sentences_string)
		#     else:
		#         next_path_string = str(s2r_index) + "#" + str(q_label) + "#" + str(next_path)
		#         next_path_sentences_string = str(s2r_index) + "#" + str(q_label) + "#" + str(next_path_sentences)   
		#         all_next_paths, all_next_path_sentences = self.filter_duplicate_s2r_index(all_next_paths, all_next_path_sentences, s2r_index, next_path, next_path_string, next_path_sentences_string)


		return all_next_paths, all_next_path_sentences
	
	def get_match_string(self, s2r_index, q_label, next_path, next_path_sentences):
		next_path_string = str(s2r_index) + "#" + str(q_label) + "#" + str(next_path)
		next_path_sentences_string = str(s2r_index) + "#" + str(q_label) + "#" + str(next_path_sentences)

		return [next_path_string], [next_path_sentences_string]
	
	def update_next_paths_for_not_matched_nodes(self, all_next_paths, all_next_path_sentences, u, v, transition_df, screen_Dict):
		updated_all_next_paths = []
		updated_all_next_path_sentences = []
		cur_transition = self.bfs.get_transition(transition_df, u, v, screen_Dict)
		interaction_info = self.get_interaction_values(transition_df, cur_transition)
		cur_transition_sentence = self.get_interaction_info_sentence_from_interaction_id(interaction_info)

		# print("u: " + str(u) + " v: " + str(v) + " " + str(cur_transition) + " " + str(cur_transition_sentence))
		for i in range(len(all_next_paths)):
			# if i==0:
			#     cur_path_splits = all_next_paths[i].split("#")
			#     next_match_paths = ast.literal_eval(cur_path_splits[2])

			#     cur_path_sentence_splits = all_next_path_sentences[i].split("#")
			#     next_match_path_sentences = ast.literal_eval(cur_path_sentence_splits[2])

			#     if len(next_match_paths)>0:
			#         next_match_paths.insert(0, cur_transition)
			#         next_match_path_sentences.insert(0, cur_transition_sentence)

			#     next_match_paths_string = cur_path_splits[0] + "#" + cur_path_splits[1] + "#" + str(next_match_paths)
			#     updated_all_next_paths.append(next_match_paths_string)
			#     next_match_path_sentences_string = cur_path_sentence_splits[0] + "#" + cur_path_sentence_splits[1] + "#" + str(next_match_path_sentences)
			#     updated_all_next_path_sentences.append(next_match_path_sentences_string)
			# else:
			updated_all_next_paths.append(all_next_paths[i])
			updated_all_next_path_sentences.append(all_next_path_sentences[i])
		return cur_transition, updated_all_next_paths, updated_all_next_path_sentences
	
	def get_necessary_info_before_recursion(self, v, parent, comp_id_list, prev_node_match, comp_infos, last_matched_info, screen_Dict, df, graph, bug_id, cur_screen_id, graph_folder_path):
		matched_ids = self.get_matched_component_ids(comp_id_list, comp_infos)
		path = []
		for matched_id in matched_ids:
			path.append(self.bfs.get_node_shortest_path(last_matched_info[0], last_matched_info[2], v, matched_id, parent, screen_Dict, df, graph))

		matched_sentences = self.get_matched_component_sentences(comp_id_list, comp_infos, bug_id, cur_screen_id, graph_folder_path)
		#path_sentences = self.get_path_sentences(path, df)
		path_sentences = []

		return matched_ids, matched_sentences, path, path_sentences
	
	def get_necessary_info_before_recursion_ground_truth(self, v, parent, interaction_id_list, prev_node_match, last_matched_info, screen_Dict, df, graph):
		q_label = self.get_labels_ground_truth(interaction_id_list, prev_node_match, df)
		matched_ids = interaction_id_list
		path = []
		for matched_id in matched_ids:
			path.append(self.bfs.get_node_shortest_path(last_matched_info[0], last_matched_info[2], v, matched_id, parent, screen_Dict, df, graph))

		#matched_sentences = self.get_matched_component_sentences(comp_id_list, comp_infos)
		#path_sentences = self.get_path_sentences(path, df)
		matched_sentences = []
		path_sentences = []

		return q_label, matched_ids, matched_sentences, path, path_sentences
	
	# def get_maximum_similar_comps(self, comp_infos, comp_info_list, object_response, s2r_sentence, llm):
	# 	comp_id_list = []
	# 	max_sim_index = 0
	# 	highest_similarity_score = 0
	# 	comp_id_list = []

	# 	similarity_score_list_dict = {}
	# 	for i in range(len(comp_infos)):
	# 		if (comp_infos[i][3]=="ImageButton" or comp_infos[i][3]=="TextView") and self.s2r_keyword(s2r_sentence) is True:
	# 			#print("screen " + str(cur_screen_id))
	# 			if len(comp_info_list[i])==0:
	# 				continue
	# 			similarity_score = llm.get_cosine_similarity(object_response, comp_info_list[i])
	# 			#print(str(object_response) + " " + str(comp_info_list[i]) + " " + str(similarity_score))
	# 			similarity_score_list_dict[i] = similarity_score
	# 			if similarity_score > 0.4 and similarity_score>highest_similarity_score:
	# 				#print("s2r: " + s2r_sentence_list[s2r_index])
	# 				max_sim_index = i+1
	# 				highest_similarity_score = similarity_score

	# 	if max_sim_index!=0:
	# 		for i in range(len(comp_infos)):
	# 			if i in similarity_score_list_dict and similarity_score_list_dict[i]==highest_similarity_score:
	# 				comp_id_list.append(i+1)
	# 		return True, comp_id_list
	# 	return False, []
	
	def get_maximum_similar_interactions(self, comp_infos, bug_id, cur_screen_id, graph_folder_path, s2r_sentence, llm):
		comp_id_list = []
		max_sim_index = 0
		highest_similarity_score = 0
		comp_id_list = []

		similarity_score_list_dict = {}

		for i in range(len(comp_infos)):
			interaction_info_sentence  = self.get_interaction_info_sentence(comp_infos, i, bug_id, cur_screen_id, graph_folder_path)
			similarity_score = llm.get_cosine_similarity(s2r_sentence, interaction_info_sentence)
			#print(str(object_response) + " " + str(comp_info_list[i]) + " " + str(similarity_score))
			#print(similarity_score)
			similarity_score_list_dict[i] = similarity_score
			if similarity_score >= 0.5 and similarity_score>highest_similarity_score:
				print("s2r: " + s2r_sentence)
				print(similarity_score)
				print(interaction_info_sentence)
				max_sim_index = i+1
				highest_similarity_score = similarity_score

		# for i in range(len(comp_infos)):
		# 	selected_interaction_id = comp_infos[i][0]
		# 	interaction_sentence = self.get_interaction_info_sentence_from_interaction_id(selected_interaction_id)
		# 	similarity_score
		# 	if (comp_infos[i][3]=="ImageButton" or comp_infos[i][3]=="TextView") and self.s2r_keyword(s2r_sentence) is True:
		# 		#print("screen " + str(cur_screen_id))
		# 		if len(comp_info_list[i])==0:
		# 			continue
		# 		similarity_score = llm.get_cosine_similarity(object_response, comp_info_list[i])
		# 		#print(str(object_response) + " " + str(comp_info_list[i]) + " " + str(similarity_score))
		# 		similarity_score_list_dict[i] = similarity_score
		# 		if similarity_score > 0.4 and similarity_score>highest_similarity_score:
		# 			#print("s2r: " + s2r_sentence_list[s2r_index])
		# 			max_sim_index = i+1
		# 			highest_similarity_score = similarity_score

		if max_sim_index!=0:
			for i in range(len(comp_infos)):
				if i in similarity_score_list_dict and similarity_score_list_dict[i]==highest_similarity_score:
					comp_id_list.append(i+1)
			return True, comp_id_list
		return False, []
	
	# def get_maximum_similar_comps_from_interaction_sentences(self, comp_infos, comp_info_list, object_response, s2r_sentence, llm):
	# 	comp_id_list = []
	# 	max_sim_index = 0
	# 	highest_similarity_score = 0
	# 	comp_id_list = []
	# 	for i in range(len(comp_infos)):
	# 		if (comp_infos[i][3]=="ImageButton" or comp_infos[i][3]=="TextView") and self.s2r_keyword(s2r_sentence) is True:
	# 			#print("screen " + str(cur_screen_id))
	# 			if len(comp_info_list[i])==0:
	# 				continue
	# 			similarity_score = llm.get_cosine_similarity(object_response, comp_info_list[i])
	# 			#print(str(object_response) + " " + str(comp_info_list[i]) + " " + str(similarity_score))
	# 			if similarity_score > 0.4 and similarity_score>highest_similarity_score:
	# 				#print("s2r: " + s2r_sentence_list[s2r_index])
	# 				max_sim_index = i+1
	# 				highest_similarity_score = similarity_score

	# 	if max_sim_index!=0:
	# 		comp_id_list.append(max_sim_index)
	# 		return True, comp_id_list
	# 	return False, []
	
	def get_selected_interaction(self, v, ret_match_info_list, comp_infos, s2r_index, q_label, selected_interaction_id, next_path, next_path_sentences, parent, screen_Dict, df, graph):
		if len(ret_match_info_list)>0:
			best_ret_match_info_list = self.select_best_matched_interaction(ret_match_info_list)
			#print("best: ")
			#print(str(best_ret_match_info_list[3]) + " " + str(best_ret_match_info_list[5]) + " " + str(best_ret_match_info_list[7]))
			
			all_next_paths, all_next_path_sentences = self.insert_match_strings(s2r_index, q_label, best_ret_match_info_list[1], best_ret_match_info_list[2], best_ret_match_info_list[6], best_ret_match_info_list[7], comp_infos, best_ret_match_info_list[0], parent, screen_Dict, df, graph, v)
			return [v, comp_infos[int(best_ret_match_info_list[0])-1][0], s2r_index, all_next_paths, all_next_path_sentences]
			#print("match path: " + str(best_ret_match_info_list[2]))
		else:
			cur_paths, cur_path_sentences = self.get_match_string(s2r_index, q_label, next_path, next_path_sentences)
		return [v, selected_interaction_id, s2r_index, cur_paths, cur_path_sentences]
	
	def get_selected_interaction_ground_truth(self, v, ret_match_info_list, s2r_index, q_label, selected_interaction_id, next_path, next_path_sentences):
		if len(ret_match_info_list)>0:
			best_ret_match_info_list = self.select_best_matched_interaction(ret_match_info_list)
			all_next_paths, all_next_path_sentences = self.insert_match_strings(s2r_index, q_label, best_ret_match_info_list[1], best_ret_match_info_list[2], best_ret_match_info_list[6], best_ret_match_info_list[7])
			return [v, best_ret_match_info_list[0], s2r_index, all_next_paths, all_next_path_sentences]
		else:
			cur_paths, cur_path_sentences = self.get_match_string(s2r_index, q_label, next_path, next_path_sentences)
		return [v, selected_interaction_id, s2r_index, cur_paths, cur_path_sentences]
	
	def get_next_node_info(self, v, comp_id_list, c_index, comp_infos, s2r_index, screen_Dict):
		comp_id = comp_id_list[c_index] 
		selected_interaction_id = comp_infos[int(comp_id)-1][0]
		last_matched_info = (v, s2r_index, comp_infos[int(comp_id)-1][0]) 
		node = self.get_value_from_key(screen_Dict, comp_infos[int(comp_id)-1][1])

		return comp_id, selected_interaction_id, last_matched_info, node
	
	def remove_duplicate(self, item_list):
		return list(set(item_list))
	
	def remove_duplicate_swipe(self, item_list):
		seen = set()
		result = []
		for item in item_list:
			if "swipe" in item:
				if item in seen:
					continue
				else:
					seen.add(item)
			result.append(item)
		return result
	
	def remove_duplicate_but_not_in_popup(self, sentence_list):
		sentence_list = self.remove_duplicate_swipe(sentence_list)
		popup_words = ["ok", "yes", "no", "save", "allow", "deny", "skip", "cancel"]
		seen = set()
		result = []
		for sentence in sentence_list:
			sentence = sentence.replace('"', "")
			words = sentence.lower().split()
			# print(words)
			popup_sentence_flag = False
			for word in popup_words:
				if word in words:
					popup_sentence_flag = True

			if popup_sentence_flag:
				result.append(sentence)
			elif not popup_sentence_flag and sentence not in seen:
				seen.add(sentence)
				result.append(sentence)
			
		return result
	
	def get_sub_folder_name(self, folder):
		sub_folders = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
		return sub_folders
	
	def get_graph_directory(self, bug_ids, graph_dir):
		graph_folder_name_list = []
		for i in range(len(bug_ids)):
			cur_dir = graph_dir + "/Bug" + str(bug_ids[i])
			sub_folders = self.get_sub_folder_name(cur_dir) 
			graph_folder_name_list.append(sub_folders[0][2:])

		return graph_folder_name_list
	
	def get_s2rs(self, bug_report, identification_response):
		s2r_response = identification_response.split("\n")[2]
		s2r_labels_splits = s2r_response.split(":")
		if len(s2r_labels_splits)>=1:
			s2r_labels = s2r_labels_splits[1]
			s2r_labels_list = [x.strip() for x in s2r_labels.split(",")]

		label_list = []
		s2r_list = []
		bug_report_splits = bug_report.split("\n")
		for sentence in bug_report_splits:
			if len(sentence)==0:
				continue
			sentence_splits = sentence.split(":")
			#print(sentence_splits)
			if len(sentence_splits)>=1:
				label = sentence_splits[0].strip()
				s2r = sentence_splits[1].strip()
				if label in s2r_labels_list:
					label_list.append(label)
					s2r_list.append(s2r)

		return label_list, s2r_list
	
	def get_parsed_individual_s2rs(self, individual_s2r_response, original_s2r_sentence):
		print(individual_s2r_response)
		if individual_s2r_response==None or len(individual_s2r_response)==0:
			return []

		if individual_s2r_response[0]=="[":
			individual_s2r_sentence_list = [x.strip() for x in individual_s2r_response[1:len(individual_s2r_response)-1].split(",")]
			individual_s2r_sentence_list = [x[1:len(x)-1] if x[0]=="\"" and x[len(x)-1]=="\"" else x for x in individual_s2r_sentence_list ]
		else:
			individual_s2r_sentence_list = [original_s2r_sentence]
		return individual_s2r_sentence_list
	
	def get_parsed_individual_s2rs_list(self, individual_s2r_response):
		if individual_s2r_response==None or len(individual_s2r_response)==0:
			return []
		individual_s2r_sentence_list = []
		if individual_s2r_response[0]=="[":
			individual_s2r_sentence_list = [x.strip() for x in individual_s2r_response[1:len(individual_s2r_response)-1].split(",")]
			individual_s2r_sentence_list = [x[1:len(x)-1] if x[0]=="\"" and x[len(x)-1]=="\"" else x for x in individual_s2r_sentence_list ]
		else:
			individual_s2r_sentence_list = individual_s2r_response.split("\n")

		print(individual_s2r_response)
		print(individual_s2r_sentence_list)

		return individual_s2r_sentence_list
	
	def check_no_dup(self, interactions, i, k):
		if interactions[i][3]=="CheckBox" or interactions[i][3]=="Switch":
			return True

		if len(interactions[i][4])>0 and interactions[i][4]==interactions[k][4]:
			return False
		if len(interactions[i][5])>0 and (interactions[i][5]==interactions[k][5] or interactions[i][5]==interactions[k][6]):
			return False
		if len(interactions[i][6])>0 and (interactions[i][6]==interactions[k][6] or interactions[i][6]==interactions[k][5]):
			return False
		return True
	
	def comp_is_duplicate(self, comp_id_list, interactions):
		check_flag = True
		for i in range(len(comp_id_list)):
			for j in range(i+1, len(comp_id_list)):
				unique = self.check_no_dup(interactions, int(comp_id_list[i])-1, int(comp_id_list[j])-1)
				if unique:
					check_flag = False

		return check_flag
	
	# def get_action_class(self):
	# 	action_dict = {
	# 		"Open": ["open", "start", "execute", "initiate", "run", "begin", "commence"],
	# 		"Toggle": ["toggle", "flip flop", "interchange", "switch", "alternate", "flip"],
	# 		"Long-click": ["long tap", "hold", "long click", "long press", "long push", "long hit", "long click on", "select", "change"],
	# 		"Click": ["tap", "tip", "click", "press", "push", "select", "go", "choose", "check", "pick", "hit", "click on", "add", "change", "save", "click back", "mark", "set", "edit", "display", "leave", "create", "enable", "start", "stop", "close", "change", "spot", "uncheck", "deselect"],
	# 		Swipe: swipe, drag, sweep, scroll, scroll down, scroll up, scroll right, scroll left, swipe down, swipe up, swipe right, swipe left
	# 		Type: type, edit, input, fill, typewrite, insert, infix, enter, introduce, write, set, add, change, press
	# 		Rotate: rotate, change, set, turn
	# 		Close: close, terminate, shut down
	# 		Back: go back
	# 	}

	def get_plural_task_words(self):
		# "from to", 
		words = ["all", "both", "other", "while", "create", "when", "add", "change", "edit", "modify", "generate"]
		return words
	
	def sentence_plural_check(self, sentence):
		sentence_splits = sentence.lower().split()
		plural_words = self.get_plural_task_words()

		if "from" in sentence_splits and "to" in sentence_splits:
			return True
		for word in plural_words:
			if word in sentence_splits:
				return True
		return False			

		


		




			



	
		






	





		

