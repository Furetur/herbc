from llvmlite import ir

from src.ast import Decl, FunDecl
from src.ast.utils import module
from src.ty import Ty, TyInt, TyBool, TyStr, TyFunc, TyVoid

LL_TRIPLE = "x86_64-pc-linux-gnu"

# primitive types
void_type = ir.VoidType()
int_type = ir.IntType(32)
bool_type = ir.IntType(1)
byte_type = ir.IntType(8)
byteptr = ir.PointerType(byte_type)
str_type = byteptr

# functions
main_fn_type = ir.FunctionType(void_type, [])
USER_MAIN_FN_NAME = "main"
OUT_MAIN_FN_NAME = "__HERB__entry"

print_int_fn_type = ir.FunctionType(void_type, [int_type])
PRINT_INT_FN_NAME = "print_int"

print_bool_fn_type = ir.FunctionType(void_type, [byte_type]) # <-- IMPORTANT: byte_type
PRINT_BOOL_FN_NAME = "print_bool"

print_str_fn_type = ir.FunctionType(void_type, [str_type])
PRINT_STR_FN_NAME = "print_str"


def func_name(fn: FunDecl):
    if fn.name != USER_MAIN_FN_NAME:
        return f"{module(fn).unique_name}.func.{fn.name}"
    else:
        return OUT_MAIN_FN_NAME


def global_name(decl: Decl):
    return f"{module(decl).unique_name}.{decl.declared_name()}"


def ll_func_type(ty: Ty) -> ir.Type:
    assert isinstance(ty, TyFunc)
    return ir.FunctionType(
        args=[ll_value_type(arg_ty) for arg_ty in ty.args],
        return_type=ll_value_type(ty.ret)
    )


def ll_value_type(ty: Ty) -> ir.Type:
    if ty == TyInt:
        return int_type
    elif ty == TyBool:
        return bool_type
    elif ty == TyStr:
        return str_type
    elif ty == TyVoid:
        return void_type
    elif isinstance(ty, TyFunc):
        return ir.PointerType(ll_func_type(ty))
    else:
        assert False, f"unexpected type: {ty}"