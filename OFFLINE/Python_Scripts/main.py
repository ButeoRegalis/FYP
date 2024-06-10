# STATUS: WORKING
# LAST UPDATED: 10/06/2024
# https://forum.dronebotworkshop.com/c-plus-plus/serial-data-transfer-from-arduino-to-python/


import os
import argparse
import tables as tb
from serial.tools import list_ports
from FeatureCollection import collectFeatureData
from Tools.Visualisation import visualiseFeatureDistribution
from Classification import classifyFeatureData
from Tools.RawDataCollection import collectRawData


hdfFile = os.path.join(os.getcwd(), 'Feature_Data.h5')


def print_all() -> None:
    """
    Print all table numbers belonging to each group in the .h5 file

    STATUS: WORKING

    : return: None
    : rtype: None
    """

    if os.path.exists(path=hdfFile):
        try:
            # Open .h5 file for reading
            h5file = tb.open_file(filename=hdfFile, mode='r')

            # List all nodes in .h5 file
            nodes = []
            for node in h5file:
                nodes.append(str(object=node))

            # Filter listed nodes based on those that are groups
            filtered_groups = list(filter(lambda x: '(Group)' in x, nodes))
            groups = [(x.split(" ")[0]) for x in filtered_groups]

            # Print a list of each table belonging to each group
            for grp in groups:
                gf_string = grp + '/'
                filtered_tables = list(filter(lambda x: gf_string in x, nodes))
                filtered_tables = list(
                    filter(lambda x: '(Table' in x, filtered_tables))
                tables = [x.split(' ')[0] for x in filtered_tables]
                print(f"GROUP: {grp}")

                for tbl in tables:
                    table_name = tbl.split('/')[-1]
                    print(f"\tTABLE: {table_name}")
                    nodeObject = h5file.get_node(where=grp, name=table_name)
                    repetitions = list(set([x['repetition'] for x in nodeObject.iterrows()]))  # type: ignore
                    repetitions.sort()
                    print(f"\t\tREP NUMS: {repetitions}")
        except:
            print("PYTABLES EXCEPTION OCCURRED!")
            print(f"IF HDF5ExtError: Most likely cause is {hdfFile} is empty")
            print("EXITING...")
        finally:
            # Close the .h5 file
            h5file.close()
            exit(code=1)
    else:
        print(f"{os.path.basename(p=hdfFile)} AT {os.path.dirname(p=hdfFile)} DOES NOT EXIST.\n")


def run(parser, args) -> None:
    """
    Run the chosen process

    STATUS: WORKING

    reference: https://stackoverflow.com/questions/59086966/pythonic-way-for-adding-parameters-to-argparse-based-on-another-parameter

    : param parser: argparse parser
    : type parser: argparse.ArgumentParser
    : param args: argparse args
    : type args: argparse.ArgumentParser().parse_args()
    : return: None
    : rtype: None
    """

    if args.command == 'F':  # Feature Data Collection
        print("STARTING FEATURE DATA COLLECTION...")
        comport = "COM" + str(object=args.port)
        collectFeatureData(port=comport, baud=args.baud, hdfFile=hdfFile, repetitions=args.reps)

    elif args.command == 'V':  # Feature Data Distribution Visualisation
        print("STARTING FEATURE DATA DISTRIBUTION VISUALISATION...")
        visualiseFeatureDistribution(hdfFile=hdfFile)

    elif args.command == 'C':  # Classification
        print("STARTING CLASSIFICATION...")
        test_split = args.splt / 100.0
        classifyFeatureData(hdfFile=hdfFile, test_split=test_split)

    elif args.command == 'R':  # Raw Data Collection
        print("STARTING RAW DATA COLLECTION...")
        comport = "COM" + str(object=args.port)
        collectRawData(port=comport, baud=args.baud, repetitions=args.reps)

    elif args.command == 'LIST':
        # List available comports
        ports = list_ports.comports()
        if ports:
            print("PORTS:")
            for port in sorted(ports):
                print("port: {}, desc: {}, hwid: {}".format(port.name, port.description, port.hwid))
            print()
        else:
            print("NO PORTS DETECTED.\n")

        # List groups in .h5 file
        print_all()


def main() -> None:
    """
    Main function

    STATUS: WORKING
    """

    # Create top-level parser
    parser = argparse.ArgumentParser(
        prog='PROG',
        description='Offline process selection.',
        epilog="See '<command> --help' to read about a specific sub-command."
    )
    subparsers = parser.add_subparsers(
        dest='command',
        help='Sub-commands'
    )

    # Create subparser for Feature Data Collection
    parser_F = subparsers.add_parser(name='F', help='Feature Data Collection Process')
    parser_F.add_argument('--port', required=True, type=int, help='comport number')
    parser_F.add_argument('--baud', default=115200, choices=(9600, 115200), type=int, help='baudrate (default: %(default)s)')
    parser_F.add_argument('--reps', default=2, type=int, help='number of reptitions to record (default: %(default)s)')
    parser_F.set_defaults(func=run)
    
    # Create subparser for Feature Data Distribution Visualisation
    parser_V = subparsers.add_parser(name='V', help='Feature Data Distribution Visualisation Process')
    parser_V.set_defaults(func=run)

    # Create subparser for Classification
    parser_C = subparsers.add_parser(name='C', help='Classification Process')
    parser_C.add_argument("--splt", default=20, type=int, choices=range(10, 51, 1), help='percentage test split to use (min: 10, max: 50, step: 1 | default: %(default)s)')
    parser_C.set_defaults(func=run)

    # Create subparser for Raw Data Collection
    parser_R = subparsers.add_parser(name='R', help='Raw Data Collection Process')
    parser_R.add_argument('--port', required=True, type=int, help='comport number')
    parser_R.add_argument('--baud', default=115200, choices=(9600, 115200), type=int, help='baudrate (default: %(default)s)')
    parser_R.add_argument('--reps', default=1, type=int, help='number of reptitions to record (default: %(default)s)')
    parser_R.set_defaults(func=run)

    # Create subparser for Listing
    parser_list = subparsers.add_parser(name='LIST', help='List available ports and .h5 file structure.')
    parser_list.set_defaults(func=run)

    # Parse args
    args = parser.parse_args()
    if args.command is not None:
        args.func(parser, args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
