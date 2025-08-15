ffmpeg -stream_loop -1 -i "001-video.mp4" -i "001.mp3" -map 0:v:0 -map 1:a:0 -c:v libx264 -c:a aac -pix_fmt yuv420p -shortest "001.mp4"

ffmpeg -stream_loop -1 -i "001-video.mp4" -i "001.mp3" -map 0:v:0 -map 1:a:0 -c:v libx264 -c:a aac -pix_fmt yuv420p -map_metadata -1 -shortest "001.mp4"

