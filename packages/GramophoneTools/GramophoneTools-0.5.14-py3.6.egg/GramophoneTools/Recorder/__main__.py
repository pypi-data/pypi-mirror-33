import sys
import Recorder

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    print(args)
    Recorder.main()

if __name__ == "__main__":
    main()