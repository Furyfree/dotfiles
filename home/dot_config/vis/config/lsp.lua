local lspc = require('config.plugins').lspc
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
