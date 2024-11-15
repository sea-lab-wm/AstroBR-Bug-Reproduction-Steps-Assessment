from helpers import Helpers

class Prompts:
	def __init__(self):
		self.helpers = Helpers()
	#     def create_zero_prompt(self, app_name, s2r_sentence, comp_str):
#         prompt = """Task Description:
# In this task, I will provide two inputs:
# 1. a step-to-reproduce (S2R) sentence from a bug report of """ + app_name + """ app
# 2. a list of the interactions (operations can be performed on that screen) of one app screen

# Your task is to identify the interaction that matches the interaction described in the S2R sentence from the available interactions on this screen. 
# We present the actions and interacted GUI component information for each interaction. For each GUI component, we include the type, identifier, text, and description. 

# Input:
# S2R Sentence: """ + s2r_sentence + "\n\n"
#         prompt += """Interactions of one screen:\n""" 
#         prompt += comp_str + "\n"
#         prompt += """If the interaction is identified, return 1; otherwise, return 0. Do not include anything else in the response."""    
#         return prompt

# 	def create_zero_prompt(self, app_name, s2r_sentence, comp_str):
# 		prompt = """Task Description:
# In this task, I will provide two inputs:
# 1. a step-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app
# 2. a list of the interactions (operations can be performed on that screen) of one app screen

# Your task is to identify the interaction that matches the interaction described in the S2R sentence from the available interactions on this screen. 

# Input:
# S2R Sentence: """ + s2r_sentence + "\n\n"
# 		prompt += """Interactions of one screen:\n""" 
# 		prompt += comp_str + "\n"
# 		prompt += """If the interaction is identified, return 1; otherwise, return 0. Do not include anything else in the response."""    
# 		return prompt
	
	def create_zero_prompt_with_activity(self, app_name, s2r_sentence, comp_str, activity):
		prompt = """Task Description:
In this task, I will provide two inputs:
1. a step-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app
2. a list of the interactions (operations can be performed on that screen) of one app screen where Activity =""" + activity + """
		
Your task is to identify the interaction that matches the interaction described in the S2R sentence from the available interactions on this screen. 

Input:
S2R Sentence: """ + s2r_sentence + "\n\n"
		prompt += """Interactions of one screen:\n""" 
		prompt += comp_str + "\n"
		prompt += """If the interaction is identified, return 1; otherwise, return 0. Do not include anything else in the response."""    
		return prompt
	
	def create_zero_prompt_for_objects(self, app_name, s2r_sentence):
		prompt = """Please identify the object from this S2R sentence of the """ + app_name + """ app. 
Input: S2R Sentence: """ + s2r_sentence + "\n\n"
		prompt += """If the interaction is identified, only return the object; otherwise, return 0. Do not include anything else in the response."""    
		return prompt
	
	def create_zero_prompt_for_all_screen_comps(self, app_name, s2r_sentence, comp_str):
		prompt = """Task Description:
In this task, I will provide two inputs:
1. a step-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app
2. a list of the GUI components of one app screen

Your task is to identify the GUI component that matches the object described in the S2R sentence from the available components on this screen. 

Input:
S2R Sentence: """ + s2r_sentence + "\n\n"
		prompt += """GUI components of one screen:\n""" 
		prompt += comp_str + "\n"
		prompt += """If the interaction is identified, return 1; otherwise, return 0. Do not include anything else in the response."""    
		return prompt
	
	def create_zero_prompt_for_cosine_similarity(self, app_name, s2r_sentence, comp_str):
		prompt = """Task Description:
In this task, I will provide two inputs:
1. a step-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app
2. a list of the interactions (operations can be performed on that screen) of one app screen

Your task is to provide rankings of the most similar for the available interactions on this screen with the interaction described in the S2R sentence.

Input:
S2R Sentence: """ + s2r_sentence + "\n\n"
		prompt += """Interactions of one screen:\n""" 
		prompt += comp_str + "\n"
		prompt += """Answer with the interaction ids (digits) only or 0 when there is no match. Do not include anything else in the response."""    
		return prompt
	
	def create_few_shot_prompt_for_rewriting_s2rs(self, app_name, s2r_sentence):
		prompt = """Task Description:
In this task, I will provide one input, i.e., a step-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app.

Your task is to identify actions and objects from the S2R sentence and rewrite it in the following format: [Action][Object]. 
If the S2R sentence includes an instruction to type a specific text, include that text as well in the rewritten S2R. In such cases, the modified S2R should be "[Action][Text] on [Object]."

Example-1: 
Input: Try to play any song by any means provided by the app
Output: Play any song

Example-2:
Input: Select a link in the article, allowing the next page to load in the WebView
Output: Select a link 

Example-3:
Input: Edit a location
Output: Edit a location

S2R Sentence: """ + s2r_sentence + "\n\n"
	
		prompt += """Return the updated S2R. Do not include anything else in the response."""    
		return prompt
	
	def create_few_shot_prompt_for_rewriting_s2rs_and_classifying_actions(self, app_name, s2r_sentence):
		prompt = """Task Description:
In this task, I will provide one input, i.e., a step-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app.

Your first objective is to identify actions and objects within the S2R sentence. Then, classify each action into one of the predefined action groups listed below, each containing verbs with similar meaning and presented in the following format: [Action Group][Verbs].

Open: open, start, execute, initiate, run, begin, commence
Toggle: toggle, flip flop, interchange, switch, alternate, flip
Long-click: long tap, hold, long click, long press, long push, long hit, long click on, select, change
Click: tap, tip, click, press, push, select, go, choose, check, pick, hit, click on, add, change, save, click back, mark, set, edit, display, leave, create, enable, start, stop, close, change, spot, uncheck, deselect
Swipe: swipe, drag, sweep, scroll, scroll down, scroll up, scroll right, scroll left, swipe down, swipe up, swipe right, swipe left
Type: type, edit, input, fill, typewrite, insert, infix, enter, introduce, write, set, add, change, press
Rotate: rotate, change, set, turn
Close: close, terminate, shut down
Back: go back

Now rewrite S2R in the following format: [Action Group][Object]. 
If the S2R sentence includes an instruction to type a specific text, include that text as well in the rewritten S2R. In such cases, the modified S2R should be "[Action Group][Text] on [Object]."

Example-1: 
Input: Try to play any song by any means provided by the app
Output: Play any song

Example-2:
Input: Select a link in the article, allowing the next page to load in the WebView
Output: Select a link 

Example-3:
Input: Edit a location
Output: Edit a location

S2R Sentence: """ + s2r_sentence + "\n\n"
	
		prompt += """Return the rewritten S2R. Do not include anything else in the response."""    
		return prompt
	
# 	def identify_zero_shot_interaction_id(self, app_name, s2r_sentence, comp_str):
# 		prompt = """Task Description:
# In this task, I will provide two inputs:
# 1. a step-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app
# 2. a list of the interactions (operations can be performed on that screen) of one app screen

# Your task is to identify the interaction that matches the interaction described in the S2R sentence from the available interactions on this screen. 

# Input:
# S2R Sentence: """ + s2r_sentence + "\n\n"
# 		prompt += """Interactions of one screen:\n""" 
# 		prompt += comp_str + "\n"
# 		prompt += """There is at least one matched interaction id among the available interactions mentioned above. Please return interaction ids. Do not include anything else in the response."""    
# 		return prompt
	
	def identify_zero_shot_interaction_id_with_activity(self, app_name, s2r_sentence, comp_str, activity):
		prompt = """Task Description:
In this task, I will provide two inputs:
1. a step-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app
2. a list of the interactions (operations can be performed on that screen) of one app screen where Activity =""" + activity + """

Your task is to identify the interaction that matches the interaction described in the S2R sentence from the available interactions on this screen. 

Input:
S2R Sentence: """ + s2r_sentence + "\n\n"
		prompt += """Interactions of one screen:\n""" 
		prompt += comp_str + "\n"
		prompt += """There is at least one matched interaction id among the available interactions mentioned above. Please return interaction ids. 
If the S2R sentence describes only a single interaction with different keywords (e.g., any, either, or, etc.), you should return only one interaction id.
Do not include anything else in the response."""    
		return prompt
	
	def create_zero_prompt_for_identifying_bug_report_components(self, app_name, bug_report):
		prompt = """In this task, I will provide a bug report from the """ + app_name + """ app, where each sentence is labeled using a number. You will identify the sentences that describe the:

Observed Behavior (OB): All sentences describing an incorrect or unexpected behavior of the app's misbehavior.
Expected Behavior (EB): All sentences describing expected or correct app behavior. 
Steps to Reproduce (S2Rs): All sentences that describe the actions made on the app to replicate or reproduce the incorrect or unexpected app behavior. 

Consider the following factors for identifying OB, EB, and S2Rs.

Observed Behavior of the app (OB): 
An OB sentence describes an incorrect or unexpected behavior of the app.
There could be multiple OB sentences anywhere in the bug report, including the first sentence of the bug report, marked with (0).
If a sentence describes only the cause for the bug but not the observed, unexpected/incorrect app behavior, the sentence is not an OB sentence.
Likewise, if a sentence contains only app or device version information or app execution trace information, the sentence is not an OB sentence.
A sentence can describe more information besides the OB; in such cases, the whole sentence is an OB sentence.
A sentence is not OB if it describes particular conditions that are necessary to reproduce the bug.
A sentence is not OB if it describes the motivation or importance of the bug. 
A sentence is not OB if it describes the rationale why the reporter considers the problem as a bug.
An OB sentence can be also an EB sentence if it describes both observed behavior and expected behavior. Typically these sentences contain phrases like “rather than”, “instead of”, etc.
Both OB and S2Rs can exist in a sentence. In these cases, the sentence should be considered as both OB and S2Rs.
The semantically opposite sentence of an explicit EB can be considered an OB. Explicit EB refers to labeled EB sentences under the headers like “Expected Behavior”/“Desired Behavior”/“Expected Results”/“Expected Output”/etc.
A sentence is OB if it describes the observed behavior even if it is a part of the sequential actions (sentences). 

Expected Behavior of the app (EB): 
An EB sentence describes expected or correct app behavior. The EB is usually the opposite of the OB. 
There could be multiple EB sentences anywhere in the bug report, including the first sentence of the bug report, marked with (0). 
A sentence can describe more information besides the EB; in such cases, the whole sentence is an EB sentence.
An EB sentence can be also an OB sentence if it describes both observed behavior and expected behavior. Typically these sentences contain phrases like “rather than”, “instead of”, etc.

Steps to Reproduce the Bug (S2Rs): 
An S2R sentence describes the actions made on the app to replicate the incorrect or unexpected app behavior. Actions represent interactions that app users make on regions or GUI components of the app screen. Common actions made on Android apps are Click, Type, Swipe, Pinch, and Long-click. These actions may be described with synonym words.
S2R sentences also describe actions that are high-level and can be worded via verbs such as start, open, add, go back, select, insert, refresh, etc.
A sentence can describe more information besides the S2Rs; in such cases, the whole sentence is considered to be an S2R sentence.
Both OB and S2Rs can exist in a sentence. In these cases, the sentence should be considered as both OB and S2Rs.
A sentence that is not an action should not be considered an S2R, even if it is a part of the sequential actions (sentences).

Bug Report: 
""" + bug_report + "\n"

		prompt += """Response format:
Please list the numbers of the sentences that describe OB, EB, or S2R, using the following format:
OB: list the numbers of the sentences that describe the Observed Behavior of the app, separated by commas
EB: list the numbers of the sentences that describe the Expected Behavior of the app, separated by commas
S2Rs: list the numbers of the sentences that describe the Steps to Reproduce the bug, separated by commas
Do not provide anything else in the response.
"""     
		return prompt
	
#     def create_zero_prompt_for_individual_s2r(self, app_name, s2r_sentence):
#         prompt = """In this task, I will provide a steps-to-reproduce (S2R) sentence from a bug report of the """ + app_name + """ app. 
# An S2R sentence may indicate only one step or multiple individual steps required to reproduce the bug linked by different linkers (e.g., and, or, etc.) or symbols (e.g., >, →, comma, etc.). 
# Your task is to identify the individual steps from the S2R sentence if there are any. 
# You should not generate any additional text to provide the individual steps, rather you will split the given S2R sentence to form the individual steps and provide them as the output.

# Target S2R sentence (delimited by triple quotes): 
# """ + s2r_sentence + "\n"

#         prompt += """Response format:
# <individual steps for the given S2R sentence in list format>
# Do not provide anything else in the response.
# """
#         return prompt
	
	def create_zero_prompt_for_individual_s2r(self, app_name, s2r_sentence_list):
		prompt = """In this task, I will provide all steps-to-reproduce (S2R) sentences from a bug report of the """ + app_name + """ app. 
An S2R sentence may describe either a single step or multiple individual steps required to reproduce the bug, often connected by different linkers (e.g., and, while, etc.) or symbols (e.g., >, →, commas, etc.). 
Your task is to identify and extract the individual sequential steps from the S2R sentences to reproduce a bug.

In cases where multiple steps are embedded in a single S2R, you are required to separate them into individual steps and provide these in the output.
If multiple individual steps after splitting represent the same interaction on the app, retain only the most relevant step and disregard any redundant ones. 
If an individual step involves only observing any behavior on the app screen, disregard that step.

Once the individual steps are identified, you must extract actions, object, preposition and object2, and represent each step as a sentence in the following format:
								[action] [object] [preposition] [object2]

Here, the [action] refers to the operation a user must perform within the app (e.g., click, type, etc.), the [object] is the GUI component upon which the action is performed, 
and [object2] is another text related to the object, connected by a [preposition]. 

S2R Sentences: 
""" 
		for i in range(len(s2r_sentence_list)):
			prompt+= s2r_sentence_list[i] + "\n"

		prompt += """Response format:
<individual steps in list format>
The output should contain only a list of sentences and sentences should contain words in text format. Do not provide anything else in the response. 
"""
		return prompt
	
	def create_few_shot_prompt_for_individual_s2r(self, app_name, s2r_sentence_list):
		prompt = """In this task, I will provide all steps-to-reproduce (S2R) sentences from a bug report of the """ + app_name + """ app. 
An S2R sentence may describe either a single step or multiple individual steps required to reproduce the bug, often connected by different linkers (e.g., and, while, etc.) or symbols (e.g., >, →, commas, etc.). 
Your task is to identify and extract the individual sequential steps from the S2R sentences to reproduce a bug.

In cases where multiple steps are embedded in a single S2R, you are required to separate them into individual steps and provide these in the output.
If multiple individual steps after splitting represent the same interaction on the app, retain only the most relevant step and disregard any redundant ones. 
If an individual step involves only observing any behavior on the app screen, disregard that step.

Once the individual steps are identified, you must extract actions, object, preposition and object2, and represent each step as a sentence in the following format:
								[action] [object] [preposition] [object2]

Here, the [action] refers to the operation a user must perform within the app (e.g., click, type, etc.), the [object] is the GUI component upon which the action is performed, 
and [object2] is another text related to the object, connected by a [preposition]. 

S2R Sentences: 
""" 
		for i in range(len(s2r_sentence_list)):
			prompt+= s2r_sentence_list[i] + "\n"

		prompt += """Response format:
<individual steps in list format>
The output should contain only a list of sentences and sentences should contain words in text format. Do not provide anything else in the response. 
"""	
		prompt += """Below, I am providing two examples with the expected responses for illustration purposes.

S2R sentences of example bug report 1:
1. Open an article.
2. Select a link in the article, allowing the next page to load in the WebView.
3. Hit back.
Expected response for example bug report 1:
1. Open article.
2. Select link in article.
3. Hit back.

S2R sentences of example bug report 2:
1. Launch Ultrasonic master in an AVD.
2. Go to settings, add server, enter name, url, user and password.
3. Click on "Test Connection".
Expected response for example bug report 2:
1. Launch Ultrasonic master
2. Go to settings
3. add server
4. enter name
5. enter url
6. enter user
7. enter password
8. Click on "Test Connection"
"""
		return prompt
	
	def create_chain_of_thought_prompt_for_individual_s2r(self, app_name, s2r_sentence_list):
		prompt = """In this task, I will provide all steps-to-reproduce (S2R) sentences from a bug report of the """ + app_name + """ app. 
An S2R sentence may describe either a single step or multiple individual steps required to reproduce the bug, often connected by different linkers (e.g., and, while, etc.) or symbols (e.g., >, →, commas, etc.). 
Your task is to identify and extract the individual sequential steps from the S2R sentences to reproduce a bug.

In cases where multiple steps are embedded in a single S2R, you are required to separate them into individual steps and provide these in the output.
If multiple individual steps after splitting represent the same interaction on the app, retain only the most relevant step and disregard any redundant ones. 
If an individual step involves only observing any behavior on the app screen, disregard that step.

Once the individual steps are identified, you must extract actions, object, preposition and object2, and represent each step as a sentence in the following format:
								[action] [object] [preposition] [object2]

Here, the [action] refers to the operation a user must perform within the app (e.g., click, type, etc.), the [object] is the GUI component upon which the action is performed, 
and [object2] is another text related to the object, connected by a [preposition]. 

S2R Sentences: 
""" 
		for i in range(len(s2r_sentence_list)):
			prompt+= s2r_sentence_list[i] + "\n"

		prompt += """Response format:
<individual steps in list format>
The output should contain only a list of sentences and sentences should contain words in text format. Do not provide anything else in the response. 
"""	
		prompt += """Below, I am providing two examples with the expected responses with reasoning for illustration purposes.

S2R sentences of example bug report 1:
1. Open an article.
2. Select a link in the article, allowing the next page to load in the WebView.
3. Hit back.
Expected response for example bug report 1:
1. Open article.
2. Select link in article.
3. Hit back.
Reason: There are three S2R sentences in this bug report and all of them represent one individual step each. The first and third S2R sentences are straightforward as they contain only one action and one object. Although the second S2R sentence is long, it also contains one individual step, i.e., "Select a link in the article". The other portion of the sentence indicates the consequence of the step and is not a step for reproducing the bug. After formatting with action and object the individual step becomes "Select link in article".

S2R sentences of example bug report 2:
1. Launch Ultrasonic master in an AVD.
2. Go to settings, add server, enter name, url, user and password.
3. Click on "Test Connection".
Expected response for example bug report 2:
1. Launch Ultrasonic master
2. Go to settings
3. add server
4. enter name
5. enter url
6. enter user
7. enter password
8. Click on "Test Connection"
Reason: There are three S2R sentences in this bug report. The first sentence indicates one individual step, i.e., “Launch Ultrasonic master”. However, the second S2R sentence contains six individual steps in one S2R sentence which are separated by comma. The third S2R sentence presents only one individual step. Formatting the eight individual steps results in the individual steps presented in the expected response.
"""
		return prompt


	
# 	def create_zero_prompt_for_individual_s2r(self, app_name, s2r_sentence_list):
# 		prompt = """In this task, I will provide all steps-to-reproduce (S2R) sentences from a bug report of the """ + app_name + """ app. 
# A single step may described by various keywords (e.g., any, either, or, etc.), and multiple steps are often described by different linkers (e.g., and, both, all, etc.) or symbols (e.g., >, →, commas, etc.). 
# Your task is to identify all individual steps from the S2R sentences to reproduce a bug.

# In cases where multiple steps are embedded in a single S2R sentence, you are required to separate them into individual steps and present them in the output.
# If an individual step involves only observing or verifying any behavior on the app screen, disregard that step.

# Once the individual steps are identified, you should extract actions, object, preposition and object2, and represent each step as a sentence in the following format:
#                                 [action] [object] [preposition] [object2]

# Here, the [action] refers to the operation a user must perform within the app (e.g., click, type, swipe, etc.), the [object] is the GUI component upon which the action is performed, and [object2] is another text connected to the object by a [preposition]. 

# S2R Sentences: 
# """ 
# 		for i in range(len(s2r_sentence_list)):
# 			prompt+= s2r_sentence_list[i] + "\n"

# 		prompt += """Response format:
# <individual steps in list format>
# The output should consist only of a list of sentences, each entirely in textual form without any square brackets. Do not provide anything else in the response.
# """
# 		return prompt
	#In cases where multiple steps are embedded in a single S2R sentence, you are required to separate them into individual steps and provide them in the output.
	#Your task is to identify and extract the individual steps from the S2R sentences to reproduce a bug.
# 	def create_zero_prompt_for_individual_s2r(self, app_name, s2r_sentence_list):
# 		prompt = """In this task, I will provide all steps-to-reproduce (S2R) sentences from a bug report of the """ + app_name + """ app. 
# An S2R sentence may describe either a single step or multiple individual steps required to reproduce the bug, often connected by different linkers (e.g., and) or symbols (e.g., ->, >). 
# Your task is to identify and retrieve the individual steps from each S2R sentence to reproduce a bug.

# In cases where multiple steps are embedded in a single S2R sentence, you are required to separate them into individual steps and provide these in the output. 
# If an individual step involves only observing any behavior on the app screen, disregard that step.

# Once the individual steps are identified, you should extract attributes, i.e., action, object, preposition and object2 (if present) from each step, and represent them in a sentence in the following format:
# 								[action] [object] [preposition] [object2]

# Here, the [action] refers to the operation a user must perform within the app (e.g., click, type, etc.), the [object] is the GUI component upon which the action is performed, 
# and [object2] is another text or number related to the object, connected by a [preposition]. 

# S2R Sentences: 
# """ 
# 		for i in range(len(s2r_sentence_list)):
# 			prompt+= s2r_sentence_list[i] + "\n"

# 		prompt += """Response format:
# <individual steps in list format>
# The response should contain only a list of sentences and each sentence should not contain isolated extracted attributes, square brackets, or bullet points (e.g., -, *). Do not provide anything else in the response.
# """
# 		return prompt
	
#The response should consist only of a list of individual s2r sentences, each in a single line without any square brackets. Do not provide anything else in the response.
	
	def create_zero_prompt_for_individual_s2r_v2(self, app_name, s2r_sentence_list):
		prompt = """In this task, I will provide all the steps-to-reproduce (S2R) sentences from a bug report of the """ + app_name + """ app.

An S2R sentence may indicate only one step or multiple individual steps required to reproduce the bug linked by different linkers (e.g., and, or, etc.) or symbols (e.g., >, →, comma, etc.). Your task is to identify the individual steps from the given S2R sentences if there are any. You should not generate any additional text or discard any text from the given S2R sentence to provide the individual steps, rather you will split the given S2R sentences to form the individual steps if needed. Note that an S2R sentence can contain additional information such as observed behavior. In that case, do not split that part as a separate individual step and consider the whole S2R sentence as the individual step. The individual step should represent an action that is required to reproduce the bug.

Target S2R sentences (delimited by triple quotes): 
"""
		for i in range(len(s2r_sentence_list)):
			prompt+= s2r_sentence_list[i] + "\n"

		prompt += """Response format:
<individual steps in list format>
Do not provide anything else in the response.
""" 
		return prompt
	
	def create_zero_prompt_interaction_id(self, app_name, s2r_sentence, comp_str):
#         prompt = """Task Description:
# In this task, I will provide two inputs:
# 1. a step-to-reproduce (S2R) sentence from a bug report of """ + app_name + """ app
# 2. a list of the interactions (operations can be performed on that screen) of one app screen

# Your task is to identify the most relevant interaction from the available interactions to the S2R sentence of the bug report. Provide the response using the response format strictly. Do not include anything else in the response. 

# Input:
# S2R Sentence: """ + s2r_sentence + "\n\n"
		prompt = """Task Description:
In this task, I will provide two inputs:
1. a step-to-reproduce (S2R) sentence from a bug report of """ + app_name + """ Android app
2. a list of the interactions (operations can be performed on that screen) of one app screen

Your task is to identify the most relevant interaction from the list of interactions to the S2R sentence of the bug report. 

Instruction:
Analyze the action and GUI component information of the given interactions and match them with the given S2R sentence. Identify the most relevant interactions for the given S2R sentence. There can be zero, one, or multiple relevant interactions for the given S2R sentence. In the response, only provide interaction_IDs or 0 using the following rules:
a. Relevant Interaction ID for one identified relevant interaction, or
b. Relevant Interaction IDs separated by a comma for multiple identified relevant interactions, or
c. 0 for no identified relevant interactions
You must not include anything else (e.g., other texts) in the response.

Input:
S2R Sentence: """ + s2r_sentence + "\n\n"
		prompt += """Interactions of one screen:\n""" 
		prompt += comp_str + "\n"
		#prompt += """Output: [<Interaction ID> for one relevant interaction; <0> for no relevant interaction]"""    
		prompt += """Response Format:
[Interaction_IDs or 0]
"""
		return prompt
	
	def create_few_shot_prompt(self, app_name, s2r_sentence, comp_str):
		prompt = """Task Description:
In this task, I will provide two inputs:
1. a step-to-reproduce (S2R) sentence from a bug report of """ + app_name + """ app
2. a list of the interactions (operations can be performed on that screen) of one app screen

Your task is to identify the most relevant interaction from the available interactions to the S2R sentence of the bug report. Below, I am providing two examples with the expected response for illustration purposes.
"""
		prompt += "Example-1:\n" 
		prompt += """Input:
S2R Sentence: 2. click "report" option

Interactions of one screen:
1. Interaction ID = 1; Action = “click”; GUI Component = [Type = “Button”, Identifier = “select_account”, Text = “Accounts”, Description = “”]
2. Interaction ID = 2; Action = “click”; GUI Component = [Type = “Button”, Identifier = “select_expenses”, Text = “Expenses”, Description = “”]
3. Interaction ID = 3; Action = “click”; GUI Component = [Type = “Button”, Identifier = “add_expense”, Text = “”, Description = “”]
4. Interaction ID = 4; Action = “click”; GUI Component = [Type = “Button”, Identifier = “add_transfer”, Text = “”, Description = “”]
5. Interaction ID = 5; Action = “click”; GUI Component = [Type = “Button”, Identifier = “select_income”, Text = “Incomes”, Description = “”]
6. Interaction ID = 6; Action = “click”; GUI Component = [Type = “Button”, Identifier = “select_income”, Text = “Incomes”, Description = “”]
7. Interaction ID = 7; Action = “click”; GUI Component = [Type = “Button”, Identifier = “select_transfers”, Text = “Transfers”, Description = “”]
8. Interaction ID = 8; Action = “click”; GUI Component = [Type = “Button”, Identifier = “select_sms_patterns”, Text = “Sms Patterns”, Description = “”]
9. Interaction ID = 9; Action = “click”; GUI Component = [Type = “Button”, Identifier = “select_charts”, Text = “Reports”, Description = “”]
10. Interaction ID = 10; Action = “click”; GUI Component = [Type = “Button”, Identifier = “add_income”, Text = “”, Description = “”]
11. Interaction ID = 11; Action = “click”; GUI Component = [Type = “Button”, Identifier = “select_templates”, Text = “Templates”, Description = “”]
12. Interaction ID = 12; Action = “click”; GUI Component = [Type = “ImageButton”, Identifier = “”, Text = “”, Description = “Open”]

Expected Output: 1
"""     
		prompt += "Example-2:\n" 
		prompt += """Input:
S2R Sentence: 4. click eye icon

Interactions of one screen:
1. Interaction ID = 1; Action = “click”; GUI Component = [Type = “ImageButton”, Identifier = “”, Text = “”, Description = “Navigate up”]
2. Interaction ID = 2; Action = “click”; GUI Component = [Type = “ActionBar$Tab”, Identifier = “”, Text = “”, Description = “Incomes by Articles”]
3. Interaction ID = 3; Action = “click”; GUI Component = [Type = “TextView”, Identifier = “”, Text = “Expenses by Articles (Pie Chart)”, Description = “Incomes by Articles”]
4. Interaction ID = 4; Action = “click”; GUI Component = [Type = “TextView”, Identifier = “action_display”, Text = “”, Description = “Display”]
5. Interaction ID = 5; Action = “click”; GUI Component = [Type = “ActionBar$Tab”, Identifier = “”, Text = “”, Description = “Expenses by Articles (Pie Char...”]
6. Interaction ID = 6; Action = “click”; GUI Component = [Type = “ActionBar$Tab”, Identifier = “”, Text = “”, Description = “Expenses by Articles”]
7. Interaction ID = 7; Action = “click”; GUI Component = [Type = “TextView”, Identifier = “action_display”, Text = “”, Description = “Display”]

Expected Output: 1
"""
		prompt += """Input:
S2R Sentence: """ + s2r_sentence + "\n\n"
		prompt += """Interactions of one screen:\n""" 
		prompt += comp_str + "\n"
		prompt += """If relevant interaction exist, return 1; otherwise, return 0. Do not include anything else in the response.\n"""   
		
		return prompt
	
	
	def create_prompt_for_segmented_xml(self, xml_code, s2r_comp):
		question_list = []
		question_list.append("""The total length of the xml code is too large to send in only one piece. Therefore, 
for sending the xml code, I will divide the xml in multiple parts and send one by one. \n""")
		
		start_len = 0
		end_len = len(xml_code)
		print("end_len: " + str(end_len))
		segment_size = 2000
		while start_len<segment_size and start_len<=end_len:
			if start_len+segment_size<=end_len:
				question_list.append(xml_code[start_len:start_len+segment_size])
			else: 
				 question_list.append(xml_code[start_len:end_len])
			start_len += segment_size
		
		question_list.append("""\nIs there any following component that corresponds to this written component described in a particular steps to reproduce? """ + s2r_comp + """\nIf there is a match, write 1; otherwise, write 0""")
		return question_list
	
	def create_prompt(self, comp_str, s2r_comp, s2r_action):
		prompt = """The available GUI components in a particular GUI screen can be represented in the following format: component ID, component text, component class, and component content description. 
The available GUI components in the current GUI screen are presented below.\n""" + str(comp_str)
		#prompt += """\nIs there any following component that corresponds to this written component described in a particular steps to reproduce? """ + s2r_comp
		prompt += """\nAre there any components that a user will interact with to perform the """ + s2r_action + """ on """ + s2r_comp + """?""" 
		prompt += """\nIf such component exist, write 1; otherwise, write 0"""

		print(prompt)

		return prompt
	
	def create_prompt_for_identifying_gui_comps(self, app_name, comp_str, s2r_comp, s2r_action):
		prompt = """A user is navigating the """ + app_name + """ app. The available GUI components in the current GUI screen are presented below.\n""" + str(comp_str)
		prompt += """\nWhich of these components does the user interact with to perform the """ + s2r_action + """ on """ + s2r_comp + """?""" 

		return prompt
	
	def create_prompt_for_detailed_gui_comps(self, app_name, comp_str, s2r_comp, s2r_action):
		prompt = """A user is navigating the """ + app_name + """ app. The available GUI components in the current GUI screen are presented below.\n""" + str(comp_str)
		prompt += """\nAre there any components that the user will interact with to perform the """ + s2r_action + """ on """ + s2r_comp + """?""" 
		prompt += """\nIf such a component exist, return 1; otherwise, return 0"""

		print(prompt)

		return prompt
	
	def comp_no_duplicates(self, i, interactions):
		for k in range(i):
			if len(interactions[i][4])>0 and interactions[i][4]==interactions[k][4]:
				return False
			if len(interactions[i][5])>0 and (interactions[i][5]==interactions[k][5] or interactions[i][5]==interactions[k][6]):
				return False
			if len(interactions[i][6])>0 and (interactions[i][6]==interactions[k][6] or interactions[i][6]==interactions[k][5]):
				return False
		return True
	
	def create_comp_interactions(self, interactions, bug_id, graph_folder_path, screen_id):
		comp_str = ""
		
		for i in range(len(interactions)):
			cur_str = str(i+1) + ". Interaction ID = " + str(i+1) 
			cur_str += "; Action = " + interactions[i][2]

			gui_str = ""
			comp_flag = False
			if len(interactions[i][3])>0:
				gui_str += "Type = " + interactions[i][3] + ", "
				comp_flag = True
			if len(interactions[i][4])>0:
				gui_str += "Identifier = " + interactions[i][4] + ", "
				comp_flag = True
			if len(interactions[i][5])>0:
				gui_str += "Text = " + interactions[i][5] + ", "
				comp_flag = True
			if len(interactions[i][6])>0:
				gui_str += "Description = " + interactions[i][6]
				comp_flag = True

			if comp_flag:
				gui_str = gui_str.strip()
				if gui_str[len(gui_str)-1]==",":
					gui_str = gui_str[:len(gui_str)-1]
				cur_str += "; GUI Component = [" + gui_str + "]" 

			if interactions[i][3]=="CheckBox" or interactions[i][3]=="Switch":
				nearby_comps = self.helpers.get_nearby_components(bug_id, graph_folder_path, screen_id, interactions[i][10], interactions[i][11], interactions[i][12], interactions[i][13], interactions[i][8], interactions[i][14], interactions[i][9])
				if len(nearby_comps)>0:
					nearby_comps_str = ""
					for j in range(len(nearby_comps)):
						if j==0:
							nearby_comps_str += nearby_comps[j]
						else:
							nearby_comps_str += ", " + nearby_comps[j]
					cur_str += ", Nearby Components: [" + nearby_comps_str + "]"

			comp_str += cur_str + "\n"
		return comp_str
	
	def create_state_all_comps(self, comp_list):
		comp_str = ""

		if len(comp_list)==0:
			return ""
		for i in range(len(comp_list[0])):
			comp_str += str(i+1) + ". " + str(comp_list[0][i]) + "\n"
		return comp_str
	
	
	def get_comp_info_list(self, interactions):
		comp_list = []

		for i in range(len(interactions)):
			# comp_str = str(i+1) + ". Action= " + interactions[i][2]
			# comp_str += "; GUI Component = [Type = " + interactions[i][3] + ", Identifier = " + interactions[i][4] + ", " + "Text = " + interactions[i][5] + ", " + "Description = " + interactions[i][6]+ "]\n"
			comp_str = ""
			# if len(interactions[i][2])>0:
			#     comp_str += interactions[i][2]
			if len(interactions[i][5])>0:
				comp_str += " " + interactions[i][5]
			elif len(interactions[i][4])>0:
				comp_str += " " + interactions[i][4]
			elif len(interactions[i][6])>0:
				comp_str += " " + interactions[i][6]
			# if len(interactions[i][3])>0:
			#     comp_str += " " + interactions[i][3]
			comp_list.append(comp_str)

		return comp_list