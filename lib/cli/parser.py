import argparse
import sys
from argparse import RawTextHelpFormatter

from config.config import check_current_version, print_help
class GlucoseBotArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='GlucoseBot is a tool to help you manage your diabetes.',
            formatter_class=RawTextHelpFormatter,
            usage='glucosebot [-h] [-v]',
            epilog='For more information, visit: https://github.com/pedrooot/TFG'
        )
        self.parser.add_argument('-v', '--version', action='version', help='Show GlucoseBot version')
    def error(self, message):
        print_help(message)
        exit(2)

    def parse(self, args=None):
        if args:
            sys.argv = args
        
        if len(sys.argv) == 1:
            self.error("too few arguments")
        
        if len(sys.argv) == 2 and sys.argv[1] == '-v':
            print(check_current_version())
        if len(sys.argv) == 2 and sys.argv[1] == '-h':
            print_help()
            exit(0)