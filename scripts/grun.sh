export CLASSPATH=".:../../../lib/antlr-4.10.1-complete.jar:$CLASSPATH"
cd src/parser/generated
java org.antlr.v4.gui.TestRig Herb prog -gui ../../../programs/$1
cd ../../..
