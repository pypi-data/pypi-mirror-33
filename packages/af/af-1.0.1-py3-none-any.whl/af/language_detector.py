from polyglot.detect import Detector
import logging


class LanguageDetector:
    def __init__(self):
        logging.getLogger('polyglot.detect.base').setLevel(logging.ERROR)

    def detect(self, text, accept_best_effort=True):
        try:
            language = Detector(text, quiet= False)
            if not language.reliable:
                if not accept_best_effort:
                    raise LanguageDetectorError('Not reliable')
            return language
        except Exception as e:
            raise LanguageDetectorError('Not reliable')

    # def is_lang(self, language_code, text):
    #     try:
    #         for language in Detector(text, quiet=False).languages:
    #             if language.code == language_code:
    #                 return True
    #     except Exception as e:
    #         raise LanguageDetectorError('Not reliable')

class LanguageDetectorError(Exception):
    def __init__(self, message):
        super(LanguageDetectorError, self).__init__(message)



