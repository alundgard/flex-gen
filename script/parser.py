
#===============================================================================
# Flex Dataset Generator

import os
import sys
import json
import math
import copy
import random
import pprint
import pickle
import hashlib
import params as p
import operator as op

#===============================================================================
# GLOBALS & PARAMS

SEN_LEGEND = {} # Stores sentence id to sentence mapping
NER_LEGEND = {} # Stores sentence id to ner output mapping
NER_LOOKUP = {} # Loads ner pickle
SET_ALREADY = [] # Stores examples already generated
ALL_DLOGS = [] # Stores all dialogs

TRAIN_SET_SZ = p.TRAIN_SET_SZ # Num of train examples to generate
TEST_SET_SZ = p.TEST_SET_SZ # Num of test examples to generate

PARA_BAG_SZ = p.PARA_BAG_SZ # Num of utterances per para bag
WITH_PARA_SAMPLE = p.WITH_PARA_SAMPLE # If true, replace orig dialog with paras

# If true, test para bag filled w/ train+test utterances
# If false, test para bag filled w/ only test utterances
FILL_WITH_BOTH = p.FILL_WITH_BOTH

SET_NAME = p.SET_NAME # Name of output set
RAND_SEED = 3 # Assign for debugging
# random.seed(RAND_SEED) # Debug only

TEST_DOC_SZ = p.TEST_DOC_SZ # Hold out for test set
TRAIN_DOC_SZ = None # Depends on num dlogs

TEST_DOC_I = None # List of test doc indices
TRAIN_DOC_I = None # List of train doc indices

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = DIR_PATH + '/../out/'
RAW_DAT_PATH = DIR_PATH + '/../raw/'
RAW_DAT_FILE = RAW_DAT_PATH+'RawFlexData.json'

################################################################################
################################################################################
####                                                                        ####
####                         GENERATOR FUNCTIONS                            ####
####                                                                        ####
################################################################################
################################################################################

#===============================================================================
# returns list of original sentence and its paraphrases
# _turn is a dict with keys paraphrases, oriSen, oriSenId
def paras_plus_one(_turn):
	return  [{'paraId':_turn['oriSenId']}] + _turn['paraphrases']

#===============================================================================
# gets a random advisor query from a given dlog
def random_advisor_query(_dlog_content):
		_ais = range(len(_dlog_content))
		_aq = [ai for ai in _ais if _dlog_content[ai]['role'] == 'ADVISOR']
		idx = pick_1_randomly_neq(_aq, None)
		return idx, _dlog_content[idx]

#===============================================================================
# checks if dlog has any admissible advisor queries
def advisor_query_exists(_dlog_content):
	for d in _dlog_content:
		if d['role'] == 'ADVISOR':
			return True
	return False

#===============================================================================
# returns list of admissible doc ids for indexing ALL_DLOGS
# depends on whether generating train or test sets
# depends on whether FILL_WITH_BOTH is true or false
def find_admissible_docs(_train_or_test):
	if _train_or_test == 'Train':
		return TRAIN_DOC_I
	elif _train_or_test == 'Test':
		if FILL_WITH_BOTH:
			return TRAIN_DOC_I + TEST_DOC_I
		else:
			return TEST_DOC_I
	else:
		print('Error! Invalid input')
		sys.exit()
	return

#===============================================================================
# fills up a bag of paraphrases size PARA_BAG_SZ
# _correct is list of correct elements to put in bag 
# _admissible is list of admissible dlog indices to ALL_DLOGS
# _curr_dlog is index of dlog to omit from bag
def fill_bag_size_N(_correct, _curr_dlog, _admissible):
	
	# check if para bag size is smaller than num of paras
	if (len(_correct) >= PARA_BAG_SZ):
		return _correct[0:PARA_BAG_SZ]

	# otherwise, fill the bag
	bag = [] + _correct
	while (len(bag) < PARA_BAG_SZ):

		# get random dlog idx
		idx = pick_1_randomly_neq(_admissible, _curr_dlog)

		# get dlog content
		dlog = ALL_DLOGS[idx]['content']

		#~~ DATASET CHECK~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		# check that advisor query exists in the dlog
		if (not advisor_query_exists(dlog)):
			continue
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		# get random advisor query
		i, aq = random_advisor_query(dlog)

		#~~ DATASET CHECK~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		# check that paraphrases exist
		if ('paraphrases' not in aq):
			continue
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

		# get paraphrases plus orig query		
		dp = paras_plus_one(aq)

		# get n random paras
		dp = pick_n_randomly(dp)

		# how many will fit in the bag?
		num2put = min(PARA_BAG_SZ-len(bag),len(dp))

		# update the bag
		bag = bag + dp[0:num2put]

	assert(len(bag) == PARA_BAG_SZ)
	return bag

#===============================================================================
# returns a single example, or False if dialog inadmissible
def generate_example(_type, _train_idx):
	global SET_ALREADY

	# pick random index i from _train_idx
	di = pick_1_randomly_neq(_train_idx, None)

	# get dialog d from ALL_DLOGS[i]
	d = ALL_DLOGS[di]['content']

	#~~ DATASET CHECK~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# check that advisor query exists in the dlog
	if (not advisor_query_exists(d)):
		return False
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	# pick random advisor query (aq) from d (and its index i)
	# note! omitting cases where there are no prior utterances
	i = 0
	while (not i):
		i, aq = random_advisor_query(d)

	# get prior utterances (pu) up to but excluding aq
	pu = copy.deepcopy(d[0:i])

	# remove extra information from pu / replace with paras
	# note! if WITH_PARA_SAMPLE, replace random prior with a paraphrase
	for u in pu:
		if 'paraphrases' in u:
			# replace rand prior utterances with their paraphrases
			if (WITH_PARA_SAMPLE and bool(random.getrandbits(1))):
				repl_para = pick_1_randomly_neq(u['paraphrases'], None)
				u['oriSenId'] = repl_para['paraId']
			del u['paraphrases']

	#~~ DATASET CHECK~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# check that paraphrases exist
	if ('paraphrases' not in aq):
		return False
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	# check that it is not already in set
	jpu = json.dumps(pu, sort_keys = True).encode('utf-8')

	# hash it
	hsh_md5 = hashlib.md5(jpu).hexdigest()

	# check that it is not already in set
	if hsh_md5 in SET_ALREADY:
		return False

	# stash it
	SET_ALREADY.append(hsh_md5)

	# get correct paraphrase set (gt) for aq
	paras = aq['paraphrases']
	gt = pick_n_randomly(paras)[:-1] # remove one
	gt = [{'paraId':aq['oriSenId']}] + gt
	if (len(gt) >= PARA_BAG_SZ):
		gt = gt[0:PARA_BAG_SZ]

	# find admissible set of docs
	didx = find_admissible_docs(_type)

	# generate bag of paraphrases size PARA_BAG_SZ
	pb = fill_bag_size_N(gt, di, _train_idx)

	# shuffle para bag
	random.shuffle(pb)

	'''
	print('-----------------------------------------------------------')
	print('--- PRIOR UTTERANCES')
	pprint.pprint(pu)
	print('-----------------------------------------------------------')
	print('--- PARAPHRASE BAG')
	pprint.pprint(pb)
	print('-----------------------------------------------------------')
	print('--- CORRECT PARAPHRASES')
	pprint.pprint(gt)
	'''

	# save example as json
	example = json.dumps({
		'x_prior_utterances': pu,
		'y_paraphrase_bag': pb,
		'y_correct_paras': gt
	}, sort_keys = True).encode('utf-8')

	return example

#===============================================================================
# generate the train/test set
def generate_set(_tt, _tt_idx):
	global SET_ALREADY

	print('------------------------------------')
	print('Generating set: ', _tt)

	GEN_SET = [] # the set currently being generated
	SET_ALREADY = [] # hash examples already generated

	if _tt == 'Train':
		SZ_2_GEN = TRAIN_SET_SZ
	if _tt == 'Test':
		SZ_2_GEN = TEST_SET_SZ

	while len(GEN_SET) < SZ_2_GEN:

		# generate new example
		new_example = generate_example(_tt, _tt_idx)

		# if new example is admissible
		if(new_example):

			# save it
			new = json.loads(new_example)
			GEN_SET = GEN_SET + [new]

			# show progress
			sys.stdout.write("Num examples generated: %d\r" % (len(GEN_SET)))
			sys.stdout.flush()

	print('\n') # for pretty output

	# save it
	save_set(_tt, GEN_SET)
	return

################################################################################
################################################################################
####                                                                        ####
####                           HELPER FUNCTIONS                             ####
####                                                                        ####
################################################################################
################################################################################

#===============================================================================
# returns n elements randomly selected from list
# n is also random
def pick_n_randomly(_l):
	return random.sample(_l,random.choice(range(len(_l))))


#===============================================================================
# returns one elements randomly selected from list _l, not equal to _omit
def pick_1_randomly_neq(_l, _omit):
	o = random.choice(_l)
	if (not _omit):
		return o
	while (o == _omit):
		o = random.choice(_l)
	return o

#===============================================================================
# ncr
def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom

################################################################################
################################################################################
####                                                                        ####
####                           SETUP FUNCTIONS                              ####
####                                                                        ####
################################################################################
################################################################################

#===============================================================================
# combines all dlog batches into a single list
def combine_all_dialogs(_RAW_DAT_FILE):
	global ALL_DLOGS # update global
	with open(_RAW_DAT_FILE) as json_file:
		data = json.load(json_file)
		for batch in data:
			ALL_DLOGS = ALL_DLOGS + batch['data']
	print('------------------------------------')
	print('Total number of dialogs: ', len(ALL_DLOGS))
	return

#===============================================================================
# splits dlogs into train/test before generating examples
def partition_train_test_docs():
	num_dlog = len(ALL_DLOGS)
	indices = [i for i in range(num_dlog)]
	random.shuffle(indices)

	tr_sz = num_dlog - TEST_DOC_SZ # num training docs
	train_idx, test_idx = indices[:tr_sz], indices[tr_sz:]

	print('Num dialogs used for train set generation: ',len(train_idx))
	print('Num dialogs used for test set generation: ',len(test_idx))

	return train_idx, test_idx

#===============================================================================
# saves the generated set to /out directory
def save_set(_tt, _GEN_SET):
	if _tt == 'Train':
		name = SET_NAME+'_train.json'
	if _tt =='Test':
		name = SET_NAME+'_test.json'

	# print('Size of set: ', len(_GEN_SET))
	print('Saving as', name)
	OUT = {
		"Sen_Legend" : SEN_LEGEND,
		"Ner_Legend" : NER_LEGEND,
		"Set_Examples" : _GEN_SET
	}
	with open(SAVE_PATH + name, 'w') as outfile:
	    json.dump(OUT, outfile, indent=4, separators=(',', ': '))
	return

#===============================================================================
# generates SEN_LEGEND dict key = sentenceId, value = sentenceString
def generate_sen_legend():
	global SEN_LEGEND

	for dlog in ALL_DLOGS:
		for d in dlog['content']:
			assert(d['oriSenId'] not in SEN_LEGEND)
			SEN_LEGEND[d['oriSenId']] = d['oriSen']
			for p in d['paraphrases']:
				assert(p['paraId'] not in SEN_LEGEND)
				SEN_LEGEND[p['paraId']] = p['para']
	# pprint.pprint(LEGEND)
	with open(SAVE_PATH + '/../_Sen_Legend.json', 'w') as outfile:
	    json.dump(SEN_LEGEND, outfile, indent=4, separators=(',', ': '))
	return

#===============================================================================
# generates NER_LEGEND dict key = sentenceId, value = nerOutput
def generate_ner_legend():
	global NER_LEGEND
	load_ner_lookup()
	for key, value in SEN_LEGEND.items():
		NER_LEGEND[key] = (lookup_ner(value))
	with open(SAVE_PATH + '/../_Ner_Legend.json', 'w') as outfile:
	    json.dump(NER_LEGEND, outfile, indent=4, separators=(',', ': '))
	return

#===============================================================================
# 
def load_ner_lookup():
	global NER_LOOKUP
	with open(RAW_DAT_PATH + 'ner_lookup.pkl', 'rb') as f:
		NER_LOOKUP = pickle.load(f)
	return

#===============================================================================
# 
def lookup_ner(text):
    if text in NER_LOOKUP:
        return NER_LOOKUP[text]
    else:
        return None, None, None, None, None

#===============================================================================
# generates LEGEND dict key = sentenceId, value = sentenceString

#===============================================================================
# removes sentence strings from ALL_DLOGS, keeps sentence ids
def scrub_strings():
	global ALL_DLOGS

	for dlog in ALL_DLOGS:
		for d in dlog['content']:
			del d['oriSen']
			for p in d['paraphrases']:
				del p['para']
	return

#===============================================================================
# print basic stats
def data_stats(_all_doc_i, _tt):
	# print('====================================================================')
	# print('STATS FOR THE '+ _tt +' PARTITION')
	tot_adv_query = 0
	tot_para = 0
	tot_utterance = 0
	for i in _all_doc_i:
		doc = ALL_DLOGS[i]['content']
		tot_utterance = tot_utterance + len(doc)
		for i, d in enumerate(doc):
			tot_para = tot_para + len(d['paraphrases'])
			if d['role'] == 'ADVISOR' and i != 0:
				tot_adv_query = tot_adv_query + 1
	# print('\tTotal number of utterances: ', tot_utterance)
	# print('\tTotal number of paraphrases: ', tot_para)
	# print('\tTotal number of advisor queries: ', tot_adv_query)
	return tot_adv_query

#===============================================================================
# print current settings
def current_settings():
	print('Running with settings:')
	print('trainsize=',TRAIN_SET_SZ)
	print('testsize=',TEST_SET_SZ) 
	print('withpara=',WITH_PARA_SAMPLE)
	print('bagsize=',PARA_BAG_SZ)
	print('setname=',SET_NAME)
	print('numhold=',TEST_DOC_SZ)
	print('fillwboth=',FILL_WITH_BOTH)
	return

#===============================================================================
# startup set generation
def start():
	global TRAIN_DOC_I, TEST_DOC_I

	current_settings()
	combine_all_dialogs(RAW_DAT_FILE)
	TRAIN_DOC_I, TEST_DOC_I = partition_train_test_docs()
	
	tr_aq = data_stats(TRAIN_DOC_I, 'TRAIN')
	te_aq =data_stats(TEST_DOC_I, 'TEST')
	all_aq = data_stats(TRAIN_DOC_I+TEST_DOC_I, 'ALL')

	# check that requested sizes do not exceed theoretical bound
	if (not WITH_PARA_SAMPLE and (TRAIN_SET_SZ > tr_aq or TEST_SET_SZ > te_aq)):
		print('Abort! Your requested set sizes exceed the maximun possible.')
		print('Requested train size: ', TRAIN_SET_SZ, ' Max possible: ', tr_aq)
		print('Requested test size: ', TEST_SET_SZ, ' Max possible: ', te_aq)
		sys.exit()

	generate_sen_legend() # Fill in sen mapping
	generate_ner_legend() # Fill in ner mapping
	scrub_strings() # Get rid of strings

	generate_set('Train', TRAIN_DOC_I) # Gen train
	generate_set('Test', TEST_DOC_I) # Gen test

	print('------------------------------------')
	print('.:: Finished.')
	return


if __name__ == "__main__":
	start()
