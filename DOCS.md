# Language

## Types

* Object types
  * Integral: i32, u8, f64, ...
  * bool
  * Composite: T[]
  * Pointer type: *T
* Function types
  * Fixed number of arguments: fn(Type1, Type2) -> Type2 or fn(Type1, Type2)
  * Vararg: fn(Type1, vararg Type2)
* Incomplete types (Object types but size cannot be determined)
  * void

## Expressions

* Identifier
* Literal
  * Number literal
  * String literal
  * Composite literal: arrays
* Parenthesized expression
* Postfix:
  * Array subscription: arr[i]
  * Call: f(x, y, z)
  * Structure member: a.b
* Unary:
  * Pointer: *T
  * Arithmetic: -x
  * Logic: !cond
* Cast expression: x as T
* Binary:
  * Multiplicative: x * y, x / y, x % y
  * Additive: x + y, x - y
  * Relational: x > y, x < y, x >= y, x <= y
  * Equality: x == y, x != y
  * Logical: x and y, x or y
* Declarations:
  * Import declaration
  * Function declaration
  * Variable declaration
* Statements:
  * Block
  * Expression statement
  * Control flow:
    * If
    * While
    * continue, break, return
  * Var, function declarations