#!/Users/agentwombat/Documents/uc-riverside-coursework/231-computer-animation/visuscript/visuscript-python/.venv/bin/python
"""
Creates a video from a Python script that outputs a stream of SVG elements to standard output.
"""

from argparse import ArgumentParser
import subprocess
import importlib.util
import sys
from visuscript.config import *

def main():

    parser = ArgumentParser(__doc__)

    parser.add_argument("input_filename",type=str, help="Python script that prints a stream of SVG elements to standard output.")
    # parser.add_argument("output_filename", help="Filename at which the output video will be stored.")

    args = parser.parse_args()

    animate_proc = subprocess.Popen(
        ["/Users/agentwombat/Documents/uc-riverside-coursework/231-computer-animation/visuscript/visuscript/animate3"],  # or the full path to your bash script
        stdin=subprocess.PIPE,
        text=True
    )

    original_stdout = sys.stdout
    sys.stdout = animate_proc.stdin
    
    spec = importlib.util.spec_from_file_location("script", args.input_filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    mod.main()


    sys.stdout.flush()
    sys.stdout = original_stdout
    animate_proc.stdin.close()
    animate_proc.wait()
    


if __name__ == "__main__":
    main()