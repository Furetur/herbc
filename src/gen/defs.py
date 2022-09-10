from llvmlite import ir

from src.ast import Decl
from src.ast.utils import module

LL_TRIPLE = "x86_64-pc-linux-gnu"

# primitive types
void_type = ir.VoidType()
int_type = ir.IntType(32)
bool_type = ir.IntType(8)
byte_type = ir.IntType(8)
byteptr = ir.PointerType(bool_type)
str_type = byteptr

# functions
main_fn_type = ir.FunctionType(int_type, [])
MAIN_FN_NAME = "main"

print_int_fn_type = ir.FunctionType(void_type, [int_type])
PRINT_INT_FN_NAME = "print_int"

print_bool_fn_type = ir.FunctionType(void_type, [bool_type])
PRINT_BOOL_FN_NAME = "print_bool"

print_str_fn_type = ir.FunctionType(void_type, [str_type])
PRINT_STR_FN_NAME = "print_str"

def global_name(self, decl: Decl):
    return f"{module(decl).unique_name}.{decl.declared_name()}"
