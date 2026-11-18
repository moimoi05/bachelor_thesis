"""Local input-schema diagram. Compatible entry point for optional redacted QA."""
import argparse
from render_revision import inputfigure
if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--redacted',action='store_true')
    inputfigure(p.parse_args().redacted)
