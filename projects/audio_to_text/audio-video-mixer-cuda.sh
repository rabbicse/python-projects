#!/bin/bash

# Check if required arguments are provided
if [ $# -lt 3 ]; then
    echo "Usage: $0 <video_file> <audio_file> <output_file> [video_volume] [music_volume]"
    echo "Example: $0 input_video.mp4 background_music.mp3 output_video.mp4 0.4 1.0"
    echo ""
    echo "Note: This version uses CUDA acceleration for faster video encoding"
    exit 1
fi

# Assign arguments
VIDEO_INPUT="$1"
AUDIO_INPUT="$2"
OUTPUT_NAME="$3"
VIDEO_AUDIO_VOLUME="${4:-0.4}"    # Default: 0.4 (40% volume)
BG_MUSIC_VOLUME="${5:-1.0}"       # Default: 1.0 (100% volume)

# Check if input files exist
if [ ! -f "$VIDEO_INPUT" ]; then
    echo "Error: Video file '$VIDEO_INPUT' not found!"
    exit 1
fi

if [ ! -f "$AUDIO_INPUT" ]; then
    echo "Error: Audio file '$AUDIO_INPUT' not found!"
    exit 1
fi

# Check if CUDA is available
if ! ffmpeg -hwaccels 2>/dev/null | grep -q cuda; then
    echo "Warning: CUDA not available. Falling back to CPU encoding."
    CUDA_AVAILABLE=false
else
    echo "CUDA acceleration available"
    CUDA_AVAILABLE=true
fi

# Get audio duration
AUDIO_DURATION=$(ffprobe -i "$AUDIO_INPUT" -show_entries format=duration -v quiet -of csv="p=0")

# Check if duration was obtained successfully
if [ -z "$AUDIO_DURATION" ]; then
    echo "Error: Could not get duration of audio file '$AUDIO_INPUT'"
    exit 1
fi

echo "Processing with CUDA acceleration:"
echo "  Video: $VIDEO_INPUT"
echo "  Audio: $AUDIO_INPUT"
echo "  Output: $OUTPUT_NAME"
echo "  Video audio volume: $VIDEO_AUDIO_VOLUME"
echo "  Background music volume: $BG_MUSIC_VOLUME"
echo "  Audio duration: $AUDIO_DURATION seconds"
echo "  CUDA available: $CUDA_AVAILABLE"

# Build ffmpeg command
if [ "$CUDA_AVAILABLE" = true ]; then
    # CUDA accelerated version with proper audio format conversion
    ffmpeg -stream_loop -1 -i "$VIDEO_INPUT" -i "$AUDIO_INPUT" -filter_complex \
    "[0:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,volume=$VIDEO_AUDIO_VOLUME[video_audio];\
     [1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,volume=$BG_MUSIC_VOLUME[bg_music];\
     [video_audio][bg_music]amix=inputs=2:duration=first:dropout_transition=0[a]" \
    -map 0:v:0 -map "[a]" \
    -c:v h264_nvenc -preset p7 -tune hq -rc vbr -cq 23 -b:v 0 \
    -c:a aac -b:a 192k \
    -pix_fmt yuv420p -map_metadata -1 \
    -t "$AUDIO_DURATION" "$OUTPUT_NAME"
else
    # CPU fallback version
    ffmpeg -stream_loop -1 -i "$VIDEO_INPUT" -i "$AUDIO_INPUT" -filter_complex \
    "[0:a]volume=$VIDEO_AUDIO_VOLUME[video_audio];[1:a]volume=$BG_MUSIC_VOLUME[bg_music];[video_audio][bg_music]amix=inputs=2:duration=first[a]" \
    -map 0:v:0 -map "[a]" \
    -c:v libx264 -preset medium -crf 23 \
    -c:a aac -b:a 192k \
    -pix_fmt yuv420p -map_metadata -1 \
    -t "$AUDIO_DURATION" "$OUTPUT_NAME"
fi

# Check if conversion was successful
if [ $? -eq 0 ]; then
    echo "Success! Output file created: $OUTPUT_NAME"
    echo "Encoding used: $(if [ "$CUDA_AVAILABLE" = true ]; then echo 'NVENC (CUDA)'; else echo 'CPU'; fi)"
else
    echo "Error: FFmpeg conversion failed!"
    exit 1
fi