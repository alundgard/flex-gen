#!/usr/bin/env python3

import sys, getopt
import params

def main(argv):
   inputfile = ''
   outputfile = ''

   opts, args = getopt.getopt(sys.argv[1:],'erpwsnf', [
                                                   'testsize=', 
                                                   'trainsize=',
                                                   'withpara=',
                                                   'bagsize=',
                                                   'setname=',
                                                   'numhold=',
                                                   'fillwboth='
                                                   ])
   TRAIN_SET_SZ = 0
   TEST_SET_SZ = 0

   for opt, arg in opts:
      if opt in ('-e','--testsize'):
         # print('--testsize = ', arg)
         params.TEST_SET_SZ = int(arg)

      elif opt in ('-r','--trainsize'):
         # print('--trainsize = ', arg)
         params.TRAIN_SET_SZ = int(arg)

      elif opt in ('-p','--bagsize'):
         # print('--bagsize = ', arg)
         params.PARA_BAG_SZ = int(arg)

      elif opt in ('-w','--withpara'):
         # print('--withpara = ', arg)
         params.WITH_PARA_SAMPLE = (arg == '1')

      elif opt in ('-s','--setname'):
         # print('--setname = ', arg)
         params.SET_NAME = str(arg)

      elif opt in ('-n','--numhold'):
         # print('--numhold = ', arg)
         params.TEST_DOC_SZ = int(arg)

      elif opt in ('-f','--fillwboth'):
         # print('--fillwboth = ', arg)
         params.FILL_WITH_BOTH = (arg == '1')

   return

if __name__ == "__main__":
   print('====================================================================')
   print('====================================================================')
   print('====================================================================')
   print('.:: Flex Dataset Generator.')
   main(sys.argv[1:])
   import parser
   parser.start()
