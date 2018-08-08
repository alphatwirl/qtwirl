# Tai Sakuma <tai.sakuma@gmail.com>
import os
import copy
import collections
import functools
import itertools
import logging

import pandas as pd

import ROOT

import alphatwirl
from alphatwirl.roottree.inspect import get_entries_in_tree_in_file
from alphatwirl.loop.splitfuncs import create_files_start_length_list
from alphatwirl.loop.merge import merge_in_order

from ._parser import parse_file, parse_reader_cfg, complete_table_cfg, _is_dict

##__________________________________________________________________||
__all__ = ['qtwirl']

##__________________________________________________________________||
def qtwirl(file, reader_cfg,
           tree_name=None,
           parallel_mode='multiprocessing',
           dispatcher_options=None,
           process=4, quiet=True,
           user_modules=None,
           max_events=-1, max_files=-1,
           max_events_per_process=-1, max_files_per_process=1,
           skip_error_files=True):
    """qtwirl (quick-twirl), one-function interface to alphatwirl

    Summarize event data in ``file`` in the way specified by
    ``reader_cfg`` and return the results.

    Parameters
    ----------
    file : str or list of str
        Input file path(s)
    reader_cfg : dict or list of dict
        Reader configuration
    parallel_mode : str, optional
        "multiprocessing" (default) or "htcondor"
    dispatcher_options : dict, optional
        Options to dispatcher
    process : int, optional
        The number of processes when ``parallel_mode`` is
        "multiprocessing"
    quiet : bool, optional
    user_modules : list, optional
        The names of modules to be sent to worker nodes when
        parallel_mode is "htcondor"
    max_events : int, optional
    max_files : int, optional
    max_events_per_process : int, optional
    max_files_per_process : int, optional
    skip_error_files, bool, default True

    Returns
    -------
    DataFrame or list of DataFrame
        Summary of event data

    """

    ##
    files = parse_file(file)

    ##
    reader = create_reader(reader_cfg)

    ##
    if dispatcher_options is None:
        dispatcher_options=dict()


    ##
    default_user_modules = ('qtwirl', 'alphatwirl')
    if user_modules is None:
        user_modules = ()
    user_modules = set(user_modules)
    user_modules.update(default_user_modules)

    ##
    parallel = alphatwirl.parallel.build_parallel(
        parallel_mode=parallel_mode, quiet=quiet,
        processes=process,
        user_modules=user_modules,
        dispatcher_options=dispatcher_options)
    func_create_file_loaders = functools.partial(
        create_file_loaders,
        tree_name=tree_name,
        max_events=max_events, max_events_per_run=max_events_per_process,
        max_files=max_files, max_files_per_run=max_files_per_process,
        check_files=True, skip_error_files=skip_error_files)
    read_files = functools.partial(
        let_reader_read, reader=reader, parallel=parallel,
        func_create_file_loaders=func_create_file_loaders)

    parallel.begin()
    ret = read_files(files=files)
    parallel.end()

    if isinstance(reader, alphatwirl.loop.ReaderComposite):
        ret = [r for r in ret if r is not None]
    return ret

##__________________________________________________________________||
def create_reader(cfg):
    cfg = parse_reader_cfg(cfg)
    if _is_dict(cfg):
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
        return alphatwirl.selection.build_selection(path_cfg=val)
    elif key == 'reader':
        return val
    else:
        return None

##__________________________________________________________________||
def create_reader_from_table_cfg(cfg):
    cfg = complete_table_cfg(cfg)
    return build_counter(cfg)

##__________________________________________________________________||
def build_counter(tblcfg):
    echo = alphatwirl.binning.Echo(nextFunc=None)
    binnings = tblcfg['binnings']
    if binnings:
        binnings = tuple(b if b else echo for b in binnings)
    keyValComposer = alphatwirl.summary.KeyValueComposer(
        keyAttrNames=tblcfg['keyAttrNames'],
        binnings=binnings,
        keyIndices=tblcfg['keyIndices'],
        valAttrNames=tblcfg['valAttrNames'],
        valIndices=tblcfg['valIndices']
    )
    nextKeyComposer = alphatwirl.summary.NextKeyComposer(binnings) if binnings is not None else None
    summarizer = alphatwirl.summary.Summarizer(
        Summary=tblcfg['summaryClass']
    )
    reader = alphatwirl.summary.Reader(
        keyValComposer=keyValComposer,
        summarizer=summarizer,
        collector=functools.partial(
            collect_results_into_dataframe,
            columns=tblcfg['keyOutColumnNames'] + tblcfg['summaryColumnNames']),
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
