'''
    Date: 28 May 2018
    Author: Guilherme Varela


    Invokes svm_srl scrips parsint command line inputs
    Usage:
    > python srl.py -help 
        Shows docs

    > python srl.py -s 0 1 2 3 -window
        Computes the models:
        0 -- L2-regularized logistic regression (primal)
        1 -- L2-regularized L2-loss support vector classification (dual)
        2 -- L2-regularized L2-loss support vector classification (primal)
        3 -- L2-regularized L1-loss support vector classification (dual)
        Using 1 set of features

    > python srl.py --s 4 5 6 7 -context -dtree -window
        Computes the models:
        4 -- support vector classification by Crammer and Singer
        5 -- L1-regularized L2-loss support vector classification
        6 -- L1-regularized logistic regression
        7 -- L2-regularized logistic regression (dual)
        Using 3 sets of features:
        context -- Context around predicate information near the predicate
        dtree -- Dependency tree set of features
        window -- Lead and lag tokens ( moving window ) across token set of features

'''

import argparse
from models import svm_srl

S = [0, 1, 2, 3, 4, 5, 6, 7]
C = 0.0625

if __name__ == '__main__':
    #Parse descriptors
    parser = argparse.ArgumentParser(
        description='''This script uses Liblinear\'s SVM for multiclass classification of Semantic Roles using 
            Propbank Br built according to the Propbank guidelines. Uses Conll 2005 Shared Task pearl evaluator
            under the hood, and the engineered features are described in (BELTRAO, 2016)''')

    parser.add_argument('-s', dest='solvers', 
        type=int, nargs='+', default=[0, 1, 2, 3, 4, 5, 6, 7],
        help=''' Liblinear\'s s parameter received as an array of integers:
                -s type : set type of solver (default 1)\n
                    for multi-class classification\n
                    \t0 -- L2-regularized logistic regression (primal)\n
                    \t1 -- L2-regularized L2-loss support vector classification (dual)\n
                    \t2 -- L2-regularized L2-loss support vector classification (primal)\n
                    \t3 -- L2-regularized L1-loss support vector classification (dual)\n
                    \t4 -- support vector classification by Crammer and Singer\n
                    \t5 -- L1-regularized L2-loss support vector classification\n
                    \t6 -- L1-regularized logistic regression\n
                    \t7 -- L2-regularized logistic regression (dual)\n''')

    parser.add_argument('-c', dest='cost', type=float, nargs=1, default=0.0625,
                    help=''' Liblinear\'s c parameter:
                            -c cost : set the parameter C (default 0.0625)''')
    parser.add_argument('-context', action='store_true', help='''uses group of feature around predicate''')
    parser.add_argument('-dtree', action='store_true', help='''dependency tree parameters''')
    parser.add_argument('-window', action='store_true', help='''lead and lag set of parameters''')
    parser.add_argument('-load', action='store_true', help='''loads precomputed features''')

    
    args = parser.parse_args()
    if not (args.context or args.dtree or args.window):
        args.window = True
    svm_srl(**args.__dict__)