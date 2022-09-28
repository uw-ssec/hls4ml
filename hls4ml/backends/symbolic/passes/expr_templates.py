import re

from hls4ml.model.layers import SymbolicExpression
from hls4ml.backends.template import LayerConfigTemplate, FunctionCallTemplate

from sympy.printing.cxx import CXX11CodePrinter
from sympy.core.numbers import Integer

# Expression templates

expr_function_template = 'y[0] = {expr_str};'

expr_include_list = ['hls_math.h']

class HLSCodePrinter(CXX11CodePrinter):
    _ns = 'hls::'

    def _symbol_to_array(self, name):
        return re.sub(r'([a-zA-Z]+)(\d+)', r'\1[\2]', name)

    def _print_Float(self, flt):
        float_str = super()._print_Float(flt)
        return f'model_default_t({float_str})'

    def _print_Pow(self, expr):
        if isinstance(expr.exp, Integer):
            symbol = next(iter(expr.free_symbols))
            symbol = self._symbol_to_array(str(symbol))
            if expr.exp > 1:
                return '*'.join([str(symbol) for _ in range(expr.exp)]) 
            elif expr.exp == -1: # 1/x
                return f'hls::recip({symbol})'
            else:
                return super()._print_Pow(expr)
        else:
            return super()._print_Pow(expr)

    def _print_Symbol(self, expr):
        name = super()._print_Symbol(expr)
        return self._symbol_to_array(name)

class ExpressionFunctionTemplate(FunctionCallTemplate):
    def __init__(self):
        super().__init__(SymbolicExpression, include_header=expr_include_list)
        self.template = expr_function_template
    
    def format(self, node):
        params = self._default_function_params(node)
        params['expr_str'] = HLSCodePrinter().doprint(node.attributes['expression'])
        return self.template.format(**params)