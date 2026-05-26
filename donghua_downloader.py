#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DonghuaWorld Video Downloader
Download videos from donghuaworld.com with best available quality
"""

import os
import re
import sys
import time
import json
import base64
import argparse
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    from curl_cffi import requests
except ImportError:
    print("Error: curl_cffi not installed. Run: pip install curl_cffi")
    sys.exit(1)


class Config:
    """Configuration settings"""
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    
    QUALITY_PRIORITY = [
        '2160p', '1440p', '1080p', '720p', '480p', '360p', '240p'
    ]
    
    QUALITY_SUFFIXES = {
        '2160p': ['kaaa', 'jaaa', 'iaaa'],
        '1440p': ['iaa', 'haa', 'gaa', 'faa', 'eaa', 'daa', 'caa', 'baa', 'aaa'],
        '1080p': ['haa', 'gaa', 'faa'],
        '720p': ['gaa', 'faa', 'eaa'],
        '480p': ['faa', 'eaa', 'daa'],
        '360p': ['eaa', 'daa', 'caa'],
        '240p': ['daa', 'caa', 'baa'],
    }
    
    TIMEOUT = 30
    DOWNLOAD_TIMEOUT = 600
    CHUNK_SIZE = 65536
    RETRY_COUNT = 3
    RETRY_DELAY = 2


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    @classmethod
    def disable(cls):
        """Disable colors for non-TTY output"""
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ''
        cls.MAGENTA = cls.CYAN = cls.WHITE = cls.RESET = cls.BOLD = ''


class Logger:
    """Logging utility"""
    
    @staticmethod
    def info(msg):
        print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")
    
    @staticmethod
    def success(msg):
        print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")
    
    @staticmethod
    def warning(msg):
        print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {msg}")
    
    @staticmethod
    def error(msg):
        print(f"{Colors.RED}[ERROR]{Colors.RESET} {msg}")
    
    @staticmethod
    def progress(current, total, prefix=""):
        if total > 0:
            pct = current * 100 // total
            mb_current = current // 1024 // 1024
            mb_total = total // 1024 // 1024
            bar_len = 30
            filled = bar_len * pct // 100
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"\r{prefix} [{bar}] {pct}% ({mb_current}/{mb_total}MB)", end='', flush=True)


class VideoSource:
    """Represents a video source with quality info"""
    def __init__(self, url, quality, size=0, source_type='mp4'):
        self.url = url
        self.quality = quality
        self.size = size
        self.source_type = source_type
    
    def __repr__(self):
        return f"VideoSource(quality={self.quality}, size={self.size//1024//1024}MB, type={self.source_type})"


class DonghuaWorldDownloader:
    """Main downloader class"""
    
    def __init__(self, output_dir=None, proxy=None, verbose=True):
        self.output_dir = output_dir or os.path.join(os.path.expanduser("~"), "Downloads", "donghua")
        self.proxy = proxy
        self.verbose = verbose
        self.session = requests.Session()
        self.stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        if not verbose:
            Colors.disable()
    
    def _get_headers(self, referer=None):
        """Get request headers"""
        headers = Config.DEFAULT_HEADERS.copy()
        if referer:
            headers['Referer'] = referer
        return headers
    
    def _request(self, url, method='GET', **kwargs):
        """Make HTTP request with retry logic"""
        kwargs.setdefault('timeout', Config.TIMEOUT)
        kwargs.setdefault('impersonate', 'chrome')
        
        if 'headers' not in kwargs:
            kwargs['headers'] = self._get_headers()
        
        for attempt in range(Config.RETRY_COUNT):
            try:
                response = self.session.request(method, url, **kwargs)
                return response
            except Exception as e:
                if attempt < Config.RETRY_COUNT - 1:
                    time.sleep(Config.RETRY_DELAY * (attempt + 1))
                    if self.verbose:
                        Logger.warning(f"Retry {attempt + 1}/{Config.RETRY_COUNT}: {str(e)[:50]}")
                else:
                    raise
        return None
    
    def get_episode_page(self, url):
        """Fetch episode page content"""
        try:
            response = self._request(url)
            if response and response.status_code == 200:
                return response.text
        except Exception as e:
            Logger.error(f"Failed to fetch page: {e}")
        return None
    
    def extract_player_sources(self, html):
        """Extract player source URLs from episode page"""
        sources = []
        
        # Find data-hash attributes (base64 encoded iframes)
        data_hashes = re.findall(r'data-hash="([^"]+)"', html)
        
        for h in data_hashes:
            try:
                # Try base64 decode
                decoded = base64.b64decode(h).decode('utf-8')
                src_match = re.search(r'src="([^"]+)"', decoded)
                if src_match:
                    sources.append(src_match.group(1))
            except:
                continue
        
        return sources
    
    def get_video_sources(self, player_url):
        """Get available video sources from player page"""
        sources = []
        
        try:
            response = self._request(player_url, headers=self._get_headers(
                referer='https://donghuaworld.com/'
            ))
            
            if not response or response.status_code != 200:
                return sources
            
            html = response.text.replace('\\/', '/')
            
            # Find base URL for video files
            base_match = re.search(
                r'(https://hugh\.cdn\.rumble\.cloud/video/[a-zA-Z0-9/]+/[A-Za-z0-9_]+)\.',
                html
            )
            
            if not base_match:
                return sources
            
            base_url = base_match.group(1)
            
            # Test all quality suffixes
            for quality in Config.QUALITY_PRIORITY:
                suffixes = Config.QUALITY_SUFFIXES.get(quality, [])
                
                for suffix in suffixes:
                    test_url = f"{base_url}.{suffix}.mp4"
                    
                    try:
                        head_response = self._request(
                            test_url, 
                            method='HEAD',
                            timeout=10
                        )
                        
                        if head_response and head_response.status_code == 200:
                            size = int(head_response.headers.get('content-length', 0))
                            if size > 1000000:  # At least 1MB
                                sources.append(VideoSource(
                                    url=test_url,
                                    quality=quality,
                                    size=size,
                                    source_type='mp4'
                                ))
                                break
                    except:
                        continue
                
                # If we found a source for this quality, stop searching lower qualities
                if sources:
                    break
            
        except Exception as e:
            if self.verbose:
                Logger.error(f"Error getting video sources: {e}")
        
        return sources
    
    def download_file(self, url, output_path, desc=""):
        """Download file with progress display"""
        try:
            response = self._request(
                url,
                stream=True,
                timeout=Config.DOWNLOAD_TIMEOUT,
                headers=self._get_headers('https://player.donghuaplanet.com/')
            )
            
            if not response or response.status_code != 200:
                return False
            
            total = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=Config.CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if self.verbose and total > 0:
                            Logger.progress(downloaded, total, desc)
            
            if self.verbose:
                print()  # New line after progress
            
            return os.path.exists(output_path) and os.path.getsize(output_path) > 0
            
        except Exception as e:
            if self.verbose:
                Logger.error(f"Download error: {e}")
            return False
    
    def download_episode(self, episode_url, output_filename=None):
        """Download a single episode"""
        if self.verbose:
            Logger.info(f"Processing: {episode_url}")
        
        # Get episode page
        html = self.get_episode_page(episode_url)
        if not html:
            if self.verbose:
                Logger.error("Failed to fetch episode page")
            return False
        
        # Extract player sources
        player_sources = self.extract_player_sources(html)
        if not player_sources:
            if self.verbose:
                Logger.warning("No player sources found")
            return False
        
        # Find best video source
        best_source = None
        all_sources = []
        
        for player_url in player_sources:
            if 'donghuaplanet.com' in player_url:
                sources = self.get_video_sources(player_url)
                all_sources.extend(sources)
                
                if sources:
                    # Sort by quality priority
                    sources.sort(key=lambda s: Config.QUALITY_PRIORITY.index(s.quality) 
                                 if s.quality in Config.QUALITY_PRIORITY else 999)
                    best_source = sources[0]
                    break
        
        if not best_source:
            if self.verbose:
                Logger.warning("No video source available")
            return False
        
        # Generate output filename
        if not output_filename:
            ep_match = re.search(r'episode-(\d+)', episode_url)
            ep_num = ep_match.group(1) if ep_match else 'video'
            output_filename = f"Ep{ep_num}.mp4"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Check if already downloaded
        if os.path.exists(output_path) and os.path.getsize(output_path) > 50000000:
            if self.verbose:
                Logger.warning(f"Already exists: {output_filename}")
            self.stats['skipped'] += 1
            return True
        
        if self.verbose:
            Logger.info(f"Quality: {best_source.quality}, Size: {best_source.size//1024//1024}MB")
            Logger.info(f"Downloading to: {output_filename}")
        
        # Download
        success = self.download_file(best_source.url, output_path, "  Downloading")
        
        if success:
            if self.verbose:
                Logger.success(f"Downloaded: {output_filename}")
            self.stats['success'] += 1
            return True
        else:
            if self.verbose:
                Logger.error(f"Failed: {output_filename}")
            self.stats['failed'] += 1
            return False
    
    def download_series(self, series_url, start_ep=1, end_ep=999):
        """Download multiple episodes from a series"""
        if self.verbose:
            Logger.info(f"Fetching series page: {series_url}")
        
        # Get series page
        response = self._request(series_url)
        if not response or response.status_code != 200:
            Logger.error("Failed to fetch series page")
            return
        
        html = response.text
        
        # Find episode links
        series_slug = re.search(r'/anime/([^/]+)/?', series_url)
        if not series_slug:
            Logger.error("Invalid series URL format")
            return
        
        slug = series_slug.group(1)
        episode_links = re.findall(
            rf'href="(https://donghuaworld\.com/{slug}-episode-\d+[^"]*)"',
            html
        )
        
        # Remove duplicates and sort
        episode_links = list(set(episode_links))
        episode_links.sort(key=lambda x: int(re.search(r'episode-(\d+)', x).group(1)))
        
        # Filter by range
        episodes_to_download = []
        for link in episode_links:
            ep_match = re.search(r'episode-(\d+)', link)
            if ep_match:
                ep_num = int(ep_match.group(1))
                if start_ep <= ep_num <= end_ep:
                    episodes_to_download.append((ep_num, link))
        
        episodes_to_download.sort(key=lambda x: x[0])
        
        if self.verbose:
            Logger.info(f"Found {len(episodes_to_download)} episodes to download")
        
        # Create series folder
        series_name = slug.replace('-', '_')
        self.output_dir = os.path.join(os.path.expanduser("~"), "Downloads", "donghua", series_name)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Download each episode
        for i, (ep_num, link) in enumerate(episodes_to_download, 1):
            if self.verbose:
                print(f"\n{'='*50}")
                Logger.info(f"Episode {ep_num} ({i}/{len(episodes_to_download)})")
            
            self.download_episode(link, f"Ep{ep_num}.mp4")
            time.sleep(1)  # Be polite to the server
        
        # Print summary
        if self.verbose:
            print(f"\n{'='*50}")
            Logger.info("Download Summary:")
            Logger.success(f"  Success: {self.stats['success']}")
            Logger.warning(f"  Skipped: {self.stats['skipped']}")
            Logger.error(f"  Failed: {self.stats['failed']}")
            Logger.info(f"Output: {self.output_dir}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Download videos from DonghuaWorld',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s -u "https://donghuaworld.com/xxx-episode-1/"
  %(prog)s -s "https://donghuaworld.com/anime/xxx/" --start 1 --end 10
  %(prog)s -u "https://donghuaworld.com/xxx-episode-1/" -o "MyVideo.mp4"
        '''
    )
    
    parser.add_argument('-u', '--url', help='Single episode URL')
    parser.add_argument('-s', '--series', help='Series page URL')
    parser.add_argument('--start', type=int, default=1, help='Start episode number')
    parser.add_argument('--end', type=int, default=999, help='End episode number')
    parser.add_argument('-o', '--output', help='Output filename')
    parser.add_argument('-d', '--dir', help='Output directory')
    parser.add_argument('-p', '--proxy', help='Proxy URL')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    parser.add_argument('-v', '--version', action='version', version='%((prog)s 1.0.0')
    
    args = parser.parse_args()
    
    if not args.url and not args.series:
        parser.print_help()
        return
    
    downloader = DonghuaWorldDownloader(
        output_dir=args.dir,
        proxy=args.proxy,
        verbose=not args.quiet
    )
    
    if args.url:
        downloader.download_episode(args.url, args.output)
    elif args.series:
        downloader.download_series(args.series, args.start, args.end)


if __name__ == '__main__':
    main()
