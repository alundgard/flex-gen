
#===============================================================================
# dataset parameters (and their default values)

TRAIN_SET_SZ = 100 # Num of train examples to generate
TEST_SET_SZ = 300 # Num of test examples to generate
PARA_BAG_SZ = 100 # Num of utterances per para bag

WITH_PARA_SAMPLE = False # If true, replace orig dialog with paraphrases
NUM_PARA_SAMPLE= 100 # Num examples generated by replacing w/ paraphrases

RAND_SEED = 3
DEBUG = False