from af.af_file import Af


def af_dir_worker(i, file_path, output_dir, mode):
    af = Af(file_path, i)
    if mode == 'analyze':
        af.analyze()
    else:
        af.run(output_dir)

