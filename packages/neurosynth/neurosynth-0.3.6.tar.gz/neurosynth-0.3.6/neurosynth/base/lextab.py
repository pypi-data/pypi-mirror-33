# lextab.py. This file automatically created by PLY (version 3.10). Don't edit!
_tabversion   = '3.10'
_lextokens    = set(('AND', 'LT', 'ANDNOT', 'WORD', 'LPAR', 'RT', 'OR', 'RPAR', 'FLOAT'))
_lexreflags   = 64
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_WORD>[a-zA-Z\\_\\-\\*]+)|(?P<t_FLOAT>[0-9\\.]+)|(?P<t_ANDNOT>\\&\\~)|(?P<t_AND>\\&)|(?P<t_LPAR>\\()|(?P<t_LT>\\<)|(?P<t_OR>\\|)|(?P<t_RPAR>\\))|(?P<t_RT>\\>)', [None, ('t_WORD', 'WORD'), ('t_FLOAT', 'FLOAT'), (None, 'ANDNOT'), (None, 'AND'), (None, 'LPAR'), (None, 'LT'), (None, 'OR'), (None, 'RPAR'), (None, 'RT')])]}
_lexstateignore = {'INITIAL': ' \t'}
_lexstateerrorf = {'INITIAL': 't_error'}
_lexstateeoff = {}
