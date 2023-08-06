set JOOO_HOME=C:\Program Files (x86)\LibreOffice 3.4\URE\java
set JUNO_HOME=C:\Program Files (x86)\LibreOffice 3.4\Basis\program\classes

set JAVAC="C:\Program Files\Java\jdk1.6.0_27\bin\javac.exe"
set JAR="C:\Program Files\Java\jdk1.6.0_27\bin\jar.exe"

set classpath=%JOOO_HOME%\juh.jar;%JOOO_HOME%\jurt.jar;%JOOO_HOME%\ridl.jar;%JOOO_HOME%\unoloader.jar;%JOOO_HOME%\java_uno.jar;%JUNO_HOME%\unoil.jar

%JAVAC% -classpath=%classpath% py3oconverter/Launch.java
%JAVAC% py3oconverter/Convertor.java

%JAR% -cf ../../py3o/renderers/juno/py3oconverter.jar py3oconverter/Convertor.class
