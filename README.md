# README #

Frame extractor to convert movies into still images for labeling.  
Extracts still frame per duration specified in --step of a movie, (optionally) deinterlaces, and saves as a png.
Uses multiple cores to speed-up computation.
  
## Run Examples
*Arguments*

  * -i input directory of video files(.mov, .mp4, anything ffmpeg will support), or single input video files; if specifying input directory must use keys
  * -o (optional, defaults to input directory) output directory to store results. 
    * Two directories are created for the results:
     * the key name, or the root filename, e.g. D0232_20160501T000030Z if input is D0232_20160501T000030Z.mov
     * imgs
  * -t or --start Start time in HH:MM:SS format (optional)
  * -e or --end End time in HH:MM:SS format (optional)
  * -m or --milliseconds Number of milliseconds to capture every step
  * -s or --step Step size in seconds to grab a frame. If not specified, extracts all frames
  * -g glob pattern list of search patterns to find video files in conjunction with -i
  * -d (optional) deinterlace method, e.g. drop or yadif
    * drop will remove every other field
    * yadif = Yet Another Deinterlacing Filer (see ffmpeg page for details on this)
    
*Examples*

Extract one frames every 5 seconds from file D0232_20160501T000030Z.mov to your desktop, no deinterlacing
```bash
docker run -v $PWD/data:/data  -v /Users/dcline/Desktop:/desktop frameextractor -i /data/D0232_20160501T000030Z.mov -o /desktop
```
Extract one frame every 5 seconds from file D0232_20160501T000030Z.mov to your desktop, drop deinterlacing
```bash
docker run -v $PWD/data:/data  -v /Users/dcline/Desktop:/desktop frameextractor -i /data/D0232_20160501T000030Z.mov -o /desktop  -d drop
```
Extract one frame every 2 seconds between 00:00:00 to 00:05:00 of file D0232_20160501T000030Z.mov to your desktop
```bash
docker run -v $PWD/data:/data  -v /Users/dcline/Desktop:/desktop frameextractor -i /data/D0232_20160501T000030Z.mov -o /desktop -s 2 --start 00:00:00 --end 00:05:00
```
Extract 2 seconds of each video to your desktop, searching for videos matching the pattern D*.MOV recursively in the /data directory. 
This will split compute for each video across each CPU available.
```bash
docker run -v $PWD/data:/data  -v /Users/dcline/Desktop:/desktop frameextractor -i /data  --keys '/**/D*.MOV' -o /desktop -s 2
```

## Developer notes 
Run interactively, mounts your current directory in the container as tmp/code, and any
changes made in that /tmp/code directory, even after the container closes will persist.

```bash
docker run -v $PWD:/tmp/code -it --entrypoint='bash' mbari/deepsea-frameextractor
```

Exiftools
All tags available by format
https://sno.phy.queensu.ca/~phil/exiftool/TagNames/index.html
For PNG
https://sno.phy.queensu.ca/~phil/exiftool/TagNames/PNG.html
