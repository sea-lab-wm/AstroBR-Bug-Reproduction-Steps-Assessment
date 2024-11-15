import os
from openai import OpenAI
import numpy as np
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from sklearn.metrics.pairwise import cosine_similarity
from write_results import WriteResults
from prompts import Prompts
from helpers import Helpers
import ast

class LLM:
	def __init__(self):
		api_key = open("gpt4br/ImportantInfo/openai_my.key").read()
		os.environ["OPENAI_API_KEY"] = api_key
		self.writeResults = WriteResults()
		self.prompts = Prompts()
		self.helpers = Helpers()

	def __init__(self, cache_dir):
		api_key = open("gpt4br/ImportantInfo/openai_my.key").read()
		os.environ["OPENAI_API_KEY"] = api_key
		self.writeResults = WriteResults()
		self.prompts = Prompts()
		self.helpers = Helpers()
		self.cache_dir = cache_dir
		self.create_directory(cache_dir)

	def create_directory(self, cache_dir):
		comp_ids_prompts_dir = cache_dir + "/comp_ids_prompts"
		if not os.path.exists(comp_ids_prompts_dir):
			os.makedirs(comp_ids_prompts_dir)
		
		comp_ids_responses_dir = cache_dir + "/comp_ids_responses"
		if not os.path.exists(comp_ids_responses_dir):
			os.makedirs(comp_ids_responses_dir)

		comps_dir = cache_dir + "/comps"
		if not os.path.exists(comps_dir):
			os.makedirs(comps_dir)

		match_prompts_dir = cache_dir + "/match_prompts"
		if not os.path.exists(match_prompts_dir):
			os.makedirs(match_prompts_dir)

		match_responses_dir = cache_dir + "/match_responses"
		if not os.path.exists(match_responses_dir):
			os.makedirs(match_responses_dir)

		objects_dir = cache_dir + "/objects"
		if not os.path.exists(objects_dir):
			os.makedirs(objects_dir)

		s2rs_dir = cache_dir + "/s2rs"
		if not os.path.exists(s2rs_dir):
			os.makedirs(s2rs_dir)

		modified_s2rs_prompts_dir = cache_dir + "/modified_s2r_prompts"
		if not os.path.exists(modified_s2rs_prompts_dir):
			os.makedirs(modified_s2rs_prompts_dir)

		modified_s2rs_responses_dir = cache_dir + "/modified_s2r_responses"
		if not os.path.exists(modified_s2rs_responses_dir):
			os.makedirs(modified_s2rs_responses_dir)

		sentences_dir = cache_dir + "/sentences"
		if not os.path.exists(sentences_dir):
			os.makedirs(sentences_dir)

		identification_dir = cache_dir + "/identification_bug_report_components"
		if not os.path.exists(identification_dir):
			os.makedirs(identification_dir)

		individual_s2rs_dir = cache_dir + "/individual_s2rs"
		if not os.path.exists(individual_s2rs_dir):
			os.makedirs(individual_s2rs_dir)
		
	def generate_response(self, chat_prompt):
		question_list = [chat_prompt]

		template = """
		{question}
		"""

		# https://python.langchain.com/docs/use_cases/question_answering/
		QA_CHAIN_PROMPT = PromptTemplate(input_variables=["question"], template=template,)
		llm = ChatOpenAI(model_name="gpt-4", temperature=0)

		llm_chain = LLMChain(llm=llm,prompt=QA_CHAIN_PROMPT)

		answer = llm_chain.run(question_list[0])
		return answer
	
	def generate_response_for_segmented_xml(self, question_list):
		template = """
		{question}
		"""

		# https://python.langchain.com/docs/use_cases/question_answering/
		QA_CHAIN_PROMPT = PromptTemplate(input_variables=["question"], template=template,)
		llm = ChatOpenAI(model_name="gpt-4", temperature=0)

		llm_chain = LLMChain(llm=llm,prompt=QA_CHAIN_PROMPT)

		for i in range(len(question_list)):
			print(question_list[i])
			answer = llm_chain.run(question_list[i])
			#print(answer)
		return answer
	
	# https://medium.com/@khiljidanial/cosine-similarity-using-gpt-models-35b6b9685d70
	# https://platform.openai.com/docs/guides/embeddings/embedding-models
	def get_embedding(self, text, model="text-embedding-3-small"):
		#return openai.Embedding.create(engine=model, input=[text])['data'][0]['embedding']
		client = OpenAI()
		return client.embeddings.create(input = [text], model=model).data[0].embedding

	def check_if_score_computed(self, embedding_file):
		if not os.path.exists(embedding_file):
			return False
		return True
	
	def check_if_file_exist(self, file):
		if not os.path.exists(file):
			return False
		return True
	
	def replace_text_for_filename(self, text):
		temp_text = text
		if "\"" in temp_text:
			temp_text = temp_text.replace("\"", "")
		if "/" in temp_text:
			temp_text = temp_text.replace("/", "")
		if len(temp_text)>=100:
			temp_text = temp_text[:100]
		return temp_text
	
	def get_cosine_similarity(self, text1, text2):
		embedding_dir = self.cache_dir

		temp_text1 = self.replace_text_for_filename(text1)
		text1_emb_file = embedding_dir + "/s2rs/" + temp_text1 + ".csv"
		text1_exist = self.check_if_score_computed(text1_emb_file)

		temp_text2 = self.replace_text_for_filename(text2)
		text2_emb_file = embedding_dir + "/comps/" + temp_text2 + ".csv"
		text2_exist = self.check_if_score_computed(text2_emb_file)
		
		if text1_exist == True:
			embedding1_np = np.loadtxt(text1_emb_file, delimiter = ",")
		else:
			embedding1 = self.get_embedding(text1)
			embedding1_np = np.array(embedding1)
			#if "\"" not in text1 and "/" not in text1:
			np.savetxt(text1_emb_file, embedding1_np, delimiter = ",")

		if text2_exist == True:
			embedding2_np = np.loadtxt(text2_emb_file, delimiter = ",")
		else: 
			embedding2 = self.get_embedding(text2)
			embedding2_np = np.array(embedding2)
			#if "\"" not in text2 and "/" not in text2:
			np.savetxt(text2_emb_file, embedding2_np, delimiter = ",")

		similarity = cosine_similarity([embedding1_np], [embedding2_np])

		return similarity[0][0]
	
	def get_sentence_cosine_similarity(self, text1, text2):
		embedding_dir = self.cache_dir

		temp_text1 = self.replace_text_for_filename(text1)
		text1_emb_file = embedding_dir + "/sentences/" + temp_text1 + ".csv"
		text1_exist = self.check_if_score_computed(text1_emb_file)

		temp_text2 = self.replace_text_for_filename(text2)
		text2_emb_file = embedding_dir + "/sentences/" + temp_text2 + ".csv"
		text2_exist = self.check_if_score_computed(text2_emb_file)
		
		if text1_exist == True:
			embedding1_np = np.loadtxt(text1_emb_file, delimiter = ",")
		else:
			embedding1 = self.get_embedding(text1)
			embedding1_np = np.array(embedding1)
			#if "\"" not in text1 and "/" not in text1:
			np.savetxt(text1_emb_file, embedding1_np, delimiter = ",")

		if text2_exist == True:
			embedding2_np = np.loadtxt(text2_emb_file, delimiter = ",")
		else: 
			embedding2 = self.get_embedding(text2)
			embedding2_np = np.array(embedding2)
			#if "\"" not in text2 and "/" not in text2:
			np.savetxt(text2_emb_file, embedding2_np, delimiter = ",")

		similarity = cosine_similarity([embedding1_np], [embedding2_np])

		return similarity[0][0]
	
	def get_screen_cosine_similarity(self, text1, text2, screen_id):
		embedding_dir = self.cache_dir
		text1_emb_file = embedding_dir + "/s2rs/" + text1 + ".csv"
		text1_exist = self.check_if_score_computed(text1_emb_file)

		text2_emb_file = embedding_dir + "/screens/" + screen_id + ".csv"
		text2_exist = self.check_if_score_computed(text2_emb_file)
		
		if text1_exist == True:
			embedding1_np = np.loadtxt(text1_emb_file, delimiter = ",")
		else:
			embedding1 = self.get_embedding(text1)
			embedding1_np = np.array(embedding1)
			if "\"" not in text1 and "/" not in text1:
				np.savetxt(text1_emb_file, embedding1_np, delimiter = ",")

		if text2_exist == True:
			embedding2_np = np.loadtxt(text2_emb_file, delimiter = ",")
		else: 
			embedding2 = self.get_embedding(text2)
			embedding2_np = np.array(embedding2)
			if "\"" not in text2 and "/" not in text2:
				np.savetxt(text2_emb_file, embedding2_np, delimiter = ",")

		similarity = cosine_similarity([embedding1_np], [embedding2_np])

		return similarity[0][0]
	
	def get_objects(self, app_name, text):
		object_dir = self.cache_dir
		text_object_file = ""
		temp_text = self.replace_text_for_filename(text)

		text_object_file = object_dir + "/objects/" + temp_text + ".txt"

		text_exist = self.check_if_score_computed(text_object_file)

		if text_exist == True:
			with open(text_object_file, "r") as f:
				object = f.read()
		else:
			object_prompt = self.prompts.create_zero_prompt_for_objects(app_name, text)
			object = self.generate_response(object_prompt)
			
			#if "\"" not in text and "/" not in text:
			with open(text_object_file, "w") as f:
				f.write(object)
				f.close()

		return object
	
	def get_bug_report_identification_components(self, app_name, bug_report, app_ver_bug):
		text_identification_file = self.cache_dir + "/identification_bug_report_components/" + app_ver_bug + ".txt"

		text_exist = self.check_if_score_computed(text_identification_file)

		if text_exist == True:
			with open(text_identification_file, "r") as f:
				identification = f.read()
		else:
			identification_prompt = self.prompts.create_zero_prompt_for_identifying_bug_report_components(app_name, bug_report)
			identification = self.generate_response(identification_prompt)
			
			with open(text_identification_file , "w") as f:
				f.write(identification)
				f.close()

		return identification
	
	def get_individual_s2rs(self, app_name, s2r_sentence_list, app_ver_bug):
		text_individual_s2r_file = self.cache_dir + "/individual_s2rs/" + app_ver_bug + ".txt"

		text_exist = self.check_if_score_computed(text_individual_s2r_file)

		if text_exist == True:
			with open(text_individual_s2r_file, "r") as f:
				individual_s2rs = f.read()
		else:
			individual_s2rs_prompt = self.prompts.create_zero_prompt_for_individual_s2r(app_name, s2r_sentence_list)
			#individual_s2rs_prompt = self.prompts.create_few_shot_prompt_for_individual_s2r(app_name, s2r_sentence_list)
			#individual_s2rs_prompt = self.prompts.create_chain_of_thought_prompt_for_individual_s2r(app_name, s2r_sentence_list)
			individual_s2rs = self.generate_response(individual_s2rs_prompt)
			
			with open(text_individual_s2r_file , "w") as f:
				f.write(individual_s2rs)
				f.close()

		return individual_s2rs
	
	def get_response_for_match(self, app_name, bug_id, s2r_index, s2r_sentence_list, comp_str, screen_id, activity):
		object_dir = self.cache_dir
		cur_filename = "Bug-" + str(bug_id) + "-S2R-" + str(s2r_index) +  "-Screen-" + str(screen_id) + ".txt"
		text_object_file = object_dir + "/match_responses/" + cur_filename
		prompt_file = object_dir + "/match_prompts/" + cur_filename
		
		text_exist = self.check_if_score_computed(text_object_file)
		match_prompt = ""
		response = ""

		if self.check_if_score_computed(prompt_file) == True:
			with open(prompt_file, "r") as f:
				match_prompt = f.read()
		else: 
			#match_prompt = self.prompts.create_zero_prompt(app_name, s2r_sentence_list[s2r_index], comp_str)
			match_prompt = self.prompts.create_zero_prompt_with_activity(app_name, s2r_sentence_list[s2r_index], comp_str, activity)
			if "\"" not in cur_filename and "/" not in cur_filename:
				with open(prompt_file, "w") as f:
					f.write(match_prompt)
					f.close()

		if text_exist == True:
			with open(text_object_file, "r") as f:
				response = f.read()
		else:
			response = self.generate_response(match_prompt)
			response = self.helpers.filter_prompt_response(response)
			
			if "\"" not in cur_filename and "/" not in cur_filename:
				with open(text_object_file, "w") as f:
					f.write(response)
					f.close()

		return match_prompt, response
	
	def get_response_for_comp_ids(self, app_name, bug_id, s2r_index, s2r_sentence_list, comp_str, screen_id, activity):
		object_dir = self.cache_dir
		cur_filename = "Bug-" + str(bug_id) + "-S2R-" + str(s2r_index) +  "-Screen-" + str(screen_id) + ".txt"
		text_object_file = object_dir + "/comp_ids_responses/" + cur_filename
		prompt_file = object_dir + "/comp_ids_prompts/" + cur_filename
		text_exist = self.check_if_score_computed(text_object_file)
		id_prompt = ""
		response = ""

		if self.check_if_score_computed(prompt_file) == True:
			with open(prompt_file, "r") as f:
				id_prompt = f.read()
		else: 
			#id_prompt = self.prompts.identify_zero_shot_interaction_id(app_name, s2r_sentence_list[s2r_index], comp_str)
			id_prompt = self.prompts.identify_zero_shot_interaction_id_with_activity(app_name, s2r_sentence_list[s2r_index], comp_str, activity)
			if "\"" not in cur_filename and "/" not in cur_filename:
				with open(prompt_file, "w") as f:
					f.write(id_prompt)
					f.close()

		if text_exist == True:
			with open(text_object_file, "r") as f:
				response = f.read()
				response = ast.literal_eval(response)
		else:
			response = self.generate_response(id_prompt)
			response = self.helpers.filter_comp_id_response(response)
			
			if "\"" not in cur_filename and "/" not in cur_filename:
				with open(text_object_file, "w") as f:
					f.write(str(response))
					f.close()

		return id_prompt, response
	
	def get_updated_s2rs(self, app_name, bug_id, s2r_index, s2r_sentence_list):
		modified_s2r_dir = self.cache_dir
		cur_filename = "Bug-" + str(bug_id) + "-S2R-" + str(s2r_index) + "-S2R-Sentence-" + str(s2r_sentence_list[s2r_index])  + ".txt"
		cur_filename = self.replace_text_for_filename(cur_filename)
		modified_s2r_response_file = modified_s2r_dir + "/modified_s2r_responses/" + cur_filename
		prompt_file = modified_s2r_dir + "/modified_s2r_prompts/" + cur_filename
		
		match_prompt = ""
		response = ""

		if self.check_if_file_exist(prompt_file):
			with open(prompt_file, "r") as f:
				match_prompt = f.read()
		else:
			#match_prompt = self.prompts.create_few_shot_prompt_for_rewriting_s2rs(app_name, s2r_sentence_list[s2r_index])
			match_prompt = self.prompts.create_few_shot_prompt_for_rewriting_s2rs_and_classifying_actions(app_name, s2r_sentence_list[s2r_index])
			#if "\"" not in cur_filename and "/" not in cur_filename:
			with open(prompt_file, "w") as f:
				f.write(match_prompt)
				f.close()

		if self.check_if_file_exist(modified_s2r_response_file):
			with open(modified_s2r_response_file, "r") as f:
				response = f.read()
		else:
			response = self.generate_response(match_prompt)
			
			#if "\"" not in cur_filename and "/" not in cur_filename:
			with open(modified_s2r_response_file, "w") as f:
				f.write(response)
				f.close()

		return match_prompt, response








	
   