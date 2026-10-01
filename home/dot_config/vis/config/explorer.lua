-- A netrw-style directory listing: Enter opens, - goes to the parent.
-- Global Space mappings keep working, and searches stay rooted at the
-- working directory.
local util = require('config.util')
local quote = util.quote

local directories = setmetatable({}, {__mode = 'k'})

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
    return
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
end

local function parent(win)
  local directory = directories[win]
  if directory == '/' then return end
  local up, name = directory:match('^(.*)/([^/]+)$')
  show(win, up == '' and '/' or up, name .. '/')
end

local function enter(win)
  local name = win.file.lines[win.selection.line]
  if not name or name == '' then return end
  if name == '../' then return parent(win) end
  local path = join(directories[win], name:gsub('/$', ''))
  if name:sub(-1) == '/' then return show(win, path) end
  -- :e replaces the window, so the listing's mappings go with it.
  util.open(path)
end

local function explore(path)
  local directory = absolute(path)
  if not directory then vis:info('Cannot open directory: ' .. path); return end
  local win = vis.win
  if not directories[win] then
    -- Like netrw's :Explore: replace an unmodified window, split a modified one.
    local previous = win
    vis:command('new')
    win = vis.win
    if not previous.file.modified then previous:close() end
    win:map(vis.modes.NORMAL, '<Enter>', function() enter(win) end, 'Open the entry under the cursor')
    win:map(vis.modes.NORMAL, '-', function() parent(win) end, 'Show the parent directory')
  end
  show(win, directory)
end

vis:command_register('Explore', function(argv)
  explore(argv[1] or '.')
  return true
end, 'Browse a directory: Enter opens, - goes up')

vis:map(vis.modes.NORMAL, ' e', function()
  local win = vis.win
  local path = win.file.path
  local directory = path and path:match('^(.*)/[^/]*$')
  explore(directories[win] or (directory == '' and '/') or directory or '.')
end, 'Browse the current file\'s directory')
