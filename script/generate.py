
import sys, getopt
import params

def main(argv):
   inputfile = ''
   outputfile = ''

   opts, args = getopt.getopt(sys.argv[1:],'erb', [ 'testsize=', 
                                                   'trainsize=',
                                                   'bagsize='
                                                   ])
   TRAIN_SET_SZ = 0
   TEST_SET_SZ = 0

   for opt, arg in opts:
      if opt in ('-e','--testsize'):
         print('--testsize : ', arg)
         params.TEST_SET_SZ = int(arg)

      elif opt in ('-r','--trainsize'):
         print('--testsize : ', arg)
         params.TRAIN_SET_SZ = int(arg)

      elif opt in ('-p','--bagsize'):
         print('--bagsize : ', arg)
         params.PARA_BAG_SZ = int(arg)

   return

if __name__ == "__main__":
   main(sys.argv[1:])
   
   import raw_parser
   raw_parser.start()