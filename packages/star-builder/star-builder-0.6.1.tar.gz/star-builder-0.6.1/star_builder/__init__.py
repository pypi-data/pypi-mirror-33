# -*- coding:utf-8 -*-
from .app import Application

from .build import main
from .build.tasks import Task

from .bases.service import Service
from .bases.components import Component
from .bases.repository import Repository
from .bases.response import FileResponse

from .solo import Solo
from .solo.manager import SoloManager

from .console import main as console

from .types import Type, TypeEncoder, validators

from .route import route, get, post, delete, put, options


__version__ = "0.6.1"
