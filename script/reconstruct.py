
#===============================================================================
# Sanity checker 
# Reconstructs a prior utterances of a dialog from sentence ids
# Replace FILE_NAME with the desired json file in the /out directory

import os
import json
import pprint

DIR_PATH = os.path.dirname(os.path.abspath(__file__))+'/../out/'
FILE_NAME ='example_test.json'

EXAMPLES = []
LEGEND = []

def parse_dialog(_dlog):
	print('===================================================================')
	print('===================================================================')
	prior = _dlog['x_prior_utterances']
	for p in prior:
		print(p['role'],'['+p['oriSenId']+']',LEGEND[p['oriSenId']])
	return

def main():
	global LEGEND, EXAMPLES

	with open(DIR_PATH + FILE_NAME) as json_file:
		data = json.load(json_file)
		LEGEND = data['Sen_Legend']
		EXAMPLES = data['Set_Examples']
	for e in EXAMPLES:
		parse_dialog(e)

if __name__ == "__main__":
	main()
