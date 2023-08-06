#!/usr/bin/env python3

import os
import sys
import tempfile
import argparse
import re
import time
import subprocess
import copy
import configparser

import requests
import html2text

from pytube import YouTube
from more_itertools import unique_everseen

from scripts.classes import ProgressBar, TimeStorage, File

class Yclip(object):
    '''text file input (.txt) = download all videos, no clipping'''
    def __init__(self):

        self.version = 0.14
        self.tmpfold = os.path.join(tempfile.gettempdir(),'yclip')
        #if yclip folder does not exist in temp folder
        #create it
        if not os.path.exists(self.tmpfold):
            os.makedirs(self.tmpfold)
        self.workdir = os.getcwd()

        self.home_folder = os.path.expanduser("~")
        self.yclip_folder = os.path.join(self.home_folder, 'yclip')
        self.videos_folder = os.path.join(self.yclip_folder, 'videos')
        self.config_file_path = os.path.join(self.yclip_folder, 'config.ini')
        self.downloaded_videos_txt = os.path.join(self.yclip_folder, 'downloaded_videos.txt')

        self.config = configparser.ConfigParser()
        self.config.read(self.config_file_path)

        #self.youtube_regex = '(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/ ]{11})'
        self.youtube_regex = '([a-zA-Z0-9_-]{11})'
        self.youtube_url = 'https://www.youtube.com/watch?v='

        #get arguments.
        #if not provided, presume they are piped in
        args = sys.argv[1:]
        if not args:
            args = sys.stdin.read()
        self.args = args

        assert self.args, 'not enough arguments'

        if '-v' in self.args:
            print(self.version)
        else:

            #if need to clip
            if len(self.args) == 3:
                self.clip_start = TimeStorage(custom_input=self.args[1])
                self.clip_end = TimeStorage(custom_input=self.args[2])
                self.clipping = True
            else:
                self.clipping = False

            #check if first argument is a file
            #if it is, scan contents for youtube ids
            if os.path.isfile(args[0]):
                with open(args[0]) as f:
                    data = f.read()
                self.youtube_ids = re.findall(self.youtube_regex, data)
                #remove duplicates from ids
                self.youtube_ids = list(unique_everseen(self.youtube_ids))
            #else youtube ids is the first argument
            else:
                self.youtube_ids = re.search(self.youtube_regex, self.args[0]).group(1)
            assert self.youtube_ids, 'no Youtube id found'

            if type(self.youtube_ids) == str:
                self.youtube_ids = [self.youtube_ids]

            for youtube_id in self.youtube_ids:
                vid_path = File(self.DownloadVideo(youtube_id))

                if vid_path.folder_path == self.tmpfold and self.clipping == False:
                    os.rename(str(vid_path), str(vid_path.set_folder_path(self.videos_folder, True)))

                elif self.clipping:
                    output_path = File(self.ClipVideo(vid_path))
                    new_path = output_path.set_folder_path(self.videos_folder, True)
                    os.rename(str(output_path), str(new_path))


    def ClipVideo(self, vid_path, extension_1 = '_clipped', extension_2 = '.mp4'):
        '''vid path is type File.type
        returns vid output path as string'''
        vid_output = vid_path.set_folder_path(self.tmpfold, True)
        vid_output.file_name_without_extension += extension_1
        vid_output.file_extension = extension_2
        cmd = '{} -y -i "{}" -ss {} -t {} -async 1 "{}"'.format(self.config['main']['ffmpeg_path'],str(vid_path), str(self.clip_start),str(self.clip_end - self.clip_start),vid_output)
        s = subprocess.Popen(cmd,stdout=subprocess.DEVNULL, shell=True)
        r = s.wait()
        return str(vid_output)

    def LoadDownloadedVideos(self):
        with open(self.downloaded_videos_txt) as f:
            return f.read().splitlines()
    def SaveDownloadedVideos(self, titles):
        #titles are with extensions
        if type(titles) == str:
            titles = [titles]

        #add new line after every title
        titles = list(map(lambda x: x + '\n', titles))
        with open(self.downloaded_videos_txt, 'a') as f:
            f.writelines(titles)

    @property
    def downloaded_videos(self):
        return self.LoadDownloadedVideos()

    def VideoLocation(self, title):
        '''check if video on tmp folder
        or video folder and if title in downloaded_videos
        returns path, else none'''
        tmp_path = os.path.join(self.tmpfold, title)
        vid_fold_path = os.path.join(self.videos_folder, title)
        potential_path = ''
        if os.path.isfile(tmp_path):
            potential_path = tmp_path
        elif os.path.isfile(vid_fold_path):
            potential_path = vid_fold_path

        if potential_path and title in self.downloaded_videos:
            return potential_path
        else:
            return None

    def ShowProgressBar(self, stream, chunk, file_handle, bytes_remaining):
        if self.pb_first_run:
            self.pb.max_val = bytes_remaining
            self.pb_first_run = False
        self.pb.Update(self.pb.max_val - bytes_remaining)

    def DownloadVideo(self, vid_id):
        '''downloads video if necessary and
        returns path to downloaded video'''

        vid_info = Yclip.get_link_info(vid_id)
        assert vid_info['status'], 'could not retrieve video title from youtube'
        title = vid_info['title']
        vid_name = title + '.mp4'

        #download only if video is on completed list
        #and can be found on temp folder or videos folder
        vid_path = self.VideoLocation(vid_name)
        if not vid_path:
            self.pb = ProgressBar()
            self.pb_first_run = True

            yt = YouTube(self.youtube_url + vid_id)
            yt.register_on_progress_callback(self.ShowProgressBar)
            #yt.register_on_complete_callback(process)
            #streams = yt.streams.order_by('fps').desc().all()
            streams = yt.streams.filter(progressive=True).order_by('resolution').desc().all()
            #streams = yt.streams.filter(only_audio=True).order_by('abr').asc().all()
            print('Stream quality:')
            print(streams[0])
            print('Downloading {}'.format(title))
            streams[0].download(self.tmpfold)
            self.SaveDownloadedVideos(vid_name)
            vid_path = self.VideoLocation(vid_name)
        assert vid_path,'video not found'
        return vid_path

    def get_link_info(link, regex = '([a-zA-Z0-9_-]{11})', filter = True):

        #match = re.match(r'(^https://(?:www\.){0,1}youtube\.com/watch\?v=.{11}.*|https://youtu\.be/.{11}.*)', link)
        match = re.search(regex, link)
        if match:
            link = 'https://youtube.com/watch?v={}'.format(match.group(0))
            html = requests.get(link).text
            if '<span id="eow-title" class="watch-title"' not in html: #might be partly broken
                status = False
            else:
                status = True
            
            if status:
                image = re.search(r'https:.*(?:maxresdefault|hqdefault)\.jpg', html).group(0)
                title = re.search(r'"eow-title".*?title="(.*?)">', html).group(1)

                match = re.search(r'id="eow-description" class="" >(.*?)<div id="watch-description-extras">', html)
                if match:
                    description = match.group(1)
                    description = html2text.html2text(description)
                    description = description[:-2] #removes 2 newlines at the end
                else:
                    description = ''



            else:
                image = None
                title = None
                description = None

            return {'youtube_link':link, 'status':status, 'title':title, 'image':image, 'description':description}
        else:
            return None

def main():
    Yclip()

if __name__ == '__main__':
    Yclip()