'''
    Created on Apr 11, 2018
        @author: Varela

    Implements a thin wrapper over liblinear
    Call this script from project root

'''


import pickle
import os
import glob
import svmlib.liblinearutil as _util
from collections import defaultdict


def to_svm(db, lexicons conll_columns):
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

    # normalize the database
    columns = sorted(list(db.keys()))

    bounds = {col: get_dim(col) for col in columns}

    inputs = defaultdict(dict)
    for idx in db['HEAD']:
        lb = 1
        for col in columns:
            if col not in ['HEAD']:
                dim = bounds[col]
                if db[col][idx]:    # might be string or non zero numeric value
                    if isinstance(db[col][idx], str):   # is a categorical column
                         inputs[idx][lb + lexicons[col][db[col][idx]]] = 1.0
                    else:
                         inputs[idx][lb] = float(db[col][idx])
                lb += dim

    outputs = db['HEAD']

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
        # print(kwargs)
        hparam = '_'.join(sorted(optargs.split('-')))
        hparam = hparam.replace(' ', '-')
        hparam =  encoding + hparam

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


if __name__ == '__main__':
    svm = SVM()

    encoding = 'hot'
    # alias = 'glo50'
    # propbank = PropbankEncoder.recover('datasets/binaries/deep_glo50.pickle')
    print('Loading train set ...')
    input_path = 'datasets/svms/{:}/train.svm'.format(encoding)
    print(input_path)
    Ytrain, Xtrain = _SVMIO.read(input_path)
    print('Loading train set ... done')

    print('Loading validation set ...')

    input_path = 'datasets/svms/{:}/valid.svm'.format(encoding)
    Yvalid, Xvalid = _SVMIO.read(input_path)
    print('Loading validation set ... done')

    for s in (0, 1, 2, 3, 4, 5, 6, 7):
        # optargs = '-s {:} -v 10'.format(s)
        optargs = '-s {:} -c {:0.4f}'.format(s, 0.0625)
        print('Training ... with_optargs({:})'.format(optargs))
        svm.fit(Xtrain, Ytrain, optargs)
        print('Training ... done')

        keys = ('y_hat', 'acc', 'mse', 'scc')
        print('Insample prediction ...')

        outputs = svm.predict(Xtrain, Ytrain)
        train_d = outputs['Yhat'].copy()
        del outputs['Yhat']
        trainstats_d = outputs.copy()

        print('Insample prediction ... done')


        print('Outsample prediction ...')
        outputs = svm.predict(Xvalid, Yvalid, i0=len(train_d))
        valid_d = outputs['Yhat'].copy()

        del outputs['Yhat']
        validstats_d = outputs.copy()

        print('Outsample prediction ... done')
        _SVMIO.dump(encoding, optargs, train=train_d, train_stats=trainstats_d,
                    valid=valid_d, valid_stats=validstats_d)
