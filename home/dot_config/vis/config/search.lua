local util = require('config.util')
local quote, pick, open = util.quote, util.pick, util.open

-- Like the Neovim pickers: include dotfiles, respect Git ignores, hide .git.
local rg = "rg --hidden -g '!.git' "

local function files()
  local path = pick(rg .. '--files -0 | fzf --read0 --print0 --no-multi')
  if path then open(path:gsub('%z$', '')) end
end
vis:map(vis.modes.NORMAL, ' ff', files, 'Find and open a file')

local function search(query, literal)
  local reload = 'reload:' .. rg .. "--line-number --no-heading --color=never --field-match-separator '\\t' "
    .. (literal and '--fixed-strings ' or '') .. '-- {q} || true'
  local match = pick('fzf --disabled --no-multi --query ' .. quote(query or '')
    .. ' --bind "start,change:' .. reload .. '"'
    .. " --delimiter '\t' --preview 'bat --paging=never --style=numbers --color=always --highlight-line {2} -- {1}'"
    .. " --preview-window 'right,60%,+{2}/2'"
    .. " --bind 'ctrl-u:preview-half-page-up,ctrl-d:preview-half-page-down'")
  local path, line = (match or ''):match('^(.-)\t(%d+)\t')
  if path and open(path) then
    vis.win.selection:to(tonumber(line), 1)
  end
end
vis:map(vis.modes.NORMAL, ' /', function() search() end, 'Search file contents with context')
vis:map(vis.modes.NORMAL, ' sw', function()
  local word = vis.win.file:text_object_word(vis.win.selection.pos)
  if word then search(vis.win.file:content(word), true) end
end, 'Search for the current word with context')

vis:map(vis.modes.NORMAL, ' ,', function()
  local windows, entries = {}, {}
  for win in vis:windows() do
    windows[#windows + 1] = win
    entries[#entries + 1] = quote(#windows .. ' ' .. (util.titles[win] or win.file.name or '[No Name]')
      .. (win.file.modified and ' [+]' or ''))
  end
  local choice = pick("printf '%s\\0' " .. table.concat(entries, ' ') .. ' | fzf --read0 --print0 --no-multi')
  local index = tonumber((choice or ''):match('^(%d+) '))
  if index then vis.win = windows[index] end
end, 'Switch to an open file')
