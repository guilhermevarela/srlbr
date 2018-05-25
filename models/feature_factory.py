'''
    Author Guilherme Varela

    Feature engineering module
    * Converts linguist and end-to-end features into objects
'''
import sys
sys.path.append('../datasets_1.1')
from collections import OrderedDict, defaultdict, deque

import pandas as pd
import networkx as nx
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt


import re

class FeatureFactory(object):
    # Allowed classes to be created
    @staticmethod
    def klasses():
        return {'ColumnDepTreeParser', 'ColumnShifter', 'ColumnShifterCTX_P',
                'ColumnPassiveVoice', 'ColumnPredDist', 'ColumnPredMarker',
                'ColumnPredMorph'}

    # Creates an instance of class given schema and db
    @staticmethod
    def make(klass, dict_db):
        if klass in FeatureFactory.klasses():
            return eval(klass)(dict_db)
        else:
            raise ValueError('klass must be in {:}'.format(FeatureFactory.klasses()))


class ColumnShifter(object):
    '''
        Shifts columns respecting proposition bounds

        Usage:
            See below (main)
    '''
    def __init__(self, dict_db):
        self.db = dict_db

    # Columns over which we want to perform the shifting
    def define(self, columns, shifts):
        '''
            Defines with columns will be effectively shifted and by what amount

            args:
                columns .: list<str> column names that will be shifted

                shifts .: list<int> of size m holding integers, negative numbers are delays
                    positive numbers are leads

                new_columns .: list<str> of size n holding new column names if none 
                                one name will be generated

            returns:
                column_shifter .: object<ColumnShifter> an instance of column shifter

        '''
        # Check if columns is subset of db columns
        if not(set(columns) <= set(self.db.keys())):
            unknown_columns = set(columns) - set(self.db.keys())
            raise ValueError('Unknown columns {:}'.format(unknown_columns))
        else:
            self.columns = columns

        shift_types = [isinstance(i, int) for i in shifts]
        if not all(shift_types):

            invalid_types = [shift[i] for i in shift_types
                             if not shift_types[i]]

            raise ValueError('Int type violation: {:}'.format(invalid_types))
        else:
            self.shifts = sorted(shifts)

        self.mapper = OrderedDict(
                {(i, col): '{:}{:+d}'.format(col, i)
                 for col in columns for i in sorted(shifts)})

        return self

    def run(self):
        '''
            Computes column shifting
            args:
            returns:
                shifted .: dict<new_columns, dict<int, column<type>>>
        '''
        if not ( self.columns or self.shifts or self.mapper):
            raise Exception('Columns to be shifted are undefined run column_shifter.define')

        # defines output data structure
        self.dict_shifted = {col: OrderedDict({}) for _, col in self.mapper.items()}

        # defines output data structure

        for time, proposition in self.db['P'].items():
            for col in self.columns:
                for s in self.shifts:
                    new_col = self.mapper[(s, col)]
                    if (time + s in self.db['P']) and\
                         (self.db['P'][time + s] == proposition):
                        self.dict_shifted[new_col][time] = self.db[col][time + s]
                    else:
                        self.dict_shifted[new_col][time] = None

        return self.dict_shifted


class ColumnShifterCTX_P(object):
    '''
        Grabs columns around predicate and shifts it

        Usage:
            See below (main)
    '''

    def __init__(self, dict_db):
        self.db = dict_db

    # Columns over which we want to perform the shifting    
    def define(self, columns, shifts):
        '''
            Defines with columns will be effectively shifted and by what amount

            args:
                columns .: list<str> column names that will be shifted

                shifts .: list<int> of size m holding integers, negative numbers are delays
                    positive numbers are leads

                new_columns .: list<str> of size n holding new column names if none 
                                one name will be generated

            returns:
                column_shifter .: object<ColumnShifter> an instance of column shifter

        '''
        # Check if columns is subset of db columns
        if not(set(columns) <= set(self.db.keys())):
            unknown_columns = set(columns) - set(self.db.keys())
            raise ValueError('Unknown columns {:}'.format(unknown_columns))
        else:
            self.columns = columns

        shift_types = [isinstance(i, int) for i in shifts]
        if not all(shift_types):
            invalid_types = [shift[i] for i in shift_types if not shift_types[i]]

            raise ValueError('Int type violation: {:}'.format(invalid_types))
        else:
            self.shifts = sorted(shifts)

        self.mapper = OrderedDict(
                {(i, col): '{:}_CTX_P{:+d}'.format(col, i)
                 for col in columns for i in sorted(shifts)})

        return self

    def run(self):
        '''
            Computes column shifting
            args:
            returns:
                shifted .: dict<new_columns, dict<int, column<type>>>
        '''
        if not ( self.columns or self.shifts or self.mapper):
            raise Exception('Columns to be shifted are undefined run column_shifter.define')

        # defines output data structure
        self.dict_shifted = {col: OrderedDict({}) for _, col in self.mapper.items()}

        # defines output data structure
        times = []
        predicate_d = _predicatedict(self.db)
        for time, proposition in self.db['P'].items():
            predicate_time =  predicate_d[proposition]

            for col in self.columns:
                for s in self.shifts:
                    new_col = self.mapper[(s, col)]
                    if (predicate_time + s in self.db['P']) and\
                         (self.db['P'][predicate_time + s] == proposition):
                        self.dict_shifted[new_col][time] = self.db[col][predicate_time + s]
                    else:
                        self.dict_shifted[new_col][time] = None

        return self.dict_shifted


class ColumnPredDist(object):
    '''
        Computes the distance to the predicate

        Usage:
            See below (main)
    '''
    def __init__(self, dict_db):
        self.db = dict_db

    # Columns over which we want to perform the shifting
    def define(self):
        '''
            Defines with columns will be effectively shifted and by what amount

            args:
                columns .: list<str> column names that will be shifted

                shifts .: list<int> of size m holding integers, negative numbers are delays
                    positive numbers are leads

                new_columns .: list<str> of size n holding new column names if none 
                                one name will be generated

            returns:
                column_shifter .: object<ColumnShifter> an instance of column shifter

        '''
        if not '(V*)' in set(self.db['ARG'].values()):
            raise ValueError('(V*) not in ARG')

        return self

    def run(self):
        '''
            Computes the distance to the target predicate
            args:
            returns:
                preddist .: dict<PRED_DIST, OrderedDict<int, int>>
        '''
        # defines output data structure
        self.preddist = {'PRED_DIST': OrderedDict({})}

        # Finds predicate position
        predicate_d = _predicatedict(self.db)
        for time, proposition in self.db['P'].items():
            predicate_time = predicate_d[proposition]

            self.preddist['PRED_DIST'][time] = predicate_time - time

        return self.preddist


class ColumnPassiveVoice(object):
    '''
        Passive voice indicator
        1 if POS of target verb GPOS=v-pcp and is preceeded by LEMMA=ser

        Usage:
            See below (main)
    '''

    def __init__(self, dict_db):
        self.db = dict_db

    def run(self):
        '''
            Computes the distance to the target predicate
            args:
            returns:
                passive_voice .: dict<PASSIVE_VOICE, OrderedDict<int, int>>
        '''
        # defines output data structure
        self.passive_voice = {'PASSIVE_VOICE': OrderedDict({})}

        # Finds predicate position
        predicate_d = _predicatedict(self.db)
        pos_d = {
            self.db['P'][time]: time
            for time, pos in self.db['GPOS'].items() if pos == 'V-PCP'
        }
        lemma_d = {
            self.db['P'][time]: time
            for time, lem in self.db['LEMMA'].items() if lem == 'ser'
        }
        
        for time, proposition in self.db['P'].items():
            predicate_time = predicate_d[proposition]
            lemma_time = lemma_d.get(proposition, None)
            pos_time = pos_d.get(proposition, None)
            if lemma_time and pos_time:
                self.passive_voice['PASSIVE_VOICE'][time] = 1 if lemma_time < predicate_time and pos_time == predicate_time else 0
            else:
                self.passive_voice['PASSIVE_VOICE'][time] = 0 

        return self.passive_voice


class ColumnPredMarker(object):
    '''
        Marks if we are in the predicate context
        1 if time > predicate_time
        0 otherwise

        Usage:
            See below (main)
    '''

    def __init__(self, dict_db):
        self.db = dict_db

    def run(self):
        '''
            Computes the distance to the target predicate
            args:
            returns:
                preddist .: dict<PRED_DIST, OrderedDict<int, int>>
        '''
        # defines output data structure
        self.predmarker = {'PRED_MARKER': OrderedDict({})}

        # Finds predicate position
        predicate_d = _predicatedict(self.db)
        for time, proposition in self.db['P'].items():
            predicate_time = predicate_d[proposition]

            self.predmarker['PRED_MARKER'][time] = 0 if predicate_time - time > 0 else 1

        return self.predmarker


class ColumnPredMorph(object):
    '''
        Genatate 32 binary array 
        the field MORF is multivalued and is pipe separator ('|')
        Receives 1 if attribute is present 0 otherwise 

        Usage:
            See below (main)
    '''
    def __init__(self, dict_db):
        self.db = dict_db

    def run(self):
        '''
            Computes 32 item list of zeros and ones
            args:
            returns:
                predmorph .: dict<PRED_MORPH, OrderedDict<int, int>>
        '''
        # defines output data structure
        self.predmorph = {'PRED_MORPH': OrderedDict({})}

        # Finds all single flag
        composite_morph = sorted(list(set(self.db['MORF'].values())))

        morph = [item
                 for sublist in
                 [m.split('|') for m in composite_morph]
                 for item in sublist]

        morph = sorted(list(set(morph)))
        rng = range(len(morph))
        morph2idx = dict(zip(morph, rng))


        for time, morph_comp in self.db['MORF'].items():
            _features = [1 if m in morph_comp.split('|') else 0
                         for m in morph2idx]

            _features = {
                'PredMorph_{:02d}'.format(i + 1):feat_i
                for i, feat_i in enumerate(_features)}

            for key, val in _features.items():
                if key not in self.predmorph['PRED_MORPH']:
                    self.predmorph['PRED_MORPH'][key] = OrderedDict({})
                self.predmorph['PRED_MORPH'][key][time] = val

        return self.predmorph


class ColumnDepTreeParser(object):
    '''
        Finds columns in Dependency Tree
    '''
    def __init__(self, dict_db):
        self.db = dict_db
        self.columns = []
    def define(self, columns):
        '''
            Defines which columns to return

            args:
                columns .: list<str> columns a column in db

            returns:
                deptree_parser .: object< ColumnDepTreeParser>

        '''
        _msg = 'columns must belong to database {:} got {:}'
        for col in columns:
            if col not in self.db:
                raise ValueError(_msg.format(list(self.db.keys()), col))
        self.columns = columns

        return self

    def run(self):
        '''
            Computes the distance to the target predicate
        '''
        # defines output data structure
        self.kernel = defaultdict(OrderedDict)

        # finds predicate time 
        predicate_d = _predicatedict(self.db)
        lb = 0
        ub = 0
        prev_prop = -1
        prev_time = -1
        process = False
        for time, proposition in self.db['P'].items():
            if prev_prop < proposition:
                if prev_prop > 0:
                    lb = ub
                    ub = prev_time + 1  # ub must be inclusive
                    process = True

            if process:
                G, root = self._build(lb, ub)
                for i in range(lb, ub):
                    # Find children, parent and grand-parent
                    result = self._make_lookupnodes()
                    q = deque(list())
                    self._dfs_lookup(G, root, i, q, result)
                    for key, nodeidx in result.items():
                        for col in self.columns:
                            new_key = '{:}_{:}'.format(col, key).upper()
                            if nodeidx is None:
                                self.kernel[new_key][i] = None
                            else:
                                self.kernel[new_key][i] = self.db[col][nodeidx]

                    # Find path to predicate
                    self._refresh(G)
                    result = {}
                    q = deque(list())
                    pred = predicate_d[prev_prop]
                    self._dfs_path(G, i, pred, q, result)

                    for key, nodeidx in result.items():
                        for col in self.columns:
                            if col in ('GPOS', 'FUNC'):
                                _key = key.split('_')[0]
                                new_key = '{:}_{:}'.format(col, _key).upper()
                                if nodeidx is None:
                                    self.kernel[new_key][i] = None
                                else:
                                    self.kernel[new_key][i] = self.db[col][nodeidx]

                    self._refresh(G)

            process = False
            prev_prop = proposition
            prev_time = time

        return self.kernel

    def _make_lookupnodes(self):
        _list_keys = ['parent', 'grand_parent', 'child_1', 'child_2', 'child_3']
        return dict.fromkeys(_list_keys)

    def _update_lookupnodes(self, children_l, ancestors_q, lookup_nodes):
        self._update_ancestors(ancestors_q, lookup_nodes)
        self._update_children(children_l, lookup_nodes)

    def _update_path(self, ancestors_q, lookup_nodes):
        for i, nidx in enumerate(ancestors_q):
            _key = '{:02d}_node'.format(i)
            lookup_nodes[_key] = nidx

    def _update_ancestors(self, ancestors_q, lookup_nodes):
        try:
            lookup_nodes['parent'] = ancestors_q.pop()
            lookup_nodes['grand_parent'] = ancestors_q.pop()
        except IndexError:
            pass

    def _update_children(self, children_l, lookup_nodes):
        n = 0
        for v in children_l:
            if (not v == lookup_nodes['parent']):
                key = 'child_{:}'.format(n + 1)
                lookup_nodes[key] = v
                n += 1
            if n == 3:
                break

    def _dfs_lookup(self, G, u, i, q, lookup_nodes):
        G.nodes[u]['discovered'] = True
        # updates ancestors if target i is undiscovered
        if not G.nodes[i]['discovered']:
            q.append(u)

        # current node u is target node i
        if i == u:
            self._update_lookupnodes(G.neighbors(u), q, lookup_nodes)
            return False
        else:
            # keep looking
            for v in G.neighbors(u):
                if not G.node[v]['discovered']:
                    search = self._dfs_lookup(G, v, i, q, lookup_nodes)
                    if not search:
                        return False

        if not G.nodes[i]['discovered']:
            q.pop()
        return True

    def _dfs_path(self, G, u, i, q, path_nodes):
        # updates ancestors if target i is undiscovered
        if not G.nodes[i]['discovered']:
            q.append(u)
        G.nodes[u]['discovered'] = True

        # current node u is target node i
        if i == u:
            self._update_path(q, path_nodes)
            return False
        else:
            # keep looking
            for v in G.neighbors(u):
                if not G.node[v]['discovered']:
                    search = self._dfs_path(G, v, i, q, path_nodes)
                    if not search:
                        return False

        if not G.nodes[i]['discovered']:
            q.pop()
        return True


    def _refresh(self, G):
        for u in G:
            G.nodes[u]['discovered'] = False

    def _build(self, lb, ub):
        G = nx.Graph()
        root = None
        for i in range(lb, ub):
            G.add_node(int(i), **self._crosssection(int(i)))

        for i in range(lb, ub):
            v = int(G.node[i]['DTREE'])  # reference to the next node
            u = int(G.node[i]['ID'])  # reference to the current node within proposition
            if v == 0:
                root = i
            else:
                G.add_edge(i, (v - u) + i)

        return G, root

    def _crosssection(self, idx):
        list_keys = list(self.db.keys())
        d = {key: self.db[key][idx] for key in list_keys}

        d['discovered'] = False
        return d


def get_shifter(db, refresh=True):
    '''
        Builds lag and lead attributes around current token
        for golden standard columns ('FORM', 'LEMMA', 'FUNC', 'GPOS')
        (BELTRAO, 2016) pg 47
        
        args:
        db          .: dict<inner_keys, dict<outer_keys, ?>>
                        inner_keys  .: str columns which should contain all base conll attributes
                     
                        outer_keys  .: int token id
                        ?           .: either text or numerical value

        refresh    .: boolean if true recompute attributes and store
        returns:
        windows    .: 
    '''
    columns_shift = ('FORM', 'LEMMA', 'FUNC', 'GPOS')
    if refresh:
        delta = 3
        shifts = [d for d in range(-delta, delta + 1, 1) if d != 0]
        windows = _process_shifter(db, columns_shift, shifts)
    else:
        windows = _load_shifter(db, columns_shift)

    return windows


def _load_shifter(dictdb, columns):
    target_dir = 'datasets_1.1/csvs/column_shifter/'
    shifted = defaultdict(dict)
    for col in columns:
        target_path = '{:}{:}.csv'.format(target_dir, col.lower())
        _df = pd.read_csv(target_path, encoding='utf-8', index_col=0)
        shifted.update(_df.to_dict())
    return shifted


def _process_shifter(dictdb, columns, shifts, store=True):

    shifter = FeatureFactory().make('ColumnShifter', dictdb)
    target_dir = 'datasets_1.1/csvs/column_shifter/'
    shifted = shifter.define(columns, shifts).run()

    if store:
        _store_columns(shifted, columns, target_dir)

    return shifted


def get_ctx_p(db, refresh=True):
    '''
        Builds lag and lead attributes (context) around PREDICATE
        for golden standard columns ('FUNC', 'GPOS', 'LEMMA', 'FORM')
        (BELTRAO, 2016) pg 47
 
        args:
        db          .: dict<inner_keys, dict<outer_keys, ?>>
                        inner_keys  .: str columns which should contain all base conll attributes                
                        outer_keys  .: int token id
                        ?           .: either text or numerical value

        refresh    .: boolean if true recompute attributes and store
        returns:
        windows    .: 
    '''
    if refresh:
        column_shifts_ctx_p = ('FUNC', 'GPOS', 'LEMMA', 'FORM')
        columns = ['PRED']
        delta = 3
        shifts = [d for d in range(-delta, delta + 1, 1)]
        contexts = _process_shifter_ctx_p(db, column_shifts_ctx_p, shifts)
        passive_voice = _process_passivevoice(db)
        predmorph = _process_predmorph(db)

    else:
        contexts = _load_ctx_p(db, column_shifts_ctx_p)
        # passive_voice = _load_passivevoice(db)
        # predmorph = _load_predmorph(db)


    return contexts


def _process_shifter_ctx_p(db, columns, shifts, store=True):

    shifter = FeatureFactory().make('ColumnShifterCTX_P', db)
    target_dir = 'datasets_1.1/csvs/column_shifts_ctx_p/'
    shifted = shifter.define(columns, shifts).run()

    if store:
        _store_columns(shifted, columns, target_dir)

    return shifted


def _load_ctx_p(dictdb, columns):
    target_dir = 'datasets_1.1/csvs/column_shifts_ctx_p/'
    ctx_p = defaultdict(dict)
    for col in columns:
        target_path = '{:}{:}.csv'.format(target_dir, col.lower())
        _df = pd.read_csv(target_path, encoding='utf-8', index_col=0)
        ctx_p.update(_df.to_dict())
    return ctx_p


def _predicatedict(db):
    d = {
        db['P'][time]: time
        for time, pred in db['PRED'].items() if (pred != '-')
    }
    return d


def _process_passivevoice(dictdb, store=True):
    pvoice_marker = FeatureFactory().make('ColumnPassiveVoice', dictdb)
    target_dir = 'datasets_1.1/csvs/column_passivevoice/'
    passivevoice = pvoice_marker.run()

    if store:
        _store(passivevoice, 'passive_voice', target_dir)

    return passivevoice


def _process_predmorph(dictdb, store=True):

    morpher = FeatureFactory().make('ColumnPredMorph', dictdb)
    target_dir = 'datasets_1.1/csvs/column_predmorph/'
    predmorph = morpher.run()

    if store:
        _store(predmorph['PRED_MORPH'], 'pred_morph', target_dir)

    return predmorph

def _process_predicate_dist(dictdb):

    pred_dist = FeatureFactory().make('ColumnPredDist', dictdb)
    d = pred_dist.define().run()

    target_dir = '/datasets_1.1/csvs/column_preddist/'
    filename = '{:}{:}.csv'.format(target_dir, 'predicate_distance')
    pd.DataFrame.from_dict(d).to_csv(filename, sep=',', encoding='utf-8')


def _process_predicate_marker(dictdb, store=True):

    column_predmarker = FeatureFactory().make('ColumnPredMarker', dictdb)
    d = column_predmarker.run()

    target_dir = 'datasets_1.1/csvs/column_predmarker/'
    filename = '{:}{:}.csv'.format(target_dir, 'predicate_marker')
    if store:
        pd.DataFrame.from_dict(d).to_csv(filename, sep=',', encoding='utf-8')

    return d


def _store_columns(columns_dict, columns, target_dir):
    for col in columns:
        d = {new_col: columns_dict[new_col]
             for new_col in columns_dict if col in new_col}

        df = pd.DataFrame.from_dict(d)
        filename = '{:}{:}.csv'.format(target_dir, col.lower())
        df.to_csv(filename, sep=',', encoding='utf-8')


    return columns_dict


def _store(d, target_name, target_dir):
        df = pd.DataFrame.from_dict(d)
        filename = '{:}{:}.csv'.format(target_dir, target_name)
        df.to_csv(filename, sep=',', encoding='utf-8', index=True)


def _process_conll():
    datasets = ('wTreino.conll', 'wValidacao.conll', 'Teste.conll')
    columns = ('ID', 'FORM', 'LEMMA', 'GPOS', 'MORF', 'DTREE', 'FUNC', 'CTREE', 'PRED', 'HEAD')
    lexicons = defaultdict(dict)
    db = defaultdict(dict)
    ind = defaultdict(dict)
    i = 0
    p = 1  # predicate
    for dataset in datasets:
        dataset_path = 'datasets_1.1/conll/{:}'.format(dataset)
        ind[dataset]['start'] = i
        with open(dataset_path, mode='r') as f:
            for line in f.readlines():
                values = re.sub('\n', '', line).split('\t')
                if len(values) == len(columns):
                    for c, column in enumerate(columns):
                        value = values[c].strip()
                        if value not in lexicons[column]:
                            l = len(lexicons[column])
                            lexicons[column][value] = l
                        else:
                            l = lexicons[column][value]

                        db[column][i] = value

                    db['P'][i] = p
                    i += 1
                else:
                    p += 1

        ind[dataset]['finish'] = i

    return db, lexicons, columns, ind


def process(refresh=True):
    '''
        Processes all engineered features
    '''
    db, lexicons, columns, ind = _process_conll()

    # Making column moving windpw around column
    # Set of featured attributes 
    windows = get_shifter(db, refresh)
    db.update(windows)

    # Making tokens around predicate available
    contexts = get_ctx_p(db, refresh=True)
    db.update(contexts)

    return db, lexicons, columns, ind


if __name__ == '__main__':
    '''
        Usage of FeatureFactory
    '''
    db, ind, columns = process()
    # datasets = ('wTreino.conll', 'wValidacao.conll', 'Teste.conll')
    # columns = ('ID', 'FORM', 'LEMMA', 'GPOS', 'MORF', 'DTREE', 'FUNC', 'CTREE', 'PRED', 'HEAD')
    # lexicons = defaultdict(dict)
    # db = defaultdict(dict)
    # ind = defaultdict(dict)
    # i = 0
    # p = 1  # predicate
    # for dataset in datasets:
    #     dataset_path = 'datasets_1.1/conll/{:}'.format(dataset)
    #     ind[dataset]['start'] = i
    #     with open(dataset_path, mode='r') as f:
    #         for line in f.readlines():
    #             values = re.sub('\n', '', line).split('\t')
    #             if len(values) == len(columns):
    #                 for c, column in enumerate(columns):
    #                     value = values[c].strip()
    #                     if value not in lexicons[column]:
    #                         l = len(lexicons[column])
    #                         lexicons[column][value] = l
    #                     else:
    #                         l = lexicons[column][value]

    #                     db[column][i] = value

    #                 db['P'][i] = p
    #                 i += 1
    #             else:
    #                 p += 1

    #     ind[dataset]['finish'] = i

    # import code; code.interact(local=dict(globals(), **locals()))
    # Making column moving windpw around column    
    # columns_shift = ('FORM', 'LEMMA', 'FUNC', 'GPOS')
    # delta = 3
    # shifts = [d for d in range(-delta, delta + 1, 1) if d != 0]
    # windows = _process_shifter(db, columns_shift, shifts)

    # db.update(result)

    # Making window around predicate
    # column_shifts_ctx_p = ('FUNC', 'GPOS', 'LEMMA', 'FORM')
    # columns = ['PRED']
    # delta = 3
    # shifts = [d for d in range(-delta, delta + 1, 1)]
    # contexts = _process_shifter_ctx_p(db, column_shifts_ctx_p, shifts)


    # import code; code.interact(local=dict(globals(), **locals()))
    # Making DepTree Parser
    depfinder = FeatureFactory().make('ColumnDepTreeParser', db)

    lemma_dependencies = depfinder.define(['LEMMA']).run()
    import code; code.interact(local=dict(globals(), **locals()))
    _store(lemma_dependencies, 'lemma', 'datasets_1.1/csvs/column_deptree/')
    # depfinder = FeatureFactory().make('ColumnDepTreeParser', db)
    # gpos_depentencies = depfinder.define(['GPOS']).run()
    # _store(gpos_depentencies, 'gpos', 'datasets_1.1/csvs/column_deptree/')
    # depfinder = FeatureFactory().make('ColumnDepTreeParser', db)
    # func_dependencies = depfinder.define(['FUNC']).run()
    # _store(func_dependencies, 'func', 'datasets_1.1/csvs/column_deptree/')

    # import code; code.interact(local=dict(globals(), **locals()))
    # _process_t(dictdb)

    # predmarker = _process_predicate_marker(db)
    # predmorph = _process_predmorph(db)

    # passivevoice = _process_passivevoice(db)
    # import code; code.interact(local=dict(globals(), **locals()))
