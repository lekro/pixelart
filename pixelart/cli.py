import argparse
import sys
import logging
from logging import StreamHandler

# Import from this package
from pixelart.processing import PixelartProcessor

class CLIBlockReportCaller:
    '''Used so the CLI can get a block report
    from the processor, and directly save it to a
    file.
    '''

    def __init__(self, path):
        self.path = path

    def done_processing(self, block_report):
        with open(self.path, mode='w') as f:
            for unique in block_report.keys():
                numstr = ('%dx' % block_report[unique]).ljust(8)
                f.write('%s%s\n' % (numstr, unique))


def valid_scale(string):
    if 'x' not in string:
        msg = "Invalid scaling option %s" % string
        raise argparse.ArgumentTypeError(msg)
    w, h = string.split('x')
    w = int(w)
    h = int(h)
    if w < 1 or h < 1:
        msg = "Scaling width and height must be 1 or greater!"
        raise argparse.ArgumentTypeError(msg)
    return w, h

def cli_process():

    parser = argparse.ArgumentParser(description='Match pixels to textures',
                                     epilog='To run the gui, use pixelart-gui.')

    # Add positional arguments
    parser.add_argument('input', metavar='INPUT', type=str,
                        help='Path to image to convert into pixelart')
    parser.add_argument('textures', metavar='TEXTURES', type=str,
                        help='Path to directory containing textures')
    parser.add_argument('output', metavar='OUTPUT', type=str,
                        help='Path to output image')

    # Add optional arguments
    parser.add_argument('--version', action='version',
                        version='%(prog)s 0.1.0')
    parser.add_argument('-p', '--p-norm', dest='p', type=float,
                        default=2,
                        help='Minkowski p-norm used for matching\
                                nearest neighbors in color space. p=2\
                                specifies Euclidean distance, while p=1\
                                specifies Manhattan distance. Any value\
                                from 0 < p < infinity may be used.\
                                (default: %(default)s)')
    parser.add_argument('-c', '--color-space', dest='colorspace', type=str,
                        choices=['RGB', 'HSV', 'YCbCr'], 
                        default='RGB',
                        help='Color space in which nearest neighbors are\
                                found. (default: %(default)s)')
    parser.add_argument('-i', '--interpolation', dest='interp', type=str,
                        choices=['nearest', 'bilinear', 'bicubic', 
                                 'lanczos'],
                        default='bicubic',
                        help='Interpolation method used to scale the\
                                input image and to find the average\
                                color of each texture. (default: \
                                %(default)s)')
    parser.add_argument('-r', '--report', dest='report', type=str,
                        default=None,
                        help='Path to output block report. This file will\
                                contain numbers and types of blocks\
                                (or textures) required to make the\
                                pixelart. (default: %(default)s)')
    parser.add_argument('-s', '--scaling', dest='scaling',
                        type=valid_scale,
                        help='Scaling to apply to input image.\
                                Must be in format MxN, where both\
                                M and N are positive integers.')
    parser.add_argument('-t', '--texture-dimension',
                        dest='texture_dimension', type=valid_scale,
                        default=(16,16),
                        help='Dimensions to expect when loading\
                                textures. All textures not of\
                                this dimension will be ignored.\
                                Must be in format MxN, where both\
                                M and N are positive integers.')
    parser.add_argument('-v', '--verbose', dest='log_level',
                        action='store_const',
                        const=logging.DEBUG, default=logging.INFO,
                        help='Show all debug messages')
    parser.add_argument('-q', '--quiet', dest='log_level',
                        action='store_const',
                        const=logging.CRITICAL, default=logging.INFO,
                        help='Show only critical messages')

    # Actually process arguments
    args = parser.parse_args(sys.argv[1:])

    
    # Create logging handler which goes to stdout
    handler = StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt='[%(levelname)s] %(message)s'))
    handler.setLevel(args.log_level)

    # Instantiate the block report writer
    if args.report is not None:
        writer = CLIBlockReportCaller(args.report)
    else:
        writer = None
    # Instantiate PixelartProcessor
    processor = PixelartProcessor(args.textures, args.input, args.output,
            colorspace=args.colorspace, interp=args.interp,
            minkowski=args.p, image_scaling=args.scaling,
            texture_dimension=args.texture_dimension,
            logging_handler=handler, ui_caller=writer)
    processor.process()

def main():
    cli_process()

if __name__ == '__main__':
    main()
