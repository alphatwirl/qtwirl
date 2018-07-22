# Tai Sakuma <tai.sakuma@gmail.com>
import os
import collections
import functools
import logging

import ROOT

import alphatwirl
from alphatwirl.roottree.inspect import get_entries_in_tree_in_file
from alphatwirl.loop.splitfuncs import create_files_start_length_list

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

    Dataset = collections.namedtuple('Dataset', 'name files')
    dataset = Dataset(name='dataset', files=file)

    pairs = create_paris_from_tblcfg([reader_cfg['summarizer']], '')
    reader_top = alphatwirl.loop.ReaderComposite()
    collector_top = alphatwirl.loop.CollectorComposite()
    for r, c in pairs:
        reader_top.add(r)
        collector_top.add(c)

    parallel = alphatwirl.parallel.build_parallel(
        parallel_mode=parallel_mode, quiet=quiet,
        processes=process,
        user_modules=user_modules,
        dispatcher_options=dispatcher_options)
    eventLoopRunner = alphatwirl.loop.MPEventLoopRunner(parallel.communicationChannel)
    create_eventbuilders = EventBuilderMaker(
        EventBuilder=alphatwirl.roottree.BuildEvents,
        treeName=tree_name)
    datasetIntoEventBuildersSplitter = DatasetIntoEventBuildersSplitter(
        func_get_files_in_dataset = functools.partial(get_files_in_dataset, max_files=max_files),
        func_get_nevents_in_file=functools.partial(get_entries_in_tree_in_file, tree_name=tree_name),
        func_create_eventbuilders = create_eventbuilders,
        max_events=max_events,
        max_events_per_run=max_events_per_process,
        max_files=max_files,
        max_files_per_run=max_files_per_process
    )
    eventReader = alphatwirl.loop.EventDatasetReader(
        eventLoopRunner=eventLoopRunner,
        reader=reader_top,
        collector=collector_top,
        split_into_build_events=datasetIntoEventBuildersSplitter
    )

    dataset_readers = alphatwirl.datasetloop.DatasetReaderComposite()
    dataset_readers.add(eventReader)

    parallel.begin()
    eventReader.begin()
    eventReader.read(dataset)
    ret = eventReader.end()
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
    resultsCombinationMethod = alphatwirl.collector.ToDataFrame(
        summaryColumnNames=tblcfg['keyOutColumnNames'] + tblcfg['valOutColumnNames']
    )
    deliveryMethod = None
    collector = alphatwirl.loop.Collector(resultsCombinationMethod, deliveryMethod)
    return reader, collector

##__________________________________________________________________||
class EventBuilderMaker(object):
    def __init__(self, EventBuilder, treeName,
                 check_files=True, skip_error_files=True):
        self.EventBuilder = EventBuilder
        self.treeName = treeName
        self.check_files = check_files
        self.skip_error_files = skip_error_files

    def __call__(self, files_start_length_list):
        configs = self.create_configs(files_start_length_list)
        eventBuilders = [self.EventBuilder(c) for c in configs]
        return eventBuilders

    def create_configs(self, files_start_length_list):
        configs = [ ]
        for files, start, length in files_start_length_list:
            config = self.create_config_for(files, start, length)
            configs.append(config)
        return configs

    def create_config_for(self, files, start, length):
        config = dict(
            events_class=alphatwirl.roottree.BEvents,
            file_paths=files,
            tree_name=self.treeName,
            max_events=length,
            start=start,
            check_files=self.check_files,
            skip_error_files=self.skip_error_files,
        )
        return config

##__________________________________________________________________||
def get_files_in_dataset(dataset, max_files=-1):
    if max_files < 0:
        return dataset.files
    return dataset.files[:min(max_files, len(dataset.files))]

##__________________________________________________________________||
class DatasetIntoEventBuildersSplitter(object):

    def __init__(self,
                 func_get_files_in_dataset,
                 func_get_nevents_in_file,
                 func_create_eventbuilders,
                 max_events=-1, max_events_per_run=-1,
                 max_files=-1, max_files_per_run=1):

        self.func_get_files_in_dataset = func_get_files_in_dataset
        self.func_create_eventbuilders = func_create_eventbuilders

        self.split = functools.partial(
            create_files_start_length_list,
            func_get_nevents_in_file=func_get_nevents_in_file,
            max_events=max_events,
            max_events_per_run=max_events_per_run,
            max_files=max_files,
            max_files_per_run=max_files_per_run
        )

    def __call__(self, dataset):

        files = self.func_get_files_in_dataset(dataset)
        # e.g., ['A.root', 'B.root', 'C.root', 'D.root', 'E.root']

        files_start_length_list = self.split(files)
        # (files, start, length)
        # e.g.,
        # [
        #     (['A.root'], 0, 80),
        #     (['A.root', 'B.root'], 80, 80),
        #     (['B.root'], 60, 80),
        #     (['B.root', 'C.root'], 140, 80),
        #     (['C.root'], 20, 10)
        # ]

        return self.func_create_eventbuilders(files_start_length_list)

##__________________________________________________________________||
