#! /usr/bin/python3

import os
import sys
import datetime
import fnmatch
import configparser
import random
from pkg_resources import Requirement, resource_filename

import youtube_dl
from moviepy.editor import *
import sox
import ffmpy

from tubedreams.version import __version__
from tubedreams.tdparser import args




# catch incompatiblity errors

if args.dontdownload and args.fresh:
    parser.error('cannot use arguments -dd and -f. arguments incompatible')
if args.dontdownload and args.downloadall:
    parser.error('cannot use arguments -dd and -da. arguments incompatible')
if args.onlyaudio and args.setaudio:
    parser.error('cannot use arguments -a and -oa. arguments incompatible')
if args.login is not None and len(args.login) is not 2:
    parser.error('Give two values for login, not {}.'.format(len(args.login)))

# remove raw downloaded videos
def removeraw():
    files = []
    print("removing raw videos")
    for file in os.listdir(directories[0]):
        absdir = os.path.abspath(directories[0])
        if fnmatch.fnmatch(file, '*' + date + '*') and os.path.isfile(absdir+'/'+file):
            os.remove(absdir + '/' + file)
            files.append(file)
    return "deleted " + str(files)

# read credentials from tubedreams.conf
def readCred(method, creds=['','']):
    if method is 'config':

        configfile = resource_filename(Requirement.parse("tubedreams"),".tubedreams.conf")
        config = configparser.ConfigParser()
        config.read(configfile)
        li = config.get("configuration","login")
        pw = config.get("configuration","password")
        return [li, pw]

    else:
        return creds

# only take audio
def audioAndQuit(a):
    a_outfile_final = output_path_temp.replace('-temp','').replace(ext,'.mp3')
    os.rename(a, a_outfile_final)
    print("finished writing " + a_outfile_final)
    # and quit, since we only care about audio
    if not args.keep and not args.dontdownload:
        print(removeraw())
    sys.exit(2)

# sox function to transform audio
def transformAudio (vid):
    audio_in = vid.audio
    a_infile = out_directory + '/audio_in-temp.mp3'
    a_outfile = out_directory + '/audio_out-temp.mp3'

    if not processaudio:
        if not args.onlyaudio:
            return vid
        else:
            audio_in.write_audiofile(a_infile, fps=44100)
            audioAndQuit(a_infile)

    else:

        audio_in.write_audiofile(a_infile, fps=44100)

        audiofx = sox.Transformer()

        n_echos = 4
        audiofx.echos(gain_in=0.8, gain_out=0.9, n_echos=n_echos, delays=[60]*n_echos, decays=[1]*n_echos)
        audiofx.fade(fade_in_len=.5, fade_out_len=3)
        audiofx.pitch(-2)
        audiofx.reverb(reverberance=80, high_freq_damping=30, room_scale=100, stereo_depth=100, pre_delay=0, wet_gain=1, wet_only=True)

        audiofx.build(a_infile, a_outfile)

        os.remove(a_infile)

        # currently implements this in an inefficient way by first concatenating moviepy video clips
        if args.onlyaudio:
            audioAndQuit(a_outfile)

        vid2 = vid.set_audio(AudioFileClip(a_outfile)) # cannot read directly from file, must make into moviepy audiofileclip first

        os.remove(a_outfile)

        return vid2

# add video filters with ffmpy (ffmpeg)
def ffmpyFX(tempPath, finalPath, filt):

    ff = ffmpy.FFmpeg(
        inputs={tempPath: '-y'}, # overwrite existing file if there is one - no confirmation dialogue
        outputs={finalPath: '-vf ' + filt}
    )

    ff.run()

    print('ffmpeg export completed: ' + finalPath)
    os.remove(tempPath)

# add login information to youtube-dl argument dictionary
def addLogin(dict, method, creds):
    if method is 'netrc':
        # uses login information in .netrc
        dict.update({'usenetrc': True })

    elif method is 'cli' or 'config':
        dict.update({'username': creds[0], 'password': creds[1]})

    # else don't add any login information

# download videos using youtube-dl
def dl(u='https://www.youtube.com/feed/history', num=1, meth='config', cred=['',''], all=False): # takes url, number of videos, login method, credentials (which can be a blank two item list i.e., c=['',''])



    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)


    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')
        if d['status'] == 'downloading':
            print(d['filename'], d['_percent_str'], d['_eta_str'], '\r', end='')

    # update credentials according to login method
    credentials = readCred(meth, cred)

    # get total number of videos from playlist by first extracting metadata
    meta_opts = {'extract_flat': True, 'quiet': True}
    addLogin(meta_opts, meth, cred)

    print('reading url...')

    with youtube_dl.YoutubeDL(meta_opts) as ydl:
        meta = ydl.extract_info(u, download=False)

    try:
        pl_total_items = len(meta['entries'])
        print('found ' + str(pl_total_items) + '... selecting ' + str(num) + ' item(s)....')

    except: # catches errors if non-playlist url is entered
        pl_total_items = 1

    #select indexes in video playlist to download
    playlist_items = ''
    if downloadall:
        for i in range (1, pl_total_items):
            playlist_items = playlist_items + str(i) + ','
    else:
        for i in range (num_to_download):
            n = random.randint(1,pl_total_items)
            playlist_items = playlist_items + str(n) + ','
    playlist_items = playlist_items[:-1]

    print('downloading item(s) ' + playlist_items + '...')



    ydl_opts = {
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        'outtmpl': directories[0]+'/rawvid-' + date + '-%(autonumber)s-%(title)s.%(ext)s',
        'playlist_items': playlist_items,
        'ignoreerrors': True,
    }
    addLogin(ydl_opts, meth, cred)


    print('starting download...')
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([u])

# chop videos using moviepy
def chop():

    clips = []
    inputs = []
    if args.grow:
        if args.exponential: exponent = 2
        else: exponent = 1

        def stretch(t, l):
            return t + (((l/output_length)**exponent)*(last_leg_length-t))
    else:
        def stretch(t, l):
            return t

    def addScaled (array, video):
        array.append(VideoFileClip(video).resize( (xdim, ydim) ) )


    for dirs in directories:
        absdir = os.path.abspath(dirs)
        for file in os.listdir(dirs):
            if fnmatch.fnmatch(file, input_match_pattern) and os.path.isfile(absdir+'/'+file):
                addScaled(inputs,dirs+'/'+file)


    all_inputs =  concatenate_videoclips(inputs)
    total_input_length = all_inputs.duration
    length_so_far = 0

    print("starting concatenation...")
    while length_so_far < output_length-last_leg_length:
        start = round(random.uniform(0,total_input_length-max_length), 2)
        base = round(random.uniform(min_length, max_length), 2)
        variable_clip_length = stretch(base, length_so_far)
        length_so_far = length_so_far + variable_clip_length
        clips.append(all_inputs.subclip(start,start+variable_clip_length))
    start = round(random.uniform(0,total_input_length-last_leg_length), 2) #have a longer last clip for some closure // this is really only necessary for --growth = False
    clips.append(all_inputs.subclip(start,start+last_leg_length))

    all_clips = concatenate_videoclips(clips) #.set_audio(audiofile) #compile clips then add audio

    print(str(len(clips)) + " clips concatenated... total length = " + str(length_so_far+last_leg_length))

    if args.setaudio is not None:
        #add audio if any specified, otherwise transform audio
        print("adding audio: "+ args.setaudio)
        audioclip = AudioFileClip(args.setaudio).subclip(0,length_so_far)
        all_clips_w_audio_fx = all_clips.set_audio(audioclip)

    else:
        #sox
        print("soxing some audio...")
        all_clips_w_audio_fx = transformAudio(all_clips)

    # get codec for video formats without moviepy defaults
    if args.codec is not None:
        extcodec = args.codec
    elif 'avi' in ext:
        extcodec = 'png'
    elif 'mkv' in ext:
        extcodec='libx264'
    else: extcodec = None # moviepy selects default codecs for mp4 (libx264), webm (libvpx) and ogv (libvorbis)

    all_clips_w_audio_fx.write_videofile(output_path_temp, codec=extcodec)

    print('moviepy export completed: ' + output_path_temp)

###########################################################################

### DO STUFF ###


# files
date = datetime.datetime.now().strftime("%m-%d-%y--%H-%M")
if args.pattern is None:
    input_match_pattern = '*'
else:
    input_match_pattern = '*' + args.pattern + '*'

if args.source is None:
    directories = ['.'] # can add multiple directories
else:
    directories = args.source

for i, d in reversed(list(enumerate(directories))): #reversed so catches errors before making new directories
    if not os.path.isdir(d):
        if i is 0: #directory which videos are downloaded to
            print('the directory', d, 'does not exist. making', d)
            os.makedirs(d)
        else:
            print(d, 'is not a directory. if you want to create this directory to store downloaded items, list this directory as the first in directory. exiting...')
            sys.exit(2)



# decide what to do with output path

default_out_directory = '.'
ext = '.mp4' # default value for output format
if args.output is None:
    out_directory = default_out_directory
    if not os.path.isdir(out_directory): os.makedirs(out_directory)
    output_path_temp = out_directory+'/'+date+ext
else:
    if os.path.isdir(args.output):
        #directory path given, make up filename
        out_directory = args.output
        output_path_temp = out_directory + '/' + date + ext
    else:
        outsplit = args.output.split('/')
        p_fn = outsplit[-1]
        p_dir = '/'.join(outsplit[0:-1])
        if p_dir is "" or os.path.isdir(p_dir):
            if p_dir is "":
                #an output file is given
                out_directory = os.getcwd()
                if not os.path.isdir(out_directory): os.makedirs(out_directory)
                output_path_temp = out_directory+'/'+date+ext

            else:
                #a full path to output file is given
                out_directory = p_dir

            if '.' in p_fn:
                #an extension is provided in path, so writeover default ext value
                output_path_temp = out_directory + '/' + p_fn
                ext = '.' + p_fn.split('.')[-1]
            else:
                #no extension is given in full path
                output_path_temp = out_directory + '/' + p_fn + ext

        else:
            print('not a valid output path. quitting...')
            sys.exit(2)

output_path_temp = output_path_temp.replace(ext,'-temp'+ext)



# download videos with youtube-dl

if not args.dontdownload:

    if args.fresh:
        input_match_pattern = '*' + date + input_match_pattern # all raw videos are marked with date and time

    downloadall = args.downloadall

    if args.number is None:
        num_to_download = 1
    else:
        num_to_download = args.number
    if args.url is None:
        url = 'https://www.youtube.com/feed/history' #default url
        print ('no url specified... so ' + url + ' will be used')
    else:
        url = args.url

    if args.login is not None:
        # uses login information passed to command line
        loginMethod = 'cli'
        credentials = args.login

    else:

        credentials = ['','']

        if args.netrc:
            # uses login information in .netrc
            loginMethod = 'netrc'

        elif not args.nologin:
            loginMethod = 'config'

        else:
            loginMethod = None

    dl(url, num_to_download, loginMethod, credentials, downloadall)


# concatenate clips and export to moviepy

if args.resolution is None:
    xdim = 854 #480 quality
    ydim = 480
elif len(args.resolution) is 1:
    ydim = args.resolution[0]
    xdim =( ydim / 9 ) * 12
else:
    xdim = max(args.resolution)
    ydim = min(args.resolution)

if args.length is None:
    output_length = 20
else:
    output_length = args.length

if args.minmax is None:
    max_length = 1
    min_length = 1
elif len(args.minmax) is 1:
    max_length = args.minmax[0]
    min_length = args.minmax[0]
else:
    max_length = max(args.minmax)
    min_length = min(args.minmax)

if args.finalclip is None:
    last_leg_length = max_length
else:
    last_leg_length = args.finalclip

processaudio = not args.dontprocessaudio

chop() # the function to call moviepy


# remove raw files after processing

if not args.keep and not args.dontdownload:
    print(removeraw())


# prepare final output

output_path_final = output_path_temp.replace('-temp','')

if args.videofilters is None:
    os.rename(output_path_temp,output_path_final)
    sys.exit(2)

# if filters are given, use ffmpy (ffmpeg) to add filters to video
else: ffmpyFX(output_path_temp, output_path_final, args.videofilters)
