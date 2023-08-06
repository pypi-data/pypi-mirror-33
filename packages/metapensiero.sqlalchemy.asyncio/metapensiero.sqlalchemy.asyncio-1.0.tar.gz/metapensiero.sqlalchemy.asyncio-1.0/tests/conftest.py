# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.sqlalchemy.asyncio
# :Creato:    gio 30 lug 2015 08:55:20 CEST
# :Autore:    Lele Gaifax <lele@metapensiero.it>
# :Licenza:   GNU General Public License version 3 or later
#

from os import getenv
import pytest

from metapensiero.sqlalchemy.asyncio import create_engine


DB_URL = getenv('TEST_DB_URL', 'postgresql://localhost/testdb')


@pytest.fixture
def engine(request, event_loop):
    db_url = getattr(request.module, 'db_url', DB_URL)
    return create_engine(db_url, loop=event_loop)
