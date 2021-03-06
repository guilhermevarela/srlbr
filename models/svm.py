'''
    Created on Apr 11, 2018
        @author: Varela

    Implements a thin wrapper over liblinear
    Call this script from project root

'''


import pickle
import os
import glob

import models.lib as _util
from numpy import isnan
from collections import defaultdict

from models.feature_factory import process
from models.evaluator import Evaluator
S = [0, 1, 2, 3, 4, 5, 6, 7]
C = 0.0625


def svm_srl(cost=C, context=True, dtree=True, solvers=S, window=True, load=False):
    # Golden standard columns
    conllcols = ('ID', 'FORM', 'LEMMA', 'GPOS', 'MORF', 'DTREE', 'FUNC', 'CTREE', 'PRED', 'HEAD')

    refresh = not load
    # Solves target directories
    target_dir = 'experiments/'
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    if context:
        target_dir += 'context'
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)
    if dtree:
        target_dir += 'dtree' if target_dir[-1] == '/' else '-dtree'

    if window:
        target_dir += 'window' if target_dir[-1] == '/' else '-window'
    if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

    db, lexicons, columns, ind = process(context, dtree, window, refresh=refresh)

    evaluator = Evaluator(db, lexicons, columns, ind, target_dir)
    inputs, outputs, bounds, feature_columns = to_svm(db, lexicons, conllcols)


    # DEFINE Xtrain, Ytrain
    start = ind['wTreino.conll']['start']
    finish = ind['wTreino.conll']['finish']
    trainrng = range(start, finish)
    Xtrain = [inputs[idx] for idx in trainrng]
    Ytrain = [outputs[idx] for idx in trainrng]

    # DEFINE Xvalid, Yvalid
    start = ind['wValidacao.conll']['start']
    finish = ind['wValidacao.conll']['finish']
    validrng = range(start, finish)
    Xvalid = [inputs[idx] for idx in validrng]
    Yvalid = [outputs[idx] for idx in validrng]

    svm = SVM()
    for s in solvers:
        optargs = '-s {:} -c {:0.4f}'.format(s, cost)
        print('Training ... with_optargs({:})'.format(optargs))
        svm.fit(Xtrain, Ytrain, optargs)
        print('Training ... done')

        keys = ('y_hat', 'acc', 'mse', 'scc')
        print('Insample prediction ...')

        predictions = svm.predict(Xtrain, Ytrain)
        train_props = predictions['Yhat'].copy()

        evaluator.evaluate(train_props, optargs)


        print('Insample prediction ... done')


        print('Outsample prediction ...')

        predictions = svm.predict(Xvalid, Yvalid, i0=len(train_props))
        valid_props = predictions['Yhat'].copy()
        evaluator.evaluate(valid_props, optargs)


        print('Outsample prediction ... done')

def to_svm(db, lexicons, conll_columns):
    '''
        Converts conll dict into a problem

        args:
            db                  .: dict<str,dict<int, ?>> is a dict of dicts representing the conll db +
                                    engineered attributes.
                                    outer_keys: attribute column name
                                    inner_keys: example index
                                    inner_values : either a category or a value 

            
            lexicons            .: dict<str,dict<str, int>>  is a dict of dicts represering all possible column values
                                    outer_keys: column_name in conll_column

            conll_columns       .: tuple with original columns in .conll files

        returns:            
            inputs dict<int, dict<int,float>>

            outputs dict<int, int>

            bounds  dict<str, int>

            columns list<str> with columns names

    '''
    # returns the dimension of a feature by approximate matching
    def get_dim(searchcol):
        for key in conll_columns:
            if key in searchcol:  # approximate comparison
                return len(lexicons[key])
        return 1

    def get_lex(searchcol):
        for key in conll_columns:
            if key in searchcol:  # approximate comparison
                return key
        return None


    # normalize the database
    columns = sorted([ col
        for col in list(db.keys()) if col not in ('HEAD','P')])

    bounds = {col: get_dim(col) for col in columns}

    inputs = defaultdict(dict)
    for idx in db['HEAD']:
        lb = 1
        for col in columns:
            # if col not in ['HEAD', 'P']:
            if col not in ['HEAD', 'P', 'ID', 'DTREE', 'CTREE']:
                dim = bounds[col]
                value = db[col].get(idx, None)
                try:
                    if value:    # might be string or non zero numeric value
                        if isinstance(value, str):   # is a categorical column
                            lexcol = get_lex(col)
                            inputs[idx][lb + lexicons[lexcol][db[col][idx]]] = 1.0
                        elif not isnan(value):
                             inputs[idx][lb] = float(db[col][idx])
                except KeyError:
                    import code; code.interact(local=dict(globals(), **locals()))
                lb += dim

    outputs = { idx: lexicons['HEAD'][val] for idx, val in db['HEAD'].items()}

    return inputs, outputs, bounds, columns

class SVM(object):
    _svm = None

    @classmethod
    def read(cls, svmproblem_path):
        Y, X = _util.svm_read_problem(svmproblem_path)
        return Y, X

    def fit(self, X, Y, argstr):
        self._svm = _util.train(Y, X, argstr)

    def predict(self, X, Y, i0=0):
        # return pred_labels, (ACC, MSE, SCC), pred_values
        labels, metrics, values = _util.predict(Y, X, self._svm)
        index = range(i0, i0 + len(labels), 1)
        d = {
            'Yhat': dict(zip(index, labels)),
            'acc': metrics[0],
            'mse': metrics[1],
            'scc': metrics[2],
            'val': values
        }
        return d

    def predict_with_propositions(self, X, Y, P_d):
        d = self.predict(X, Y)

        indexes = list(P_d.keys())

        Yhat_d = {indexes[i]: int(y_hat)
                  for i, y_hat in enumerate(d['y_hat'])}

        labels_d = defaultdict(dict)
        labels_d['P'] = P_d
        labels_d['Y'] = Yhat_d
        del d['y_hat']
        return labels_d, d


class _SVMIO(object):

    @classmethod
    def read(cls, svmproblem_path):
        Y, X = _util.svm_read_problem(svmproblem_path)
        return Y, X

    @classmethod
    def dump(cls, encoding, optargs, **kwargs):
        '''
            Writes output in pickle format
        '''
        hparam = '_'.join(sorted(optargs.split('-')))
        hparam = hparam.replace(' ', '-')
        hparam = encoding + hparam

        target_dir = 'outputs/svm/{:}/'.format(hparam)
        if not os.path.exists(target_dir):
            os.mkdir(target_dir)

        target_glob = '{:}[0-9]*'.format(target_dir)
        num_outputs = len(glob.glob(target_glob))
        target_dir += '{:02d}/'.format(num_outputs)
        os.mkdir(target_dir)

        for key, value in kwargs.items():
            picklename = '{:}{:}.pickle'.format(target_dir, key)
            with open(picklename, '+wb') as f:
                pickle.dump(value, f, pickle.HIGHEST_PROTOCOL)
