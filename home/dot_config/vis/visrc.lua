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

-- Vim semantics: n repeats the last search's direction, N reverses it.
vis:map(vis.modes.NORMAL, 'n', '<vis-motion-search-repeat>')
vis:map(vis.modes.NORMAL, 'N', '<vis-motion-search-repeat-reverse>')

-- Run an fzf picker from the working directory; nil when cancelled.
local function pick(command)
  local status, choice, err = vis:pipe(command, true)
  if status == 0 and choice and choice ~= '' then
    return choice
  elseif status ~= 1 and status ~= 130 then
    vis:info(err or 'Picker failed')
  end
end

-- Quote for Vis's command parser; :e keeps its unsaved-change check.
local function open(path)
  vis:command('e "' .. path:gsub('[\\"]', '\\%0') .. '"')
end

-- Like the Neovim pickers: include dotfiles, respect Git ignores, hide .git.
local rg = "rg --hidden -g '!.git' "

vis:map(vis.modes.NORMAL, '  ', function()
  local path = pick(rg .. '--files -0 | fzf --read0 --print0 --no-multi')
  if path then open(path:gsub('%z$', '')) end
end, 'Find and open a file')

vis:map(vis.modes.NORMAL, ' /', function()
  local reload = 'reload:' .. rg .. '--line-number --no-heading --color=never -- {q} || true'
  local match = pick('fzf --disabled --no-multi --bind "start,change:' .. reload .. '"')
  local path, line = (match or ''):match('^(.-):(%d+):')
  if path then
    open(path)
    vis.win.selection:to(tonumber(line), 1)
  end
end, 'Search file contents')

-- Optional plugins, pinned; the editor stays usable without them. Install once:
--   git clone https://github.com/erf/vis-plug ~/.config/vis/plugins/vis-plug
--   git -C ~/.config/vis/plugins/vis-plug checkout e963a93e563c1424fdd2b296261a5fcb593b6b44
-- then run :plug-install in Vis and restart. Startup never downloads.
local plug_ok, plug = pcall(require, 'plugins/vis-plug')
if not plug_ok then return end
plug.init({
  { 'https://codeberg.org/muhq/vis-lspc', ref = 'c54c24b2639c8e9f9b3dd03d7a4fe556da328a76', alias = 'lspc' },
  { 'Nomarian/vis-commentary', ref = '223dcc6f3f7003304d57f882607027e746fa0510', alias = 'commentary' },
  { 'milhnl/vis-editorconfig-options', ref = '2f34c4501da79467f5b2af24708eae35e9918b45' },
})

-- gcc / gc{motion}, as in Neovim and Vim's comment package.
if plug.plugins.commentary then plug.plugins.commentary() end

local lspc = plug.plugins.lspc
if lspc then
  -- Mise tools; gopls is a built-in default.
  lspc.ls_map.python = { name = 'ruff', cmd = 'ruff server' }
  lspc.ls_map.toml = { name = 'taplo', cmd = 'taplo lsp stdio' }
  -- Info notices open a window that steals focus from later lspc commands.
  lspc.message_level = 2
end
