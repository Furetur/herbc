mkdir -p runtime/build
clang-14 -S -emit-llvm runtime/console.c -o runtime/build/console.ll
clang-14 -S -emit-llvm runtime/main.c -o runtime/build/main.ll