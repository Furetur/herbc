from llvmlite import ir


# primitive types
void_type = ir.VoidType()
int_type = ir.IntType(32)
bool_type = ir.IntType(8)

# functions
main_fn_type = ir.FunctionType(int_type, [])
MAIN_FN_NAME = "main"

print_int_fn_type = ir.FunctionType(void_type, [int_type])
PRINT_INT_FN_NAME = "print_int"

print_bool_fn_type = ir.FunctionType(void_type, [bool_type])
PRINT_BOOL_FN_NAME = "print_bool"
