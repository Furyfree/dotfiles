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

-- Status feedback expires even when no further keys are pressed.
local feedback, feedback_timer, feedback_name
local feedback_serial = 0
local function notify(text)
  if feedback_timer and io.type(feedback_timer) == 'file' then feedback_timer:close() end
  feedback_serial = feedback_serial + 1
  feedback_name = 'vis-status-feedback-' .. feedback_serial
  feedback = text
  feedback_timer = vis:communicate(feedback_name, 'exec sleep 2')
end
vis.events.subscribe(vis.events.PROCESS_RESPONSE, function(name, event)
  if not name:match('^vis%-status%-feedback%-') then return end
  if name == feedback_name and (event == 'EXIT' or event == 'SIGNAL') then
    feedback, feedback_timer, feedback_name = nil, nil, nil
    vis:redraw()
  end
  return true
end, 1)

-- Keep native yanks; register 0 changes only when an unnamed yank completes.
local pending_yank
local function yank_text()
  local parts = vis.registers['0']
  for i, text in ipairs(parts) do parts[i] = text:gsub('%z$', '') end
  return table.concat(parts)
end
local function finish_yank()
  if not pending_yank or vis.mode == vis.modes.OPERATOR_PENDING then return end
  local previous = pending_yank
  pending_yank = nil
  local text = yank_text()
  if text == '' then
    vis.registers['0'] = previous
    return
  end
  local clipboard = io.popen('vis-clipboard --copy --selection clipboard', 'w')
  if not clipboard then notify('Clipboard unavailable'); return end
  local written = clipboard:write(text)
  local ok = clipboard:close()
  notify(written and ok and 'Copied' or 'Clipboard copy failed')
end

for _, mode in ipairs({vis.modes.NORMAL, vis.modes.VISUAL, vis.modes.VISUAL_LINE}) do
  vis:map(mode, 'y', function()
    finish_yank()
    if vis.register == '"' then
      pending_yank = vis.registers['0']
      vis.registers['0'] = {}
    end
    vis:feedkeys('<vis-operator-yank>')
    finish_yank()
  end, 'Yank and copy to the system clipboard')
  for key, action in pairs({p = '<vis-put-after>', P = '<vis-put-before>'}) do
    vis:map(mode, key, function()
      finish_yank()
      if vis.register == '"' then
        local status, text = vis:pipe('vis-clipboard --paste --selection clipboard')
        if status ~= 0 then notify('Clipboard paste failed'); return end
        if not text or text == '' then notify('Clipboard is empty'); return end
        -- Preserve linewise and multiple-selection paste for our own yanks.
        vis.register = text == yank_text() and '0' or '+'
      end
      vis:feedkeys(action)
    end, 'Paste from the system clipboard')
  end
end

local modes = {
  [vis.modes.NORMAL] = {'NORMAL', 'cyan'},
  [vis.modes.OPERATOR_PENDING] = {'PENDING', 'blue'},
  [vis.modes.INSERT] = {'INSERT', 'green'},
  [vis.modes.REPLACE] = {'REPLACE', 'magenta'},
  [vis.modes.VISUAL] = {'VISUAL', 'yellow'},
  [vis.modes.VISUAL_LINE] = {'VISUAL LINE', 'yellow'},
}
vis.events.subscribe(vis.events.WIN_STATUS, function(win)
  if win == vis.win then finish_yank() end
  local mode = modes[vis.mode]
  local keys = vis.input_queue
  local label = vis.mode == vis.modes.NORMAL and keys:sub(1, 1) == ' '
    and 'SPACE' .. keys:sub(2) .. ' …' or mode[1]
  local left = (win == vis.win and label .. ' | ' .. (feedback and feedback .. ' | ' or '') or '')
    .. (win.file.name or '[No Name]')
    .. (win.file.modified and ' [+]' or '') .. (vis.recording and ' @' or '')
  if win == vis.win then
    local foreground = vis.mode == vis.modes.OPERATOR_PENDING and 'white' or 'black'
    win:style_define(win.STYLE_STATUS_FOCUSED, 'fore:' .. foreground .. ',back:' .. mode[2] .. ',bold')
  end
  local selection = win.selection
  local right = keys ~= '' and keys or tostring(vis.count or '')
  if #win.selections > 1 then right = right .. ' ' .. selection.number .. '/' .. #win.selections end
  right = right .. ' ' .. (selection.line or 0) .. ':' .. (selection.col or 0)
  win:status(' ' .. left .. ' ', ' ' .. right .. ' ')
  return true
end, 1)

local function quote(text)
  return "'" .. text:gsub("'", "'\\''") .. "'"
end

-- Run an fzf picker from the working directory; nil when cancelled.
local function pick(command)
  local status, choice, err = vis:pipe(command, true)
  if status == 0 and choice and choice ~= '' then
    return choice
  elseif status ~= 1 and status ~= 130 then
    vis:info(err and err ~= '' and err or 'Picker failed')
  end
end

-- Quote for Vis's command parser; :e keeps its unsaved-change check.
local function open(path)
  return vis:command('e "' .. path:gsub('[\\"]', '\\%0') .. '"')
end

-- Like the Neovim pickers: include dotfiles, respect Git ignores, hide .git.
local rg = "rg --hidden -g '!.git' "

local function files()
  local path = pick(rg .. '--files -0 | fzf --read0 --print0 --no-multi')
  if path then open(path:gsub('%z$', '')) end
end
vis:map(vis.modes.NORMAL, '  ', files, 'Find and open a file')
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
    entries[#entries + 1] = quote(#windows .. ' ' .. (win.file.name or '[No Name]')
      .. (win.file.modified and ' [+]' or ''))
  end
  local choice = pick("printf '%s\\0' " .. table.concat(entries, ' ') .. ' | fzf --read0 --print0 --no-multi')
  local index = tonumber((choice or ''):match('^(%d+) '))
  if index then vis.win = windows[index] end
end, 'Switch to an open file')

local function browse()
  local directory = '.'
  while true do
    local path = pick("(printf '%s\\0' " .. quote(directory .. '/..') .. '; find ' .. quote(directory)
      .. "/. ! -name . -prune -type d -exec printf '%s/\\0' {} +; find " .. quote(directory)
      .. "/. ! -name . -prune ! -type d -exec printf '%s\\0' {} +) | fzf --read0 --print0 --no-multi"
      .. ' --header ' .. quote(directory .. ' | Enter: open; /..: parent; Esc: close')
      .. " --preview 'if test -d {}; then ls -A -- {}; else bat --paging=never --style=numbers --color=always -- {}; fi'")
    if not path then return end
    path = path:gsub('%z$', '')
    local status = vis:pipe('test -d ' .. quote(path))
    if status ~= 0 then open(path); return end
    local ok, absolute = vis:pipe('cd ' .. quote(path) .. ' && pwd -P')
    if ok ~= 0 then vis:info('Cannot open directory'); return end
    directory = absolute:gsub('\n$', '')
  end
end

-- Optional plugins, pinned; the editor stays usable without them. Install once:
--   git clone https://github.com/erf/vis-plug ~/.config/vis/plugins/vis-plug
--   git -C ~/.config/vis/plugins/vis-plug checkout e963a93e563c1424fdd2b296261a5fcb593b6b44
-- then run :plug-install in Vis and restart. Startup never downloads.
local plug_ok, plug = pcall(require, 'plugins/vis-plug')
if plug_ok then
  plug.init({
    { 'https://codeberg.org/muhq/vis-lspc', ref = 'c54c24b2639c8e9f9b3dd03d7a4fe556da328a76', alias = 'lspc' },
    { 'Nomarian/vis-commentary', ref = '223dcc6f3f7003304d57f882607027e746fa0510', alias = 'commentary' },
    { 'milhnl/vis-editorconfig-options', ref = '2f34c4501da79467f5b2af24708eae35e9918b45' },
  })
end

-- gcc / gc{motion}, as in Neovim and Vim's comment package.
if plug_ok and plug.plugins.commentary then plug.plugins.commentary() end

local lspc = plug_ok and plug.plugins.lspc
if lspc then
  -- Mise tools; gopls is a built-in default.
  lspc.ls_map.python = { name = 'ruff', cmd = 'ruff server' }
  lspc.ls_map.toml = { name = 'taplo', cmd = 'taplo lsp stdio' }
  -- Info notices open a window that steals focus from later lspc commands.
  lspc.message_level = 2
end

local function language(command)
  if not lspc then vis:info('Language support is not installed'); return end
  return vis:command('lspc-' .. command)
end
for key, command in pairs({
  gd = 'definition', gD = 'declaration', gI = 'implementation', gy = 'typeDefinition',
  gr = 'references', K = 'hover', gK = 'signature-help', ['<C-t>'] = 'back',
  ['<C-]>'] = 'definition', [' cd'] = 'show-diagnostics', ['[d'] = 'prev-diagnostic',
  [']d'] = 'next-diagnostic', [' cf'] = 'format', [' ss'] = 'navigate-symbols',
}) do
  vis:map(vis.modes.NORMAL, key, function() language(command) end, 'LSP: ' .. command)
end
vis:map(vis.modes.NORMAL, ' cr', function()
  if not lspc then vis:info('Language support is not installed'); return end
  vis:feedkeys(':lspc-rename ')
end, 'Rename the current symbol; enter its new name')
vis:map(vis.modes.INSERT, '<C- >', function()
  language('completion')
  vis.mode = vis.modes.INSERT
end, 'LSP completion')
vis:map(vis.modes.NORMAL, ' e', browse, 'Browse files and directories')
