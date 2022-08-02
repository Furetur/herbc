mkdir -p runtime/build
clang-14 -S -emit-llvm runtime/console.c -o runtime/build/console.ll