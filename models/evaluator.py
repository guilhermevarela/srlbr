'''
    This module works a wrapper for pearl's conll task evaluation script

    Created on Mar 15, 2018

    @author: Varela


    ref:
    
    CONLL 2005 SHARED TASK
        HOME: http://www.lsi.upc.edu/~srlconll/
        SOFTWARE: http://www.lsi.upc.edu/~srlconll/soft.html

'''
import subprocess
import utils


PEARL_SRLEVAL_PATH = './srlconll-1.1/bin/srl-eval.pl'


class Evaluator(object):
    # db, lexicons, columns, ind
    def __init__(self, db, lexicons, columns, ind, target_dir='./'):
        '''
            args:
            ds_type
            S           .:  dict<int,int> keys are the index, values are sentences
            P       .:  dict<int,int> keys are the index, values are propositions
            PRED    .:  dict<int,str> keys are the index, values are verbs/ predicates
            ARG     .:  dict<int,str> keys are the index, values are ARG
        '''                     
        self.db = db
        self.lexicons = lexicons
        self.columns = columns
        self.ind = ind
        self.target_dir = target_dir
        self.gold_dir = 'datasets_1.1/props/'

        self._refresh()

    def evaluate(self, Y, hparams):
        '''
            Evaluates the conll scripts returning total precision, recall and F1
                if self.target_dir is set will also save conll.txt@self.target_dir

            Performs a 6-step procedure in order to use the script evaluation
            1) Formats      .: inputs in order to obtain proper conll format ()
            2) Saves      .:  two tmp files tmpgold.txt and tmpy.txt on self.root_dir.
            3) Run            .:  the perl script using subprocess module.
            4) Parses     .:  parses results from 3 in variables self.f1, self.prec, self.rec. 
            5) Stores     .:  stores results from 3 in self.target_dir 
            6) Cleans     .:  files left from step 2.
                
            args:
                PRED            .: list<string> predicates according to PRED column
                T               .: list<string> target according to ARG column
                Y               .: list<string> 
            returns:
                prec            .: float<> precision
                rec       .: float<> recall 
                f1        .: float<> F1 score
        '''

        #Resets state
        self._refresh()
        #Step 1 - Transforms columns into with args and predictions into a dictionary
        # ready with conll format
        if min(Y) == self.ind['wTreino.conll']['start']:
            ds_type = 'train'
            gold_path = '{:}wTreino.golden.props'.format(self.gold_dir)
        elif min(Y) == self.ind['wValidacao.conll']['start']:
            ds_type = 'valid'
            gold_path = '{:}wValidacao.golden.props'.format(self.gold_dir)
        else:
            ds_type = 'test'
            gold_path = '{:}Teste.golden.props'.format(self.gold_dir)

        target_dir = utils.store(ds_type, self.db, self.lexicons, Y, hparams, self.target_dir)

        #Step 3 - Popen runs the pearl script storing in the variable PIPE
        target_path = '{:}{:}.props'.format(target_dir, ds_type)
        pipe = subprocess.Popen(['perl',PEARL_SRLEVAL_PATH, gold_path, target_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #out is a byte with each line separated by \n
        #ers is stderr      
        txt, err = pipe.communicate()
        self.txt = txt.decode('UTF-8')
        self.err = err.decode('UTF-8')

        if (self.err):
            print('srl-eval.pl says:\t{:}'.format(self.err))

        #Step 4 - Parse
        self._parse(self.txt)

        # Step 5 - Stores
        target_path= '{:}conllscore_{:}.txt'.format(target_dir, ds_type)
        with open(target_path, 'w+') as f:
            f.write(self.txt)

    def _refresh(self):
        self.num_propositions = -1
        self.num_sentences = -1
        self.perc_propositions = -1
        self.txt = ''
        self.err = ''
        self.f1 = -1
        self.precision = -1
        self.recall = -1

    def _parse(self, txt):
        '''
        Parses srlconll-1.1/bin/srl-eval.pl script output text 



        args:
            txt .: string with lines separated by \n and fields separated by tabs

        returns:

        example:
        Number of Sentences    :         326
        Number of Propositions :         553
        Percentage of perfect props :   4.70
                          corr.  excess  missed    prec.    rec.      F1
        ------------------------------------------------------------
                 Overall      398    2068     866    16.14   31.49   21.34
        ----------
                    A0      124     285     130    30.32   48.82   37.41
                    A1      202    1312     288    13.34   41.22   20.16
                    A2       18     179     169     9.14    9.63    9.37
                    A3        1      14      15     6.67    6.25    6.45
                    A4        2      14       9    12.50   18.18   14.81
                AM-ADV        4      19      19    17.39   17.39   17.39
                AM-CAU        0      16      17     0.00    0.00    0.00
                AM-DIR        0       0       1     0.00    0.00    0.00
                AM-DIS        6      17      20    26.09   23.08   24.49
                AM-EXT        0       3       5     0.00    0.00    0.00
                AM-LOC        9      65      46    12.16   16.36   13.95
                AM-MNR        0      24      28     0.00    0.00    0.00
                AM-NEG       10       5      24    66.67   29.41   40.82
                AM-PNC        0       9       9     0.00    0.00    0.00
                AM-PRD        0      15      18     0.00    0.00    0.00
                AM-TMP       22      91      68    19.47   24.44   21.67
        ------------------------------------------------------------
                     V      457      32      96    93.46   82.64   87.72
        ------------------------------------------------------------

        '''
        lines = txt.split('\n')
        for i, line in enumerate(lines):
            if (i == 0):
                self.num_sentences = int(line.split(':')[-1])
            if (i == 1):
                self.num_propositions = int(line.split(':')[-1])
            if (i == 2):
                self.perc_propositions = float(line.split(':')[-1])
            if (i == 6):
                self.precision, self.recall, self.f1 = map(float, line.split()[-3:])
                break