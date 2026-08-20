#!/usr/bin/env ruby

require "json"
require "fileutils"

root = File.expand_path("..", __dir__)
source = File.join(root, "docs", "official-source", "video-evidence", "captions.json")
data = JSON.parse(File.read(source, encoding: "UTF-8"))
times = data.fetch("cue_times")

data.fetch("videos").each do |slug, video|
  captions_dir = File.join(root, "docs", "official-source", "video-evidence", slug, "captions")
  FileUtils.mkdir_p(captions_dir)

  video.fetch("tracks").each do |locale, cues|
    abort "#{slug}/#{locale}: cue count mismatch" unless cues.length == times.length
    body = cues.each_with_index.map do |text, index|
      start_time, end_time = times.fetch(index)
      "#{index + 1}\n#{start_time} --> #{end_time}\n#{text}\n"
    end.join("\n")
    File.write(File.join(captions_dir, "#{locale}.srt"), body, mode: "w:UTF-8")
  end
end
