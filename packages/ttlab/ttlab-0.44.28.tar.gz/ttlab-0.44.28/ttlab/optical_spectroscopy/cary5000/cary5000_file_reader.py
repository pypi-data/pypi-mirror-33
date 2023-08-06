import numpy as np


class Data:

    def __init__(self):
        self.wavelength = []
        self.transmission = []

class Cary5000FileReader:

    @staticmethod
    def read_data(filename,**kwargs):

        if 'IgnoreEntries' in kwargs:
            ignore_entries = kwargs.get("IgnoreEntries")
        else:
            ignore_entries = []

        names = []
        wavelength = []
        transmission = []
        with open(filename, "br") as file:
            for count, line in enumerate(file):
                if line == b'\r\n':
                    break
                else:
                    line=str(line).strip('b\'')

                if count == 0:
                    for i,key in enumerate(line.split(',')):
                        if i%2==0 and i<len(line.split(','))-1:
                            names.append(key)
                    for i, tmp in enumerate(names):
                        transmission.append([])

                if count == 1:
                    pass    # maybe add or check the units and if its transmission
                if count > 1:
                    k=0
                    for i,key in enumerate(line.split(',')):
                        if i == 0:
                           wavelength.append(float(key))
                        elif i%2==1 and i<len(line.split(','))-1:
                            transmission[k].append(float(key))
                            k += 1

        data = dict()
        for i, key in enumerate(names):
            if key in ignore_entries:
                continue
            data[key]=Data()
            data[key].wavelength= np.array(wavelength)
            data[key].transmission = np.array(transmission[i])

        return data
