"""
The MIT License

Copyright (c) 2010 FreshBooks
Modified by iFixit for personal use

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import fileinput
from SmartyToPHP.smarty_grammar import smarty_language
from SmartyToPHP.pyPEG import parse, parseLine, parser

"""
Parse a smarty template file.
"""
def parse_file(file_name, language=smarty_language):
    file_input = fileinput.FileInput(file_name)
    return parse(language, file_input, False)

"""
Parse a Smarty template string.
"""
def parse_string(text, language=smarty_language):
    p = parser()
    result, text = p.parseLine(text, language, [], False)
    return result[0][1] # Don't return the 'smarty_language' match.
