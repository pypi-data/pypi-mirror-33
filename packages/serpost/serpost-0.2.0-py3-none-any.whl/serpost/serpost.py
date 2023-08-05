# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import sys
from datetime import datetime

from bs4 import BeautifulSoup

if sys.version_info >= (3, 0):
    from urllib.request import urlopen, Request
else:
    from urllib2 import urlopen, Request


TRACKING_URL = 'http://clientes.serpost.com.pe/prj_online/Web_Busqueda.aspx/Consultar_Tracking'
TRACKING_DETAIL_URL = 'http://clientes.serpost.com.pe/prj_online/Web_Busqueda.aspx/Consultar_Tracking_Detalle'


def _make_request(url, payload):
    headers = {
        'Content-Type': 'application/json',
    }
    req = Request(url, headers=headers)
    data = json.dumps(payload).encode('utf8')
    response = urlopen(req, data=data)
    return json.loads(response.read())


def _process_detail(raw):
    soup = BeautifulSoup(raw, 'lxml')
    rows = []
    for row in soup.find_all('tr'):
        cells = []
        for td in row.find_all('td'):
            cells.append(td.text.strip())
        rows.append(cells)

    res = []
    for row in rows:
        place, date_str, message = row
        data = datetime.strptime(date_str, '%d/%m/%Y')
        res.append({
            'date': data,
            'message': message,
            'place': place,
        })
    return sorted(res, key=lambda x: x['date'])


def query_tracking_code(tracking_code):
    """
    Given a tracking_code return a list of events related the tracking code
    """
    payload = {
        'Anio': datetime.now().year,
        'Tracking': tracking_code,
    }
    response = _make_request(TRACKING_URL, payload)

    if not response['d']:
        return []

    data = response['d'][0]

    destination = data['RetornoCadena6']
    payload.update({
        'Destino': destination,
    })

    response = _make_request(TRACKING_DETAIL_URL, payload)
    return _process_detail(response['d']['ResulQuery'])
