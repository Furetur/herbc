# Clean
rm -rf src/parser/generated
mkdir -p src/parser/generated
echo "" > src/parser/generated/__init__.py

# Generate grammars
cd src/parser/g4
java -jar ../../../lib/antlr-4.10.1-complete.jar -Dlanguage=Python3 -visitor -no-listener -o ../generated Herb.g4
java -jar ../../../lib/antlr-4.10.1-complete.jar -no-listener -no-visitor -o ../generated Herb.g4

# Compile Java
cd ../generated
export CLASSPATH=".:../../../lib/antlr-4.10.1-complete.jar:$CLASSPATH"
javac *.java

cd ../../..