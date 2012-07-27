import re
import pprint

"""
Takes an AST of a parsed smarty program
and returns the parsed PHTML template. This
is meant as a helper it does not understand 100%
of the Smarty synatx.
"""
class TreeWalker(object):
    
    # Lookup tables for performing some token
    # replacements not addressed in the grammar.
    replacements = {
        'smarty\.foreach.*\.index': 'index fix this##',
        'smarty\.foreach.*\.iteration': 'iteration fix this##'
    }
    
    keywords = {
        'foreachelse': '<? else: ?>',
        'else': '<? else: ?>',
        'rdelim': '{rdelim}',
        'ldelim': '{ldelim}'
    }

    """
    The AST structure is created by pyPEG.
    """
    def __init__(self, ast, extension="", path=""):
        self.language_handler = { 'smarty_language': self.smarty_language }
        self.symbol_handler = { 'symbol': self.symbol }
        self.expression_handler = { 'expression': self.expression }
        self.operator_handler = {
            'and_operator': self.and_operator,
            'equals_operator': self.equals_operator,
            'gte_operator': self.gte_operator,
            'lte_operator': self.lte_operator,
            'lt_operator': self.lt_operator,
            'gt_operator': self.gt_operator,
            'ne_operator': self.ne_operator,
            'nee_operator': self.nee_operator,
            'not_operator': self.not_operator,
            'or_operator': self.or_operator
        }

        self.param_handler = {
            'expression': self.expression,
            'operator': self.operator,
            'parameter': self.parameter,
            'not_operator': self.not_operator,
            'and_operator': self.and_operator,
            'equals_operator': self.equals_operator,
            'gte_operator': self.gte_operator,
            'lte_operator': self.lte_operator,
            'lt_operator': self.lt_operator,
            'gt_operator': self.gt_operator,
            'ne_operator': self.ne_operator,
            'nee_operator': self.nee_operator,
            'not_operator': self.not_operator,
            'or_operator': self.or_operator,
            'right_paren': self.rparen,
            'left_paren': self.lparen 
        }

        self.extension = 'phtml'
        self.path = ''
        
        if extension:
           self.extension = extension 
           
        if path:
            self.path = path
        
        # Top level handler for walking the tree.
        self.code = self.smarty_language(ast, '')        

    """
    Tree walking helper function.
    """
    def __walk_tree(self, handlers, ast, code):
        for k, v in ast:
            if handlers.has_key(k):
                if k == 'comment':
                    # Comments in php have <? /* not {*
                    code = "%s<? /* %s */ ?>" % (
                        code,
                        # value between {* and *}
                        v[2:len(v) - 2]
                    )
                else:
                    code = handlers[k](v, code)
                
        return code
                
    """
    The entry-point for the parser. 
    Contains a set of top-level smarty statements.
    """
    def smarty_language(self, ast, code):
        handler = {
            'include_statement': self.include_statement,
            'function_statement': self.function_statement,
            'if_statement': self.if_statement,
            'content': self.content,
            'comment': self.function_statement,
            'print_statement': self.print_statement,
            'for_statement': self.for_statement,
            'literal': self.literal,
            'strip': self.strip,
            'capture_statement': self.capture_statement,
            'assign_statement': self.assign,
            'guri_statement': self.guri,
            'curi_statement': self.curi,
            'uri_statement': self.uri,
            'buri_statement': self.buri,
            'static_call': self.static_call,
            'translate': self.translate
        }
        
        return self.__walk_tree(handler, ast, code)

    def strip(self, ast, code):
        stripped = ast
        stripped = stripped.replace('{/strip}', '')
        stripped = stripped.replace('{strip}', '')
        
        return "%s%s" % (code, stripped)

    def capture_assign(self, ast, code):
        return "%s$%s" % (code, self.__walk_tree(self.symbol_handler, ast, ""))

    def capture_name(self, ast, code):
        return "%s$%s" % (code, self.__walk_tree(self.symbol_handler, ast, ""))

    def capture_statement(self, ast, code):
        capture_handler = {
            'capture_name': self.capture_name,
            'capture_assign': self.capture_assign
        }

        code = "%s<? %s = " % (code, self.__walk_tree(capture_handler, ast, ""))

        return "%s%s; ?>" % (code, self.__walk_tree(self.language_handler, ast, ""))

    def math_statement(self, ast, code):
        return code

    def static_class(self, ast, code):
        return ast[2].strip('\'')

    def static_function(self, ast, code):
        return ast[2].strip('\'')

    def static_param(self, ast, code):
        return self.__walk_tree(self.expression_handler, ast, code)

    def static_call(self, ast, code): 
        static_handler = {
            'static_param': self.static_param,
            'static_function': self.static_function,
            'static_class': self.static_class
        }

        static_class = static_fun = args = ''

        static_class = self.__walk_tree({'static_class': self.static_class}, ast, code)
        static_function = self.__walk_tree({'static_function': self.static_function}, ast, code)

        for k, v in ast:
            if k == 'static_param':
                args = '%s%s' % (args, self.__walk_tree({'static_param': self.static_param}, ast, ""))

        return "%s%s::%s(%s)" % (code, static_class, static_function, args)

    def assign_var(self, ast, code):
        for k, v in ast:
            if k == 'symbol':
                code = "$%s = " % v[0]

        return code

    def assign_value(self, ast, code):
        expression = '%s' % self.__walk_tree(self.expression_handler, ast, "")

        if expression:
            return "%s%s" % (code, expression)
        else:
            return code

    def assign(self, ast, code):
        handlers = { 
            'assign_value': self.assign_value, 
            'assign_var': self.assign_var 
        }

        return "%s<? %s; ?>" % (code, self.__walk_tree(handlers, ast, code))

    def open_tag(self, ast, code):
        return '%s<? ' % code

    def close_tag(self, ast, code):
        return '%s ?>' % code

    def dollar(self, ast, code):
        return '%s$' % code

    def arrow(self, ast, code):
        return '%s->' % code

    def lparen(self, ast, code):
        return '%s(' % code

    def rparen(self, ast, code):
        return '%s)' % code

    def php_param(self, ast, code):
        return code

    def php_fun(self, ast, code):
        php_handler = {
            'dollar': self.dollar,
            'arrow': self.arrow,
            'symbol': self.symbol,
            'left_paren': self.lparen,
            'expression': self.expression,
            'right_paren': self.rparen
        }

        base = self.__walk_tree(php_handler, ast, code)
        return "%s%s" % (code, base)
        
    """
    A literal block in smarty, we can just drop the {literal} tags because 
    php is less ambiguous.
    """
    def literal(self, ast, code):
        literal_string = ast
        literal_string = literal_string.replace('{/literal}', '')
        literal_string = literal_string.replace('{literal}', '')
        
        return "%s%s" % (code, literal_string)
        
    """
    A complex string containing variables, e.x.,
    
        "`$foo.bar` Hello World $bar"
    """
    def variable_string(self, ast, code):
        
        code = "%s\"" % code
        
        # Crawl through the ast snippet and create a
        # string in the format "%s%s%s"
        # and a set of the parameters that will be
        # outputted with this string.
        variables = []
        string_contents = ''
        for k, v in ast:
            
            # Plain-text.
            if k == 'text':
                for text in v:
                    string_contents = "%s%s" % (string_contents, text)
                
            else: # An expression.
                string_contents = "%s%s" % (string_contents, '%s')
                
                expression = self.__walk_tree (
                    self.expression_handler,
                    [('expression', v)],
                    ""
                )
                variables.append(expression)
                
        # Now insert all the parameters
        function_params_string = ''
        i = 0
        size = len(variables)
        for v in variables:
            function_params_string = "%s%s" % (function_params_string, v)
            
            i += 1
            if not i == size:
                function_params_string = "%s, " % function_params_string
    
        return code

    #def include_params(self, ast, code):
    def rreplace(self, s, old, new, occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)
        
    # Deal with the special case of an include function in
    # smarty this should be mapped onto php's include tag.
    def include_statement(self, ast, code):
        params = {}
        args = filename = ''
        for k, v in ast:
            if k == 'include_params':
                symbol = self.__walk_tree(self.symbol_handler, v, "")
                expression = self.__walk_tree(self.expression_handler, v, "")
                params[symbol] = expression

        if len(params) > 1 and 'file' in params:
            args = ", array("

        for k, v in params.items():
            if k == 'file':
                filename = v
            # create additional args array
            else:
                args += '%s=>%s, ' % (k, v)
                
        # if there are args, remove the trailing `,` from the array
        if not args == '':
            args = "%s)" % self.rreplace(args, ',', '', 1)

        return "%s <?= $this->fetch(%s%s); ?>" % (code, filename, args)

    """
    Smarty functions are mapped to a modifier in
    php with a hash as input.
    """        
    def function_statement(self, ast, code):
        # The variable that starts a function statement.

        function_name = self.__walk_tree (self.symbol_handler, ast, "")
        expression = self.__walk_tree(self.expression_handler, ast, "")
        
        code = "%s%s(%s)" % (code, function_name, expression)
        return code
        
    """
    A print statement in smarty includes:
    
    {foo}
    {foo|bar:parameter}
    """
    def print_statement(self, ast, code):
        print_handler = {
            'expression_handler': self.expression,
            'guri_statement': self.guri,
            'curi_statement': self.curi,
            'uri_statement': self.uri,
            'buri_statement': self.buri
        }
                        
        # Walking the expression that starts a modifier statement.
        expression = self.__walk_tree (self.expression_handler, ast, "")
        
        # Perform any keyword replacements if found.        
        if self.keywords.has_key(expression):
            return "%s%s" % (code, self.keywords[expression])
                
        return "%s<?= %s ?>" % (code, expression)
        
    """
    A modifier statement:
    
    foo|bar:a:b:c
    """
    def modifier(self, ast, code):
        modifier_handler = {
            'symbol': self.symbol,
            'array': self.array,
            'string': self.string,
            'variable_string': self.variable_string,
            'object_dereference': self.object_dereference,
            'modifier_right': self.modifier_right,
            'static_call': self.static_call,
            'php_fun': self.php_fun
        }
                
        # Walking the expression that starts a modifier statement.
        return self.__walk_tree(modifier_handler, ast, code)
        
    """
    The right-hand side of the modifier
    statement:
    
    bar:a:b:c
    """
    def modifier_right(self, ast, code):
        handler = {
            'symbol': self.symbol,
            'default': self.default,
            'string': self.string,
            'escape': self.escape,
            'wordbreak': self.wordbreak,
            'urldecode': self.urldecode,
            'variable_string': self.variable_string
        }

        return self.__walk_tree(handler, ast, code)

    def escape(self, ast, code):
        escape_type = self.__walk_tree(self.expression_handler, ast, "")

        if escape_type:
           code = "%s, %s" % (code, escape_type)
        else:
           code = "%s" % code

        return "escape(%s)" % code

    def urldecode(self, ast, code):
        return "urldecode(%s)" % self.__walk_tree(self.expression_handler, ast, "")

    def wordbreak(self, ast, code):
        return "wordbreak(%s)" % self.__walk_tree(self.expression_handler, ast, code)

    def php_obj(self, ast, code):
        uri_handler = {
            'symbol': self.symbol,
            'arrow': self.arrow,
            'left_paren': self.lparen,
            'right_paren': self.rparen,
            'dollar': self.dollar
        }

        return self.__walk_tree(uri_handler, ast, code)

    def uri(self, ast, code, base_class):
        uri_handler = {
            'expression': self.expression,
            'php_obj': self.php_obj,
            'arrow': self.arrow,
            'dollar': self.dollar
        }

        method_name = args = ''

        code = "%s<?= %s" % (code, base_class)
        i = 0
        for k, v in ast:
            key = self.__walk_tree(self.symbol_handler, v, "")
            value = self.__walk_tree(uri_handler, v, "")
            if i == 0:
                code = "%s%s(%s, " % (code, key, value)
            else:
                code = "%s%s, " % (code, value)
            i += 1

        return "%s) ?> " % self.rreplace(code, ', ', '', 1)

    def guri(self, ast, code):
        return self.uri(ast, code, "GuideURI::")

    def buri(self, ast, code):
        return self.uri(ast, code, "URIBase::")

    def curi(self, ast, code):
        return self.uri(ast, code, "URIGenerator::")
        
    """
    Raw content, e.g.,
    
    <html>
        <body>
            <b>Hey</b>
        </body>
    </html>
    """
    def content(self, ast, code):
        return "%s%s" % (code, ast)
        
    """
    A foreach statement in smarty:
    
    {foreach from=expression item=foo key=koo name=bar}
    {foreachelse}
    {/foreach}
    """ 
    def for_statement(self, ast, code):

        name = _from = _key = _item = _name = ''
        
        for k, v in ast:
            if k == 'for_from':
                _from = "%s as " % self.__walk_tree (self.expression_handler, v, "")
            elif k == 'for_key':
                _key = "$%s => " % self.__walk_tree (self.symbol_handler, v, "")
            elif k == 'for_item':
                _item = "$%s" % self.__walk_tree (self.symbol_handler, v, "")
            elif k == 'for_name':
                _name = "$%s = '';" % self.__walk_tree (self.symbol_handler, v, "")
        
        # TODO: figure out what to do with name and iteration
        code = "%s<? foreach (%s%s%s): ?> " % (code, _from, _key, _item)

        # The content inside the if statement.
        code = self.__walk_tree (self.language_handler, ast, code)

        # Else and elseif statements.
        code = self.__walk_tree (
            { 'foreachelse_statement': self.else_statement },
            ast,
            code
        )

        return '%s<? endforeach; ?>' % code
    
    def parameter(self, ast, code):
        return '%s,' % self.__walk_tree(self.param_handler, ast, code)
                
    """
    An if statement in smarty:
    
    {if expression (operator expression)}
    {elseif expression (operator expression)}
    {else}
    {/if}
    """ 
    def if_statement(self, ast, code):
                   
        code = "%s<? if (" % code

        # Walking the expressions in an if statement.
        code = self.__walk_tree (self.param_handler, ast, code)
        
        code = "%s): ?>" % self.rreplace(code, ',', '', 1)
         
        # The content inside the if statement.
        code = self.__walk_tree (self.language_handler, ast, code)
        
        # Else and elseif statements.
        code = self.__walk_tree (
            {
                'elseif_statement': self.elseif_statement,
                'else_statement': self.else_statement
            },
            ast,
            code
        )

        return '%s<? endif; ?>' % code
        
    """
    The elseif part of an if statement, essentially
    this is the same as an if statement but without
    the elseif or else part.
    
    {elseif expression (operator expression)}
    """        
    def elseif_statement(self, ast, code):

        code = "%s<? elseif(" % code

        # Walking the expressions in an elseif statement.
        code = "%s): ?>" % self.__walk_tree (self.param_handler, ast, code)

        return self.__walk_tree (self.language_handler, ast, code)

    """
    The else part of an if statement.
    """
    def else_statement(self, ast, code):
        code = "%s<? else: ?>" % code
        
        # The content inside the if statement.
        return self.__walk_tree (self.language_handler, ast, code)

    """
    Operators in smarty.
    """
    def operator(self, ast, code):
        # Evaluate the different types of expressions.
        return self.__walk_tree(self.operator_handler, ast, code)
            
    """
    >= operator in Smarty.
    """
    def gte_operator(self, ast, code):
        return '%s >= ' % code
        
    """
    <= operator in smarty.
    """
    def lte_operator(self, ast, code):
        return '%s <= ' % code

    """
    < operator in smarty.
    """
    def lt_operator(self, ast, code):
        return '%s < ' % code
        
    """
    > operator in smarty.
    """
    def gt_operator(self, ast, code):
        return '%s > ' % code
        
    """
    ne, neq, != opeartor in Smarty.
    """
    def ne_operator(self, ast, code):
        return '%s != ' % code

    """
    ne, neq, != opeartor in Smarty.
    """
    def nee_operator(self, ast, code):
        return '%s !== ' % code
    
    """
    &&, and operator in Smarty.
    """
    def and_operator(self, ast, code):
        return '%s && ' % code
        
    """
    ||, or, operator in Smarty.
    """
    def or_operator(self, ast, code):
        return '%s || ' % code
        
    """
    eq, == opeartor in Smarty.
    """
    def equals_operator(self, ast, code):
        return '%s == ' % code

    def not_operator(self, ast, code):
        return '%s!' % code
    
    """
    A top level expression in Smarty that statements
    are built out of mostly expressions and/or symbols (which are
    encompassed in the expression type.
    """
    def expression(self, ast, code):
        # Evaluate the different types of expressions.
        expression = self.__walk_tree (
            {
                'symbol': self.symbol,
                'string': self.string,
                'variable_string': self.variable_string,
                'object_dereference': self.object_dereference,
                'function_statement': self.function_statement,
                'php_fun': self.php_fun,
                'static_call': self.static_call,
                'array': self.array,
                'modifier': self.modifier
            },
            ast,
            ""
        )
        
        #print "expression:",expression
        
        # Should we perform any replacements?
        for k, v in self.replacements.items():
            if re.match(k, expression):
                expression = v
                break

        return "%s%s" % (code, expression)
        
    """
    An object dereference expression in Smarty:
    
    foo.bar
    """
    def object_dereference(self, ast, code):
        handlers = {
            'expression': self.expression,
            'symbol': self.symbol,
            'string': self.string,
            'variable_string': self.variable_string,
            'dereference': self.dereference,
            'assignment_op': self.assignment_op,
            'array': self.array
        }

        for k, v in ast:
            code = "%s%s" % (code, handlers[k](v, ""))

        return code

    def assignment_op(self, ast, code):
        return code

    def dereference(self, ast, code):
        object_handlers = {
            'expression': self.expression,
            'symbol': self.symbol,
            'string': self.string,
            'variable_string': self.variable_string,
            'array': self.array
        }
        return "[\'%s\']" % self.__walk_tree(object_handlers, ast, "")
        
    """
    An array expression in Smarty:
    
    foo[bar]
    """
    def array(self, ast, code):
        handlers = {
            'expression': self.expression,
            'array': self.array,
            'symbol': self.symbol,
            'string': self.string,
            'variable_string': self.variable_string
        }

        code = handlers[ast[0][0]](ast[0][1], code)

        if (len(ast) > 1):
            code = "%s[\"%s\"]" % (
                code, 
                handlers[ast[1][0]](ast[1][1], "")
            )
        else:
            code = "%s[]" % code

        return code

    def translate_params(self, ast, code):
        params = ', '.join(re.sub("[0-9]+\=", "", ast[1]).split(' '))
        return "%s, %s" % (code, params)

    def translate(self, ast, code):
        params = self.__walk_tree({'translate_params': self.translate_params}, ast, "")
        return "%s <?= ___('%s'%s) ?>" % (code, self.__walk_tree(self.language_handler, ast, ""), params)

    """
    A string in Smarty.
    """
    def string(self, ast, code):
        return "%s%s" % (code, ''.join(ast))

    """
    Default values in Smarty.  Since there isn't a direct way of doing default
    values, we can just check isset() on it, which will prevent uninitiialized
    vars from throwing an error when checked.  

    {foo|default:false}
    {foo|default:""}
    """
    def default(self, ast, code):
        prefix = ''
        default_val = self.__walk_tree(self.expression_handler, ast, "")

        if default_val:
            return "%scheck(%s, %s)" % (prefix, code, default_val)
        else:
            return "%scheck(%s)" % (prefix, code)

    """
    Boolean values in Smarty 
    true
    false
    """
    def boolean(self, ast, code):
        return code

    """
    A symbol (variable) in Smarty, e.g,
    
    !foobar
    foo_bar
    foo3
    """
    def symbol(self, ast, code):
        # Assume no $ on the symbol.
        variable = ast[0]
        
        # Is there a ! operator.
        if len(variable) > 0:
            if variable[0] == 'not_operator':
                next_sym = ast[1][0]
                if  next_sym == 'dollar':
                    code = "!$%s" % code
                else:
                    code = "!%s" % code
            elif variable[0] == 'dollar':
                code = "$%s" % code
            elif variable[0] == 'at_operator':
              pass # are @ symbols supported?
        
        # Maybe there was a $ on the symbol?.
        if len(ast) > 1:
            variable = ast[len(ast) - 1]
            
        return "%s%s" % (code, variable)
       
