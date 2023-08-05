from hashlib import md5
import datetime
import json
import time

import six
from six.moves import xmlrpc_client

from django.http import HttpResponse
import django.core.exceptions
from celery.result import AsyncResult
import yaml


def json_response(obj, status=200):
    """Given a Python object, dump it to JSON and return a Django HttpResponse
    with the contents and proper Content-Type"""
    resp = HttpResponse(json.dumps(obj), status=status)
    resp['Content-Type'] = 'application/json'
    return resp


def get_task_status(task_id):
    """
    Given a task ID, return a dictionary with status information.
    """
    task = AsyncResult(task_id)
    status = {
        'successful': task.successful(),
        'result': str(task.result),  # result can be any picklable object
        'status': task.status,
        'ready': task.ready(),
        'failed': task.failed(),
    }

    if task.failed():
        status['traceback'] = task.traceback
    return status


def clean_task_value(v):
    date_types = datetime.datetime, datetime.date
    if isinstance(v, date_types):
        return v.isoformat()

    sp_types = int, float, tuple, list, dict, bool, type(None)
    sp_types += six.string_types
    if isinstance(v, sp_types):
        return v


def task_to_dict(task):
    """
    Given a Celery TaskState instance, return a JSONable dict with its
    information.
    """
    # Make a copy of task.__dict__, leaving off any of the cached complex
    # objects
    return {
        k: clean_task_value(v)
        for k, v in task.__dict__.items()
        if not k.startswith('_')
    }


def yamlize(dct):
    "Shortcut for convenience."
    return yaml.safe_dump(dct, default_flow_style=False)


def build_swarm_trace_id(swarm):
    return md5(str(swarm) + str(time.time())).hexdigest()


def validate_xmlrpc(data):
    """
    Raise an error if the data can't be
    dumped to XMLRPC format.

    Given that the Supervisor RPC interface can return any proc's config, and
    that some things (like >32 bit ints, or integer keys in dicts) can't be
    marshalled as XML RPC, this check protects the system
    from problems deployed under Supervisor D.
    """
    try:
        xmlrpc_client.dumps((data,), allow_none=True)
    except Exception as e:
        tmpl = "Cannot be marshalled to XMLRPC: %s"
        raise django.core.exceptions.ValidationError(tmpl % e)
    return data
