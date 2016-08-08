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
