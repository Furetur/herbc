from llvmlite import ir


# primitive types
void_type = ir.VoidType()
int_type = ir.IntType(32)

# functions
main_fn_type = ir.FunctionType(int_type, [])
MAIN_FN_NAME = "main"

print_int_fn_type = ir.FunctionType(void_type, [int_type])
PRINT_INT_FN_NAME = "print_int"
