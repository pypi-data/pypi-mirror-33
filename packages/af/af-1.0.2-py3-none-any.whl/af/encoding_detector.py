import os.path
from chardet.universaldetector import UniversalDetector


class EncodingDetector:

    @staticmethod
    def getEncoding(filepath,  lineToCheck = 1000): #0 = no limit
        if not os.path.isfile(filepath):
            raise ValueError('Error enconding detection. ' + filepath + ' is not a file' )
        detector = UniversalDetector()
        detector.reset()
        with open(filepath, "rb") as f:
            k = 0
            for line in f:
                k += 1
                detector.feed(line)
                if detector.done:
                    break
                if lineToCheck !=0 and k % lineToCheck == 0:
                    break
        detector.close()
        return detector.result['encoding']






