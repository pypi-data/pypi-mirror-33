import argparse
import glob
from dtsr.util import load_dtsr

if __name__ == '__main__':
    argparser = argparse.ArgumentParser('''
    Utility for loading and repickling old DTSR objects after metadata changes.
    ''')
    argparser.add_argument('path', nargs='+', help='Path(s) to DTSR object directory')
    args = argparser.parse_args()
    paths = []
    for path in args.path:
        paths += glob.glob(path)

    for path in paths:
        dtsr_model = load_dtsr(path)
        dtsr_model.save()