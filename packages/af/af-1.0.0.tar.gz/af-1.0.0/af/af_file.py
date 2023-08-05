from af.language_detector import LanguageDetector
from af.language_detector import LanguageDetectorError
from af.encoding_detector import EncodingDetector
import os
import json
import hashlib
from datetime import datetime
import logging
import af.shared_memory as shared_memory

class Af:
    INFO_VERSION = '3.0'

    def __init__(self, file_path, worker_index):
        # self._output_dir = output_dir
        # self._output_error_dir = output_error_dir
        self._worker_index = worker_index

        self._languages_detection_batch_size = 500
        self._language_detector = LanguageDetector()
        self._warning_encoding_error = 10

        # Files
        self._file_path = file_path
        self._file_basename = os.path.basename(self._file_path)

        # Size
        self._size = os.path.getsize(self._file_path)

        # Modified time
        self._modified_time = os.path.getmtime(self._file_path)

        # Modified date
        self._modified_date = datetime.fromtimestamp(self._modified_time).strftime("%b %d, %Y %I:%M")

        # Hash
        hash = self._file_path + '-' + str(self._size) + '-' + str(self._modified_time) + Af.INFO_VERSION
        self._hash = hashlib.sha224(hash.encode('utf-8')).hexdigest()

    def get_info(self):
        info_file_path = self._get_info_file_path()
        if os.path.isfile(info_file_path):
            with open(info_file_path) as info_file_handler:
                info_json = json.load(info_file_handler)
                return {
                    'encoding': info_json['encoding'],
                    'num_lines': info_json['num_lines'],
                    'line_format_sep': info_json['line_format_sep'],
                    'line_format_src_index': info_json['line_format_src_index'],
                    'line_format_tgt_index': info_json['line_format_tgt_index'],
                    'src_lang': info_json['src_lang'],
                    'tgt_lang': info_json['tgt_lang'],
                    'encoding_errors': info_json['encoding_errors']
                }





    def _has_valid_cache(self):
        info_file_path = self._get_info_file_path()
        has_valid_cache = False
        if os.path.isfile(info_file_path):
            with open(info_file_path) as info_file_handler:
                info_json = json.load(info_file_handler)
            if info_json['hash'] == self._hash:
                has_valid_cache = True
        return has_valid_cache

    def _set_info_from_cache(self):
        info_file_path = self._get_info_file_path()
        if os.path.isfile(info_file_path):
            with open(info_file_path) as info_file_handler:
                info_json = json.load(info_file_handler)
                self._encoding = info_json['encoding']
                self._num_lines = info_json['num_lines']
                self._line_format_sep = info_json['line_format_sep']
                self._line_format_src_index = info_json['line_format_src_index']
                self._line_format_tgt_index = info_json['line_format_tgt_index']
                self._src_lang = info_json['src_lang']
                self._tgt_lang = info_json['tgt_lang']
                self._encoding_errors = info_json['encoding_errors']

    def analyze(self, use_cache = True):
        # Info
        if self._has_valid_cache() and use_cache:
            self._set_info_from_cache()
            shared_memory.total[self._worker_index] = self._num_lines
        else:
            # Encoding
            self._encoding = EncodingDetector.getEncoding(self._file_path, 1000)
            encoding_errors = []
            num_encoding_error = 0

            # Array for language detection
            src_langs = []
            tgt_langs = []

            # default line format
            self._line_format_sep = '|||'
            self._line_format_src_index = 0
            self._line_format_tgt_index = 1

            # Num line
            num_line = 0
            num_line_ok = 0

            with open(self._file_path, 'rb') as f:
                for num_line, binary_line in enumerate(f):
                    try:
                        line = binary_line.decode(self._encoding)
                        num_line_ok += 1

                        # Get format
                        if num_line_ok == 1:
                            line = line.strip()
                            if self._line_format_sep not in line:
                                self._line_format_sep = '\t'
                            parts = line.split(self._line_format_sep)
                            if len(parts) == 3:
                                self._line_format_src_index = 1
                                self._line_format_tgt_index = 2

                        # Detect languages
                        if len(src_langs) <= self._languages_detection_batch_size:
                            src, tgt = self._get_src_tgt(line)
                            try:
                                src_detection = self._language_detector.detect(src)
                                tgt_detection = self._language_detector.detect(tgt)
                                if src_detection.language.code != tgt_detection.language.code:
                                    src_langs.append(src_detection.language.code)
                                    tgt_langs.append(tgt_detection.language.code)
                            except LanguageDetectorError as e:
                                continue
                    except Exception:
                        encoding_errors.append((num_line, str(binary_line)))
                        num_encoding_error += 1
                        #print('--ENCODING ERROR--', self._file_basename, 'LINE', num_line)

                if not src_langs or not tgt_langs:
                    print('--No language found', self._file_basename)
                self._src_lang = max(src_langs, key=src_langs.count)
                self._tgt_lang = max(tgt_langs, key=tgt_langs.count)

            info = {
                'info_version': Af.INFO_VERSION,
                'hash': self._hash,
                'encoding': self._encoding,
                'line_format_sep': self._line_format_sep,
                'line_format_src_index': self._line_format_src_index,
                'line_format_tgt_index': self._line_format_tgt_index,
                'src_lang': self._src_lang,
                'tgt_lang': self._tgt_lang,
                'num_lines': num_line + 1,
                'encoding_errors': encoding_errors
            }
            with open(self._get_info_file_path(), 'w') as f:
                json.dump(info, f)

            shared_memory.total[self._worker_index] = num_line + 1



    def _get_info_file_path(self):
        dir = os.path.dirname(self._file_path)
        file_name = os.path.basename(self._file_path)
        info_file_name = '.' + os.path.splitext(file_name)[0] + '.json'
        info_file_path =  os.path.join(dir, info_file_name )
        return info_file_path

    def run(self, output_dir):
        self._set_info_from_cache()
        try:
            self._to_bilingual(output_dir)
        except Exception as e:
            logging.exception("message")
            print('----- Error ----', self._file_path)
            print(e)
            return ''
        self._info()
        return

    def _info(self):
        out = '-----' + self._file_basename + '-----' + '\n'
        out += 'Encoding: ' + self._encoding + '\n'
        out += 'Languages: ' + self._src_lang + '/' + self._tgt_lang + '\n'
        out += 'Success: ' + str(self._success) + '\n'
        out += 'Short Success: ' + str(self._success_short) + '\n'
        out += 'Error: ' + str(self._errors) + '\n'
        out += 'Error bad format: ' + str(self._errors_bad_format) + '\n'
        #print(out)

    def _get_src_tgt(self, line):
        text = line.rstrip()
        parts = text.split(self._line_format_sep)
        src = parts[self._line_format_src_index]
        tgt = parts[self._line_format_tgt_index]
        return src, tgt

    def _to_bilingual(self, output_dir):

        # Errors and Success
        self._success = 0
        self._success_short = 0
        self._errors = 0
        self._errors_bad_format = 0
        self._errors_encoding = 0

        self._file = open(self._file_path, 'rb')

        basename_without_ext = os.path.splitext(self._file_basename)[0]

        self._src_file_path = os.path.join(
            output_dir,
            basename_without_ext + '.' + self._src_lang
        )
        self._tgt_file_path = os.path.join(
            output_dir,
            basename_without_ext + '.' + self._tgt_lang
        )
        # self._error_file_path = os.path.join(
        #     output_error_dir,
        #     basename_without_ext + '.error.txt'
        # )

        self.src_file = open(self._src_file_path, 'w', encoding='utf-8')
        self._tgt_file = open(self._tgt_file_path, 'w', encoding='utf-8')
        # self._error_file = open(self._error_file_path, 'w', encoding='utf-8')

        for i, binaray_line in enumerate(self._file):
            shared_memory.progress[self._worker_index] += 1
            try:
                line = binaray_line.decode(self._encoding)
            except:
                self._errors_encoding += 1
                continue

            try:
                src, tgt = self._get_src_tgt(line)
            except:
                self._errors_bad_format += 1
                continue

            # \error
            if '\r' in src or '\r' in tgt:
                self._handler_error('....', i, src, tgt, self._src_lang, self._tgt_lang)
                continue

            # Deepl error
            if '....' in src or '....' in tgt:
                self._handler_error('....', i, src, tgt, self._src_lang, self._tgt_lang)
                continue

            # Empty
            if src.isspace() or tgt.isspace():
                self._handler_error('Empty', i, src, tgt, self._src_lang, self._tgt_lang)
                continue

            if len(src.split())<7:
                self._handler_sucess(src, tgt)
                self._success_short += 1
                continue
            try:
                src_lang = self._language_detector.detect(src).language.code
                tgt_lang = self._language_detector.detect(tgt).language.code
                if src_lang != self._src_lang or tgt_lang != self._tgt_lang:
                    self._handler_error('Bad language', i, src, tgt, src_lang, tgt_lang)
                    continue
                self._handler_sucess(src,tgt)
            except LanguageDetectorError:
                self._handler_error('Unknow language', i, src, tgt, 'unk', 'unk')
                continue

        shared_memory.success[self._worker_index] = self._success
        shared_memory.error[self._worker_index] = self._errors

        self.src_file.close()
        self._tgt_file.close()
        #self._error_file.close()
        self._file.close()

    def _handler_error(self, error_type, k, src, tgt, src_lang, tgt_lang):
        #out = str(k) + ' | ' + error_type + '|' + ' (' + src_lang + ') ' + src + ' (' + tgt_lang + ') ' + tgt + '\n'
        #self._error_file.write(out)
        self._errors += 1

    def _handler_sucess(self, src, tgt):
        self.src_file.write(src + '\n')
        self._tgt_file.write(tgt + '\n')
        self._success += 1

    def get_name(self):
        return self._file_basename



