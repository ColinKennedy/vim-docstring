" Vim folding file
" Language:     Python (docstring)
" Author:       Eric Chiang, Milly (module)
" Last Change:  20 Jan 2018
" Version:      1.1


if exists('g:loaded_python_docstring')
    finish
endif
let g:loaded_python_docstring = 1

if !has('pythonx')
    echomsg "Error: Docstring requires vim compiled with +python or +python3"
    finish
endif


function! PyDocHide()
    setlocal foldmethod=manual
pythonx << EOF
from vim_docstring import vim_docstring_python

try:
    vim_docstring_python.set_folds()
except Exception as e:
    print("Error: %s" % (e,))
EOF
endfunction


function! s:PySaveOpenedFolds()
pythonx << EOF
from vim_docstring import vim_docstring_python
try:
    vim_docstring_python.save_opened_folds()
except (IndentationError, SyntaxError):
    # If this errors then most likely the file is just WIP. Just ignore it
    pass
EOF
endfunction


function! s:PyRestoreOpenedFolds()
pythonx << EOF
from vim_docstring import vim_docstring_python
try:
    vim_docstring_python.restore_opened_folds()
except (IndentationError, SyntaxError):
    # If this errors then most likely the file is just WIP. Just ignore it
    pass
EOF
endfunction


" This function is meant to be run after Python folds have been
" destroyed by another function call. (For example, if you run isort or
" black or something on an open buffer).
"
" Important: To make sure opened folds are restored correcty, you must
" run `PySaveOpenedFolds` before running the function that destroys
" folds and then run `PyClearAndRestoreFolds` afterwards.
"
" :PySaveOpenedFolds
" :SomeFunctionThatBreaksFolds
" :PyClearAndRestoreFolds
"
function! s:PyClearAndRestoreFolds()
    " Delete all of the existing folds
    normal zE

    PyDocHide
    PyRestoreOpenedFolds
endfunction


function! s:PySaveAndRestoreFolds(command)
    PySaveOpenedFolds
    execute a:command
    PyClearAndRestoreFolds
endfunction


command! -bar PyDocHide call PyDocHide()
command! -bar -nargs=0 PySaveOpenedFolds call s:PySaveOpenedFolds()
command! -bar -nargs=1 PySaveAndRestoreFolds call s:PySaveAndRestoreFolds(<f-args>)
command! -bar -nargs=0 PyRestoreOpenedFolds call s:PyRestoreOpenedFolds()
command! -bar -nargs=0 PyClearAndRestoreFolds call s:PyClearAndRestoreFolds()
