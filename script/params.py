
#===============================================================================
# Dataset parameters (and their default values)
from datetime import datetime

TRAIN_SET_SZ = 1000 # Num of train examples to generate
TEST_SET_SZ = 100 # Num of test examples to generate

PARA_BAG_SZ = 100 # Num of utterances per para bag
WITH_PARA_SAMPLE = False # If true, replace orig dialog with paraphrases

# If true, test para bag filled w/ train+test utterances
# If false, test para bag filled w/ only test utterances
FILL_WITH_BOTH = False

TEST_DOC_SZ = 50 # Num dialogs to hold out for test set generation
SET_NAME = str(datetime.now().strftime('%H-%M_%h-%d-%Y'))
