import sys, getopt
from ForwarderSender import ForwarderSender

def usage():
    print('USAGE:')
    print('  python3 run.py [OPTIONS] [DEVICE] [CAMERA]')
    print('  --tucson'.ljust(20, ' '), 'Run with Tucson config file')
    print('  --ncsa'.ljust(20, ' '), 'Run with NCSA config file')
    print('  --timer'.ljust(20, ' '), 'Run with sleep timer in seconds')
    print('  --fwdr'.ljust(20, ' '), 'Run with number of forwarder')
    print('  --image'.ljust(20, ' '), 'Run for number of image')
    print('  -h'.ljust(20, ' '), 'Help menu\n')
    print('DEVICE:')
    print('    * fwdr\n')
    print('CAMERA:')
    print('    * AT')

def main():
    config = None
    timer = None
    forwarder = None
    image = None
    devices = ['fwdr']
    cameras = ['AT']

    try: 
        opts, args = getopt.getopt(sys.argv[1:], 'h:', [
            'config=', 
            'tucson',
            'ncsa',
            'timer=',
            'fwdr=',
            'image=',
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
        if opt in ('--tucson'):
            config = 'TestStandTucson.yaml'
        elif opt in ('--ncsa'):
            config = 'TestStandNCSA.yaml'
        elif opt in ('--timer'):
            timer = arg
        elif opt in ('--fwdr'):
            forwarder = arg
        elif opt in ('--image'):
            image = arg
        elif opt in ('-h'):
            usage()
        else:
            usage()
            exit(0)

    fwdr = ForwarderSender(config, timer)
    fwdr.run((forwarder, image), args[1])
    
if __name__ == "__main__": main()
