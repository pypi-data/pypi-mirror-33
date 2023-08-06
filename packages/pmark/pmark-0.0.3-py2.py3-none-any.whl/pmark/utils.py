# -*- coding: utf-8 -*-
"""
| **@created on:** 30/06/18,
| **@author:** prathyushsp,
| **@version:** v0.0.1
|
| **Description:**
| Utils Module
|
| **Sphinx Documentation Status:** --
|
..todo::
"""
import datetime


def generate_timestamp() -> str:
    """
    | **@author:** Prathyush SP
    |
    | Genetate Timestamp
    :return: Timestamp in String : Format(YYYY-MM-DD_HH:mm:SEC)
    .. todo::
        Prathyush SP:
            1. Support for custom formatting

    """
    # todo: Prathyush SP: Support for custom formatting
    return str(datetime.datetime.now().replace(microsecond=0)).replace(' ', '_').replace(':', '').replace('-', '')
