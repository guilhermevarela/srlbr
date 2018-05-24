from models import process, to_svm, SVM, Evaluator
# import os
# import re


if __name__ == '__main__':
    conllcols = ('ID', 'FORM', 'LEMMA', 'GPOS', 'MORF', 'DTREE', 'FUNC', 'CTREE', 'PRED', 'HEAD')
    target_dir = 'datasets_1.1/rolling_window'
    db, lexicons, columns, ind = process(refresh=False)
    
    evaluator = Evaluator(db, lexicons, columns, ind, target_dir)
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
        import code; code.interact(local=dict(globals(), **locals()))
        evaluator.evaluate(train_props, optargs)
        

        # store('train', db, lexicons, train_props, train_stats, optargs, target_dir)
        print('Insample prediction ... done')


        print('Outsample prediction ...')

        predictions = svm.predict(Xvalid, Yvalid, i0=len(train_props))
        valid_props = predictions['Yhat'].copy()
        del predictions['Yhat']
        valid_stats = predictions.copy()
        evaluator.evaluate(train_props, hparams)
        # store('valid', db, lexicons, valid_props, valid_stats, optargs, target_dir)

        print('Outsample prediction ... done')


    import code; code.interact(local=dict(globals(), **locals()))
