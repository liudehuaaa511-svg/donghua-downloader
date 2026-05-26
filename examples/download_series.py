#!/usr/bin/env python3
"""
Example: Download multiple episodes from a series
"""

import sys
sys.path.insert(0, '..')

from donghua_downloader import DonghuaWorldDownloader

# Create downloader instance
downloader = DonghuaWorldDownloader(
    output_dir='./downloads',
    verbose=True
)

# Download series (episodes 1-10)
series_url = 'https://donghuaworld.com/anime/renegade-immortal-xian-ni/'
downloader.download_series(series_url, start_ep=1, end_ep=10)

print('Batch download completed!')
