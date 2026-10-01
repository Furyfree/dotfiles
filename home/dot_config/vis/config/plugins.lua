-- Optional plugins, pinned; the editor stays usable without them. Install once:
--   git clone https://github.com/erf/vis-plug ~/.config/vis/plugins/vis-plug
--   git -C ~/.config/vis/plugins/vis-plug checkout e963a93e563c1424fdd2b296261a5fcb593b6b44
-- then run :plug-install in Vis and restart. Startup never downloads.
local plug_ok, plug = pcall(require, 'plugins/vis-plug')
if not plug_ok then return {} end

plug.init({
  { 'https://codeberg.org/muhq/vis-lspc', ref = 'c54c24b2639c8e9f9b3dd03d7a4fe556da328a76', alias = 'lspc' },
  { 'Nomarian/vis-commentary', ref = '223dcc6f3f7003304d57f882607027e746fa0510', alias = 'commentary' },
  { 'milhnl/vis-editorconfig-options', ref = '2f34c4501da79467f5b2af24708eae35e9918b45' },
  { 'https://repo.or.cz/vis-quickfix.git', ref = '61ee0cd14dfb9a0965f3b4a55931897ad61c6f06', alias = 'quickfix' },
  { 'https://repo.or.cz/vis-surround.git', ref = '49674c957d9af22f4fbbe118d388bd3c81372a04', alias = 'surround' },
  { 'erf/vis-cursors', ref = 'ddea23c7a19f70316bc3431efbade49aca39f474' },
})
local plugins = plug.plugins

-- gcc / gc{motion}, as in Neovim and Vim's comment package.
if plugins.commentary then plugins.commentary() end

-- ys/cs/ds take the delimiter first (ys"iw). Keep Vim's Visual C and D;
-- Visual S surrounds, as in vim-surround.
if plugins.surround then
  plugins.surround.prefix.change[2] = nil
  plugins.surround.prefix.delete[2] = nil
end

-- :grep fills the quickfix list like Vim's; ]q / [q move through it.
if plugins.quickfix then plugins.quickfix.grepprg = "rg --vimgrep --hidden -g '!.git'" end

return plugins
