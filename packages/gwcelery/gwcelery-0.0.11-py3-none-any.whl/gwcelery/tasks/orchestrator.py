"""Routing of LVAlert messages to other tasks."""
import os

from celery import group

from . import bayestar
from . import circulars
from . import gracedb
from . import lvalert
from . import raven
from . import skymaps
# from .voevent import send


@lvalert.handler('cbc_gstlal',
                 'cbc_pycbc',
                 'cbc_mbtaonline',
                 'cbc_gstlal_mdc',
                 shared=False)
def handle(alert):
    """Parse an LVAlert message and dispatch it to other tasks."""
    # Determine GraceDB ID
    graceid = alert['uid']

    if alert['alert_type'] == 'update' and 'voevent_type' in alert['object']:
        # FIXME: temporarily disable sending GCNs as per P. Brady request
        pass  # send.delay(alert['object']['text'])
    elif alert['alert_type'] == 'update' and alert.get('file'):
        _, versioned_filename = os.path.split(alert['object']['file'])
        filename, _, _ = versioned_filename.rpartition(',')
        filebase, fitsext, _ = filename.rpartition('.fits')
        tags = alert['object']['tag_names']
        if fitsext:
            skymaps.annotate_fits(
                versioned_filename, filebase, graceid, tags).delay()
        elif filename == 'psd.xml.gz':
            group(
                bayestar.bayestar(graceid),
                circulars.create_circular.s(graceid) |
                gracedb.upload.s('circular.txt', graceid,
                                 'Automated circular')
            ).delay()


@lvalert.handler('superevent',
                 'external_fermi',
                 'external_fermi_grb',
                 'external_grb',
                 'external_snews',
                 'external_snews_supernova',
                 'external_swift',
                 shared=False)
def handle_superevents_externaltriggers(alert):
    """Parse an LVAlert message related to superevents/external triggers and
    dispatch it to other tasks."""
    # Determine GraceDb ID
    graceid = alert['uid']

    if alert['alert_type'] == 'new':
        raven.coincidence_search(graceid, alert['object'])
