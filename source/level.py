from misc import Rectangle, worldToScreen
from ship import *
import os
import re
from random import *
from math import *

from boss3 import *


class Level(object):
    """
    This class is used to build the level for the game
    """

    def __init__(self, difficulty, world, org):
        # dictionnary used to match the string and the class
        self.dico = {'StandingEnnemies': StandingEnnemies,
                     'BasicShit': BasicShit,
                     'AngryBird': AngryBird,
                     'Carrier': Carrier,
                     'SmallWall': SmallWall,
                     'Boss3': Boss3}
        # this list will contain ennemies of the random level
        self.level = []
        # initialize by loading informations of dcbbf files
        self.loadedblocks = load_blocks()
        # blocks extracted in the dcbbf files
        self.levelblocks = []
        # difficulty of the level
        self.difficulty = difficulty
        self.world = world
        self.org = org

    def joinblocks(self, lg):
        """
        Function used to join blocks randomely chosen among the loaded blocks
        which difficulty match with the given difficulty. Selected blocks
        are in the self.levelblocks list
        """

        d, dBoss = getfdict(self.loadedblocks, self.difficulty), getfdictBoss(self.loadedblocks)

        for i in range(lg):
            self.levelblocks += [getrandomblock(d)]
        self.levelblocks += [getrandomblock(dBoss)]

    def makelevel(self, lg=6):
        """
        Function used to make the level by using informations in the self.levelblocks
        list to create of the ennemies within the selected blocks. The default number
        of blocks in a random level is 6, this number could be changed when the Function
        is called
        """

        n = 1
        self.joinblocks(lg)
        for blk in self.levelblocks:
            for enn in blk.enns:
                en = self.dico[enn[0]](self.world, Rectangle(int(enn[1]), int(
                    enn[2]) - n * 1000 + self.org, self.dico[enn[0]].wh[0], self.dico[enn[0]].wh[1]))
                self.level += [en]
            n += 1
        self.level = sorted(self.level, key=lambda en: en.hitbox.y, reverse=True)


class Blocks(object):
    """
    This class is used to memorize informations within dcbbf files
    """

    def __init__(self, difficulty, rarity, enns):
        if int(difficulty) >= 0:
            self.difficulty = int(difficulty)
            self.rarity = int(rarity[int(self.difficulty)])
            self.enns = enns
        else:
            self.difficulty = int(difficulty)
            self.rarity = int(rarity[abs(int(difficulty)) - 1])
            self.enns = enns


def cumsum(l):
    """
    This function used to make the cumulative sum of a list of numbers
    """

    tot = 0
    sums = []
    for v in l:
        tot += v
        sums.append(tot)
    return sums


def load_blocks():
    """
    This functions used to load of the blocks contained in the
    dcbbf files
    """

    lblocks = []
    for element in os.listdir('ressources/blocks'):
        if re.search(r'\.dcbbf', element) != None:
            block = open('ressources/blocks/' + element)
            # insérer un try pour contrôler les exceptions avec des fichiers de mauvais formats
            diff = (block.readline().split())[0]
            rarity = (block.readline().split())
            line = block.readline().split()
            enns = []
            while line != []:
                enns += [line]
                line = block.readline().split()
                lblocks += [Blocks(diff, rarity, enns)]
    return lblocks


def getfdict(blocks, difficulty):
    """
    Function used to get the apparition's frequency of some blocks
    for a given difficulty, it build a dictionnary with block as key and
    frequency as value
    """

    d = {}
    gr = 0
    for blk in blocks:
        if blk.difficulty <= difficulty and blk.difficulty > -1:
            gr += blk.rarity
            d[blk] = blk.rarity
    for it in d:
        d[it] = d[it] / gr
    return d


def getfdictBoss(blocks):
    """
    Function used to get the apparition's frequency of some blocks
    for boss blocks, it build a dictionnary with block as key and
    frequency as value
    """

    dBoss = {}
    grb = 0
    for blk in blocks:
        if blk.difficulty < 0:
            grb += blk.rarity
            dBoss[blk] = blk.rarity
    for it in dBoss:
        dBoss[it] = dBoss[it] / grb
    return dBoss


def getrandomblock(d):
    """
    Function used to get a random block by using the given
    dictionnay of ennemies's apparition frequency
    """

    cles, vals = zip(*d.items())
    cdist = cumsum(vals)

    def fun():
        r = random()
        k = 0
        while r > cdist[k]:
            k += 1
        return cles[k]
    return fun()

# TODO real level, random level done
