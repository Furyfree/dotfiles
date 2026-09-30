require('vis')

vis.events.subscribe(vis.events.INIT, function()
  vis:command('set theme default')
  vis:command('set autoindent on')
end)

vis.events.subscribe(vis.events.WIN_OPEN, function()
  vis:command('set numbers on')
  vis:command('set expandtab on')
  vis:command('set tabwidth 2')
end)

vis:map(vis.modes.NORMAL, '  ', function()
  local status, path, err = vis:pipe(
    "find . -type d -name .git -prune -o -type f -print0 | fzf --read0 --print0 --no-multi",
    true
  )
  if status == 0 and path and path ~= '' then
    -- Quote for Vis's command parser; :e keeps its unsaved-change check.
    path = path:gsub('[\\"]', '\\%0')
    vis:command('e "' .. path .. '"')
  elseif status ~= 0 and status ~= 1 and status ~= 130 then
    vis:info(err or 'File picker failed')
  end
end, 'Find and open a file')
