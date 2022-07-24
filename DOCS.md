# Types

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

# Syntax

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

## Declarations

* Import declaration
* Function declaration
* Variable declaration

### Import declaration

Examples: 
* `import root.path.to.package`
* `import alias = root.path.to.package`
* `import .relative.path.to.package`
* `import alias = .relative.path.to.package`

#### Import path resolution

There are two types of import paths:
* absolute paths: `import root.a.b`
* relative paths: `import .a.b`

**Relative paths**. Relative paths are resolved relative to the project root: `.a.b` is mapped to `$projectRoot/a/b`.

**Absolute paths**. The first identifier in the absolute path corresponds to a _root package_, 
the paths is resolved relative to that package: `root.a.b` is mapped to `$root/a/b`. 
All root packages must be defined in `herb.yaml` at the root of the project.

## Statements

* Block
* Expression statement
* Control flow:
  * `if`
  * `while`
  * `continue`, `break`, `return`
* Variable declarations

# Module System

Compilation units: 
* entry file -- file with a defined entry point
* package -- module

Packages is a folder with `.herb` files.