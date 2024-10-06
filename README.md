# Long Video to Short!
- Trying to recreate CapCut's Long Video to Short AI



## Expected Process

- Merge audio track: ```track_merger.py```

- Extract audio(?): ```audio_extract.py```
- Extract transcript/subtitles ```subtitle_generator.py```
- Decide sections ```clip_decider.py```
- Cut sections ```clip_creator.py```
- Cut into short format ```short_scene_formatter.py```

- Extract transcript/subtitles ```subtitle_generator.py```
- Fix transcript/subtitles - I'll save this for later
- Add subtitle to section ```ffmpeg_subtitle.py```

## Bugs to fix
- Force under 1 minute
- Find better model?
- Set to 2 channels cause of 6 channels messing up Instagram upload