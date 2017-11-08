#
# Flex Generator 
#

import os
import json
import random
import pprint
import params as p

ALL_DLOGS = [] # All dialogs

TRAIN_SET_SZ = p.TRAIN_SET_SZ # Num of train examples to generate
TEST_SET_SZ = p.TEST_SET_SZ # Num of test examples to generate
PARA_BAG_SZ = p.PARA_BAG_SZ # Num of utterances per para bag

WITH_PARA_SAMPLE = p.WITH_PARA_SAMPLE # If true, replace orig dialog with paraphrases
NUM_PARA_SAMPLE= p.NUM_PARA_SAMPLE # Num examples generated by replacing w/ paraphrases

DEBUG = p.DEBUG
RAND_SEED = p.RAND_SEED
random.seed(RAND_SEED)

RAW_DAT_PATH = os.path.dirname(os.path.abspath(__file__))+'/../raw/'
RAW_DAT_FILE = RAW_DAT_PATH+'RawFlexData.json'

TRAIN_SET = []
TEST_SET = []
SET_ALREADY = [] # list of 'oriSenId' (keeps track of examples already generated)

#===============================================================================
# returns n elements randomly selected from list
# n is also random
def pick_n_randomly(_l):
	_lis = [i for i in range(len(_l))] # indices of list
	n = random.choice(_lis) # randomly select n indices
	random.shuffle(_lis) # random shuffle indices
	return [_l[i] for i in _lis[0:n]] # return list of n random

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
# returns list of original sentence and its paraphrases
# _turn is a dict with keys paraphrases, oriSen, oriSenId
def paras_plus_one(_turn):
	return _turn['paraphrases'] + [{
				'oriSen':_turn['oriSen'],
				'oriSenId':_turn['oriSenId']}]

#===============================================================================
# fills up a bag of paraphrases size PARA_BAG_SZ
# _correct is list of correct elements to put in bag 
# _admissible is list of admissible dlog indices to ALL_DLOGS
# _curr_dlog is index of dlog to omit from bag
def fill_bag_size_N(_correct, _curr_dlog, _admissible):
	
	# Check if para bag size is smaller than num of paras
	if (len(_correct) >= PARA_BAG_SZ):
		return _correct[0:PARA_BAG_SZ]

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

		# how many to put in bag
		num2put = min(PARA_BAG_SZ-len(bag),len(dp))

		# update bag
		bag = bag + dp[0:num2put]

	assert(len(bag) == PARA_BAG_SZ)
	return bag

#===============================================================================
# 
def random_advisor_query(_dlog_content):
		_ais = range(len(_dlog_content))
		_aq = [ai for ai in _ais if _dlog_content[ai]['role'] == 'ADVISOR']
		idx = pick_1_randomly_neq(_aq, None)
		return idx, _dlog_content[idx]

#===============================================================================
# 
def advisor_query_exists(_dlog_content):
	for d in _dlog_content:
		if d['role'] == 'ADVISOR':
			return True
	return False

#===============================================================================
# returns example, or False if example in SET_ALREADY
def generate_example(_train_idx):
	global DEBUG

	# print('===========================================================')
	# print('Generating example')

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

	#~~ DATASET CHECK~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# check if advisor query already generated example
	if (aq['oriSenId'] in SET_ALREADY):
		return False
	# check that paraphrases exist
	if ('paraphrases' not in aq):
		# raise ValueError('paraphrases not in aq')
		return False
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	# get prior utterances (pu) up to but excluding aq
	pu = d[0:i]

	# remove extra information from pu
	for u in pu:
		if 'paraphrases' in u:
			del u['paraphrases']

	# get ground truth paraphrase set (gt) for aq
	paras_plus = paras_plus_one(aq)
	gt = pick_n_randomly(paras_plus)

	# generate bag of paraphrases size PARA_BAG_SZ
	pb = fill_bag_size_N(gt, di, _train_idx)
	random.shuffle(pb)

	if(DEBUG):
		print('-----------------------------------------------------------')
		print('--- PRIOR UTTERANCES')
		pprint.pprint(pu)
		print('-----------------------------------------------------------')
		print('--- PARAPHRASE BAG')
		pprint.pprint(pb)
		# print('bag length: ',len(pb))
		print('-----------------------------------------------------------')
		print('--- CORRECT PARAPHRASES')
		pprint.pprint(gt)

	example = json.dumps({
		'x_prior_utterances': pu,
		'x_paraphrase_bag': pb,
		'y_correct_paras': gt
	})
	return example

#===============================================================================
#
def combine_all_dialogs(_RAW_DAT_FILE):
	global ALL_DLOGS

	print(_RAW_DAT_FILE)
	with open(_RAW_DAT_FILE) as json_file:
		data = json.load(json_file)

		for batch in data:
			# print('=========================================================')
			# print('Collect Time: ', batch['collectTime'])
			# print('Num Dialogs: ', len(batch['data']))
			ALL_DLOGS = ALL_DLOGS + batch['data']

	print('===========================================================')
	print('Total Num Dialogs: ', len(ALL_DLOGS))
	return

#===============================================================================
#
def partition_train_test_docs():
	global TEST_SET_SZ, RAND_SEED

	num_dlog = len(ALL_DLOGS)
	indices = [i for i in range(num_dlog)]
	random.shuffle(indices)

	tr_sz = num_dlog - TEST_SET_SZ # training set size
	train_idx, test_idx = indices[:tr_sz], indices[tr_sz:]

	print('Num train examples: ',len(train_idx))
	print('Num test examples: ',len(test_idx))

	return train_idx, test_idx

#===============================================================================
#
def generate_set(_tt, _tt_idx):
	global DEBUG, SET_ALREADY, TRAIN_SET
	print('Generating set: ', _tt)

	GEN_SET = []

	if _tt == 'train':
		SZ_2_GEN = TRAIN_SET_SZ
	if _tt == 'test':
		SZ_2_GEN = TEST_SET_SZ

	#-------------------------------------------------------------
	# without random paraphrase sample (WITH_PARA_SAMPLE False)
	# IS_IN_THE_SET [hash1, hash2]
	# [dialogID, turnID, paraID]

	#-------------------------------------------------------------
	# with random paraphrase sample (WITH_PARA_SAMPLE True)
	# IS_IN_THE_SET
	# [dialogID, turnID, random paraphrase sample

	#-------------------------------------------------------------
	# while number train <= TRAIN_SET_SZ
	# pick random dialog
	# pick random advisor turn
	# pick random set paraphrases
	while len(GEN_SET) < SZ_2_GEN:

		new_example = generate_example(_tt_idx)

		if(new_example):

			new = json.loads(new_example)

			# FIXME! Check that example is not already in set

			GEN_SET = GEN_SET + [new]

	save_set(_tt, GEN_SET)

	return

#===============================================================================
#
def save_set(_tt, _GEN_SET):
	if _tt == 'train':
		name = 'train.json'

	if _tt =='test':
		name = 'test.json'

	print('Saving :', name, 'Size: ', len(_GEN_SET))

	return

#===============================================================================
#
def generate_test_set(_test_idx):

	return

#===============================================================================
#
def get_next_query():

	return

#===============================================================================
#
def get_bag_para():

	return

#===============================================================================
#
def zip_x_y():

	return

#===============================================================================
#
def generate_dataset(_train_doc_i, _test_doc_i):
	if(DEBUG):
		print('-----------------------------------------------------------')
		print('-----------------------------------------------------------')
		print('--- GENERATING DATASET')

	# print('_train_doc_i',_train_doc_i)
	# print('_test_doc_i',_test_doc_i)

	generate_set('train', _train_doc_i)
	generate_set('test', _test_doc_i)

	return

#===============================================================================
#	Main
#===============================================================================
def start():
	combine_all_dialogs(RAW_DAT_FILE)

	train_doc_i, test_doc_i = partition_train_test_docs()

	generate_dataset(train_doc_i, test_doc_i)

	return


if __name__ == "__main__":
	start()
