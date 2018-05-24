from models import process, to_svm, to_file

if __name__ == '__main__':
    conllcols = ('ID', 'FORM', 'LEMMA', 'GPOS', 'MORF', 'DTREE', 'FUNC', 'CTREE', 'PRED', 'HEAD')
    db, lexicons, columns, ind = process(refresh=False)

    inputs, outputs, bounds, feature_columns = to_svm(db, lexicons, conllcols)

    svm_paths = to_file('rolling-window', inputs, outputs, ind)

    import code; code.interact(local=dict(globals(), **locals()))
