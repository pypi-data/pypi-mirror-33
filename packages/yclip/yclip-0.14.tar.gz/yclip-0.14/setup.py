'''TO DO: maybe not overwrite config'''

import os
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
#from subprocess import check_call

def post_install():
    '''makes program folder at home
    and ads config in it'''
    home_folder = os.path.expanduser("~")
    yclip_folder = os.path.join(home_folder, 'yclip')
    yclip_videos_folder = os.path.join(yclip_folder, 'videos')
    config_file_path = os.path.join(yclip_folder, 'config.ini')
    downloaded_videos_txt = os.path.join(yclip_folder, 'downloaded_videos.txt')
    if not os.path.exists(yclip_videos_folder):
        os.makedirs(yclip_videos_folder)

    default_config = '''\
[main]
ffmpeg_path = ffmpeg

#hq, normal
#hq not yet implemented
default_mode = normal
'''

    with open(config_file_path, 'w') as f:
        f.write(default_config)

    with open(downloaded_videos_txt, 'w') as f:
        pass

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        #check_call("apt-get install this-package".split())
        develop.run(self)
        post_install()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        #check_call("apt-get install this-package".split())
        install.run(self)
        post_install()


setup(
    name='yclip',
    version=0.14,
    packages=find_packages(),
    author = 'Henri Airaksinen',
    author_email = 'henri.airaksinen@gmail.com',
    install_requires = ['pytube>=9.2.2',
                        'more_itertools',
                        'requests',
                        'html2text'],
    entry_points = {
        'console_scripts': [
        "yclip = scripts.yclip:main"
        ]
        },
    cmdclass = {
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    }
    
)


#https://stackoverflow.com/questions/20288711/post-install-script-with-python-setuptools
