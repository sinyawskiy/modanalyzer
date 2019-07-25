#!/usr/local/bin/python3

import ast
import sys
# import inspect
# import importlib


""" The data we collect.  Each key is a function name; each value is a dict
with keys: firstline, sigend, docend, and lastline and values of line numbers
where that happens. """

functions = {}
arguments = {}

def process(file, functions):
    module = file.split('.py')[0]
    """ Handle the function data stored in functions. """
    # print arguments.keys()
    result = ["ns = APINamespace('{module}', description=u'')".format(**{
        'module': module
    })]
    for argument in arguments.keys():
        result.append("""
{module}_{argument} = ns.model('{module_capitalize}{argument_capitalize}', {{
    '{argument}': fields.String(required=True, default='', description=u'')
}})
        """.format(**{
            'module': module,
            'module_capitalize': module.capitalize(),
            'argument': argument,
            'argument_capitalize': argument.capitalize()
        }))
        arguments[argument] = '{module}_{argument}'.format(**{
            'module': module,
            'argument': argument
        })

    for funcname, data in functions.items():
        if len(data['args']) > 1:
            result.append("""
{module}_{funcname}_params = ns.clone('{module_capitalize}{funcname_camel}Params', {function_arguments})
            """.format(**{
                'module': module,
                'module_capitalize': module.capitalize(),
                'funcname': funcname,
                'funcname_camel': ''.join([item.capitalize() for item in funcname.split('_')]),
                'function_arguments': ', '.join([arguments[item] for item in data['args']])
            }))
            functions[funcname]['result_arguments'] = '{module}_{funcname}_params'.format(**{
                'module': module,
                'funcname': funcname
            })
        else:
            if data['args']:
                functions[funcname]['result_arguments'] = arguments[data['args'][0]]
            else:
                functions[funcname]['result_arguments'] = None

    for funcname, data in functions.items():
        if data['result_arguments']:
            result.append("""
@ns.route('/{funcname}/', methods=['POST'], endpoint='{module}__{funcname}')
class {module_capitalize}{funcname_camel}(CronosResource):

    @login_required
    @ns.auth_header()
    @ns.doc(id='{module}__{funcname}', description=u'')
    @ns.expect({result_arguments})
    def post(self):
        u\"""
            

        \"""
        return self.add_task(u'')
        """.format(**{
            'module': module,
            'funcname': funcname,
            'module_capitalize': module.capitalize(),
            'result_arguments': data['result_arguments'],
            'funcname_camel': ''.join([item.capitalize() for item in funcname.split('_')]),
            }))
        else:
            result.append("""
            @ns.route('/{funcname}/', methods=['POST'], endpoint='{module}__{funcname}')
            class {module_capitalize}{funcname_camel}(CronosResource):

                @login_required
                @ns.auth_header()
                @ns.doc(id='{module}__{funcname}', description=u'')
                def post(self):
                    u\"""


                    \"""
                    return self.add_task(u'')
                    """.format(**{
                'module': module,
                'funcname': funcname,
                'module_capitalize': module.capitalize(),
                'funcname_camel': ''.join([item.capitalize() for item in funcname.split('_')]),
            }))

    print '\n'.join(result)

    # for funcname, data in functions.items():
    #     print("function:", funcname)
    #     print("arguments:", data['args'])



    #     print("\tstarts at line:",data['firstline'])
    #     print("\tsignature ends at line:",data['sigend'])
    #     if ( data['sigend'] < data['docend'] ):
    #         print("\tdocstring ends at line:",data['docend'])
    #     else:
    #         print("\tno docstring")
    #     print("\tfunction ends at line:",data['lastline'])
    #     print()

class FuncLister(ast.NodeVisitor):
    def visit_FunctionDef(self, node):
        """ Recursively visit all functions, determining where each function
        starts, where its signature ends, where the docstring ends, and where
        the function ends. """
        if node.args.kwarg == 'kwargs':
            functions[node.name] = {}
            # functions[node.name] = {'firstline': node.lineno}
            # sigend = max(node.lineno, lastline(node.args))
            # functions[node.name]['sigend'] = sigend
            functions[node.name]['args'] = [argument.id for argument in node.args.args if argument.id != 'self']
            for argument in functions[node.name]['args']:
                arguments[argument] = ''

            # docstring = ast.get_docstring(node)
            # docstringlength = len(docstring.split('\n')) if docstring else -1
            # functions[node.name]['docend'] = sigend+docstringlength
            # functions[node.name]['lastline'] = lastline(node)
            self.generic_visit(node)

def lastline(node):
    """ Recursively find the last line of a node """
    return max( [ node.lineno if hasattr(node,'lineno') else -1 , ]
                +[lastline(child) for child in ast.iter_child_nodes(node)] )

def readin(pythonfilename):
    """ Read the file name and store the function data into functions. """
    with open(pythonfilename) as f:
        code = f.read()
    FuncLister().visit(ast.parse(code))

# def inspecting(file, functions):
#     for funcname, data in functions.items():
#         module_name = file.split('.py')[0]
#         module_func = '{}.{}'.format(module_name, funcname)
#         text_function = importlib.import_module(module_name)
#         # print(module_func)
#         for key, inspect_data in inspect.getargspec(text_function):
#             print(key, inspect_data)
#         # for key, inspect_data in inspect.getmembers(module_func):
#         #     print(key, inspect_data)


def analyze(file,process):
    """ Read the file and process the function data. """
    readin(file)
    # inspecting(file, functions)
    process(file, functions)

if __name__ == '__main__':
    if len(sys.argv)>1:
        for file in sys.argv[1:]:
            analyze(file, process)
    else:
        analyze(sys.argv[0],process)
