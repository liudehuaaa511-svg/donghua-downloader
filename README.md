# DonghuaWorld Video Downloader

Download videos from donghuaworld.com with the best available quality.

## Features

- Download single episodes or entire series
- Automatically selects highest quality (up to 1440p)
- Support for multiple video sources
- Progress display with download speed
- Resume support for incomplete downloads
- GUI interface available
- Command line interface
- Proxy support

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Download a single episode:
```bash
python donghua_downloader.py -u "https://donghuaworld.com/xxx-episode-1/"
```

Download multiple episodes:
```bash
python donghua_downloader.py -s "https://donghuaworld.com/anime/xxx/" --start 1 --end 10
```

Custom output directory:
```bash
python donghua_downloader.py -u "https://donghuaworld.com/xxx-episode-1/" -d "/path/to/output"
```

Custom filename:
```bash
python donghua_downloader.py -u "https://donghuaworld.com/xxx-episode-1/" -o "MyVideo.mp4"
```

### GUI Interface

```bash
python gui.py
```

## Available Qualities

| Quality | Resolution |
|---------|------------|
| 1440p   | 2560x1440  |
| 1080p   | 1920x1080  |
| 720p    | 1280x720   |
| 480p    | 854x480    |
| 360p    | 640x360    |
| 240p    | 426x240    |

Note: The downloader automatically selects the highest available quality.

## Options

| Option | Description |
|--------|-------------|
| `-u, --url` | Single episode URL |
| `-s, --series` | Series page URL |
| `--start` | Start episode number (default: 1) |
| `--end` | End episode number (default: 999) |
| `-o, --output` | Output filename |
| `-d, --dir` | Output directory |
| `-p, --proxy` | Proxy URL |
| `-q, --quiet` | Quiet mode |

## Troubleshooting

### Connection Errors

If you experience connection issues:
1. Check your internet connection
2. Try using a proxy/VPN
3. Wait a few minutes and retry

### Download Failures

If downloads fail:
1. Check if the URL is correct
2. Make sure you have enough disk space
3. Check if the video is available in your region

### Cloudflare Protection

The script uses `curl_cffi` to bypass Cloudflare protection. If you still encounter issues:
- Update to the latest version
- Try a different network

## Legal Notice

This tool is for personal use only. Please respect copyright laws and the website's terms of service. The authors are not responsible for any misuse of this software.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Changelog

### v1.0.0
- Initial release
- Support for single and series downloads
- Automatic quality selection
- GUI interface
