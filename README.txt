
README.txt

================================================================================
Entire Dataset
================================================================================

As of Nov 9, 2017:

Total number of utterances: 6070
Total number of paraphrases:  39666
Total number of admissible advisor queries: 2920


================================================================================
	Output
================================================================================

A json file containing:
	'Sen_Legend' : a dictionary that maps sentence ids to sentence strings
	'Ner_Legend' : a dictionary that maps sentence ids to ner output
	'Set_Examples' : a list of examples (see below)

To reduce file size, sentence strings are encoded by their ids, and can be
retrieved by indexing into Sen_Legend.

Each example in Set_Examples is structured as follows.

Set_Examples = [
			{
				'x_prior_utterances': [{},...],
				'y_correct_paras': [{},...]
				'y_paraphrase_bag': [{},...],
			}, 
			... ]

x_prior_utterances : a list of prior utterances in temporal / spoken order
y_correct_paras : a list of paraphrases (the correct subset of y_paraphrase_bag) 
y_paraphrase_bag : a list of paraphrases in shuffled order


================================================================================
Dataset Type 0: No paraphrases appear in preceding dialog
================================================================================

Preceding utterances are all original (not replaced with their paraphrases)


================================================================================
Dataset Type 1: Paraphrases appear in preceding dialog
================================================================================

Preceding utterances are replaced with their paraphrases at random


================================================================================
	Instructions
================================================================================

Flags:
	--trainsize=INT (desired size of the generated train set)
		default value: 1000

	--testsize=INT (desired size of the generated test set)
		default value: 100

	--bagsize=INT (desired size of the paraphrase bag)
		default value: 100

	--withpara=BOOL (generate examples by replacing with paraphrases)
		default value: 0

	--setname=STRING (name for set being generated)
		default value: Datetime

	--numhold=INT (number of dialogs to hold for generating the test set)
		default value: 50

	--fillwboth=BOOL (fill test set paraphrase bags with test+train utterances)
		default value: 0

Note: 	
	--withpara=0 generates Dataset Type 0
	--withpara=1 generates Dataset Type 1

	--fillwboth=0 test para bag filled w/ only test utterances
	--fillwboth=1 test para bag filled w/ train+test utterances

For example, to generate a dataset with the following sizes:

	train set size == 1234
	test set size == 567
	para bag size == 89
	with paraphrase == 0

Run the following command from the /scripts directory

python3 generate.py --trainsize=1234 --testsize=567 --bagsize=89 --withpara=1


================================================================================
	Notes
================================================================================

We omit examples where there are no prior utterances (advisor speaks first)
We omit examples where there are 0 correct paraphrases in the bag




