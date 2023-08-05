import argparse
import time
import os.path
from af.af_dir import AfDir


if __name__ == '__main__':

    # Args
    parser = argparse.ArgumentParser(description='Pangeanic af2bilingual')
    parser.add_argument('input_dir', type=str)
    parser.add_argument('output_dir', nargs='?', type=str, default='')
    parser.add_argument('-w', type=int, required=False, default=10, help="Num workers")
    parser.add_argument('-o', required=False, default=False,  help="Override output dir", action="store_true")
    args = parser.parse_args()

    input_dir = vars(args).get('input_dir', '')
    output_dir = vars(args).get('output_dir', '')
    num_workers = vars(args).get('w', '')
    override_output_dir = vars(args).get('o', '')

    if not os.path.isdir(input_dir):
        print('Input directory not found')
        exit(1)

    input_dir = os.path.abspath(input_dir)
    if output_dir == '':
        output_dir = os.path.join(os.path.dirname(input_dir), 'bilingual')

    start = time.time()

    af_dir = AfDir(
        input_dir=input_dir,
        output_dir=output_dir,
        num_workers=num_workers,
        override_output_dir = override_output_dir
    )
    af_dir.run()

    end = time.time()
    runtime = end - start
    msg = "runtime  {0} secs ".format(runtime)
    print(runtime)

