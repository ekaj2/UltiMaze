# Copyright 2017 Integrity Software and Games, LLC
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of UltiMaze.
#
# UltiMaze is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UltiMaze is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with UltiMaze.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

"""WEIghted RAndom Number Generator aka WeiRa"""


import random
from random import random


def unpack(list_items):
    items = [a[0] for a in list_items]
    weights = [a[1] for a in list_items]
    return items, weights


def weira_choice(list_items):
    """list_items = [[item1, prob], [item2, prob], ...]"""
    items, weights = unpack(list_items)
    
    factor = sum(weights)
    rand = random()
    val = round(rand * factor)
    
    i = 0
    while i < len(weights):
        if sum(weights[:i]) <= val <= sum(weights[:i+1]):
            return items[i]
        i += 1


def weira_shuffle(list_items, bias):
    items, weights = unpack(list_items)
    weights = [bias * a + random() * max(weights) + min(weights) for a in weights]

    ordered_list = [x for (y, x) in sorted(zip(weights, items), key=lambda pair: pair[0])]

    return ordered_list


def main():
    list_items = [['a', 1], ['b', 10], ['c', 0]]
    print(weira_shuffle(list_items, 1))
        
if __name__ == "__main__":
    main()
