#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Config:
    Settings = None
    DetAddress = '10.10.10.100:41234'
    Readout1 = '0.0023'
    Readout2 = '0.0130'
    Separator = '24'
    ServerDir = '/ramdisk/'
    LogFile = 'pylatus.log'
    UserDir = '/data/users/'
    NoBeamCounts = '10'
    MonitorSpec = 'snbla1.esrf.fr:monitor:mon'
    MusstSpec = 'snbla1.esrf.fr:rhmusst'
    MusstTimeout1 = '0'
    MusstTimeout2 = '0'
    MusstFirmware = '/users/blissadm/local/isg/musst/pilatus_bm01.mprg'
    NumberOfFilters = '10'
    BeamstopOn = '0'
    BeamstopOff = '6'
    RootHash = ''
    Mono = 'mono'
    Phi = 'phi'
    Prphi = 'prphi'
    Omega = 'omega'
    Kappa = 'kappa'
    Bstop = 'bstop'
    Pldistf = 'pldistf'
    Pldistd = 'pldistd'
    Plvert = 'plvert'
    Plrot = 'plrot'
    Prver = 'prver'
    Prhor = 'prhor'
    Filter = 'filter'
    ScanAxis = 'mirror4'
    ScanTime = '0.1'
    ScanRange = '30'
    ScanStep = '24'
    ScanFilter = '7'
    MonitorMult = '1'
    Timescan = '0'
    MonoDspacing = '3.1356'  # Si 111
    MonoOffset = '0'
    MonSecName = 'sec'
    MonMeasTime = '0'
    MusstReadData = False
    AdjustThreshold = False
    RabbitMQAddress = 'localhost'
    ThresholdTimeout = '35'
    ShutterMotor = ''
    ShutterClosed = 150
    ShutterOpen = 75
    ShutterCollimated = 145
