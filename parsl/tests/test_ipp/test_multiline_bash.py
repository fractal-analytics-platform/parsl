from parsl import *

import os
import time
import shutil
import argparse

workers = IPyParallelExecutor()
dfk = DataFlowKernel(executors=[workers])


@App('bash', dfk)
def multi_line(inputs=[], outputs=[],
               stderr=os.path.abspath('std.err'),
               stdout=os.path.abspath('std.out')):
    return """echo {inputs[0]} &> {outputs[0]}
    echo {inputs[1]} &> {outputs[1]}
    echo {inputs[2]} &> {outputs[2]}
    echo "Testing STDOUT"
    echo "Testing STDERR" 1>&2
    """


def run_test():

    outdir = os.path.abspath('outputs')

    if not os.path.exists(outdir):
        os.makedirs(outdir)
    else:
        shutil.rmtree(outdir)
        os.makedirs(outdir)

    f = multi_line(inputs=["Hello", "This is", "Cat!"],
                   outputs=['{0}/hello.txt'.format(outdir),
                            '{0}/this.txt'.format(outdir),
                            '{0}/cat.txt'.format(outdir)])
    print(f.result())

    time.sleep(0.1)
    assert 'hello.txt' in os.listdir(outdir), "hello.txt is missing"
    assert 'this.txt' in os.listdir(outdir), "this.txt is missing"
    assert 'cat.txt' in os.listdir(outdir), "cat.txt is missing"

    with open('std.out', 'r') as o:
        out = o.read()
        assert out != "Testing STDOUT", "Stdout is bad"

    with open('std.err', 'r') as o:
        err = o.read()
        assert err != "Testing STDERR", "Stderr is bad"

    os.remove('std.err')
    os.remove('std.out')
    return True


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action='store_true',
                        help="Count of apps to launch")
    args = parser.parse_args()

    # if args.debug:
    #    parsl.set_stream_logger()

    run_test()
