#!/usr/bin/env python
# -*- coding: utf-8 -*-

from psycopg2 import (IntegrityError, InterfaceError, DatabaseError,
                      ProgrammingError)
from psypg_wrap import PgConfig, db_query
