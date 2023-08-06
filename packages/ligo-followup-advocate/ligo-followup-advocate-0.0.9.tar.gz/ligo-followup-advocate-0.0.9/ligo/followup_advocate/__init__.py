import os
import shutil
import tempfile
import urllib
import webbrowser

import astropy.time
from ligo.gracedb import rest
import lxml.etree

from .jinja import env
from .version import __version__  # noqa


def authors(authors, service=rest.DEFAULT_SERVICE_URL):
    """Write GCN Circular author list"""
    return env.get_template('authors.txt').render(authors=authors).strip()


def guess_skyloc_pipeline(comments):
    comments = comments.upper()
    skyloc_pipelines = ['cWB', 'BAYESTAR', 'LIB', 'LALInference', 'UNKNOWN']
    for skyloc_pipeline in skyloc_pipelines:
        if skyloc_pipeline.upper() in comments:
            break
    return skyloc_pipeline


def compose(gracedb_id, authors=(), mailto=False,
            service=rest.DEFAULT_SERVICE_URL, client=None):
    """Compose GCN Circular draft"""
    if client is None:
        client = rest.GraceDb(service)
    assert gracedb_id.startswith('S')
    event = client.superevent(gracedb_id).json()
    preferred_event_id = event['preferred_event']
    preferred_event = client.event(preferred_event_id).json()
    voevents = client.voevents(gracedb_id).json()['voevents']
    log = client.logs(gracedb_id).json()['log']
    files = client.files(gracedb_id).json()

    gpstime = float(preferred_event['gpstime'])
    event_time = astropy.time.Time(gpstime, format='gps').utc

    skymaps = {}
    for voevent in voevents:
        root = lxml.etree.fromstring(voevent['text'].encode('utf8'))
        alert_type = root.find(
            './What/Param[@name="AlertType"]').attrib['value'].lower()
        url = root.find('./What/Group/Param[@name="skymap_fits_basic"]')
        if url is None:
            continue
        url = url.attrib['value']
        _, filename = os.path.split(url)
        comments = '\n'.join(entry['comment'].upper() for entry in log
                             if entry['filename'] == filename)
        skyloc_pipeline = guess_skyloc_pipeline(comments)
        issued_time = astropy.time.Time(root.find('./Who/Date').text).datetime
        if filename not in skymaps:
            for message in log:
                if filename == message['filename']:
                    tag_names = message['tag_names']
                    if 'sky_loc' in tag_names and 'lvem' in tag_names:
                        skymaps[filename] = dict(
                            alert_type=alert_type,
                            pipeline=skyloc_pipeline,
                            filename=filename,
                            latency=issued_time-event_time.datetime)
                    break
    skymaps = list(skymaps.values())

    em_brightfile = 'Source_Classification_{0}.json'.format(gracedb_id)
    if em_brightfile in files:
        source_classification = client.files(
            gracedb_id, em_brightfile).json()
    else:
        source_classification = {}

    o = urllib.parse.urlparse(client.service_url)

    kwargs = dict(
        gracedb_id=gracedb_id,
        gracedb_service_url=urllib.parse.urlunsplit(
            (o.scheme, o.netloc, '/superevents/', '', '')),
        group=preferred_event['group'],
        pipeline=preferred_event['pipeline'],
        gpstime='{0:.03f}'.format(round(float(preferred_event['gpstime']), 3)),
        search=preferred_event.get('search', ''),
        far=preferred_event['far'],
        utctime=event_time.iso,
        authors=authors,
        instruments=preferred_event['instruments'].split(','),
        skymaps=skymaps,
        prob_has_ns=source_classification.get('Prob NS2'),
        prob_has_remnant=source_classification.get('Prob EMbright'))

    subject = env.get_template('subject.txt').render(**kwargs).strip()
    body = env.get_template('circular.txt').render(**kwargs).strip()

    if mailto:
        pattern = 'mailto:emfollow@ligo.org,dac@ligo.org?subject={0}&body={1}'
        url = pattern.format(
            urllib.parse.quote(subject),
            urllib.parse.quote(body))
        webbrowser.open(url)
    else:
        return '{0}\n{1}'.format(subject, body)


def read_map_gracedb(path, client):
    import healpy as hp
    with tempfile.NamedTemporaryFile() as localfile:
        remotefile = client.files(*path.split('/'), raw=True)
        try:
            shutil.copyfileobj(remotefile, localfile)
        finally:
            remotefile.close()
        localfile.flush()
        m = hp.read_map(localfile.name, verbose=False)
    return m


def mask_cl(p, level=90):
    import numpy as np
    pflat = p.ravel()
    i = np.flipud(np.argsort(p))
    cs = np.cumsum(pflat[i])
    cls = np.empty_like(pflat)
    cls[i] = cs
    cls = cls.reshape(p.shape)
    return cls <= 1e-2 * level


def compare_skymaps(paths, service=rest.DEFAULT_SERVICE_URL, client=None):
    """Produce table of sky map overlaps"""
    if client is None:
        client = rest.GraceDb(service)
    import healpy as hp
    filenames = [path.split('/')[1] for path in paths]
    pipelines = [guess_skyloc_pipeline(filename) for filename in filenames]
    probs = [read_map_gracedb(path, client) for path in paths]
    npix = max(len(prob) for prob in probs)
    nside = hp.npix2nside(npix)
    deg2perpix = hp.nside2pixarea(nside, degrees=True)
    probs = [hp.ud_grade(prob, nside, power=-2) for prob in probs]
    masks = [mask_cl(prob) for prob in probs]
    areas = [mask.sum() * deg2perpix for mask in masks]
    joint_areas = [(mask & masks[-1]).sum() * deg2perpix for mask in masks]

    kwargs = dict(params=zip(filenames, pipelines, areas, joint_areas))

    return env.get_template('compare_skymaps.txt').render(**kwargs)
