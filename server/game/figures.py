# encoding: utf-8

from __future__ import absolute_import, division, with_statement


class Rect(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Circle(object):

    def __init__(self, x, y, radius, vY=0, vX=0):
        self.x = x
        self.y = y
        self.radius = radius
        self.width = radius
        self.height = radius
        self.vX = vX
        self.vY = vY


def is_object_collision(a, b):
    return a.x + a.width > b.x and a.x < b.x + b.width and \
        a.y + a.height > b.y and a.y < b.y + b.height
