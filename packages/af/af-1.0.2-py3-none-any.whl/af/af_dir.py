import os
import glob
import shutil
import af.shared_memory as shared_memory
from multiprocessing import Pool, Array
from af.af_dir_worker import af_dir_worker
from prettytable import PrettyTable
from af.monitor import Monitor
from af.af_file import Af


def init_process(progress, total, success, error):
    shared_memory.progress = progress
    shared_memory.total = total
    shared_memory.success = success
    shared_memory.error = error

class AfDir:
    def __init__(self, input_dir, output_dir, num_workers=10, override_output_dir=False):
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._override_output_dir = override_output_dir

        if not os.path.isdir(self._input_dir):
            print('Input directory not found')
            exit(1)

        if os.path.isdir(self._output_dir):
            if os.listdir(self._output_dir) and not override_output_dir:
                print('Output directory already exists and is not empty')
                exit(1)
            else:
                shutil.rmtree(self._output_dir)

        os.mkdir(self._output_dir)

        # #self._output_dir = os.path.join(input_dir, 'export')
        # if os.path.isdir(self._output_dir):
        #     shutil.rmtree(self._output_dir)


        # self._output_error_dir= os.path.join(input_dir, 'export_error')
        # if os.path.isdir(self._output_error_dir):
        #     shutil.rmtree(self._output_error_dir)
        # os.mkdir(self._output_error_dir)

        self._file_paths = glob.glob(self._input_dir + '/*.txt')
        print('\nScanning directory "'+ os.path.basename(input_dir) +'". Please wait...')

        self._num_workers = num_workers

    def check_encoding(self):
        pass

    def run(self):
        # For stats
        num_files = len(self._file_paths)

        init_progress = [0] * num_files
        progress = Array('i', init_progress)

        init_total = [0] * num_files
        total = Array('i', init_total)

        init_success = [0] * num_files
        success = Array('i', init_success)

        init_error = [0] * num_files
        error = Array('i', init_error)

        worker_args = [(i, file_path, self._output_dir,  'analyze') for i,file_path in enumerate(self._file_paths)]
        with Pool(self._num_workers, initializer=init_process, initargs=(progress,total, success, error)) as pool:
            pool.starmap(af_dir_worker, worker_args)

        x = PrettyTable()
        x.field_names = ['file', 'src lang', 'tgt lang', 'encoding', 'encoding errors', 'lines']

        num = 0
        num_encoding_errors = 0
        for field in x.field_names:
            x.align[field] = 'l'
        for i, file_path in enumerate(self._file_paths):
            af = Af(file_path, i)
            info = af.get_info()
            x.add_row([
                af.get_name(),
                info['src_lang'],
                info['tgt_lang'],
                info['encoding'],
                len(info['encoding_errors']),
                info['num_lines']
            ])
            num += info['num_lines']
            num_encoding_errors += len(info['encoding_errors'])
        x.add_row(['ALL', '', '', '', num_encoding_errors, num])
        print(x)
        print('\nConverting af files. Please wait...')
        monitor =  Monitor(progress, total)
        monitor.start()

        worker_args = [(i, file_path, self._output_dir, 'tobilingual') for i, file_path in
                       enumerate(self._file_paths)]
        with Pool(self._num_workers, initializer=init_process, initargs=(progress, total, success, error)) as pool:
            pool.starmap(af_dir_worker, worker_args)

        monitor.shutdown()

        x = PrettyTable()
        x.field_names = ['file', 'src lang', 'tgt lang', 'encoding', 'encoding errors', 'lines', 'error', 'success']
        num = 0
        num_encoding_errors = 0
        num_success = 0
        num_error = 0
        for field in x.field_names:
            x.align[field] = 'l'
        for i, file_path in enumerate(self._file_paths):
            af = Af(file_path, i)
            info = af.get_info()
            x.add_row([
                af.get_name(),
                info['src_lang'],
                info['tgt_lang'],
                info['encoding'],
                len(info['encoding_errors']),
                info['num_lines'],
                success[i],
                error[i]
            ])
            num += info['num_lines']
            num_encoding_errors += len(info['encoding_errors'])
            num_success += success[i]
            num_error += error[i]
        x.add_row(['ALL', '', '', '', num_encoding_errors, num, num_error, num_success])
        print('\n\nResults')
        print(x)
        print('\nThe end...')
