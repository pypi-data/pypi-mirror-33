"""Celery application configuration."""

from celery import Celery


class Base:
    """Base application configuration."""

    # Celery application settings.
    # Use pickle serializer, because it supports byte values.

    accept_content = ['json', 'pickle']
    event_serializer = 'json'
    result_serializer = 'pickle'
    task_serializer = 'pickle'

    # GWCelery-specific settings.

    gcn_bind_address = ''
    """Address on which to listen for outbound (sending) connections to GCN;
    empty to listen on all addresses."""

    gcn_bind_port = 5341
    """Port on which to listen for outbound (sending) connections to GCN."""

    gcn_remote_address = 'capella2.gsfc.nasa.gov'
    """Address to listen for inbound (receiving) connections to GCN."""

    superevent_d_t_start = dict(gstlal=1.0,
                                pycbc=1.0,
                                mbtaonline=1.0)
    """Pipeline based lower extent of superevent segments.
    For cwb and lib this is decided from extra attributes."""

    superevent_d_t_end = dict(gstlal=1.0,
                              pycbc=1.0,
                              mbtaonline=1.0)
    """Pipeline based upper extent of superevent segments
    For cwb and lib this is decided from extra attributes."""

    superevent_query_d_t_start = 100.
    """Lower extent of superevents query"""

    superevent_query_d_t_end = 100.
    """Upper extent of superevents query"""

    superevent_default_d_t_start = 1.0
    """Default lower extent of superevent segments"""

    superevent_default_d_t_end = 1.0
    """Default upper extent for superevent segments"""

    superevent_far_threshold = 1.9e-07
    """Maximum false alarm rate to consider events superevents."""


class Production(Base):
    """Application configuration for ``gracedb.ligo.org``."""

    external_trigger_event_type = 'External'
    """GraceDb group for external triggers (e.g. GRBs, SNe, neutrinos)."""

    lvalert_host = 'lvalert.cgca.uwm.edu'
    """LVAlert host."""

    gracedb_host = 'gracedb.ligo.org'
    """GraceDb host."""


class Test(Base):
    """Application configuration for ``gracedb-test.ligo.org``."""

    external_trigger_event_type = 'Test'
    """GraceDb group for external triggers (e.g. GRBs, SNe, neutrinos)."""

    lvalert_host = 'lvalert-test.cgca.uwm.edu'
    """LVAlert host."""

    gracedb_host = 'gracedb-test.ligo.org'
    """GraceDb host."""


class Development(Test):
    """Application configuration for ``gracedb-dev1.ligo.org``."""

    gracedb_host = 'gracedb-dev1.ligo.org'
    """GraceDb host."""


class Playground(Test):
    """Application configuration for ``gracedb-playground.ligo.org``."""

    gracedb_host = 'gracedb-playground.ligo.org'
    """GraceDb host."""


# Celery application object.
# Use redis broker, because it supports locks (and thus singleton tasks).
app = Celery('gwcelery', broker='redis://', config_source=Playground)

# Use the same URL for both the result backend and the broker.
app.conf['result_backend'] = app.conf.broker_url
