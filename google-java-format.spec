Name:		google-java-format
Version:	1.35.0
Release:	1
Summary:	Reformats Java source to the Google Java Style
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/google/google-java-format
# Tag v1.35.0. The archive has no prebuilt jars or class files.
Source0:	https://github.com/google/google-java-format/archive/refs/tags/v%{version}.tar.gz#/google-java-format-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem
BuildRequires:	mvn(com.google.guava:guava)
BuildRequires:	mvn(com.google.guava:failureaccess)
BuildRequires:	mvn(org.jspecify:jspecify)
BuildRequires:	mvn(com.google.errorprone:error_prone_annotations)
BuildRequires:	mvn(com.google.auto.value:auto-value)
BuildRequires:	mvn(com.google.auto.value:auto-value-annotations)
BuildRequires:	mvn(com.google.auto.service:auto-service-annotations)
BuildRequires:	mvn(com.google.auto:auto-common)
BuildRequires:	mvn(com.google.escapevelocity:escapevelocity)
BuildRequires:	mvn(com.squareup:javapoet)
BuildRequires:	mvn(net.ltgt.gradle.incap:incap)
BuildRequires:	mvn(org.ow2.asm:asm)
BuildRequires:	mvn(org.checkerframework:checker-qual)

%description
google-java-format %{version} reformats Java source to the Google Java
Style. Error Prone 2.50.0 links this jar. The formatter calls into
com.sun.tools.javac, so it is compiled with -source 17 -target 17.
--release cannot see those JDK-internal packages. AutoValue generates
the helper types. The auto-service processor is not packaged, so the
two service files are written here.

%prep
%autosetup -n google-java-format-%{version}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
find core/src/main/java -name '*.java' > sources.list
test "$(wc -l < sources.list)" -eq 46
mkdir -p gen/com/google/googlejavaformat/java
sed 's/%%VERSION%%/%{version}/' \
	core/src/main/java/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java.template \
	> gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java
grep -F -q 'return "%{version}";' gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java
echo gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java >> sources.list

CP=%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{_javadir}/jspecify.jar:%{_javadir}/error_prone_annotations.jar:%{_javadir}/auto-value-annotations.jar:%{_javadir}/auto-service-annotations.jar:%{_javadir}/auto-value.jar:%{_javadir}/auto-common.jar:%{_javadir}/escapevelocity.jar:%{_javadir}/javapoet.jar:%{_javadir}/incap.jar:%{_javadir}/asm.jar:%{_javadir}/checker-qual.jar
mkdir -p classes
javac -source 17 -target 17 -encoding UTF-8 -proc:full -Xlint:-options \
	--add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED \
	-cp "$CP" -d classes @sources.list
mkdir -p classes/META-INF/services
printf '%s\n' 'com.google.googlejavaformat.java.GoogleJavaFormatTool' > classes/META-INF/services/javax.tools.Tool
printf '%s\n' 'com.google.googlejavaformat.java.GoogleJavaFormatToolProvider' > classes/META-INF/services/java.util.spi.ToolProvider
/bin/cp -a core/src/main/resources/META-INF/native-image classes/META-INF/
cat > manifest.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: com.google.googlejavaformat
Main-Class: com.google.googlejavaformat.java.Main
Add-Exports: jdk.compiler/com.sun.tools.javac.api jdk.compiler/com.sun.tools.javac.code jdk.compiler/com.sun.tools.javac.file jdk.compiler/com.sun.tools.javac.parser jdk.compiler/com.sun.tools.javac.tree jdk.compiler/com.sun.tools.javac.util

EOF
jar cfm google-java-format.jar manifest.mf -C classes .
jar i google-java-format.jar
javap -verbose -cp google-java-format.jar com.google.googlejavaformat.java.Formatter | grep -F 'major version: 61'

cat > google-java-format.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.google.googlejavaformat</groupId>
  <artifactId>google-java-format</artifactId>
  <version>1.35.0</version>
  <name>google-java-format</name>
  <description>Reformats Java source to the Google Java Style</description>
  <licenses>
    <license>
      <name>Apache-2.0</name>
    </license>
  </licenses>
  <dependencies>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>33.6.0-jre</version>
    </dependency>
    <dependency>
      <groupId>org.jspecify</groupId>
      <artifactId>jspecify</artifactId>
      <version>1.0.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.google.errorprone</groupId>
      <artifactId>error_prone_annotations</artifactId>
      <version>2.52.0</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.google.auto.value</groupId>
      <artifactId>auto-value-annotations</artifactId>
      <version>1.11.1</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.google.auto.service</groupId>
      <artifactId>auto-service-annotations</artifactId>
      <version>1.1.1</version>
      <optional>true</optional>
    </dependency>
  </dependencies>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact google-java-format.pom:google-java-format.jar \
	--file-name google-java-format \
	--filelist .mfiles

%check
set -eo pipefail
mkdir -p check
cat > check/Smoke.java << 'EOF'
import com.google.googlejavaformat.java.Formatter;
public class Smoke {
	public static void main(String[] args) throws Exception {
		String out = new Formatter().formatSource("class A{int x=1;}");
		String flat = out.replace('\n', ' ');
		if (!flat.contains("class A") || !flat.contains("int x = 1;")) {
			throw new RuntimeException(flat);
		}
		System.out.println("gjf_ok 1.35.0 " + flat.trim());
	}
}
EOF
JAR=%{buildroot}%{_javadir}/google-java-format.jar
test -f "$JAR"
CP="$JAR:%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar"
javac -source 17 -target 17 -encoding UTF-8 -Xlint:-options -cp "$CP" -d check check/Smoke.java
java --add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED \
	-cp "check:$CP" Smoke > check/out.txt
cat check/out.txt
grep -F -q 'gjf_ok 1.35.0' check/out.txt
grep -F -q 'int x = 1;' check/out.txt

%files -f .mfiles
%doc LICENSE README.md
