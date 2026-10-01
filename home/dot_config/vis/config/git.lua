-- Git hunks like the Neovim gitsigns keys: ]h / [h jump, Space ghp previews.
-- A hunk is a group of changed lines, compared with Git's index (the staged
-- copy), including unsaved edits. Vis has no sign column, so nothing is drawn.
local quote = require('config.util').quote

local function hunks()
  local file = vis.win.file
  if not file.path then vis:info('No file'); return end
  local directory, name = file.path:match('^(.*)/([^/]*)$')
  directory, name = directory or '.', name or file.path
  if directory == '' then directory = '/' end
  local status, out = vis:pipe(file, {start = 0, finish = file.size},
    'index=$(mktemp) || exit 2; trap \'rm -f "$index"\' EXIT; git -C ' .. quote(directory)
    .. ' show :./' .. quote(name) .. ' > "$index" 2>/dev/null || exit 2; diff -U0 "$index" -')
  if status == 0 then vis:info('No Git changes'); return end
  if status ~= 1 then vis:info('Not tracked by Git'); return end
  local list, current = {}
  for line in out:gmatch('([^\n]*)\n') do
    local first, count = line:match('^@@ %-[%d,]+ %+(%d+),?(%d*) @@')
    if first then
      first = math.max(tonumber(first), 1)
      current = {first = first, last = first + math.max(tonumber(count) or 1, 1) - 1, text = {line}}
      list[#list + 1] = current
    elseif current then
      table.insert(current.text, line)
    end
  end
  return list
end

-- Wraps around at either end, as gitsigns does by default.
local function jump(forward)
  local list = hunks()
  if not list then return end
  local here, target = vis.win.selection.line
  for _, hunk in ipairs(list) do
    if forward and hunk.first > here then target = hunk; break end
    if not forward and hunk.first < here then target = hunk end
  end
  target = target or list[forward and 1 or #list]
  vis.win.selection:to(target.first, 1)
end

vis:map(vis.modes.NORMAL, ']h', function() jump(true) end, 'Next Git hunk')
vis:map(vis.modes.NORMAL, '[h', function() jump(false) end, 'Previous Git hunk')
vis:map(vis.modes.NORMAL, ' ghp', function()
  local here = vis.win.selection.line
  for _, hunk in ipairs(hunks() or {}) do
    if hunk.first <= here and here <= hunk.last then
      vis:message(table.concat(hunk.text, '\n'))
      return
    end
  end
  vis:info('No Git hunk at the cursor')
end, 'Preview the Git hunk at the cursor')
