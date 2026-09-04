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
// 🪐 1. MÓDULO AGREGADOR MAESTRO (MONOREPO ROOT)
// ==============================================================================
lazy val root = (project in file("."))
  .aggregate(coreModels, gatewayApi, flinkRuntime, sparkRuntime, customApi)
  .settings(name := "ai-deequ-orchestrator")


// ==============================================================================
// 🪐 2. CONTRATOS BINARIOS CENTRALIZADOS (AUTOGENERACIÓN SCALAPB)
// ==============================================================================
lazy val coreModels = (project in file("core-models"))
  .settings(
    name := "core-models",
    Compile / PB.targets := Seq(
      scalapb.gen(flatPackage = true) -> (Compile / sourceManaged).value / "scalapb"
    ),
    libraryDependencies ++= Seq(
      "com.lihaoyi" %% "upickle" % "3.1.3",
      "com.thesamet.scalapb" %% "scalapb-runtime" % scalapb.compiler.Version.scalapbVersion % "protobuf",
      "com.thesamet.scalapb" %% "scalapb-runtime-grpc" % scalapb.compiler.Version.scalapbVersion
    )
  )


// ==============================================================================
// 🪐 3. PERIMETRAL DE RED HISTÓRICO (GATEWAY-API)
// ==============================================================================
lazy val gatewayApi = (project in file("gateway-api"))
  .dependsOn(coreModels)
  .enablePlugins(AssemblyPlugin)
  .settings(
    name := "gateway-api",
    assembly / assemblyOutputPath := {
      val targetDir = baseDirectory.value / ".." / "target" / "artifacts"
      IO.createDirectory(targetDir) 
      targetDir / "gateway-api.jar"
    },
    assembly / assemblyMergeStrategy := {
      case "reference.conf" => MergeStrategy.concat
      case "application.conf" => MergeStrategy.concat
      case PathList("META-INF", "services", xs @ _*) => MergeStrategy.concat
      case PathList("META-INF", xs @ _*) => MergeStrategy.discard
      case _ => MergeStrategy.first
    },
    libraryDependencies ++= Seq(
      "com.typesafe.akka" %% "akka-actor-typed" % "2.6.20",
      "com.typesafe.akka" %% "akka-stream"      % "2.6.20",
      "com.typesafe.akka" %% "akka-http"        % "10.2.10",
      "com.typesafe"       % "config"           % "1.4.2",
      "org.apache.pulsar"  % "pulsar-client"    % "3.0.0",
      "ch.qos.logback"     % "logback-classic"  % "1.4.12" force()
    )
  )


// ==============================================================================
// 🪐 4. ORQUESTADOR DE STREAMING DE ALTA DISPONIBILIDAD (FLINK-RUNTIME)
// ==============================================================================
lazy val flinkRuntime = (project in file("flink-runtime"))
  .dependsOn(coreModels)
  .enablePlugins(AssemblyPlugin)
  .settings(
    name := "flink-runtime",
    assembly / assemblyOutputPath := {
      val targetDir = baseDirectory.value / ".." / "target" / "artifacts"
      IO.createDirectory(targetDir)
      targetDir / "flink-stream-agent.jar"
    },
    assembly / assemblyMergeStrategy := {
      case "reference.conf" => MergeStrategy.concat
      case "application.conf" => MergeStrategy.concat
      case PathList("META-INF", "services", xs @ _*) => MergeStrategy.concat
      case PathList("META-INF", xs @ _*) => MergeStrategy.discard
      case _ => MergeStrategy.first
    },
    libraryDependencies ++= Seq(
      "org.apache.flink" %% "flink-scala"          % "1.18.1" % "provided",
      "org.apache.flink" %% "flink-streaming-scala" % "1.18.1" % "provided",
      "org.apache.flink"  % "flink-clients"         % "1.18.1" % "provided",
      "org.apache.flink"  % "flink-connector-base"   % "1.18.1" % "provided",
      "org.apache.flink"  % "flink-connector-pulsar" % "4.1.0-1.18",
      "com.typesafe"       % "config"                 % "1.4.2",
      "com.thesamet.scalapb" %% "scalapb-runtime" % "0.11.13",
      "com.fasterxml.jackson.core"   %  "jackson-databind"     % "2.17.2",
      "com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.17.2"
    )
  )


// ==============================================================================
// 🪐 5. PROCESADOR ANALÍTICO DISTRIBUIDO HISTÓRICO (SPARK-RUNTIME)
// ==============================================================================
lazy val sparkRuntime = (project in file("spark-runtime"))
  .dependsOn(coreModels)
  .enablePlugins(AssemblyPlugin)
  .settings(
    name := "spark-runtime",
    assembly / assemblyOutputPath := {
      val targetDir = baseDirectory.value / ".." / "target" / "artifacts"
      IO.createDirectory(targetDir)
      targetDir / "spark-engine.jar"
    },
    assembly / assemblyMergeStrategy := {
      case PathList("META-INF", "services", xs @ _*) => MergeStrategy.concat
      case PathList("META-INF", xs @ _*) => MergeStrategy.discard
      case _ => MergeStrategy.first
    },
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-core" % "3.5.0" % "provided",
      "org.apache.spark" %% "spark-sql"  % "3.5.0" % "provided",
      "redis.clients"     % "jedis"      % "5.0.2"
    )
  )


// ==============================================================================
// 🪐 6. COMPUERTA DE INGESTA FACTORÍA MEJORADA (CUSTOM-API)
// ==============================================================================
lazy val customApi = (project in file("custom-api"))
  .dependsOn(coreModels)
  .enablePlugins(AssemblyPlugin)
  .settings(
    name := "custom-api",
    
    // 🚀 MEJORA DE ARQUITECTURA: Declaramos formalmente la nueva clase principal
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
      "com.typesafe"       % "config"          % "1.4.2", // Inyectado para Typesafe Config
      "org.apache.pulsar"  % "pulsar-client"   % "3.1.0", // Inyectado para Fan-Out distribuidor
      "ch.qos.logback"     % "logback-classic" % "1.4.12" force()
    )
  )
