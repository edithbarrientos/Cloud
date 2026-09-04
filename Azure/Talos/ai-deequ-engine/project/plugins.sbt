addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "2.1.1")

// 🚀 SOPORTE DE PROTOBUF GLOBAL: Compilador de archivos .proto para todos los submódulos
addSbtPlugin("com.thesamet" % "sbt-protoc" % "1.0.6")
libraryDependencies += "com.thesamet.scalapb" %% "compilerplugin" % "0.11.13"
