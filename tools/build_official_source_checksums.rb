#!/usr/bin/env ruby

require "digest"

root = File.expand_path("..", __dir__)
source = File.join(root, "docs", "official-source")
output = File.join(source, "SHA256SUMS")

paths = Dir.glob(File.join(source, "**", "*"))
  .select { |path| File.file?(path) && path != output }
  .sort

body = paths.map do |path|
  relative = path.delete_prefix("#{source}/")
  "#{Digest::SHA256.file(path).hexdigest}  #{relative}"
end.join("\n") + "\n"

File.write(output, body, mode: "w:UTF-8")
