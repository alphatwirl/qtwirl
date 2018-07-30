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
           dispatcher_options=dict(),
           process=4, quiet=False,
           user_modules=(),
           max_events=-1, max_files=-1,
           max_events_per_process=-1, max_files_per_process=1):
    """qtwirl (quick-twirl), a one-function interface to alphatwirl

    Args:
        file:
        reader_cfg:

    Returns:
        a list of results of readers

    """

    files = parse_file(file)

    reader = create_reader(reader_cfg)

    parallel = alphatwirl.parallel.build_parallel(
        parallel_mode=parallel_mode, quiet=quiet,
        processes=process,
        user_modules=user_modules,
        dispatcher_options=dispatcher_options)
    eventLoopRunner = alphatwirl.loop.MPEventLoopRunner(parallel.communicationChannel)
    func_create_fileloaders = functools.partial(
        create_fileloaders,
        tree_name=tree_name,
        max_events=max_events, max_events_per_run=max_events_per_process,
        max_files=max_files, max_files_per_run=max_files_per_process,
        check_files=True, skip_error_files=True)
    eventReader = EventReader(
        eventLoopRunner=eventLoopRunner,
        reader=reader,
        split_into_build_events=func_create_fileloaders,
    )

    parallel.begin()
    ret = eventReader.read(files=files)
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
    keyValComposer = alphatwirl.summary.KeyValueComposer(
        keyAttrNames=tblcfg['keyAttrNames'],
        binnings=tblcfg['binnings'],
        keyIndices=tblcfg['keyIndices'],
        valAttrNames=tblcfg['valAttrNames'],
        valIndices=tblcfg['valIndices']
    )
    nextKeyComposer = alphatwirl.summary.NextKeyComposer(tblcfg['binnings']) if tblcfg['binnings'] is not None else None
    summarizer = alphatwirl.summary.Summarizer(
        Summary=tblcfg['summaryClass']
    )
    collector = Collector(
        summaryColumnNames=tblcfg['keyOutColumnNames'] + tblcfg['summaryColumnNames']
    )
    reader = alphatwirl.summary.Reader(
        keyValComposer=keyValComposer,
        summarizer=summarizer,
        collector=collector,
        nextKeyComposer=nextKeyComposer,
        weightCalculator=tblcfg['weight'],
        nevents=tblcfg['nevents']
    )
    return reader

##__________________________________________________________________||
def create_fileloaders(
        files, tree_name,
        max_events=-1, max_events_per_run=-1,
        max_files=-1, max_files_per_run=1,
        check_files=True, skip_error_files=False):

        func_get_nevents_in_file = functools.partial(
            get_entries_in_tree_in_file, tree_name=tree_name)

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
class EventReader(object):
    def __init__(self, eventLoopRunner, reader,
                 split_into_build_events):

        self.eventLoopRunner = eventLoopRunner
        self.reader = reader
        self.split_into_build_events = split_into_build_events

        self.EventLoop = alphatwirl.loop.EventLoop

        self.runids = [ ]

        name_value_pairs = (
            ('eventLoopRunner', self.eventLoopRunner),
            ('reader', self.reader),
            ('split_into_build_events', self.split_into_build_events),
        )
        self._repr = '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{}={!r}'.format(n, v) for n, v in name_value_pairs]),
        )

    def __repr__(self):
        return self._repr

    def read(self, files):
        self.eventLoopRunner.begin()

        build_events_list = self.split_into_build_events(files)
        njobs = len(build_events_list)
        eventLoops = [ ]
        for i, build_events in enumerate(build_events_list):
            reader = copy.deepcopy(self.reader)
            eventLoop = self.EventLoop(build_events, reader, '{} / {}'.format(i, njobs))
            eventLoops.append(eventLoop)
        runids = self.eventLoopRunner.run_multiple(eventLoops)
        # e.g., [0, 1, 2]

        runid_reader_map = collections.OrderedDict([(i, None) for i in runids])
        # e.g., OrderedDict([(0, None), (1, None), (2, None)])

        runids_towait = runids[:]
        while runids_towait:
            runid, reader = self.eventLoopRunner.receive_one()
            merge_in_order(runid_reader_map, runid, reader)
            runids_towait.remove(runid)

        # assert 1 == len(runid_reader_map)
        reader = list(runid_reader_map.values())[0]
        return reader.collect()

##__________________________________________________________________||
class Collector(object):
    def __init__(self, summaryColumnNames):
        self.summaryColumnNames = summaryColumnNames

    def __repr__(self):
        name_value_pairs = (
            ('summaryColumnNames', self.summaryColumnNames),
        )
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{} = {!r}'.format(n, v) for n, v in name_value_pairs]),
        )

    def __call__(self, reader):
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
        return pd.DataFrame(tuple_list, columns=self.summaryColumnNames)

##__________________________________________________________________||
