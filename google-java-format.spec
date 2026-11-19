Name:		google-java-format
Version:	2.0.0
Release:	1
Summary:	Formats Java source to the Google Java Style
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/google/google-java-format
# Tag v plus the package version. The archive has no prebuilt jars.
# Error Prone requires 1.35.0, so that release stays beside this one.
Source0:	https://github.com/google/google-java-format/archive/refs/tags/v%{version}.tar.gz#/google-java-format-%{version}.tar.gz
Source1:	https://github.com/google/google-java-format/archive/refs/tags/v1.35.0.tar.gz#/google-java-format-1.35.0.tar.gz

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
BuildRequires:	mvn(org.commonmark:commonmark)
BuildRequires:	mvn(org.commonmark:commonmark-ext-gfm-tables)

%{!?commonmark_jar:%global commonmark_jar %{_javadir}/commonmark.jar}
%{!?commonmark_tables_jar:%global commonmark_tables_jar %{_javadir}/commonmark-ext-gfm-tables.jar}

%description
google-java-format %{version} formats Java source to the Google Java
Style. This release parses Markdown in Javadoc with the packaged
CommonMark library. Error Prone requires 1.35.0, so that jar stays
installed. The new class files stay at major version 65. Nothing is
downloaded.

%prep
%autosetup -n google-java-format-%{version}
find . -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries.list
if [ -s binaries.list ]; then
	cat binaries.list
	exit 1
fi
test -s LICENSE
test -s README.md
test -s core/src/main/java/com/google/googlejavaformat/java/Formatter.java
test -s core/src/main/java/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java.template
test -s core/src/main/java/com/google/googlejavaformat/java/javadoc/MarkdownPositions.java
test -s core/src/main/resources/META-INF/native-image/reachability-metadata.json
tar -C %{_builddir} -xf %{SOURCE1}
find "%{_builddir}/google-java-format-1.35.0" -type f \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -print > binaries-1.35.0.list
if [ -s binaries-1.35.0.list ]; then
	cat binaries-1.35.0.list
	exit 1
fi
test -s "%{_builddir}/google-java-format-1.35.0/core/src/main/java/com/google/googlejavaformat/java/Formatter.java"
test -s "%{_builddir}/google-java-format-1.35.0/core/src/main/java/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java.template"

%build
set -eo pipefail
build_135() (
	set -eo pipefail
	cd "%{_builddir}/google-java-format-1.35.0"
	find core/src/main/java -name '*.java' > sources.list
	test "$(wc -l < sources.list)" -eq 46
	mkdir -p gen/com/google/googlejavaformat/java gensrc classes
	sed 's/%%VERSION%%/1.35.0/' \
		core/src/main/java/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java.template \
		> gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java
	grep -F -q 'return "1.35.0";' gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java
	echo gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java >> sources.list
	CP=%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{_javadir}/jspecify.jar:%{_javadir}/error_prone_annotations.jar:%{_javadir}/auto-value-annotations.jar:%{_javadir}/auto-service-annotations.jar:%{_javadir}/auto-value.jar:%{_javadir}/auto-common.jar:%{_javadir}/escapevelocity.jar:%{_javadir}/javapoet.jar:%{_javadir}/incap.jar:%{_javadir}/asm.jar:%{_javadir}/checker-qual.jar
	javac -source 17 -target 17 -encoding UTF-8 -proc:full -Xlint:-options \
		--add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED \
		-cp "$CP" -s gensrc -d classes @sources.list
	mkdir -p classes/META-INF/services
	printf '%%s\n' 'com.google.googlejavaformat.java.GoogleJavaFormatTool' > classes/META-INF/services/javax.tools.Tool
	printf '%%s\n' 'com.google.googlejavaformat.java.GoogleJavaFormatToolProvider' > classes/META-INF/services/java.util.spi.ToolProvider
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
	jar tf google-java-format.jar > jar.list
	grep -q '^com/google/googlejavaformat/java/Formatter.class$' jar.list
	grep -q '^META-INF/services/java.util.spi.ToolProvider$' jar.list
	if grep -E -q 'module-info|\.(java|jar|so|node|wasm)$' jar.list; then
		grep -E 'module-info|\.(java|jar|so|node|wasm)$' jar.list
		exit 1
	fi
	cat > google-java-format.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.google.googlejavaformat</groupId>
  <artifactId>google-java-format</artifactId>
  <version>1.35.0</version>
  <name>google-java-format</name>
  <description>Formats Java source to the Google Java Style</description>
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
	grep -F -q '<version>1.35.0</version>' google-java-format.pom
	test "$(grep -c '<optional>true</optional>' google-java-format.pom)" -eq 4
)
build_200() (
	set -eo pipefail
	cd "%{_builddir}/google-java-format-%{version}"
	test -s "%{commonmark_jar}"
	test -s "%{commonmark_tables_jar}"
	find core/src/main/java -name '*.java' > sources.list
	test "$(wc -l < sources.list)" -eq 55
	mkdir -p gen/com/google/googlejavaformat/java gensrc classes
	sed 's/%%VERSION%%/%{version}/' \
		core/src/main/java/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java.template \
		> gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java
	grep -F -q 'return "%{version}";' gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java
	echo gen/com/google/googlejavaformat/java/GoogleJavaFormatVersion.java >> sources.list
	CP=%{_javadir}/guava.jar:%{_javadir}/failureaccess.jar:%{_javadir}/jspecify.jar:%{_javadir}/error_prone_annotations.jar:%{_javadir}/auto-value-annotations.jar:%{_javadir}/auto-service-annotations.jar:%{_javadir}/auto-value.jar:%{_javadir}/auto-common.jar:%{_javadir}/escapevelocity.jar:%{_javadir}/javapoet.jar:%{_javadir}/incap.jar:%{_javadir}/asm.jar:%{_javadir}/checker-qual.jar:%{commonmark_jar}:%{commonmark_tables_jar}
	javac -source 21 -target 21 -encoding UTF-8 -proc:full -Xlint:-options \
		--add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED \
		-cp "$CP" -s gensrc -d classes @sources.list
	mkdir -p classes/META-INF/services
	printf '%%s\n' 'com.google.googlejavaformat.java.GoogleJavaFormatTool' > classes/META-INF/services/javax.tools.Tool
	printf '%%s\n' 'com.google.googlejavaformat.java.GoogleJavaFormatToolProvider' > classes/META-INF/services/java.util.spi.ToolProvider
	/bin/cp -a core/src/main/resources/META-INF/native-image classes/META-INF/
	cat > manifest.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: com.google.googlejavaformat
Main-Class: com.google.googlejavaformat.java.Main
Add-Exports: jdk.compiler/com.sun.tools.javac.api jdk.compiler/com.sun.tools.javac.code jdk.compiler/com.sun.tools.javac.file jdk.compiler/com.sun.tools.javac.parser jdk.compiler/com.sun.tools.javac.tree jdk.compiler/com.sun.tools.javac.util

EOF
	jar cfm google-java-format.jar manifest.mf -C classes .
	jar i google-java-format.jar
	javap -verbose -cp google-java-format.jar com.google.googlejavaformat.java.Formatter | grep -F 'major version: 65'
	jar --describe-module --file google-java-format.jar > describe.txt
	if grep -F -q 'Unable to derive' describe.txt; then
		cat describe.txt
		exit 1
	fi
	jar tf google-java-format.jar > jar.list
	grep -q '^com/google/googlejavaformat/java/Formatter.class$' jar.list
	grep -q '^com/google/googlejavaformat/java/javadoc/MarkdownPositions.class$' jar.list
	grep -q '^META-INF/services/java.util.spi.ToolProvider$' jar.list
	grep -q '^META-INF/services/javax.tools.Tool$' jar.list
	if grep -E -q 'module-info|\.(java|jar|so|node|wasm)$' jar.list; then
		grep -E 'module-info|\.(java|jar|so|node|wasm)$' jar.list
		exit 1
	fi
	cat > google-java-format.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.google.googlejavaformat</groupId>
  <artifactId>google-java-format</artifactId>
  <version>%{version}</version>
  <name>google-java-format</name>
  <description>Formats Java source to the Google Java Style</description>
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
      <groupId>org.commonmark</groupId>
      <artifactId>commonmark</artifactId>
      <version>0.32.0</version>
    </dependency>
    <dependency>
      <groupId>org.commonmark</groupId>
      <artifactId>commonmark-ext-gfm-tables</artifactId>
      <version>0.32.0</version>
    </dependency>
    <dependency>
      <groupId>org.jspecify</groupId>
      <artifactId>jspecify</artifactId>
      <version>1.0.1</version>
      <optional>true</optional>
    </dependency>
    <dependency>
      <groupId>com.google.errorprone</groupId>
      <artifactId>error_prone_annotations</artifactId>
      <version>2.50.0</version>
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
	grep -F -q '<version>%{version}</version>' google-java-format.pom
	grep -F -q '<artifactId>commonmark</artifactId>' google-java-format.pom
	grep -F -q '<artifactId>commonmark-ext-gfm-tables</artifactId>' google-java-format.pom
	test "$(grep -c '<optional>true</optional>' google-java-format.pom)" -eq 4
)
build_135
build_200

%install
set -eo pipefail
old="%{_builddir}/google-java-format-1.35.0"
sysjar install --buildroot %{buildroot} \
	--artifact "${old}/google-java-format.pom:${old}/google-java-format.jar" \
	--file-name google-java-format-1.35.0 \
	--filelist .mfiles-old
index="%{buildroot}/usr/share/sysjar/index/com.google.googlejavaformat/google-java-format.sysjar"
test -f "$index"
/bin/mv "$index" "%{buildroot}/usr/share/sysjar/index/com.google.googlejavaformat/google-java-format-1.35.0.sysjar"
sed -i 's|/usr/share/sysjar/index/com\.google\.googlejavaformat/google-java-format\.sysjar|/usr/share/sysjar/index/com.google.googlejavaformat/google-java-format-1.35.0.sysjar|' .mfiles-old
idx="%{buildroot}/usr/share/sysjar/index/com.google.googlejavaformat/google-java-format-1.35.0.sysjar"
grep -F -q '"version": "1.35.0"' "$idx"
grep -F -q '"artifactId": "google-java-format"' "$idx"
new="%{_builddir}/google-java-format-%{version}"
sysjar install --buildroot %{buildroot} \
	--artifact "${new}/google-java-format.pom:${new}/google-java-format.jar" \
	--file-name google-java-format \
	--filelist .mfiles-new
idxn="%{buildroot}/usr/share/sysjar/index/com.google.googlejavaformat/google-java-format.sysjar"
grep -F -q '"version": "%{version}"' "$idxn"
grep -F -q '"artifactId": "google-java-format"' "$idxn"
test -s %{buildroot}%{_javadir}/google-java-format-1.35.0.jar
test -s %{buildroot}%{_javadir}/google-java-format.jar
: > .mfiles
for list in .mfiles-old .mfiles-new
do
	while IFS= read -r line; do
		grep -qxF -- "$line" .mfiles || printf '%%s\n' "$line" >> .mfiles
	done < "$list"
done
grep -F -q '/google-java-format.jar' .mfiles
grep -F -q '/google-java-format-1.35.0.jar' .mfiles

%check
set -eo pipefail
mkdir -p check
cat > check/Smoke.java << 'EOF'
import com.google.googlejavaformat.java.Formatter;
import com.google.googlejavaformat.java.JavaFormatterOptions;
public class Smoke {
	public static void main(String[] args) throws Exception {
		String out = new Formatter().formatSource("class A{int x=1;}");
		String flat = out.replace('\n', ' ');
		if (!flat.contains("class A") || !flat.contains("int x = 1;")) {
			throw new RuntimeException(flat);
		}
		if (JavaFormatterOptions.Style.GOOGLE == null) {
			throw new RuntimeException("style");
		}
		System.out.println("gjf_ok " + args[0] + " " + flat.trim());
	}
}
EOF
cat > check/NewSmoke.java << 'EOF'
import com.google.googlejavaformat.java.Formatter;
import com.google.googlejavaformat.java.JavaFormatterOptions;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.spi.ToolProvider;
public class NewSmoke {
	public static void main(String[] args) throws Exception {
		if (!"GOOGLE".equals(JavaFormatterOptions.Style.GOOGLE.name())) {
			throw new RuntimeException("style");
		}
		String md = "/// | a |\n/// | --- |\n/// | ok |\nclass B{int y=2;}\n";
		String mdout = new Formatter().formatSource(md);
		if (!mdout.contains("ok") || !mdout.contains("int y = 2;")) {
			throw new RuntimeException(mdout);
		}
		Path file = Path.of(args[0]);
		Files.writeString(file, "class C{int z=3;}\n");
		ToolProvider tool = ToolProvider.findFirst("google-java-format").orElseThrow();
		if (!"google-java-format".equals(tool.name())) {
			throw new RuntimeException(tool.name());
		}
		int rc = tool.run(new java.io.PrintWriter(System.out, true), new java.io.PrintWriter(System.err, true), "-i", file.toString());
		if (rc != 0) {
			throw new RuntimeException("tool " + rc);
		}
		String rewritten = Files.readString(file);
		if (!rewritten.contains("int z = 3;")) {
			throw new RuntimeException(rewritten);
		}
		System.out.println("gjf_tool_ok %{version}");
	}
}
EOF
J="%{_javadir}"
BASE="$J/guava.jar:$J/failureaccess.jar"
run_check() {
	label=$1
	jar=$2
	expect=$3
	extra=$4
	test -s "$jar"
	mkdir -p "check/${label}"
	javac -source 17 -target 17 -encoding UTF-8 -Xlint:-options -cp "${jar}:${BASE}:${extra}" -d "check/${label}" check/Smoke.java
	java --add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED \
		--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED \
		-cp "check/${label}:${jar}:${BASE}:${extra}" Smoke "$expect" > "check/${label}/out.txt"
	cat "check/${label}/out.txt"
	grep -F -q "gjf_ok ${expect}" "check/${label}/out.txt"
	grep -F -q 'int x = 1;' "check/${label}/out.txt"
}
run_check old "%{buildroot}%{_javadir}/google-java-format-1.35.0.jar" 1.35.0 ""
run_check new "%{buildroot}%{_javadir}/google-java-format.jar" %{version} "%{commonmark_jar}:%{commonmark_tables_jar}"
mkdir -p check/tool
javac -source 21 -target 21 -encoding UTF-8 -Xlint:-options \
	-cp "%{buildroot}%{_javadir}/google-java-format.jar:${BASE}:%{commonmark_jar}:%{commonmark_tables_jar}" \
	-d check/tool check/NewSmoke.java
java --add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED \
	--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED \
	-cp "check/tool:%{buildroot}%{_javadir}/google-java-format.jar:${BASE}:%{commonmark_jar}:%{commonmark_tables_jar}" \
	NewSmoke check/tool/C.java > check/tool/out.txt
cat check/tool/out.txt
grep -F -q 'gjf_tool_ok %{version}' check/tool/out.txt
javap -verbose -cp %{buildroot}%{_javadir}/google-java-format.jar com.google.googlejavaformat.java.Formatter | grep -F 'major version: 65'
javap -verbose -cp %{buildroot}%{_javadir}/google-java-format-1.35.0.jar com.google.googlejavaformat.java.Formatter | grep -F 'major version: 61'

%files -f .mfiles
%license LICENSE
%doc README.md
