#!/usr/bin/env lua5.4

-- Read standard input line by line and tally keyword occurrences using a Lua table
local keywords = { "error", "fail", "warn", "usb", "systemd", "kernel" }
local counts = {}

for _, kw in ipairs(keywords) do
    counts[kw] = 0
end

local total_lines = 0

for line in io.lines() do
    total_lines = total_lines + 1
    local lower = string.lower(line)
    for _, kw in ipairs(keywords) do
        if string.find(lower, kw, 1, true) then
            counts[kw] = counts[kw] + 1
        end
    end
end

print(string.format("=== Lua Log Tally (%d lines scanned) ===", total_lines))
for _, kw in ipairs(keywords) do
    print(string.format("  %-10s : %d", kw, counts[kw]))
end

