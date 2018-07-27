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

    pairs = create_paris_from_tblcfg(reader_cfg['summarizer'], '')
    reader_top = alphatwirl.loop.ReaderComposite()
    collector_top = CollectorComposite()
    for r, c in pairs:
        reader_top.add(r)
        collector_top.add(c)

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
        reader=reader_top,
        collector=collector_top,
        split_into_build_events=func_create_fileloaders,
    )

    parallel.begin()
    ret = eventReader.read(files=file)
    parallel.end()

    return ret

##__________________________________________________________________||
def create_paris_from_tblcfg(tblcfg, outdir):

    tableConfigCompleter = alphatwirl.configure.TableConfigCompleter(
        defaultSummaryClass=alphatwirl.summary.Count,
        defaultOutDir=outdir,
        createOutFileName=alphatwirl.configure.TableFileNameComposer(default_prefix='tbl_n.dataset')
    )

    tblcfg = [tableConfigCompleter.complete(c) for c in tblcfg]

    # do not recreate tables that already exist unless the force option is used
    tblcfg = [c for c in tblcfg if c['outFile'] and not os.path.exists(c['outFilePath'])]

    ret = [build_counter_collector_pair(c) for c in tblcfg]
    return ret

##__________________________________________________________________||
def build_counter_collector_pair(tblcfg):
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
    reader = alphatwirl.summary.Reader(
        keyValComposer=keyValComposer,
        summarizer=summarizer,
        nextKeyComposer=nextKeyComposer,
        weightCalculator=tblcfg['weight'],
        nevents=tblcfg['nevents']
    )
    resultsCombinationMethod = ToDataFrame(
        summaryColumnNames=tblcfg['keyOutColumnNames'] + tblcfg['valOutColumnNames']
    )
    deliveryMethod = None
    collector = alphatwirl.loop.Collector(resultsCombinationMethod, deliveryMethod)
    return reader, collector

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
    def __init__(self, eventLoopRunner, reader, collector,
                 split_into_build_events):

        self.eventLoopRunner = eventLoopRunner
        self.reader = reader
        self.collector = collector
        self.split_into_build_events = split_into_build_events

        self.EventLoop = alphatwirl.loop.EventLoop

        self.runids = [ ]

        name_value_pairs = (
            ('eventLoopRunner', self.eventLoopRunner),
            ('reader', self.reader),
            ('collector', self.collector),
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

        Dataset = collections.namedtuple('Dataset', 'name files')
        dataset = Dataset(name='dataset', files=files)

        build_events_list = self.split_into_build_events(files)
        eventLoops = [ ]
        for build_events in build_events_list:
            reader = copy.deepcopy(self.reader)
            eventLoop = self.EventLoop(build_events, reader, dataset.name)
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
        reader = runid_reader_map.values()[0]
        dataset_readers_list = [(dataset.name, reader)]

        return self.collector.collect(dataset_readers_list)

##__________________________________________________________________||
class CollectorComposite(object):

    """A composite of collectors.

    This class is a composite in the composite pattern.

    Examples of collectors are instances of `Collector`,
    `NullCollector`, and this class.

    """

    def __init__(self):

        self.components = [ ]

    def __repr__(self):
        name_value_pairs = (
            ('components',       self.components),
        )
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{}={!r}'.format(n, v) for n, v in name_value_pairs]),
        )

    def add(self, collector):
        """add a collector


        Args:
            collector: the collector to be added

        """
        self.components.append(collector)

    def collect(self, dataset_readers_list):
        """collect results


        Returns:
            a list of results

        """

        ret = [ ]
        for i, collector in enumerate(self.components):
            report = alphatwirl.progressbar.ProgressReport(name='collecting results', done=(i + 1), total=len(self.components))
            alphatwirl.progressbar.report_progress(report)
            ret.append(collector.collect([(d, (r.readers[i], )) for d, r in dataset_readers_list ]))
        return ret


class ToTupleList(object):
    def __init__(self, summaryColumnNames
                 ):

        self.summaryColumnNames = summaryColumnNames

    def __repr__(self):

        name_value_pairs = (
            ('summaryColumnNames', self.summaryColumnNames),
        )
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{} = {!r}'.format(n, v) for n, v in name_value_pairs]),
        )

    def combine(self, dataset_readers_list):


        if len(dataset_readers_list) == 0: return None

        # e.g.,
        # dataset_readers_list = [
        #     ('QCD',    (reader1, reader2)),
        #     ('TTJets', (reader3, )),
        #     ('WJets',  (reader4, )),
        #     ('ZJets',  ( )),
        # ]

        readers_list = itertools.chain(*(r for _, r in dataset_readers_list))
        # e.g.,
        # readers_list = (reader1, reader2, reader3, reader4)

        summarizers_list = (r.results() for r in readers_list)
        # e.g.,
        # summarizers_list = (summarizer1, summarizer2, summarizer3, summarizer4)

        summarizer = sum(summarizers_list)

        ret = summarizer.to_tuple_list()
        # e.g.,
        # ret = [
        #         (200, 2, 120, 240),
        #         (300, 2, 490, 980),
        #         (300, 3, 210, 420)
        #         (300, 2, 20, 40),
        #         (300, 3, 15, 30)
        # ]

        ret.insert(0, self.summaryColumnNames)
        # e.g.,
        # [
        #     ('htbin', 'njetbin', 'n', 'nvar'),
        #     (    200,         2, 120,    240),
        #     (    300,         2, 490,    980),
        #     (    300,         3, 210,    420),
        #     (    300,         2,  20,     40),
        #     (    300,         3,  15,     30)
        # ]

        return ret

class ToDataFrame(object):
    def __init__(self, summaryColumnNames):

        self.summaryColumnNames = summaryColumnNames
        self.to_tuple_list = ToTupleList(summaryColumnNames = summaryColumnNames)

    def __repr__(self):

        name_value_pairs = (
            ('summaryColumnNames', self.summaryColumnNames),
        )
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{} = {!r}'.format(n, v) for n, v in name_value_pairs]),
        )

    def combine(self, dataset_readers_list):
        tuple_list = self.to_tuple_list.combine(dataset_readers_list)
        if tuple_list is None:
            return None
        header = tuple_list[0]
        contents = tuple_list[1:]
        return pd.DataFrame(contents, columns = header)

##__________________________________________________________________||
