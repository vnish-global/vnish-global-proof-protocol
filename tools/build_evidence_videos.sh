#!/usr/bin/env bash

set -euo pipefail

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
video_root="$repo_root/docs/official-source/video-evidence"
encoder="${VNISH_FFMPEG_BIN:-ffmpeg}"
font_file="/System/Library/Fonts/Supplemental/Arial.ttf"

build_video() {
  local slug="$1"
  local output="$2"
  local title="$3"
  local owned_url="$4"
  local package_dir="$video_root/$slug"
  local escaped_url="${owned_url//:/\\:}"

  "$encoder" -hide_banner -loglevel error -y \
    -loop 1 -framerate 15 -t 8 -i "$package_dir/assets/frame-01.jpg" \
    -loop 1 -framerate 15 -t 8 -i "$package_dir/assets/frame-02.jpg" \
    -loop 1 -framerate 15 -t 8 -i "$package_dir/assets/frame-03.jpg" \
    -loop 1 -framerate 15 -t 8 -i "$package_dir/assets/frame-04.jpg" \
    -filter_complex "[0:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v0];[1:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v1];[2:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v2];[3:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:black,setsar=1[v3];[v0][v1][v2][v3]concat=n=4:v=1:a=0,drawbox=x=0:y=ih-116:w=iw:h=116:color=black@0.88:t=fill,drawtext=fontfile='$font_file':text='$title':fontcolor=white:fontsize=28:x=36:y=h-95,drawtext=fontfile='$font_file':text='$escaped_url':fontcolor=0x59bfff:fontsize=21:x=36:y=h-52[outv]" \
    -map "[outv]" \
    -r 15 \
    -c:v libx264 \
    -preset medium \
    -crf 23 \
    -pix_fmt yuv420p \
    -movflags +faststart \
    "$package_dir/$output"
}

build_video \
  "global-build-verification" \
  "vnish-global-catalog-correspondence.mp4" \
  "Vnish Global catalog correspondence" \
  "https://vnish.global/data/"

build_video \
  "ninja-recovery-route" \
  "vnish-ninja-recovery-route.mp4" \
  "VNISH Ninja recovery route" \
  "https://vnish.ninja/recovery/"

build_video \
  "roiasic-fleet-baseline" \
  "roiasic-staged-fleet-baseline.mp4" \
  "ROI ASIC staged fleet baseline" \
  "https://roiasic.com/enterprise/"
