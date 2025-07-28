" ---------------------
" Basics
" ---------------------
syntax on                 " Enable syntax highlighting
set number                " Line numbers
set relativenumber        " Relative line numbers
set mouse=a               " Enable mouse
set clipboard=unnamedplus " Use system clipboard
set tabstop=4             " Tabs = 4 spaces
set shiftwidth=4
set expandtab             " Use spaces instead of tabs
set smartindent           " Auto indenting
set autoindent
" Tell Vim to set the terminal title to the file name
set title
set titlestring=%t

" ---------------------
" UI
" ---------------------
" set cursorline            " Highlight current line
set showmatch             " Highlight matching brackets
set nowrap                " Don't wrap lines
set scrolloff=8           " Keep 8 lines above/below cursor
set signcolumn=no        " Don't show signcolumn

" ---------------------
" Search
" ---------------------
set ignorecase            " Case insensitive search...
set smartcase             " ...unless capital letters are used
set incsearch             " Incremental search
set hlsearch              " Highlight search results

" ---------------------
" Keybinds
" ---------------------
nnoremap <Space> :nohlsearch<CR>  " Clear search highlight

" ---------------------
" File Handling
" ---------------------
set undofile              " Persistent undo
set noswapfile            " No swap files
" set backupdir=~/.vim/tmp/backup//
" set directory=~/.vim/tmp/swap//
" set undodir=~/.vim/tmp/undo//

" Create dirs if missing
if !isdirectory(expand(&undodir))
  call mkdir(expand(&undodir), "p", 0700)
endif

" ---------------------
" Keybinds
" ---------------------
nnoremap <Space> :nohlsearch<CR>   " Clear search highlight

" Escape insert mode quickly
inoremap jj <Esc>
inoremap jk <Esc>

" Make double-key escape responsive
set timeoutlen=300
