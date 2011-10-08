#!/usr/bin/python
from wsgiref.handlers import CGIHandler
from cdRack import app

CGIHandler().run(app)
