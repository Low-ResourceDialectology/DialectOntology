
import argparse
import csv
from datetime import date
import glob
import json
import os
import sys

""" 
# Setup
git clone git@github.com:Low-ResourceDialectology/DialectOntology.git
python3 -m venv venvDO

# Use
cd DialectOntology
source ./../venvDO/bin/activate
python3 language_info.py --lang German --proj "German Varieties"
"""


""" Process
==== 1. Look up terms in Glottolog data → ISO codes (and more)
==== 2. Look up ISO codes in Ethnologue data → Info for language varieties 
		- in various countries (China, Iran, ...),
		- of various types (Language, Dialect, ...),
		- in various local orthographhies (Kurmancî, Kurmanji)
==== 3. Look up previously unknown names in Glottolog data → ISO codes (and more)
==== 4. Repeat until no new names are found
==== 5. Loop up language names in Ethnologue data → Country information
==== 6. Write language information as dictionaries to json file
"""

def main():
	parser = argparse.ArgumentParser(description='Create Configuration')
	parser.add_argument('--lang', type=str, help='directory of language data', default="Kurdish")
	parser.add_argument('--proj', type=str, help='project name', default="Kurdish Varieties Showcase")

	args = parser.parse_args()
	input_path = f'./languages/{args.lang}/'

	"""
	===========================================================================
	Helper Functions
	===========================================================================
	"""
	def read_csv_file(input_file, newline='', delimiter=',', quotechar='"'):
		data_rows = []
		with open(input_file, newline=newline) as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=delimiter, quotechar=quotechar)
			for row in csv_reader:
				data_rows.append(row)
		return data_rows
	
	def create_directory(path):
		# Check whether directory already exists
		if not os.path.exists(path):
			os.mkdir(path)
			print("Folder %s created!" % path)
		else:
			print("Folder %s already exists" % path)


	"""
	===========================================================================
	Paths to Directories and Files
	===========================================================================
	"""
	# Project Files
	input_eth_countrycodes = './data/ethnologue/CountryCodes.tab'
	input_eth_languagecodes = './data/ethnologue/LanguageCodes.tab'
	input_eth_languageindex = './data/ethnologue/LanguageIndex.tab'
	input_glo_languages = './data/glottolog/languages.csv'
	input_glo_languagesanddialectsgeo = './data/glottolog/languages_and_dialects_geo.csv'
	
	# Language Files
	inter_path = f'{input_path}/inter/'
	output_path = f'{input_path}/output/'
	
	# Create output directory if not existing
	create_directory(inter_path)
	create_directory(output_path)
	

	""" 
	===========================================================================
	Manually collected Data
	===========================================================================
	INPUT:	A dictionary containing the language terms to be explored. 
			TODO: Implement handling multiple formats of input file.
	OUTPUT: A list of terms associated with language varieties.
	"""
	# =========================================================================
	# Read provided list of language identifying terms
	def read_language_names(input_path):

		# List of all variations of names for the found dialects
		dialect_word_list = []

		# List everything in the language input directory but only consider files, not subdirectories
		input_files = glob.glob(f'{input_path}*', recursive = False)
		input_files = [f for f in input_files if os.path.isfile(f)]

		for input_file in input_files:
			# Check extension of current file
			file_extension = os.path.basename(input_file).split(".")[-1]

			# Read from .json file (structure such as in the Kurdish example file)
			if file_extension in ["json", "jsonl"]:
				
				# Read word list from info file
				with open(input_file, 'r') as f:
					print(f'Reading file: {input_file}')
					dialect_info = json.load(f)

				# For each "super" item in the json
				for dialect_name in dialect_info["dialects"].keys():
					for dialect_name_variation in dialect_info["dialects"][dialect_name]["nameOrthographies"]:
						dialect_word_list.append(dialect_name_variation)

			# Read from .txt file (one name per line)
			elif file_extension in ["txt"]:

				# Read word list from info file
				with open(input_file, 'r') as f:
					print(f'Reading file: {input_file}')
					dialect_names = f.readlines()
				
				# Get variety name from each text line
				for dialect_name in dialect_names:
					dialect_word_list.append(dialect_name.replace('\n',''))

		return dialect_word_list

	# =========================================================================
	# Turn a list of words into a dictionary of keys
	def word_list_to_dict(dialect_word_list):

		# Dictionary to hold aggregated info about terms from word_list
		dialect_info_dict = {} 

		# Create a new item for each term in the dictionary
		for term in dialect_word_list:
			# These lists are later to be filled with info found
			dialect_info_dict[term] = {}

		return dialect_info_dict


	""" 
	===========================================================================
	Glottolog Data
	===========================================================================
	INPUT:  A list of terms associated with language varieties.
	OUTPUT: Additional information for each of these terms that is contained
			in the Glottolog data, such as ISO codes used further below.
	"""
	# languages_and_dialects_geo.csv
	""" Header:
	['glottocode', 'name', 'isocodes', 'level', 'macroarea', 'latitude', 'longitude']
	['3adt1234', '3Ad-Tekles', '', 'dialect', 'Africa', '', '']
	['aala1237', 'Aalawa', '', 'dialect', 'Papunesia', '', '']
	"""
	# =========================================================================
	# Read Glottolog (Languages and Dialects) Data
	def read_glottolog_ld_data(input_file):
		csv_glotto_langdial = read_csv_file(input_file, '', ',', '"')
		#print(f'Glottolog Languages and Dialects:')
		#print(csv_glotto_langdial[0])
		#print(csv_glotto_langdial[1])
		#print(csv_glotto_langdial[2])
		return csv_glotto_langdial
	
	# =========================================================================
	# Filter Glottolog (Languages and Dialects) Data for Information
	def filter_glottolog_ld_data(dialect_info_dict, csv_glotto_langdial):
		for lang_key in dialect_info_dict.keys():
			for entry in csv_glotto_langdial:
				# Name in Glottolog == Input term
				if entry[1] == lang_key:
					dialect_info_dict[lang_key]["glottocode_ld"] = entry[0]
					dialect_info_dict[lang_key]["isocode_ld"] = entry[2]
					dialect_info_dict[lang_key]["level_ld"] = entry[3]
					dialect_info_dict[lang_key]["macroarea_ld"] = entry[4]
					dialect_info_dict[lang_key]["latitude_ld"] = entry[5]
					dialect_info_dict[lang_key]["longitude_ld"] = entry[6]
		return dialect_info_dict
		""" New Information in dialect_info_dict
		original_term, glottocode_ld, isocode_ld, level_ld, macroarea_ld, latitude_ld, longitude_ld
		Southern Kurdish, sout2640, sdh, language, Eurasia, 32.8977, 46.5976
		Central Kurdish, original_term2, cent1972, ckb, language, Eurasia, 35.6539, 46.5976
		Northern Kurdish, nort2641, kmr, language, Eurasia, 37, 43
		"""

	# =========================================================================
	# languages.csv
	""" Header:
	['ID', 'Name', 'Macroarea', 'Latitude', 'Longitude', 'Glottocode', 'ISO639P3code', 'Countries', 'Family_ID', 'Language_ID', 'Closest_ISO369P3code', 'First_Year_Of_Documentation', 'Last_Year_Of_Documentation']
	['fuln1247', 'Fulniô', 'South America', '-9.02591', '-37.1402', 'fuln1247', 'fun', 'BR', '', '', 'fun', '', '']
	['demm1245', 'Dem', 'Papunesia', '-3.72183', '137.632', 'demm1245', 'dem', 'ID', '', '', 'dem', '', '']
	"""
	# =========================================================================
	# Read Glottolog (Languages) Data
	def read_glottolog_l_data(input_file):
		csv_glotto_lang = read_csv_file(input_file, '', ',', '"')
		#print(f'Glottolog Languages:')
		#print(csv_glotto_lang[0])
		#print(csv_glotto_lang[1])
		#print(csv_glotto_lang[2])
		return csv_glotto_lang

	# =========================================================================
	# Filter Glottolog (Languages) Data for Information
	def filter_glottolog_l_data(dialect_info_dict, csv_glotto_lang):
		for lang_key in dialect_info_dict.keys():
			for entry in csv_glotto_lang:
				# Name in Glottolog == Input term OR ID in Glottolog == above added glottocode_ld
				# NOTE: The first case searches for names just as before, 
				#		the second case double checks for varying orthographies via use of glottocode
				if entry[1] == lang_key:
					dialect_info_dict[lang_key]["id_l"] = entry[0]
					dialect_info_dict[lang_key]["macroarea_l"] = entry[2]
					dialect_info_dict[lang_key]["latitude_l"] = entry[3]
					dialect_info_dict[lang_key]["longitude_l"] = entry[4]
					dialect_info_dict[lang_key]["glottocode_l"] = entry[5]
					dialect_info_dict[lang_key]["isocode_l"] = entry[6]
					dialect_info_dict[lang_key]["countries_l"] = entry[7]
					dialect_info_dict[lang_key]["familyid_l"] = entry[8]
					dialect_info_dict[lang_key]["languageid_l"] = entry[9]
					dialect_info_dict[lang_key]["closestisocode_l"] = entry[10]
				elif "glottocode_ld" in dialect_info_dict[lang_key]:
					if entry[0] == dialect_info_dict[lang_key]["glottocode_ld"]:
						dialect_info_dict[lang_key]["id_l"] = entry[0]
						dialect_info_dict[lang_key]["macroarea_l"] = entry[2]
						dialect_info_dict[lang_key]["latitude_l"] = entry[3]
						dialect_info_dict[lang_key]["longitude_l"] = entry[4]
						dialect_info_dict[lang_key]["glottocode_l"] = entry[5]
						dialect_info_dict[lang_key]["isocode_l"] = entry[6]
						dialect_info_dict[lang_key]["countries_l"] = entry[7]
						dialect_info_dict[lang_key]["familyid_l"] = entry[8]
						dialect_info_dict[lang_key]["languageid_l"] = entry[9]
						dialect_info_dict[lang_key]["closestisocode_l"] = entry[10]
				else:
					pass
		return dialect_info_dict
		""" New Information in dialect_info_dict
		original_term, id_l, macroarea_l, latitude_l, longitude_l, glottocode_l, isocode_l, countries_l, familyid_l, languageid_l, closestisocode_l
		Southern Kurdish, sout2640, Eurasia, 32.8977, 46.5976, sout2640, sdh, IQ;IR, indo1319, , sdh
		Central Kurdish, cent1972, Eurasia, 35.6539, 46.5976, cent1972, ckb, IQ;IR, indo1319, , ckb
		Northern Kurdish, nort2641, Eurasia, 37, 43, nort2641, kmr, AM;AZ;IQ;IR;JO;KW;SY;TM;TR, indo1319, , kmr
		"""

	

	""" 
	===========================================================================
	Ethnologue Data
	===========================================================================
	INPUT: 	A list of terms associated with language varieties + additional data
		   	such as ISO codes acquired in the step above.
	OUTPUT: Additional information for each of these terms that is contained
			in the Glottolog data, such as ISO codes used further below
	"""

	# =========================================================================
	# Select already known language codes to guide exploration
	def select_iso_codes(dialect_info_dict):
		known_iso_codes = []
		for lang_key in dialect_info_dict.keys():
			lang_id = "None"
			# If the first glottolog-query resulted in an ISO code
			if "isocode_ld" in dialect_info_dict[lang_key]:
				if not dialect_info_dict[lang_key]["isocode_ld"] == '':
					lang_id = dialect_info_dict[lang_key]["isocode_ld"]
			# If the second glottolog-query resulted in an ISO code
			elif "isocode_l" in dialect_info_dict[lang_key]:
				if not dialect_info_dict[lang_key]["isocode_l"] == '':
					lang_id = dialect_info_dict[lang_key]["isocode_l"]
			# If there was only a "closest" ISO code to be found
			elif "closestisocode_l" in dialect_info_dict[lang_key]:
				if not dialect_info_dict[lang_key]["closestisocode_l"] == '':
					lang_id = dialect_info_dict[lang_key]["closestisocode_l"]
			else:
				pass
				
			known_iso_codes.append(lang_id)
		# Debugging
		#print(f'Currently known ISO codes: {known_iso_codes}')
		known_iso_codes = list(set(known_iso_codes))

		# NOTE: This check only became necessary once I used the output (35 varieties) from the German input (3 varieties)
		if "None" in known_iso_codes:
			known_iso_codes.remove("None")
		print(f'Currently known unique ISO codes: {known_iso_codes}')

		# Dictionary to hold new items from ethnologue
		dialect_info_dict_ethno = {} 

		# Fill the known ISO codes into the dictionary to start Ethnologue look-up
		for iso_code in known_iso_codes:
			dialect_info_dict_ethno[iso_code] = {}

		return dialect_info_dict_ethno


	# LanguageIndex.tab
	""" Header:
	['LangID', 'CountryID', 'NameType', 'Name']
	['aaa', 'NG', 'L', 'Ghotuo']
	['aaa', 'NG', 'LA', 'Otuo']

	LangID, CountryID, NameType, Name
	kmr	AM	L	Kurdish, Northern
	kmr	AZ	L	Kurdish, Northern
	...
	kmr	IR	D	Northern Kurdish
	"""
	# =========================================================================
	# Read Ethnologue (Language Index) Data
	def read_ethnologue_li(input_eth_languageindex):
		csv_ethno_langindex = read_csv_file(input_eth_languageindex, '', '\t', '"')
		#print(f'Ethnologue Language Index:')
		#print(csv_ethno_langindex[0])
		#print(csv_ethno_langindex[1])
		#print(csv_ethno_langindex[2])
		return csv_ethno_langindex
		
	# =========================================================================
	# Filter Ethnologue (Language Index) Data
	def filter_ethnologue_li(dialect_info_dict_ethno, csv_ethno_langindex):
		for iso_code in dialect_info_dict_ethno.keys():
			for entry in csv_ethno_langindex:
				# For each entry in the ethno_language_index data
				if entry[0] == iso_code:
					# Item for each language name to hold the CountryID and NameType
					#lang_iso = entry[0]
					lang_country = entry[1]
					lang_type = entry[2]
					lang_name = entry[3]
					
					# Simply add new information if item for this Name already exists
					if lang_name in dialect_info_dict_ethno[iso_code]:
						dialect_info_dict_ethno[iso_code][lang_name][lang_country] = lang_type
					
					# Create new item with Name from entry if not exists
					else:
						dialect_info_dict_ethno[iso_code][lang_name] = {}
						dialect_info_dict_ethno[iso_code][lang_name][lang_country] = lang_type
		return dialect_info_dict_ethno
		""" New Information in dialect_info_dict_ethno
		"kmr":{
			"Kurdish, Northern": {
				"AM":"L",
				"AZ":"L", ...
			}, ...
		},
		"ckb": {
			"Kurdish, Central": {
				"IQ":"L", ...
			}, ...
		}, ...
		"""


	
	""" 
	dialect_info_dict = {
		"Central Kurdish": {
			"key":"item", ...
		},
		"Sorani": {
			"key":"item", ...
		}, ...
	}

	dialect_info_dict_ethno_country = {
		"hac": {
			"Kakai": {
				"IQ": "D"
			}.
			"Zengana": {
				"IQ": "D"
			}, ...
		},
		"kmr": {
			"Kurdish, Northern": {
				"AM": "L", ...
			}, ...
		}, ...
	}
	"""

	# =========================================================================
	# Filter Ethnologue Names and Original Names to find new Language Names
	def filter_ethno_new(dialect_word_list, dialect_info_dict_ethno_country):
		known_lang_names = dialect_word_list
		#print(f'Known Language Names: {known_lang_names}')
		#for lang_name in dialect_info_dict.keys():
		#	known_lang_names.append(lang_name)

		new_lang_names = []
		for iso_code in dialect_info_dict_ethno_country.keys():
			for lang_name in dialect_info_dict_ethno_country[iso_code].keys():
				new_lang_names.append(lang_name)
		
		# Keep unique names and remove already known names
		new_lang_names = list(set(new_lang_names))
		for known_name in known_lang_names:
			if known_name in new_lang_names:
				new_lang_names.remove(known_name)

		return new_lang_names


	# CountryCodes.tab
	""" Header:
	['CountryID', 'Name', 'Area']
	['AD', 'Andorra', 'Europe']
	['AE', 'United Arab Emirates', 'Asia']
	"""
	# =========================================================================
	# Read Ethnologue (Country ID) Data
	def read_etnologue_ci(input_eth_countrycodes):
		csv_ethno_country = read_csv_file(input_eth_countrycodes, '', '\t', '"')
		#print(f'Ethnologue Country Codes:')
		#print(csv_ethno_country[0])
		#print(csv_ethno_country[1])
		#print(csv_ethno_country[2])
		return csv_ethno_country
		"""
		CountryID, Name, Area
		IR	Iran	Asia
		SY	Syria	Asia
		"""
	


	# LanguageCodes.tab
	""" Header:
	['LangID', 'CountryID', 'LangStatus', 'Name']
	['aaa', 'NG', 'L', 'Ghotuo']
	['aab', 'NG', 'L', 'Arum']
	"""
	# =========================================================================
	# Read Ethnologue (Language Codes) Data
	def read_ethnologue_lc(input_eth_languagecodes):
		csv_ethno_langcode = read_csv_file(input_eth_languagecodes, '', '\t', '"')
		print(f'Ethnologue Language Codes:')
		print(csv_ethno_langcode[0])
		print(csv_ethno_langcode[1])
		print(csv_ethno_langcode[2])
		return csv_ethno_langcode
		"""
		LangID, CountryID, LangStatus, Name
		kmr	TR	L	Kurdish, Northern
		ckb	IQ	L	Kurdish, Central
		sdh	IR	L	Kurdish, Southern
		"""

	
	



	""" 
	===========================================================================
	Execution of Script
	===========================================================================
	"""
	# Input Language Terms
	dialect_word_list = read_language_names(input_path)
	dialect_info_dict = word_list_to_dict(dialect_word_list)

	# Glottolog Data
	csv_glotto_langdial = read_glottolog_ld_data(input_glo_languagesanddialectsgeo)
	dialect_info_dict = filter_glottolog_ld_data(dialect_info_dict, csv_glotto_langdial)
	csv_glotto_lang = read_glottolog_l_data(input_glo_languages)
	dialect_info_dict = filter_glottolog_l_data(dialect_info_dict, csv_glotto_lang)

	# ISO Codes from Glottolog
	dialect_info_dict_ethno_country = select_iso_codes(dialect_info_dict)

	# Ethnologue Data
	csv_ethno_langindex = read_ethnologue_li(input_eth_languageindex)
	dialect_info_dict_ethno_country = filter_ethnologue_li(dialect_info_dict_ethno_country, csv_ethno_langindex)


	# NOTE: Writing of intermediate files for manual checking of functionalities
	# Serializing jsons and write to files
	json_object = json.dumps(dialect_info_dict, indent=4)
	output_json = f'{inter_path}dialect_info_dict_intermediate.json'
	with open(output_json, "w") as outfile:
		outfile.write(json_object)

	json_object = json.dumps(dialect_info_dict_ethno_country, indent=4)
	output_json = f'{inter_path}dialect_country_dict_intermediate.json'
	with open(output_json, "w") as outfile:
		outfile.write(json_object)


	# Filter new language names found in Ethnologue Data
	new_lang_names = filter_ethno_new(dialect_word_list, dialect_info_dict_ethno_country)
	new_lang_dict = word_list_to_dict(new_lang_names)

	# TODO: Turn into loop until no new language names are found(?)
	dialect_info_dict_new = filter_glottolog_ld_data(new_lang_dict, csv_glotto_langdial)
	dialect_info_dict_new = filter_glottolog_l_data(dialect_info_dict_new, csv_glotto_lang)
	dialect_info_dict_ethno_country_new = select_iso_codes(new_lang_dict)
	dialect_info_dict_ethno_country_new = filter_ethnologue_li(dialect_info_dict_ethno_country_new, csv_ethno_langindex)

	# Serializing jsons and write to files
	json_object = json.dumps(dialect_info_dict_new, indent=4)
	output_json = f'{inter_path}dialect_info_dict_new.json'
	with open(output_json, "w") as outfile:
		outfile.write(json_object)

	json_object = json.dumps(dialect_info_dict_ethno_country_new, indent=4)
	output_json = f'{inter_path}dialect_country_dict_new.json'
	with open(output_json, "w") as outfile:
		outfile.write(json_object)

	# TODO: Handle these files for more info
	#csv_ethno_country = read_etnologue_ci(input_eth_countrycodes)
	#csv_ethno_langcode = read_ethnologue_lc(input_eth_languagecodes)


	# Merge intermediate dictionaries wie new dictionaries into output files
	# NOTE: The second list is merged into the first list and no new list is created. 
	dialect_info_dict_out = dialect_info_dict
	dialect_info_dict_out.update(dialect_info_dict_new)

	dialect_info_dict_ethno_country_out = dialect_info_dict_ethno_country
	dialect_info_dict_ethno_country_out.update(dialect_info_dict_ethno_country_new)

	# Serializing jsons and write to files
	# All the country information from Ethnologue
	json_object = json.dumps(dialect_info_dict_ethno_country_out, indent=4)
	output_json = f'{output_path}dialect_country_dict.json'
	with open(output_json, "w") as outfile:
		outfile.write(json_object)

	# All found information from Glottolog
	json_object = json.dumps(dialect_info_dict_out, indent=4)
	output_json = f'{output_path}dialect_info_dict_extra.json'
	with open(output_json, "w") as outfile:
		outfile.write(json_object)

	# =========================================================================
	# Select specific information for output dialect dictionary
	dialect_info_dict_selected = {}
	# Add basic information for dictionary file
	project_name = args.proj
	current_date = date.today()
	current_date = current_date.strftime("%d.%m.%Y")
	base_information = {
		"projectName":project_name,
        "date":current_date
	}
	dialect_info_dict_selected["information"] = base_information 
	dialect_info_dict_selected["dialects"] = {}

	for lang_name in dialect_info_dict_out.keys():
		
		# Add information for each item
		new_lang_item = {"languageInformation":{}}

		# First, check if this key is in the item
		if "isocode_ld" in dialect_info_dict_out[lang_name]:
			# Then, check if it is not empty
			if not dialect_info_dict_out[lang_name]["isocode_ld"] == '':
				new_lang_item["languageInformation"]["iso639"] = dialect_info_dict_out[lang_name]["isocode_ld"]
			# NOTE: Seems unnecessary to also include "closest iso code" at this point.
			#elif "closestisocode_l" in dialect_info_dict_out[lang_name]:
			#	if not dialect_info_dict_out[lang_name]["closestisocode_l"]:
			#		new_lang_item["languageInformation"]["iso639"] = dialect_info_dict_out[lang_name]["closestisocode_l"]
		#elif "closestisocode_l" in dialect_info_dict_out[lang_name]:
		#	new_lang_item["languageInformation"]["iso639Closest"] = dialect_info_dict_out[lang_name]["closestisocode_l"]
		if "latitude_ld" in dialect_info_dict_out[lang_name]:
			if not dialect_info_dict_out[lang_name]["latitude_ld"] == '':
				new_lang_item["languageInformation"]["latitude"] = dialect_info_dict_out[lang_name]["latitude_ld"]
		if "latitude_l" in dialect_info_dict_out[lang_name]:
			new_lang_item["languageInformation"]["latitude"] = dialect_info_dict_out[lang_name]["latitude_l"]
		if "longitude_ld" in dialect_info_dict_out[lang_name]:
			if not dialect_info_dict_out[lang_name]["longitude_ld"] == '':
				new_lang_item["languageInformation"]["longitude"] = dialect_info_dict_out[lang_name]["longitude_ld"]
		if "longitude_l" in dialect_info_dict_out[lang_name]:
			if not dialect_info_dict_out[lang_name]["longitude_l"] == '':
				new_lang_item["languageInformation"]["longitude"] = dialect_info_dict_out[lang_name]["longitude_l"]
		if "level_id" in dialect_info_dict_out[lang_name]:
			new_lang_item["languageInformation"]["level"] = dialect_info_dict_out[lang_name]["level_id"]
		if "countries_l" in dialect_info_dict_out[lang_name]:
			if not dialect_info_dict_out[lang_name]["countries_l"] == '':
				new_lang_item["languageInformation"]["countries"] = dialect_info_dict_out[lang_name]["countries_l"]
		if "glottocode_ld" in dialect_info_dict_out[lang_name]:
			if not dialect_info_dict_out[lang_name]["glottocode_ld"] == '':
				new_lang_item["languageInformation"]["glottocode"] = dialect_info_dict_out[lang_name]["glottocode_ld"]

		dialect_info_dict_selected["dialects"][lang_name] = new_lang_item

	# Number of dialects in the output dictionary
	number_of_keys_in_dict = len(dialect_info_dict_selected["dialects"].keys())
	dialect_info_dict_selected["information"]["dialects"] = number_of_keys_in_dict

	# Number of dialects in the output dictionary that have additional information
	number_of_keys_in_dict_with_info = 0
	for dialect_key in dialect_info_dict_selected["dialects"].keys():
		current_dialect_item_length = len(dialect_info_dict_selected["dialects"][dialect_key]["languageInformation"])
		if current_dialect_item_length > 0:
			number_of_keys_in_dict_with_info += 1
	
	dialect_info_dict_selected["information"]["dialects_with_info"] = number_of_keys_in_dict_with_info

	#for key in dialect_info_dict_selected.keys():
	#	print(key)
		# → "information" and "dialects"
	#for key in dialect_info_dict_selected["dialects"].keys():
	#	print(type(dialect_info_dict_selected["dialects"][key]))
		# → <class 'dict'>
	#print(type(dialect_info_dict_selected))
	# → <class 'dict'>
	#print(dialect_info_dict_selected)
	#sys.exit()
		
		
	# Selected information for each language name
	json_object = json.dumps(dialect_info_dict_selected, indent=4)
	output_json = f'{output_path}dialect_info_dict.json'
	with open(output_json, "w") as outfile:
		outfile.write(json_object)

	# Create a simple list of all language names and write to file
	# NOTE: For original names from input and new ones for comparison
	lang_name_list = []
	for lang_name in dialect_info_dict_out.keys():
		lang_name_list.append(lang_name)
	with open(f'{output_path}dialect_info_list_output.txt', "w") as outfile:
		for name in lang_name_list:
			outfile.write(name.replace('\n','')+'\n')
	with open(f'{output_path}dialect_info_list_input.txt', "w") as outfile:
		for name in dialect_word_list:
			outfile.write(name.replace('\n','')+'\n')
	



	
if __name__ == "__main__":
	
	main()