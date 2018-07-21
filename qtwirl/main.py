# Tai Sakuma <tai.sakuma@gmail.com>
import os
import collections
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
           process=4, user_modules=(),
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
        parallel_mode=parallel_mode, quiet=False,
        processes=process,
        user_modules=user_modules,
        dispatcher_options=dispatcher_options)
    eventLoopRunner = alphatwirl.loop.MPEventLoopRunner(parallel.communicationChannel)
    eventBuilderConfigMaker = EventBuilderConfigMaker(treeName=tree_name)
    datasetIntoEventBuildersSplitter = DatasetIntoEventBuildersSplitter(
        EventBuilder=alphatwirl.roottree.BuildEvents,
        eventBuilderConfigMaker=eventBuilderConfigMaker,
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
class EventBuilderConfigMaker(object):
    def __init__(self, treeName,
                 check_files=True, skip_error_files=True):
        self.treeName = treeName
        self.check_files = check_files
        self.skip_error_files = skip_error_files

    def create_configs(self, dataset, file_start_length_list):
        configs = [ ]
        for files, start, length in file_start_length_list:
            config = self.create_config_for(dataset, files, start, length)
            configs.append(config)
        return configs

    def create_config_for(self, dataset, files, start, length):
        config = dict(
            events_class=alphatwirl.roottree.BEvents,
            file_paths=files,
            tree_name=self.treeName,
            max_events=length,
            start=start,
            check_files=self.check_files,
            skip_error_files=self.skip_error_files,
            name=dataset.name, # for the progress report writer
        )
        return config

    def file_list_in(self, dataset, max_files):
        if max_files < 0:
            return dataset.files
        return dataset.files[:min(max_files, len(dataset.files))]

    def nevents_in_file(self, path):
        ret = get_entries_in_tree_in_file(path, tree_name=self.treeName)
        if not self.skip_error_files:
            if ret is None:
                logger = logging.getLogger(__name__)
                msg = 'cannot get the number of events in {}'.format(path)
                logger.error(msg)
                raise RuntimeError(msg)
        return ret

##__________________________________________________________________||
class DatasetIntoEventBuildersSplitter(object):

    def __init__(self, EventBuilder, eventBuilderConfigMaker,
                 max_events=-1, max_events_per_run=-1,
                 max_files=-1, max_files_per_run=1
    ):

        self.EventBuilder = EventBuilder
        self.eventBuilderConfigMaker = eventBuilderConfigMaker
        self.max_events = max_events
        self.max_events_per_run = max_events_per_run
        self.max_files = max_files
        self.max_files_per_run = max_files_per_run

        self.func_get_files_in_dataset = self.eventBuilderConfigMaker.file_list_in
        self.func_get_nevents_in_file = self.eventBuilderConfigMaker.nevents_in_file

    def __repr__(self):
        return '{}(EventBuilder={!r}, eventBuilderConfigMaker={!r}, max_events={!r}, max_events_per_run={!r}, max_files={!r}, max_files_per_run={!r})'.format(
            self.__class__.__name__,
            self.EventBuilder,
            self.eventBuilderConfigMaker,
            self.max_events,
            self.max_events_per_run,
            self.max_files,
            self.max_files_per_run
        )

    def __call__(self, dataset):

        files = self.func_get_files_in_dataset(dataset, max_files=self.max_files)
        # e.g., ['A.root', 'B.root', 'C.root', 'D.root', 'E.root']

        files_start_length_list = create_files_start_length_list(
            files,
            func_get_nevents_in_file=self.func_get_nevents_in_file,
            max_events=self.max_events,
            max_events_per_run=self.max_events_per_run,
            max_files=self.max_files,
            max_files_per_run=self.max_files_per_run
        )
        # (files, start, length)
        # e.g.,
        # [
        #     (['A.root'], 0, 80),
        #     (['A.root', 'B.root'], 80, 80),
        #     (['B.root'], 60, 80),
        #     (['B.root', 'C.root'], 140, 80),
        #     (['C.root'], 20, 10)
        # ]

        configs = self.eventBuilderConfigMaker.create_configs(dataset, files_start_length_list)
        eventBuilders = [self.EventBuilder(c) for c in configs]
        return eventBuilders

##__________________________________________________________________||
