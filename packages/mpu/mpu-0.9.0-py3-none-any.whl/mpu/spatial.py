#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module for spatial datastructures."""


class Point(object):
    """Point in R^n."""

    def __init__(self):
        pass


class AABB(object):
    """
    Axis-Aligned Bounding Box.

    Parameters
    ----------
    points : list
        List of Point objects
    """
