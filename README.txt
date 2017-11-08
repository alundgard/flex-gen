README

================================================================================
Dataset 0: No paraphrases in preceding dialog
================================================================================



A dialog d consists of a set of chronological utterances between student and advisor, indexed by turn t

For each dialog, for each advisor utterance, create a bag of paraphrases consisting of the following:

Bag of paraphrases for d_t (where d_t is an advisor utterance):

================================================================================
Dataset 1: Paraphrases in preceding dialog
================================================================================

50, 100, 200 MB

100 dialog for test


================================================================================
	Instructions
================================================================================

Flags:
	--trainsize (desired size of the generated train set)
	--testsize (desired size of the generated test set)
	--bagsize (desired size of the paraphrase bag)

For example, to generate a flex dataset with the following sizes:
	train set size == 1234
	test set size == 567
	para bag size == 89

Run the following command from the /scripts directory

python generate.py --trainsize=1234 --testsize=567 --bagsize=89

Generally speaking, it is safe to run with following relative sizes:

	trainsize >>> testsize >> bagsize


================================================================================
	Output
================================================================================

example = json.dumps({
	'x_prior_utterances': pu,
	'x_paraphrase_bag': pb,
	'y_correct_paras': gt
})

x_prior_utterances : a list of utterances in temporal / spoken order
x_paraphrase_bag : a list of paraphrases in shuffled order
y_correct_paras : a list of paraphrases (the correct subset of x_paraphrase_bag) 


================================================================================
	Notes
================================================================================

We omit examples where there are no prior utterances (advisor speaks first)
We omit examples where there are 0 correct paraphrases in the bag




