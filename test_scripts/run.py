import sys, getopt
from ForwarderSender import ForwarderSender

def usage():
    print('USAGE:')
    print('  python3 run.py [OPTIONS] [DEVICE] [CAMERA]')
    print('  -c, --config=CONFIG'.ljust(20, ' '), 'Run with config file')
    print('  --tucson'.ljust(20, ' '), 'Run with Tucson config file')
    print('  --ncsa'.ljust(20, ' '), 'Run with NCSA config file')
    print('  -h'.ljust(20, ' '), 'Help menu\n')
    print('DEVICE:')
    print('    * fwdr\n')
    print('CAMERA:')
    print('    * AT')

def main():
    config = None
    devices = ['fwdr']
    cameras = ['AT']

    try: 
        opts, args = getopt.getopt(sys.argv[1:], 'c:h:', [
            'config=', 
            'tucson',
            'ncsa'
        ])
    except getopt.GetoptError:
        usage()
        exit(0)

    if len(args) < 2:
        print('Error: DEVICE or CAMERA not defined')
        usage()
        exit(0)

    if args[0] not in devices and args[1] not in cameras:
        print('Error: DEVICE or CAMERA do not match with predefined values')
        usage()
        exit(0)

    for opt, arg in opts:
        if opt in ('-c', '--config'):
            config = arg
        elif opt in ('--tucson'):
            config = 'TestStandTucson.yaml'
        elif opt in ('--ncsa'):
            config = 'TestStandNCSA.yaml'
        elif opt in ('-h'):
            usage()
        else:
            usage()
            exit(0)

    fwdr = ForwarderSender(config)
    fwdr.run_oneFwdr_oneImage(args[1])
    
if __name__ == "__main__": main()
