from django.conf.urls import patterns, url, include

from .resources import v1
from ..urls import procname_re, hostname_re, swarm_re

urlpatterns = patterns(
    'vr.server.api.views',

    # SSE streams
    url(r'^streams/events/', 'event_stream', name='api_events'),
    url(r'^streams/proc_changes/$', 'proc_event_stream',
        name='api_proc_events'),
    url(r'^streams/proc_log/' + hostname_re + '/' + procname_re + '/$',
        'proc_log_stream', name='api_proc_log'),

    # API over Supervisor RPC info
    url(r'^v1/hosts/' + hostname_re + '/procs/$', 'host_procs',
        name='api_host_procs'),
    url(r'^v1/hosts/' + hostname_re + '/procs/' + procname_re + '/$',
        'host_proc', name='api_host_proc'),
    url(r'^v1/swarms/' + swarm_re + '/procs/$', 'swarm_procs',
        name='api_swarm_procs'),

    # Redirector for latest uptest run
    url(r'^v1/testruns/latest/$', 'uptest_latest',
        name='api_testruns_latest'),

    # TASTYPIE DRIVEN API
    (r'^', include(v1.urls)),
)
