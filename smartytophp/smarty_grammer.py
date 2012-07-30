"""
Inspired by FreshBooks https://github.com/freshbooks/smartytotwig
Hacked to convert to PHP
"""

import re, fileinput
from pyPEG import *
from pyPEG import parse, keyword, _and, _not, ignore

"""
Misc.
"""

def content():                  return re.compile(r'[^{]+')

def comment():                  return re.compile("{\*.*?\*}", re.S)

def literal():                  return re.compile("{literal}.*?{/literal}", re.S)

def strip():                    return re.compile("{strip}.*?{/strip}", re.S)

def junk():                     return -1, re.compile(r'\s')

def quotes():                   return 0, ['"', '\'']

def equals():                   return '='

"""
Logical operators.
"""
def and_operator():             return [keyword('and'), '&&']

def or_operator():              return [keyword('or'), '||']

def equals_operator():          return ['==', keyword('eq')]

def ne_operator():              return ['!=', keyword('ne'), keyword('neq')]

def nee_operator():             return '!=='

def gt_operator():              return ['>', 'gt']

def lt_operator():              return ['<', 'gt']

def lte_operator():             return ['<=']

def gte_operator():             return ['>=']

def right_paren():              return junk, ')'

def left_paren():               return junk, '('

def operator():                 return 0, ' ', [nee_operator, ne_operator, at_operator, and_operator, mod, equals_operator, gte_operator, lte_operator, lt_operator, gt_operator, or_operator], junk

"""
Smarty variables.
"""
def text():                     return -2, [re.compile(r'[^$`"\\]'), re.compile(r'\\.')]

def string():                   return 0, ' ', [(re.compile(r'"'), -1, [re.compile(r'[^$`"\\]'), re.compile(r'\\.')], re.compile(r'"')), (re.compile(r'\''), -1, [re.compile(r'[^\'\\]'), re.compile(r'\\.')], re.compile(r'\''))]

def variable_string():          return '"', -2, [text, ('`', expression, '`'), ('$', expression)], '"'
#def variable_string():          return -2, [re.compile(r'([\"\"\'])(?:(?=(\\?))\2.)*?\1'), re.compile(r'[A-Za-z0-9\/\.\'\"_-]+')]

def false():                    return 'false'

def true():                     return 'true'

def boolean():                  return [false, true]

def dollar():                   return '$'

def mod():                      return '%'

def arrow():                    return '->'

def not_operator():             return '!'

def at_operator():              return '@'

def symbol():                   return -1, [' ', '\n', '\t'], 0, [not_operator, at_operator], 0, dollar, re.compile(r'[\w\-\+\_]+(?<!-)')

def array():                    return symbol, "[", 0, expression, "]"

def exp_no_modifier():          return [object_dereference, static_call, php_fun, boolean, array, symbol, variable_string, string]

def modifier():                 return [static_call, php_fun, object_dereference, boolean, array, symbol, variable_string, string], -2, modifier_right, 0, junk

def modifier_right():           return '|', 0, at_operator, [default, count, truncate, local_date, lower, count, upper, capitalize, urldecode, regex_replace, escape, wordbreak, symbol], -1, (':', exp_no_modifier)

def object_dereference():       return [array, symbol], -2, [assignment_op, dereference]

def dereference():              return '.', [symbol, array, object_dereference, string, variable_string]

def assignment_op():            return arrow, [symbol, object_dereference], 0, left_paren, 0, expression, -1, (',', expression), 0, right_paren, 0, junk

def php_obj():                  return junk, symbol, -2, (arrow, symbol), 0, left_paren, 0, right_paren, junk

def php_fun():                  return junk, symbol, -2, (arrow, symbol), 0, left_paren, 0, expression, -1, (',', expression), 0, right_paren, junk

def static_class():             return junk, quotes, re.compile(r'\w+'), quotes, junk

def static_function():          return junk, quotes, re.compile(r'\w+'), quotes, junk

def static_param():             return junk, expression, junk

def static_call():              return junk, -1, [operator, not_operator],  dollar, keyword('static'), arrow, keyword('call'), left_paren, static_class, ',', static_function, -1, (',', static_param), right_paren, junk

def expression():               return [modifier, static_call, object_dereference, php_fun, function_statement, array, symbol, string, variable_string]

def default():                  return keyword('default'), ':', expression

def escape():                   return keyword('escape'), 0, ':', 0, expression

def urldecode():                return keyword("urldecode")

def lower():                    return keyword("lower")

def count():                    return keyword("count")

def upper():                    return keyword("upper")

def capitalize():               return keyword("capitalize")

def regex_replace():            return keyword("regex_replace"), ':', expression, ':', expression

def truncate():                 return keyword("truncate"), ':', expression, 0, ':', 0, expression

def wordbreak():                return keyword("wordbreak"), 0, ':', 0, expression

def local_date():               return keyword("local_date")

"""
Smarty statements.
"""
def parameter():                return junk, -1, [operator, not_operator, at_operator], -1, left_paren, expression, -1, right_paren, -1, (-1, [operator, not_operator, at_operator], -1, left_paren, expression, -1, right_paren), junk

def if_statement():             return '{', keyword('if'), -2, parameter, '}', -1, smarty_language, -1, [else_statement, elseif_statement], '{/', keyword('if'), '}'

def elseif_statement():         return '{', keyword('elseif'), -2, parameter, '}', -1, smarty_language

def else_statement():           return '{', keyword('else'), '}', -1, smarty_language

def for_from():                 return junk, keyword('from'), equals, [php_obj, php_fun, expression], junk

def for_item():                 return junk, keyword('item'), equals, quotes, symbol, quotes, junk

def for_name():                 return junk, keyword('name'), equals, quotes, symbol, quotes, junk

def for_key():                  return junk, keyword('key'), equals, quotes, symbol, quotes, junk

def for_statement():            return '{', keyword('foreach'), -2, [for_from, for_item, for_name, for_key], '}', -1, smarty_language, 0, foreachelse_statement, '{/', keyword('foreach'), '}'

def foreachelse_statement():    return '{', keyword('foreachelse'), '}', -1, smarty_language

def print_statement():          return '{', 0, 'e ', -2, [expression, wiki_statement, guri_statement, curi_statement, uri_statement, buri_statement], '}'

def assign_var():               return junk, keyword('var'), 0, equals, quotes, symbol, quotes, junk

def forward_slash():            return '/'

def period():                   return '.'

def file_path():                return symbol, -2, (forward_slash, symbol), period, symbol
#def file_path():                return re.compile(r'.*?')

def assign_value():             return junk, keyword('value'), 0, equals, [file_path, expression], junk

def assign_statement():         return '{', keyword('assign'), assign_var, assign_value, '}'

def capture_name():             return junk, keyword('name'), equals, quotes, symbol, quotes, junk

def capture_assign():           return junk, keyword('assign'), equals, quotes, symbol, quotes, junk

def capture_statement():        return '{', keyword('capture'), -1, [capture_name, capture_assign], '}', -1, smarty_language, '{/', keyword('capture'), '}'

def include_params():           return junk, symbol, equals, [file_path, expression], junk

def include_statement():        return '{', keyword('include'), -2, include_params, '}'

def function_statement():       return junk, 0, [operator, not_operator], symbol, left_paren, expression, right_paren, junk

"""
iFixit specific statements
"""
def uri_param():                return junk, symbol, equals, [php_obj, file_path, expression], junk

def uri_statement():            return '{', keyword('URI'), -2, uri_param, '}'

def buri_statement():           return '{', keyword('BURI'), -2, uri_param, '}'

def curi_statement():           return '{', keyword('CURI'), -2, uri_param, '}'

def guri_statement():           return '{', keyword('GURI'), -2, uri_param, '}'

def wiki_statement():           return '{', keyword('WIKI'), -2, uri_param, '}'

def translate_params():         return junk, re.compile(r'[A-Za-z0-9\&\:\;\=\+\-\.\_\$\%\<\>\/\'\"\| ]+'), junk

def translate():                return '{', keyword('t'), 0, translate_params, '}', -2, smarty_language, '{/', keyword('t'), '}'

"""
Finally, the actual language description.
"""
def smarty_language():          return -2, [literal, strip, if_statement, for_statement, curi_statement, buri_statement, uri_statement, wiki_statement, guri_statement, assign_statement, translate, comment, include_statement, capture_statement, print_statement, content]

"""
print_trace = True

files = fileinput.input()
result = parse(smarty_language(), files, True, comment)
print result
"""
