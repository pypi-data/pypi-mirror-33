#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import hashlib
from .config import Config


LAMBDA = 12.398419739640717  # c * h / ev * 1e7
DEFAULT_WAVELENGTH = 0.7  # Mo K-alpha
DEFAULT_MONODSPACING = 3.1356  # Si 111


def wavelength_energy(mono):
    """mono angle --> wavelength, energy"""
    if Config.MonoDspacing:
        offset = float(Config.MonoOffset) if Config.MonoOffset else 0
        wl = 2 * float(Config.MonoDspacing) * math.sin(math.radians(mono + offset))
    else:
        wl = DEFAULT_WAVELENGTH
    en = LAMBDA / wl
    return wl, en


def wavelength(mono):
    """mono angle --> wavelength"""
    return wavelength_energy(mono)[0]


def energy(mono):
    """mono angle --> energy"""
    return wavelength_energy(mono)[1]


def angle(wl):
    """wavelength --> mono angle"""
    if Config.MonoDspacing:
        d = float(Config.MonoDspacing)
    else:
        d = DEFAULT_MONODSPACING
    return math.degrees(math.asin(wl / d / 2))


def hash_pass(password):
    return hashlib.sha1(password.encode('utf8', errors='ignore')).hexdigest()
