ffmpeg -stream_loop -1 -i "001-video.mp4" -i "001.mp3" -map 0:v:0 -map 1:a:0 -c:v libx264 -c:a aac -pix_fmt yuv420p -shortest "001.mp4"

ffmpeg -stream_loop -1 -i "001-video.mp4" -i "001.mp3" -map 0:v:0 -map 1:a:0 -c:v libx264 -c:a aac -pix_fmt yuv420p -map_metadata -1 -shortest "001.mp4"

# loop video and mix audio of video and external audio, also reduce volume of original video
ffmpeg -i "112-base.mp4" -i "112.mp3" -filter_complex "[0:a]volume=0.3[a0];[1:a]aloop=loop=-1[looped];[a0][looped]amix=inputs=2:duration=first[a]" -map 0:v:0 -map "[a]" -c:v libx264 -c:a aac -pix_fmt yuv420p -map_metadata -1 "112-short.mp4"

# loop video, lower video volume and add audio with full volume
ffmpeg -stream_loop -1 -i "qadr.mp4" -i "97.mp3" -filter_complex "[0:a]volume=0.4[video_audio];[1:a]volume=1.0[bg_music];[video_audio][bg_music]amix=inputs=2:duration=first[a]" -map 0:v:0 -map "[a]" -c:v libx264 -c:a aac -pix_fmt yuv420p -map_metadata -1 -t $(ffprobe -i "97.mp3" -show_entries format=duration -v quiet -of csv="p=0") "97-short.mp4"