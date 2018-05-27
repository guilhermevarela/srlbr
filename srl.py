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
                -s type : set type of solver (default 1)
                    for multi-class classification
                    0 -- L2-regularized logistic regression (primal)
                    1 -- L2-regularized L2-loss support vector classification (dual)
                    2 -- L2-regularized L2-loss support vector classification (primal)
                    3 -- L2-regularized L1-loss support vector classification (dual)
                    4 -- support vector classification by Crammer and Singer
                    5 -- L1-regularized L2-loss support vector classification
                    6 -- L1-regularized logistic regression
                    7 -- L2-regularized logistic regression (dual)''')

    parser.add_argument('-c', dest='cost', type=float, nargs=1, default=0.0625,
                    help=''' Liblinear\'s c parameter:
                            -c cost : set the parameter C (default 0.0625)''')

    parser.add_argument('-dtree', action='store_true', help='''dtree provides dtree parameter''')
    parser.add_argument('-context', action='store_true', help='''context provides context parameter''')
    parser.add_argument('-window', action='store_true', help='''window provides window parameter''')

    # parser.add_argument('--embeddings', dest='embeddings_model', type=check_embeddings, nargs=1, default=EMBEDDING_MODEL,
    #                 help='''embedding model name and size in format 
    #                 <embedding_name>_s<embedding_size>. Examples: glove_s50, wang2vec_s100\n''')

    # parser.add_argument('--ctx_p', dest='ctx_p', type=int, nargs=1, default=1, choices=[0,1,2,3],
    #                 help='''Size of sliding window around predicate\n''')

    # parser.add_argument('--lr', dest='lr', type=float, nargs=1, default=LEARNING_RATE,
    #                 help='''Learning rate of the model\n''')

    # parser.add_argument('--batch_size', dest='batch_size', type=int, nargs=1, default=BATCH_SIZE,
    #                 help='''Group up to batch size propositions during training.\n''')

    # parser.add_argument('--epochs', dest='epochs', type=int, nargs=1, default=N_EPOCHS,
    #                 help='''Number of times to repeat training set during training.\n''')
    import code; code.interact(local=dict(globals(), **locals()))
    args = parser.parse_args()
    if not (args.context or args.dtree or args.window):
        args.window = True 
    svm_srl(**args)