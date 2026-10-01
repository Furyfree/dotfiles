-- Fullscreen for saved files, split for unsaved files, like netrw's :Explore.
local util = require('config.util')
local quote = util.quote

local directories = setmetatable({}, {__mode = 'k'})
local explorer, origin, browse

vis.events.subscribe(vis.events.WIN_CLOSE, function(win)
  directories[win], util.titles[win] = nil, nil
  if origin and win == origin.win then origin.win = nil end
  if win == explorer then explorer = nil end
end)

local function absolute(path)
  local status, out = vis:pipe('cd -- ' .. quote(path) .. ' && pwd -P')
  if status == 0 then return (out:gsub('\n$', '')) end
end

local function join(directory, name)
  return (directory == '/' and '' or directory) .. '/' .. name
end

-- Show directory in win, with the cursor on entry when it is listed.
local function show(win, directory, entry)
  -- -L lists linked directories as directories; broken links still print
  -- a name but make ls exit nonzero.
  local status, out, err = vis:pipe('ls -ApL -- ' .. quote(directory))
  if status ~= 0 and (out or '') == '' then
    vis:info(err and err ~= '' and err or 'Cannot list ' .. directory)
    return false
  end
  local entries, files = {'../'}, {}
  for name in (out or ''):gmatch('[^\n]+') do
    table.insert(name:sub(-1) == '/' and entries or files, name)
  end
  table.move(files, 1, #files, #entries + 1, entries)
  local file = win.file
  file:delete(0, file.size)
  file:insert(0, table.concat(entries, '\n') .. '\n')
  file.modified = false
  directories[win], util.titles[win] = directory, directory .. (directory == '/' and '' or '/')
  local line = 1
  for i, name in ipairs(entries) do
    if name == entry then line = i end
  end
  win.selection:to(line, 1)
  return true
end

local function parent(win)
  local directory = directories[win]
  if directory == '/' then return end
  local up, name = directory:match('^(.*)/([^/]+)$')
  show(win, up == '' and '/' or up, name .. '/')
end

local function return_to_file(win)
  if not origin or not (origin.win or origin.path) then
    vis:info('No editing window to return to')
    return
  end
  browse = {file = origin.path, directory = directories[win], entry = win.file.lines[win.selection.line]}
  if origin.win then
    vis.win = origin.win
    if not win:close() then vis.win = win end
  else
    local line, col = origin.line, origin.col
    util.open(origin.path)
    if vis.win ~= win then vis.win.selection:to(line, col) end
  end
end

local function enter(win)
  local name = win.file.lines[win.selection.line]
  if not name or name == '' then return end
  if name == '../' then return parent(win) end
  local path = join(directories[win], name:gsub('/$', ''))
  if name:sub(-1) == '/' then return show(win, path) end
  if origin and path == origin.path then return return_to_file(win) end
  local target = origin and origin.win or win
  vis.win = target
  util.open(path)
  -- Vis 0.9 can return true after :e refuses unsaved changes. A successful
  -- edit replaces the target window; only then close the separate listing.
  if vis.win ~= target then
    browse = nil
    if target ~= win then win:close() end
  else
    vis.win = win
  end
end

local function explore(path, entry)
  local directory = absolute(path)
  if not directory then vis:info('Cannot open directory: ' .. path); return end
  local previous = vis.win
  local created = not explorer
  if created then
    if not vis:command('new') or vis.win == previous then return end
    explorer = vis.win
  end
  local win = explorer
  vis.win = win
  if not show(win, directory, entry) then
    vis.win = previous
    if created then win:close() end
    return
  end
  if previous ~= win then
    origin = {win = previous, path = previous.file.path,
      line = previous.selection.line, col = previous.selection.col}
    if not previous.file.modified then previous:close() end
  end
  if created then
    for _, key in ipairs({'<Enter>', 'l'}) do
      win:map(vis.modes.NORMAL, key, function() enter(win) end, 'Open the entry under the cursor')
    end
    for _, key in ipairs({'-', 'h'}) do
      win:map(vis.modes.NORMAL, key, function() parent(win) end, 'Show the parent directory')
    end
  end
end

vis:command_register('Explore', function(argv)
  explore(argv[1] or '.')
  return true
end, 'Browse a directory: l/Enter opens, h/- goes up')

vis:map(vis.modes.NORMAL, '  ', function()
  vis:command('!cd -- ' .. quote(directories[vis.win] or '.')
    .. " && printf '\\033[2J\\033[H' && exec " .. quote(os.getenv('SHELL') or vis.options.shell))
end, 'Open a shell in this folder; exit to return to the editor')

vis:map(vis.modes.NORMAL, ' e', function()
  local win = vis.win
  if win == explorer then return return_to_file(win) end
  local path = win.file.path
  if browse and browse.file == path then return explore(browse.directory, browse.entry) end
  local directory = path and path:match('^(.*)/[^/]*$')
  explore((directory == '' and '/') or directory or '.', path and path:match('[^/]+$'))
end, 'Browse the current file\'s directory; return from the explorer')
