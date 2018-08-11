# Tai Sakuma <tai.sakuma@gmail.com>
import copy
import collections
import functools

import pandas as pd

import alphatwirl
from alphatwirl.roottree.inspect import get_entries_in_tree_in_file
from alphatwirl.loop.splitfuncs import create_files_start_length_list
from alphatwirl.loop.merge import merge_in_order

from .._misc import is_dict

##__________________________________________________________________||
def create_reader(cfg):
    if is_dict(cfg):
        return _create_reader_for_single_cfg(cfg)
    readers = [_create_reader_for_single_cfg(c) for c in cfg]
    ret = alphatwirl.loop.ReaderComposite(readers=readers)
    return ret

def _create_reader_for_single_cfg(cfg):
    # cfg is a dict with one item
    key, val = list(cfg.items())[0]
    if key == 'table_cfg':
        return create_reader_from_table_cfg(val)
    elif key == 'selection_cfg':
        return alphatwirl.selection.build_selection(path_cfg=val['condition'])
    elif key == 'reader':
        return val
    else:
        return None

##__________________________________________________________________||
def create_reader_from_table_cfg(cfg):
    return build_counter(cfg)

##__________________________________________________________________||
def build_counter(tblcfg):
    echo = alphatwirl.binning.Echo(nextFunc=None)
    binnings = tblcfg['key_binning']
    if binnings:
        binnings = tuple(b if b else echo for b in binnings)
    keyValComposer = alphatwirl.summary.KeyValueComposer(
        keyAttrNames=tblcfg['key_name'],
        binnings=binnings,
        keyIndices=tblcfg['key_index'],
        valAttrNames=tblcfg['val_name'],
        valIndices=tblcfg['val_index']
    )
    nextKeyComposer = alphatwirl.summary.NextKeyComposer(binnings) if binnings is not None else None
    summarizer = alphatwirl.summary.Summarizer(
        Summary=tblcfg['agg_class']
    )
    reader = alphatwirl.summary.Reader(
        keyValComposer=keyValComposer,
        summarizer=summarizer,
        collector=functools.partial(
            collect_results_into_dataframe,
            columns=tblcfg['key_out_name'] + tblcfg['agg_name']),
        nextKeyComposer=nextKeyComposer,
        weightCalculator=tblcfg['weight'],
        nevents=tblcfg['nevents']
    )
    return reader

##__________________________________________________________________||
def create_file_loaders(
        files, tree_name,
        max_events=-1, max_events_per_run=-1,
        max_files=-1, max_files_per_run=1,
        check_files=True, skip_error_files=False):

        func_get_nevents_in_file = functools.partial(
            get_entries_in_tree_in_file,
            tree_name=tree_name,
            raises=not skip_error_files
        )

        files_start_length_list = create_files_start_length_list(
            files,
            func_get_nevents_in_file=func_get_nevents_in_file,
            max_events=max_events,
            max_events_per_run=max_events_per_run,
            max_files=max_files,
            max_files_per_run=max_files_per_run
        )
        # list of (files, start, length), e.g.,
        # [
        #     (['A.root'], 0, 80),
        #     (['A.root', 'B.root'], 80, 80),
        #     (['B.root'], 60, 80),
        #     (['B.root', 'C.root'], 140, 80),
        #     (['C.root'], 20, 10)
        # ]

        ret = [ ]
        for files, start, length in files_start_length_list:
            config = dict(
                events_class=alphatwirl.roottree.BEvents,
                file_paths=files,
                tree_name=tree_name,
                max_events=length,
                start=start,
                check_files=check_files,
                skip_error_files=skip_error_files,
            )
            ret.append(alphatwirl.roottree.BuildEvents(config))
        return ret

##__________________________________________________________________||
def let_reader_read(files, reader, parallel, func_create_file_loaders):
    eventLoopRunner = alphatwirl.loop.MPEventLoopRunner(parallel.communicationChannel)
    eventLoopRunner.begin()

    file_loaders = func_create_file_loaders(files)
    njobs = len(file_loaders)
    eventLoops = [ ]
    for i, file_loader in enumerate(file_loaders):
        reader_copy = copy.deepcopy(reader)
        eventLoop = alphatwirl.loop.EventLoop(file_loader, reader_copy, '{} / {}'.format(i, njobs))
        eventLoops.append(eventLoop)
    runids = eventLoopRunner.run_multiple(eventLoops)
    # e.g., [0, 1, 2]

    runid_reader_map = collections.OrderedDict([(i, None) for i in runids])
    # e.g., OrderedDict([(0, None), (1, None), (2, None)])

    runids_towait = runids[:]
    while runids_towait:
        runid, reader_returned = eventLoopRunner.receive_one()
        merge_in_order(runid_reader_map, runid, reader_returned)
        runids_towait.remove(runid)

    if runid_reader_map:
        # assert 1 == len(runid_reader_map)
        reader = list(runid_reader_map.values())[0]
    return reader.collect()

##__________________________________________________________________||
def collect_results_into_dataframe(reader, columns):
    tuple_list = reader.summarizer.to_tuple_list()
    # e.g.,
    # ret = [
    #         (200, 2, 120, 240),
    #         (300, 2, 490, 980),
    #         (300, 3, 210, 420)
    #         (300, 2, 20, 40),
    #         (300, 3, 15, 30)
    # ]

    if tuple_list is None:
        return None
    return pd.DataFrame(tuple_list, columns=columns)

##__________________________________________________________________||
