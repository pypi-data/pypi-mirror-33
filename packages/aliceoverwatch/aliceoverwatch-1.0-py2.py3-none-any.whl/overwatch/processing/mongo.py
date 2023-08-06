#!/usr/bin/env python

import mongoengine

# Determine choices
hltModes = ()

# Main class
class timeFrame(mongoengine.Document):
    timeStamp = mongoengine.DateTimeFiled(required = True)
    runNumber = mongoengine.Float(required = True)
    subsystems = mongoengine.List(required = True)
    hltMode = mongoengine.Title(required = True, choices = hltModes)

class run(mongoengine.Document):
    runNumber = mongoengine.Title(required = True)

    #self.runDir = runDir
    #self.runNumber = int(runDir.replace("Run", ""))
    #self.prettyName = "Run {0}".format(self.runNumber)
    #self.mode = fileMode
    #self.subsystems = BTrees.OOBTree.BTree()
    #self.hltMode = hltMode

class runContainer(object):
    def __init__(self, run):
        self.runDir = run.runDir
        self.runNumber = int(run.runDir.replace("Run", ""))
        self.prettyName = "Run {0}".format(self.runNumber)
        self.mode = run.fileMode

