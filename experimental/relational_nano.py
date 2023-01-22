from functools import reduce
import glob
import subprocess, uproot, time, tqdm, os, io, itertools, vector
import tarfile
import numpy as np
import pandas as pd
import dask as dd
from dask.distributed import Client
from sqlalchemy import create_engine
from collections import defaultdict
import logging
import plotly.express as px

logging.basicConfig(level=logging.DEBUG)

def ttree_keys(file):
    out = []
    for obj_name in [k.split(';')[0] for k in file.keys()]:
        class_match = [file.classname_of(obj_name).startswith(classname) for classname in ['TTree']]

        if any(class_match):
            out.append(obj_name)         

    return out 

def get_collection_dict(file, ttree_name):
    tree = file[ttree_name]
    edm_filter = lambda b: 'edm::' not in b.typename

    if len(tree.keys(filter_branch=edm_filter)) == 0:
        return 'Cound not open TTree due to unsupported branches in edm namespace.'

    branch_names = tree.keys(filter_branch=edm_filter) 

    out = defaultdict(list)
    print ('Getting collection dict...')
    for branch_name in tqdm.tqdm(branch_names):
        has_many = tree.typenames()[branch_name].endswith('[]')
        
        if not has_many:
            out['event'].append(branch_name)

        else:
            if '_' in branch_name:
                collection, variable = branch_name.split('_',1)
            else:
                collection, variable = branch_name, branch_name

            out[collection].append(variable)

    for coll_name in out.keys():
        while f'n{coll_name}' in out['event']:
            out['event'].remove(f'n{coll_name}')

    return out

def extract_to_collections(file, ttree_name, nano=False):
    collection_dict = get_collection_dict(file, ttree_name)
    if isinstance(collection_dict, str):
        return None

    tree = file[ttree_name]
    if nano:
        event_array = tree['event'].array(library='np')
    
    out = {}
    print (f'Extracting branches in {ttree_name} to pandas; nano == {nano}')    
    pbar = tqdm.tqdm(collection_dict.items())
    for coll_name, val_names in pbar:
        pbar.set_description(coll_name)

        if (coll_name != 'event') and nano:
            if coll_name != val_names[0]:
                branch_names = [f'{coll_name}_{val_name}' for val_name in val_names]
            else:
                branch_names = [coll_name]

            nobj_array = tree[f'n{coll_name}'].array(library='np')
            arrays = tree.arrays(branch_names, library='np')

            arrays['event'] = np.array([], dtype='object')
            for event, nobj in zip(event_array, nobj_array):
                arrays['event'] = np.append(arrays['event'], np.array([event]*nobj, dtype=np.uint64) )

            branch_names = list(arrays.keys())
            for branch_name in branch_names:
                if '_' in branch_name:
                    val_name = branch_name.split('_',1)[1] # rename to be just 'pt' instead of 'Electron_pt'
                else:
                    val_name = branch_name
                arrays[val_name] = np.hstack(arrays.pop(branch_name))

            out[coll_name] = pd.DataFrame(arrays)

        else:
            if coll_name == 'event' or coll_name == val_names[0]:
                arrays = tree.arrays(val_names, library='np')
            else:
                arrays = tree.arrays([f'{coll_name}_{val_name}' for val_name in val_names], library='np')

        for k,a in arrays.items():
            if a.dtype == np.uint64:
                arrays[k] = a.astype(np.uint32)

        out[coll_name] = pd.DataFrame(arrays)

    return out

def make_relational_sql(filename, output_name='', overwrite=False):
    input_file = uproot.open(filename)
    if not output_name:
        output_name = filename.replace('.root','.db')

    if overwrite:
        subprocess.call(['rm',output_name])
    
    engine = create_engine(f'sqlite:///{output_name}')
    with engine.connect() as conn, conn.begin():
        for ttree_key in ttree_keys(input_file):
            collections = extract_to_collections(input_file, ttree_key, True if ttree_key == 'Events' else False)
            if collections is None:
                continue
            
            for collection, df in collections.items():
                df.to_sql(f'{ttree_key}-{collection}', engine, chunksize=1000)

def make_relational_parquet(filename, output_name='', overwrite=False):
    input_file = uproot.open(filename)
    if not output_name:
        output_name = os.path.expanduser(filename.replace('.root','/'))

    if overwrite:
        subprocess.call(['rm','-rf',output_name])
    
    os.mkdir(output_name)


    for ttree_key in ['Events']:#ttree_keys(input_file):
        collections = extract_to_collections(input_file, ttree_key, True if ttree_key == 'Events' else False)
        if collections is None:
                continue

        for collection, df in collections.items():
            df.to_parquet(f'{output_name}{ttree_key}_{collection}.parquet')

def read_tgz(filename, tree='Events', collections=None):
    file = tarfile.open(filename, 'r:gz')
    out = defaultdict(dict)
    for subfilename in [n for n in file.getnames() if not n.endswith('/')]:
        if subfilename == '.':
            continue
        tree_name, coll_name = subfilename.split('/')[-1].split('.',1)[0].split('_')
        if (collections is None) or (coll_name in collections and tree_name == tree):
            subfile = file.extractfile(subfilename)
            out[tree_name][coll_name] = pd.read_parquet(io.BytesIO(subfile.read()))

    return out

def read_folder(folder, tree='Events', collections=None):
    out = defaultdict(dict)
    for subfilename in [n for n in glob.glob(folder)]:
        logging.debug(subfilename)
        tree_name, coll_name = subfilename.split('/')[-1].split('.',1)[0].split('_')
        if (collections is None) or (coll_name in collections and tree_name == tree):
            logging.debug(f'{tree_name} {coll_name}')
            out[tree_name][coll_name] = dd.dataframe.read_parquet('file://'+subfilename)
    
    return out

def run_bench1(filename):
    '''Plot the MET (missing transverse energy) of all events.'''
    dfs = read_tgz(filename,collections=['event'])
    fig = px.histogram(dfs['Events']['event'], 'MET_sumEt')
    fig.write_image("test_images/fig1.pdf")

def run_bench2(filename):
    '''Plot the pT (transverse momentum) of all jets in all events.'''
    dfs = read_tgz(filename,collections=['Jet'])
    fig = px.histogram(dfs['Events']['Jet'], 'pt')
    fig.write_image("test_images/fig2.pdf")

def run_bench3(filename):
    '''Plot the pT of jets with |eta| < 1 (jet pseudorapidity).'''
    dfs = read_tgz(filename,collections=['Jet'])
    jets = dfs['Events']['Jet']
    jets = jets[abs(jets.eta) < 1.0]
    fig = px.histogram(jets, 'pt')
    fig.write_image("test_images/fig3.pdf")

def run_bench4(filename):
    '''Plot the MET of the events that have at least two jets with pT > 40 GeV.'''
    dfs = read_tgz(filename,collections=['event','Jet'])
    jets = dfs['Events']['Jet']
    events = dfs['Events']['event']

    events_w_jets = jets.groupby('event').filter(lambda j: sum(j.pt > 40) > 1).event.unique()
    events = events[events.event.isin(events_w_jets)]

    fig = px.histogram(events, 'MET_sumEt')
    fig.write_image("test_images/fig4.pdf")

def LVector(*pargs):
    if len(pargs) == 0:
        return vector.obj(pt=0, eta=0, phi=0, m=0)
    elif len(pargs) == 1:
        p = pargs[0]
        return vector.obj(pt=p.pt, eta=p.eta, phi=p.phi, m=p.mass)
    else:
        return reduce(lambda x,y: x+y, [LVector(p) for p in pargs])

def InvariantMass(*plist):
    return LVector(*plist).mass

def extract_rows(df, *idxs):
    return [df.loc[idx,:] for idx in idxs]

def run_bench5(filename):
    '''Plot the MET of events that have an opposite-charge muon pair with an invariant mass between 60 GeV and 120 GeV.'''   
    def opposite_muons(muons):
        muon_combos = []
        for im1, im2 in itertools.combinations(muons.index, 2):
            m1, m2 = extract_rows(muons, im1, im2)
            if m1.charge != m2.charge:
                M = InvariantMass(m1,m2)
                if M > 60 and M < 120:
                    muon_combos.append((m1,m2))

        return len(muon_combos) > 0

    dfs = read_tgz(filename, collections=['event','Muon'])
    muons = dfs['Events']['Muon']
    opposite_muon_events = muons.groupby('event').filter(opposite_muons).event.unique()
    events = dfs['Events']['event']
    events = events[events.event.isin(opposite_muon_events)]

    fig = px.histogram(events, 'MET_sumEt')
    fig.write_image("test_images/fig5.pdf")

def run_bench6(filename):
    '''For events with at least three jets, plot the pT of the trijet system four-momentum
       (i.e., any combination of three distinct jets within the same event) that has the invariant mass
       closest to 172.5 GeV in each event and plot the maximum b-tagging discriminant value among the jets in this trijet.'''
    def get_best_combo(jets):
        best_system = False
        best_mass = 0
        for ij1, ij2, ij3 in itertools.combinations(jets.index, 3):
            j1, j2, j3 = extract_rows(jets, ij1, ij2, ij3)
            if not best_system:
                best_system = [j1, j2, j3]
            else:
                M = InvariantMass(j1,j2,j3)
                if abs(best_mass - 172.5) > abs(M - 172.5):
                    best_system = [j1, j2, j3]
                    best_mass = M

        return dd.DataFrame(best_system)
    
    dfs = read_folder(filename, collections=['event','Jet'])
    print(dfs['Events']['Jet'].shape)
    jets = dfs['Events']['Jet'].groupby('event').filter(lambda j: len(j) > 2)
    print (jets.shape)
    jets = jets.groupby('event', as_index=False).apply(get_best_combo)
    
    trijet_pt = jets.groupby('event').pt.sum()
    figA = px.histogram(trijet_pt, 'pt')
    figA.write_image('test_images/fig6a.pdf')

    max_btag = jets.groupby('event').btagDeepB.max()
    figB = px.histogram(max_btag, 'btagDeepB')
    figB.write_image('test_images/fig6b.pdf')


def run_bench7(filename):
    '''Plot the scalar sum in each event of the pT of the jets with
       pT > 30 GeV that are not within 0.4 in \Delta R of any light
       lepton (i.e., electron or muon) with pT > 10 GeV.'''
    pass

def run_bench8(filename):
    '''For events with at least three light leptons and a same-flavor
       opposite-charge light lepton pair, find such a pair that has the
       invariant mass closest to 91.2 GeV in each event and plot
       the transverse mass of the system, consisting of the missing
       transverse momentum and the highest-pT light lepton not
       in this pair'''
    pass


if __name__ == '__main__':
    start = time.time()
    client = Client()
    print(client.dashboard_link)
    # run_bench1('nano_4.tgz')
    # run_bench2('nano_4.tgz')
    # run_bench3('nano_4.tgz')
    # run_bench4('nano_4.tgz')
    # run_bench5('nano_4.tgz')
    # run_bench6('/home/lucas/CMS/temp/nano_4/*.parquet')
    make_relational_parquet('/home/lucas/Projects/RDFanalyzer/TIMBER/examples/GluGluToHToTauTau_full.root','GluGluToHToTauTau_full',overwrite=True)
    print (f'{(time.time()-start)/60} min')

