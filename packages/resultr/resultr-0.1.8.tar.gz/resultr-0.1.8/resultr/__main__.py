import sys
import argparse
import resultr

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Makes UCL PHAS results better')
    parser.add_argument('--input', '-i',
                        type=str, help="csv file to import")
    parser.add_argument('--format', '-f', type=str,
                        help="reformats results by module and exports it to file specified")
    parser.add_argument('--plot', '-p', action='store_true',
                        help="plot the module results")
    parser.add_argument('--exportplots', '-ep', type=str,
                        help="export all plots to /path/you/want/")
    parser.add_argument('--showplots', '-sp',
                        action='store_true', help="show all plots")
    parser.add_argument(
        '--my', '-m', action="store_true", help="returns your weighted average for the year")
    parser.add_argument('--year', '-y', help="specify your year")
    parser.add_argument('--rank', '-r', action='store_true',
                        help="returns your rank in the year")
    parser.add_argument('--candidate', '-c',
                        help="specify your candidate number")
    args = parser.parse_args()

    #########################
    #                       #
    #         end           #
    #       argparse        #
    #                       #
    #                       #
    #########################
    resultr.main(args)

if __name__ == "__main__":
    main()