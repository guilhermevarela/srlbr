'''
   Created on May 24, 2018

    @author: Varela

    utility functions
'''
import os
import re

def store(ds_type, db, lexicons, props, hparams, target_dir, stats=None):
    '''
        Stores props and stats into target_dir 
    '''
    hparams = re.sub(' ', '-', re.sub('-', '', hparams))
    target_dir += '/{:}/'.format(hparams)
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    target_path = '{:}/{:}.props'.format(target_dir, ds_type)

    head = {idx: token for token, idx in lexicons['HEAD'].items()}
    p = db['P'][min(props)]
    with open(target_path, mode='w+') as f:
        for idx, prop in props.items():
            if db['P'][idx] != p:
                f.write('\n')
                p = db['P'][idx]
            f.write('{:}\t{:}\n'.format(db['PRED'][idx], head[int(prop)]))

    if stats:
        target_path = '{:}/{:}.stats.txt'.format(target_dir, ds_type)
        with open(target_path, mode='w+') as f:
            for name, value in stats.items():
                f.write('{:}\t{:}\n'.format(name, value))

    return target_dir