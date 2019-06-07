# Tai Sakuma <tai.sakuma@gmail.com>
import functools

import alphatwirl

from ._parser.inputs import parse_data
from ._parser.readerconfig import expand_reader_config
from ._builder.func import build_reader, create_file_loaders, let_reader_read

##__________________________________________________________________||
__all__ = ['qtwirl']

##__________________________________________________________________||
def qtwirl(data=None,
           reader_cfg=None,
           tree_name=None,
           parallel_mode='multiprocessing',
           dispatcher_options=None,
           process=4, quiet=False,
           user_modules=None,
           max_events=-1, max_files=-1,
           max_events_per_process=-1, max_files_per_process=1,
           skip_error_files=True,
           file_loaders=None):
    """qtwirl (quick-twirl), one-function interface to alphatwirl

    Summarize event data in ``file`` in the way specified by
    ``reader_cfg`` and return the results.

    Parameters
    ----------
    data : str or list of str, optional
        Input file path(s)
    reader_cfg : dict or list of dict
        Reader configuration
    tree_name : str, optional
        The name of tree
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
        The maximum number of events to be processed. No limit if `-1`
        (default).
    max_files : int, optional
        The maximum number of files to be processed. No limit if `-1`
        (default).
    max_events_per_process : int, optional
        The maximum number of events to be processed in each chunk. No
        limit if `-1` (default).
    max_files_per_process : int, optional
        The maximum number of files to be processed in each chunk. No
        limit if `-1` (default).
    skip_error_files, bool, default True
        Skip error files if true
    file_loaders : list of func, optional
        List of file_loaders. If given, the following options will be
        ignored:`data`, `tree_name`, `max_events`,
        `max_events_per_process`, `max_files`,
        `max_files_per_process`, `skip_error_files`

    Returns
    -------
    DataFrame or list of DataFrame
        Summary of event data

    """

    ##
    reader_cfg = expand_reader_config(reader_cfg)
    reader = build_reader(reader_cfg)

    ##
    if dispatcher_options is None:
        dispatcher_options = dict()

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


    ##
    if file_loaders is None:
        files = parse_data(data)
        file_loaders = create_file_loaders(
            files, tree_name=tree_name,
            max_events=max_events,
            max_events_per_run=max_events_per_process,
            max_files=max_files,
            max_files_per_run=max_files_per_process,
            check_files=True,
            skip_error_files=skip_error_files)

    parallel.begin()
    ret = let_reader_read(file_loaders=file_loaders, reader=reader, parallel=parallel)
    parallel.end()

    if isinstance(reader, alphatwirl.loop.ReaderComposite):
        ret = [r for r in ret if r is not None]
    return ret

##__________________________________________________________________||
