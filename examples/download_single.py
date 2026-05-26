#!/usr/bin/env python3
"""
Example: Download a single episode
"""

import sys
sys.path.insert(0, '..')

from donghua_downloader import DonghuaWorldDownloader

# Create downloader instance
downloader = DonghuaWorldDownloader(
    output_dir='./downloads',
    verbose=True
)

# Download single episode
url = 'https://donghuaworld.com/renegade-immortal-xian-ni-episode-114-4k-multi-subtitles/'
success = downloader.download_episode(url)

if success:
    print('Download completed!')
else:
    print('Download failed!')
