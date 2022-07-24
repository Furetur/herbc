cd src/parser/g4
java -jar ../../../lib/antlr-4.7.2-complete.jar -Dlanguage=Python3 -o ../generated Herb.g4
java -jar ../../../lib/antlr-4.7.2-complete.jar -o ../generated Herb.g4
cd ../generated
javac *.java
cd ../../..