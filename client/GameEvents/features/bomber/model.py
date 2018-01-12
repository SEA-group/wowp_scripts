# Embedded file name: scripts/client/GameEvents/features/bomber/model.py
from __future__ import absolute_import
from GameEventsCommon.db.backends import BundledBackend
from GameEventsCommon.db.model import Model
import _ge_bomber_db
BomberModel = Model(backend=BundledBackend(modules=[_ge_bomber_db]))