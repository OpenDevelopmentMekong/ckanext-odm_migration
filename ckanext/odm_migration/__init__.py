# this is a namespace package
import ckan.lib.jobs as jobs
import logging
log = logging.getLogger(__name__)

try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)


DEFAULT_QUEUE_NAME = u'default'
DEFAULT_JOB_TIMEOUT = 180

def custom_enqueue(fn, args=None, kwargs=None, title=None, queue=DEFAULT_QUEUE_NAME,
            timeout=DEFAULT_JOB_TIMEOUT):
    u'''
    Enqueue a job to be run in the background.
    :param function fn: Function to be executed in the background
    :param list args: List of arguments to be passed to the function.
        Pass an empty list if there are no arguments (default).
    :param dict kwargs: Dict of keyword arguments to be passed to the
        function. Pass an empty dict if there are no keyword arguments
        (default).
    :param string title: Optional human-readable title of the job.
    :param string queue: Name of the queue. If not given then the
        default queue is used.
    :param integer timeout: The timeout, in seconds, to be passed
        to the background job via rq.
    :returns: The enqueued job.
    :rtype: ``rq.job.Job``
    '''
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    job = jobs.get_queue(queue).enqueue_call(func=fn, args=args, kwargs=kwargs,
                                        timeout=timeout)
    job.meta[u'title'] = title
    job.save()
    msg = u'Added background job {}'.format(job.id)
    if title:
        msg = u'{} ("{}")'.format(msg, title)
    msg = u'{} to queue "{}"'.format(msg, queue)
    log.info(msg)
    return job

jobs.enqueue = custom_enqueue
