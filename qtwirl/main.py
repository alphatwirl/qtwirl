# Tai Sakuma <tai.sakuma@gmail.com>
import os
import collections

import ROOT

import alphatwirl
from alphatwirl.roottree.inspect import is_ROOT_null_pointer

##__________________________________________________________________||
def qtwirl(file, reader_cfg,
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
    datasets = [Dataset(name='dataset', files=file)]

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
    eventBuilderConfigMaker = EventBuilderConfigMaker()
    datasetIntoEventBuildersSplitter = alphatwirl.loop.DatasetIntoEventBuildersSplitter(
        EventBuilder=alphatwirl.roottree.BEventBuilder,
        eventBuilderConfigMaker=eventBuilderConfigMaker,
        maxEvents=max_events,
        maxEventsPerRun=max_events_per_process,
        maxFiles=max_files,
        maxFilesPerRun=max_files_per_process
    )
    eventReader = alphatwirl.loop.EventDatasetReader(
        eventLoopRunner=eventLoopRunner,
        reader=reader_top,
        collector=collector_top,
        split_into_build_events=datasetIntoEventBuildersSplitter
    )

    dataset_readers = alphatwirl.datasetloop.DatasetReaderComposite()
    dataset_readers.add(eventReader)

    if parallel_mode in ('subprocess', 'htcondor'):
        loop = alphatwirl.datasetloop.ResumableDatasetLoop(
            datasets=datasets, reader=dataset_readers,
            workingarea=parallel.workingarea
        )
    else:
        loop = alphatwirl.datasetloop.DatasetLoop(
            datasets=datasets,
            reader=dataset_readers
        )

    parallel.begin()
    ret = loop()
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
EventBuilderConfig = collections.namedtuple(
    'EventBuilderConfig',
    'inputPaths treeName maxEvents start name'
)

##__________________________________________________________________||
class EventBuilderConfigMaker(object):
    def __init__(self, treeName='Events'):
        self.treeName = treeName

    def create_config_for(self, dataset, files, start, length):
        config = EventBuilderConfig(
            inputPaths=files,
            treeName=self.treeName,
            maxEvents=length,
            start=start,
            name=dataset.name # for the progress report writer
        )
        return config

    def file_list_in(self, dataset, maxFiles):
        if maxFiles < 0:
            return dataset.files
        return dataset.files[:min(maxFiles, len(dataset.files))]

    def nevents_in_file(self, path):
        file_ = ROOT.TFile.Open(path)
        if is_ROOT_null_pointer(file_) or file_.IsZombie():
            logger = logging.getLogger(__name__)
            if self.skip_error_files:
                logger.warning('cannot open {}'.format(path))
                return 0
            logger.error('cannot open {}'.format(path))
            raise OSError('cannot open {}'.format(path))
        tree = file_.Get(self.treeName)
        return tree.GetEntriesFast()

##__________________________________________________________________||
