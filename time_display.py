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

class TimeDisplay:
    def __init__(self):
        self.hms = [0, 0, 0]

    def __str__(self):
        hms = self.hms
        if hms[0]:
            return "{} hours, {} minutes, {} seconds".format(hms[0], hms[1], hms[2])
        elif hms[1]:
            return "{} minutes, {} seconds".format(hms[1], hms[2])
        else:
            return "{} seconds".format(hms[2])

    def upper(self):
        return self.__str__().upper()

    def lower(self):
        return self.__str__().lower()

    def title(self):
        return self.__str__().title()

    def convert(self, a):
        if type(a) is int or type(a) is float:
            h = int(a / 3600)
            m = int(a % 3600 / 60)
            s = a % 60
            self.hms = [h, m, s]
            return self.hms

        elif type(a) is list and len(a) == 3:
            self.hms = a
            h, m, s = a
            return h * 3600 + m * 60 + s

        else:
            self.hms = [0, 0, 0]
            return "?"


def main():
    time_disp = TimeDisplay()
    print(time_disp.convert(10000))
    print(time_disp.convert([2, 46, 40]))
    time_disp.convert(.57)
    print(time_disp)
    print(time_disp.upper())

if __name__ == "__main__":
    main()
