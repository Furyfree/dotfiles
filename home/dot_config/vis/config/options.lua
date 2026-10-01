vis.events.subscribe(vis.events.INIT, function()
  vis:command('set theme default')
  vis:command('set autoindent on')
end)

vis.events.subscribe(vis.events.WIN_OPEN, function()
  vis:command('set numbers on')
  vis:command('set expandtab on')
  vis:command('set tabwidth 2')
end)

-- Vim semantics: n repeats the last search's direction, N reverses it.
vis:map(vis.modes.NORMAL, 'n', '<vis-motion-search-repeat>')
vis:map(vis.modes.NORMAL, 'N', '<vis-motion-search-repeat-reverse>')
