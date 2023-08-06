# parse options with argparse

import argparse
from tubedreams.version import __version__

def required_length(nmin,nmax):
    class RequiredLength(argparse.Action):
        def __call__(self, parser, args, values, option_string=None):
            if not nmin<=len(values)<=nmax:
                msg='argument "{f}" requires between {nmin} and {nmax} arguments'.format(
                    f=self.dest,nmin=nmin,nmax=nmax)
                raise argparse.ArgumentTypeError(msg)
            setattr(args, self.dest, values)
    return RequiredLength

parser = argparse.ArgumentParser(
    description='create dream-sequences from your video browsing history',
    prog='tubedreams',
    )

parser.add_argument('-v', '--version', action='version', version="%(prog)s ("+__version__+")", help='show program\'s version number and exit')
parser.add_argument('-dd', '--dontdownload', action='store_true', help="don't download any videos or connect to youtube-dl. will only use local videos from source directories.")
parser.add_argument('-s', '--source', nargs='*', help='specify directories to draw raw footage from. the first directory listed also specifies the location for new videos to download', metavar="")
parser.add_argument('-p', '--pattern', nargs='?', help='only use videos from input directories which contain a given string. note: will still download raw videos that do not match pattern.', metavar="")
parser.add_argument('-f', '--fresh', action='store_true', help='only include videos downloaded this run')
parser.add_argument('-o', '--output', nargs='?', help='specify file name and directory for final video output', metavar="")
parser.add_argument('-k', '--keep', action='store_true', help='keep raw downloaded videos after processing is completed')

ytdl_options = parser.add_argument_group('youtube-dl options')

ytdl_options.add_argument('-u', '--url', nargs='?', help='the url of the playlist, search page, or video to download from. default is to grab history from https://www.youtube.com/feed/history', metavar="")
ytdl_options.add_argument('-n', '--number', type=int, nargs='?', help='number of videos to download', metavar="")
ytdl_options.add_argument('-da', '--downloadall', action='store_true', help='download all videos in playlist. overrides -n')
ytdl_options.add_argument('-N', '--netrc', action='store_true', help='use .netrc file for login instead of .tubedreams.conf')
ytdl_options.add_argument('-L', '--login', nargs='*', help='username and password for accessing YouTube or other site via youtube-dl.', metavar='')
ytdl_options.add_argument('-nl', '--nologin', action='store_true', help='do not log into an account to access site')

video_options = parser.add_argument_group('video output options')

video_options.add_argument('-l', '--length', type=float, nargs='?', help='total length of video to output', metavar="")
video_options.add_argument('-m', '--minmax', metavar="", type=float, nargs='*', action=required_length(1,2), help='minimum and maximum length of each clip. one input fixes a static clip length. two inputs sets range.')
video_options.add_argument('-fc', '--finalclip', type=float, nargs='?', help='specify length of final clip', metavar="")
video_options.add_argument('-g', '--grow', action='store_true', help='scale length of clips so that they gradually get longer or shorter to match finalclip. must use with finalclip.')
video_options.add_argument('-x', '--exponential', action='store_true', help='makes length scaling exponential. must use with grow.')
video_options.add_argument('-r', '--resolution', type=int, nargs='*', action=required_length(1,2), help='select dimensions to output to. one input specifies y dimension for 12:9 ratio.\
 for two inputs, the smaller specifies y and the larger specifies x. default is 480p.',metavar="")
video_options.add_argument('-c', '--codec', nargs='?', metavar="", help='choose codec for uncommon video format or override default codec. defaults are included for \
mp4 (libx264), mkv (libx264), webm (libvpx), ogv (libvorbis) and avi (png).')
video_options.add_argument('-a', '--setaudio', nargs='?', help='add path to audio track to use',metavar="")
video_options.add_argument('-oa', '--onlyaudio', action='store_true', help='only export to mp3 audio, no video.')
video_options.add_argument('-dp', '--dontprocessaudio',action='store_true', help='keep raw audio and do not apply sox filters.')
video_options.add_argument('-vf', '--videofilters', nargs='?', help='add ffmpeg video filters to output video. type "ffmpeg -filters | grep \'V->\'" for list of available filters.', metavar="")

args = parser.parse_args()
