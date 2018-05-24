from models import process, to_svm, to_file, SVM
import os
import re


def store(ds_type, db, lexicons, props, stats, hparams,target_dir):
    '''
    '''
    hparams = re.sub(' ', '-', re.sub('-', '', hparams))
    target_dir += '/{:}'.format(hparams)
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    target_path = '{:}/{:}.props'.format(target_dir, ds_type)
    p = 1
    head = {idx: token for token, idx in lexicons['HEAD'].items()}

    with open(target_path, mode='w+') as f:
        for idx, prop in props.items():
            if db['P'][idx] != p:
                f.write('\n')
                p = db['P'][idx]
            f.write('{:}\t{:}\n'.format(db['PRED'][idx], head[int(prop)]))

    target_path = '{:}/{:}.stats.txt'.format(target_dir, ds_type)

    with open(target_path, mode='w+') as f:
        for name, value in stats.items():
            f.write('{:}\t{:}\n'.format(name, value))


if __name__ == '__main__':
    conllcols = ('ID', 'FORM', 'LEMMA', 'GPOS', 'MORF', 'DTREE', 'FUNC', 'CTREE', 'PRED', 'HEAD')
    db, lexicons, columns, ind = process(refresh=False)

    inputs, outputs, bounds, feature_columns = to_svm(db, lexicons, conllcols)

    # svm_paths = to_file('rolling-window', inputs, outputs, ind)

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
    target_dir = 'datasets_1.1/rolling_window'
    for s in (0, 1, 2, 3, 4, 5, 6, 7):
        # optargs = '-s {:} -v 10'.format(s)
        optargs = '-s {:} -c {:0.4f}'.format(s, 0.0625)
        print('Training ... with_optargs({:})'.format(optargs))
        svm.fit(Xtrain, Ytrain, optargs)
        print('Training ... done')

        keys = ('y_hat', 'acc', 'mse', 'scc')
        print('Insample prediction ...')

        predictions = svm.predict(Xtrain, Ytrain)
        train_props = predictions['Yhat'].copy()

        del predictions['Yhat']
        train_stats = predictions.copy()
        del train_stats['val']


        store('train', db, lexicons, train_props, train_stats, optargs, target_dir)
        print('Insample prediction ... done')


        print('Outsample prediction ...')

        predictions = svm.predict(Xvalid, Yvalid, i0=len(train_props))
        valid_props = predictions['Yhat'].copy()
        del predictions['Yhat']
        valid_stats = predictions.copy()
        store('valid', db, lexicons, valid_props, valid_stats, optargs, target_dir)

        print('Outsample prediction ... done')


    import code; code.interact(local=dict(globals(), **locals()))
