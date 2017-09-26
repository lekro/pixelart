import argparse
import sys
import logging

def valid_scale(string):
    if 'x' not in string:
        msg = "Invalid scaling option %s" % string
        raise argparse.ArgumentTypeError(msg)
    w, h = a.split('x')
    w = int(w)
    h = int(h)
    if w < 1 or h < 1:
        msg = "Scaling width and height must be 1 or greater!"
        raise argparse.ArgumentTypeError(msg)
    return w, h

def cli_process():

    parser = argparse.ArgumentParser(description='Match pixels to textures')

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
    parser.add_argument('-c', '--color-space', dest='space', type=str,
                        choices=['RGB', 'HSV', 'YCbCr', 'LAB'], 
                        default='RGB',
                        help='Color space in which nearest neighbors are\
                                found. (default: %(default)s)')
    parser.add_argument('-i', '--interpolation', dest='interp', type=str,
                        choices=['nearest', 'bilinear', 'bicubic', 
                                 'lanczos'],
                        default='lanczos',
                        help='Interpolation method used to scale the\
                                input image and to find the average\
                                color of each texture. (default: \
                                %(default)s)')
    parser.add_argument('-r', '--report', dest='report', type=str,
                        help='Path to output block report. This file will\
                                contain numbers and types of blocks\
                                (or textures) required to make the\
                                pixelart. (default: %(default)s)')
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
    print(args)

if __name__ == '__main__':
    cli_process()
