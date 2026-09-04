import sbtassembly.AssemblyPlugin.autoImport._
import sbtassembly.{MergeStrategy, PathList}

ThisBuild / version      := "4.0.0"
ThisBuild / scalaVersion := "2.12.18"

ThisBuild / scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-encoding", "utf-8"
)

// ==============================================================================
// 1. MÓDULO AGREGADOR MAESTRO (MONOREPO ROOT)
// ==============================================================================
lazy val root = (project in file("."))
  .aggregate(flinkRuntime, customApi)
  .settings(name := "ai-nlp-engine-orchestrator")


// ==============================================================================
// 2. ORQUESTADOR DE STREAMING DE ALTA DISPONIBILIDAD (FLINK-RUNTIME)
// ==============================================================================
lazy val flinkRuntime = (project in file("flink-runtime"))
  .enablePlugins(AssemblyPlugin)
  .settings(
    name := "flink-runtime",
    
    assembly / assemblyOutputPath := {
      val targetDir = baseDirectory.value / ".." / "target" / "artifacts"
      IO.createDirectory(targetDir)
      targetDir / "ai-nlp-stream-agent.jar"
    },
    
    assembly / assemblyMergeStrategy := {
      case "reference.conf" => MergeStrategy.concat
      case "application.conf" => MergeStrategy.concat
      case PathList("META-INF", "services", xs @ _*) => MergeStrategy.concat
      case PathList("META-INF", xs @ _*) => MergeStrategy.discard
      case _ => MergeStrategy.first
    },
    
    libraryDependencies ++= Seq(
      // 🛡️ NÚCLEO CORE DE FLINK EXCLUIDO DEL JAR (YA PROVISTOS POR DOCKER)
      "org.apache.flink" %% "flink-scala"          % "1.18.1" % "provided",
      "org.apache.flink" %% "flink-streaming-scala" % "1.18.1" % "provided",
      "org.apache.flink"  % "flink-clients"         % "1.18.1" % "provided",
      "org.apache.flink"  % "flink-connector-base"   % "1.18.1" % "provided",
      
      // 📦 CONECTORES E INYECTORES ELÁSTICOS QUE SÍ DEBEN EMPAQUETARSE
      "org.apache.flink"  % "flink-connector-pulsar" % "4.1.0-1.18",
      "com.typesafe"       % "config"                 % "1.4.2",
      
      // 🚀 INCLUSIÓN EXACTA: Empaquetamos Jackson de forma embebida para anular el NoClassDefFoundError
      "com.fasterxml.jackson.core"   %  "jackson-databind"     % "2.17.2",
      "com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.17.2",
      
      // ENVIRONMENTS DE PRUEBAS UNITARIAS
      "org.scalatest"    %% "scalatest"             % "3.2.15" % Test,
      "org.apache.flink"  % "flink-test-utils"       % "1.18.1" % Test
    )
  )


// ==============================================================================
// 3. COMPUERTA DE INGESTA FACTORÍA DE AKKA HTTP (CUSTOM-API ADAPTADA)
// ==============================================================================
lazy val customApi = (project in file("custom-api"))
  .enablePlugins(AssemblyPlugin)
  .settings(
    name := "custom-api",
    
    Compile / mainClass := Some("com.orchestra.ado.custom.AkkaGatewayApp"),
    
    assembly / assemblyOutputPath := {
      val targetDir = baseDirectory.value / ".." / "target" / "artifacts"
      IO.createDirectory(targetDir)
      targetDir / "custom-api.jar"
    },
    
    assembly / assemblyMergeStrategy := {
      case "reference.conf" => MergeStrategy.concat
      case "application.conf" => MergeStrategy.concat
      case PathList("META-INF", "services", xs @ _*) => MergeStrategy.concat
      case PathList("META-INF", xs @ _*) => MergeStrategy.discard
      case _ => MergeStrategy.first
    },
    
    libraryDependencies ++= Seq(
      "com.typesafe.akka" %% "akka-actor"     % "2.6.20",
      "com.typesafe.akka" %% "akka-stream"    % "2.6.20",
      "com.typesafe.akka" %% "akka-http"      % "10.2.10",
      "com.typesafe"       % "config"          % "1.4.2",
      "org.apache.pulsar"  % "pulsar-client"   % "3.1.0",
      "ch.qos.logback"     % "logback-classic" % "1.4.12" force()
    )
  )