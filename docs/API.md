# API Reference

## DonghuaWorldDownloader

Main class for downloading videos.

### Constructor

```python
DonghuaWorldDownloader(output_dir=None, proxy=None, verbose=True)
```

**Parameters:**
- `output_dir` (str, optional): Output directory for downloads. Defaults to `~/Downloads/donghua`.
- `proxy` (str, optional): Proxy URL for requests.
- `verbose` (bool, optional): Enable verbose output. Defaults to `True`.

### Methods

#### download_episode

Download a single episode.

```python
download_episode(episode_url, output_filename=None)
```

**Parameters:**
- `episode_url` (str): URL of the episode page.
- `output_filename` (str, optional): Custom output filename.

**Returns:**
- `bool`: True if download successful, False otherwise.

**Example:**
```python
downloader = DonghuaWorldDownloader()
success = downloader.download_episode('https://donghuaworld.com/xxx-episode-1/')
```

#### download_series

Download multiple episodes from a series.

```python
download_series(series_url, start_ep=1, end_ep=999)
```

**Parameters:**
- `series_url` (str): URL of the series page.
- `start_ep` (int, optional): First episode to download. Defaults to 1.
- `end_ep` (int, optional): Last episode to download. Defaults to 999.

**Example:**
```python
downloader = DonghuaWorldDownloader()
downloader.download_series('https://donghuaworld.com/anime/xxx/', start_ep=1, end_ep=10)
```

#### get_video_sources

Get available video sources for a player URL.

```python
get_video_sources(player_url)
```

**Parameters:**
- `player_url` (str): URL of the video player.

**Returns:**
- `list[VideoSource]`: List of available video sources.

## VideoSource

Represents a video source with quality information.

### Attributes

- `url` (str): Video URL.
- `quality` (str): Quality label (e.g., '1080p').
- `size` (int): File size in bytes.
- `source_type` (str): Source type ('mp4', 'm3u8').

## Config

Configuration settings class.

### Class Attributes

- `QUALITY_PRIORITY` (list): Priority order for quality selection.
- `QUALITY_SUFFIXES` (dict): Mapping of quality to URL suffixes.
- `TIMEOUT` (int): Request timeout in seconds.
- `DOWNLOAD_TIMEOUT` (int): Download timeout in seconds.
- `CHUNK_SIZE` (int): Download chunk size in bytes.
- `RETRY_COUNT` (int): Number of retries for failed requests.

## Logger

Logging utility for output formatting.

### Static Methods

- `Logger.info(msg)`: Print info message.
- `Logger.success(msg)`: Print success message.
- `Logger.warning(msg)`: Print warning message.
- `Logger.error(msg)`: Print error message.
- `Logger.progress(current, total, prefix)`: Print progress bar.

## Command Line Interface

### Usage

```bash
python donghua_downloader.py [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--url` | `-u` | Single episode URL |
| `--series` | `-s` | Series page URL |
| `--start` | | Start episode number |
| `--end` | | End episode number |
| `--output` | `-o` | Output filename |
| `--dir` | `-d` | Output directory |
| `--proxy` | `-p` | Proxy URL |
| `--quiet` | `-q` | Quiet mode |
| `--version` | `-v` | Show version |
