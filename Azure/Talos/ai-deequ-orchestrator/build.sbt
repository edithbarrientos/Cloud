import sbtassembly.AssemblyPlugin.autoImport._
import sbtassembly.{MergeStrategy, PathList}

ThisBuild / version      := "4.0.0"
ThisBuild / scalaVersion := "2.12.18"

ThisBuild / scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-encoding", "utf-8"
)

// MÓDULO AGREGADOR MAESTRO
lazy val root = (project in file("."))
  .aggregate(coreModels, gatewayApi, flinkRuntime, sparkRuntime)
  .settings(name := "ai-deequ-orchestrator")

// MÓDULO 1: CORE MODELS (Contratos Base Inmutables)
lazy val coreModels = (project in file("core-models"))
  .settings(
    name := "core-models",
    libraryDependencies ++= Seq(
      "com.lihaoyi" %% "upickle" % "3.1.3",
      "org.scalatest" %% "scalatest" % "3.2.15" % Test
    )
  )

// MÓDULO 2: GATEWAY API (Akka gRPC Server)
lazy val gatewayApi = (project in file("gateway-api"))
  .dependsOn(coreModels)
  .enablePlugins(AkkaGrpcPlugin, AssemblyPlugin)
  .settings(
    name := "gateway-api",
    // 🟢 CORE FIX AUTOFUNDANTE: Obliga a la JVM a fundar la carpeta artifacts si no existe antes de escribir el jar
    assembly / assemblyOutputPath := {
      val targetDir = baseDirectory.value / ".." / "target" / "artifacts"
      IO.createDirectory(targetDir) 
      targetDir / "gateway-api.jar"
    },
    assembly / assemblyMergeStrategy := {
      case PathList("META-INF", "versions", xs @ _*) => MergeStrategy.first
      case PathList("META-INF", xs @ _*) =>
        xs.map(_.toLowerCase) match {
          case "manifest.mf" :: Nil | "index.list" :: Nil | "dependencies.list" :: Nil => MergeStrategy.discard
          case "io.netty.versions.properties" :: Nil => MergeStrategy.first
          case ps if ps.last.endsWith(".sf") || ps.last.endsWith(".dsa") || ps.last.endsWith(".rsa") => MergeStrategy.discard
          case _ => MergeStrategy.first
        }
      case PathList("google", "protobuf", xs @ _*) => MergeStrategy.first
      case "findbugsExclude.xml" => MergeStrategy.discard
      case _ => MergeStrategy.first
    },
    libraryDependencies ++= Seq(
      "com.typesafe" % "config" % "1.4.2",
      "org.apache.pulsar" % "pulsar-client" % "3.0.0",
      "org.scalatest" %% "scalatest" % "3.2.15" % Test
    )
  )

// MÓDULO 3: FLINK RUNTIME (Stream Plane Continuo)
lazy val flinkRuntime = (project in file("flink-runtime"))
  .dependsOn(coreModels)
  .enablePlugins(AkkaGrpcPlugin, AssemblyPlugin)
  .settings(
    name := "flink-runtime",
    // 🟢 CORE FIX AUTOFUNDANTE
    assembly / assemblyOutputPath := {
      val targetDir = baseDirectory.value / ".." / "target" / "artifacts"
      IO.createDirectory(targetDir)
      targetDir / "flink-stream-agent.jar"
    },
    assembly / assemblyMergeStrategy := {
      case PathList("META-INF", "versions", xs @ _*) => MergeStrategy.first
      case PathList("META-INF", xs @ _*) =>
        xs.map(_.toLowerCase) match {
          case "manifest.mf" :: Nil | "index.list" :: Nil | "dependencies.list" :: Nil => MergeStrategy.discard
          case "io.netty.versions.properties" :: Nil => MergeStrategy.first
          case ps if ps.last.endsWith(".sf") || ps.last.endsWith(".dsa") || ps.last.endsWith(".rsa") => MergeStrategy.discard
          case _ => MergeStrategy.first
        }
      case PathList("google", "protobuf", xs @ _*) => MergeStrategy.first
      case "findbugsExclude.xml" => MergeStrategy.discard
      case _ => MergeStrategy.first
    },
    libraryDependencies ++= Seq(
      "org.apache.flink" %% "flink-scala" % "1.18.1" % "provided",
      "org.apache.flink" %% "flink-streaming-scala" % "1.18.1" % "provided",
      "com.typesafe" % "config" % "1.4.2",
      "org.apache.flink" % "flink-connector-pulsar" % "4.1.0-1.18",
      "org.scalatest" %% "scalatest" % "3.2.15" % Test
    )
  )

// MÓDULO 4: SPARK RUNTIME (Data Plane Batch Analítico)
lazy val sparkRuntime = (project in file("spark-runtime"))
  .dependsOn(coreModels)
  .enablePlugins(AssemblyPlugin)
  .settings(
    name := "spark-runtime",
    // 🟢 CORE FIX AUTOFUNDANTE
    assembly / assemblyOutputPath := {
      val targetDir = baseDirectory.value / ".." / "target" / "artifacts"
      IO.createDirectory(targetDir)
      targetDir / "spark-engine.jar"
    },
    assembly / assemblyMergeStrategy := {
      case PathList("META-INF", "versions", xs @ _*) => MergeStrategy.first
      case PathList("META-INF", xs @ _*) =>
        xs.map(_.toLowerCase) match {
          case "manifest.mf" :: Nil | "index.list" :: Nil | "dependencies.list" :: Nil => MergeStrategy.discard
          case "io.netty.versions.properties" :: Nil => MergeStrategy.first
          case ps if ps.last.endsWith(".sf") || ps.last.endsWith(".dsa") || ps.last.endsWith(".rsa") => MergeStrategy.discard
          case _ => MergeStrategy.first
        }
      case PathList("google", "protobuf", xs @ _*) => MergeStrategy.first
      case "findbugsExclude.xml" => MergeStrategy.discard
      case _ => MergeStrategy.first
    },
    libraryDependencies ++= Seq(
      "org.apache.spark" %% "spark-core" % "3.5.0" % "provided",
      "org.apache.spark" %% "spark-sql" % "3.5.0" % "provided",
      "redis.clients" % "jedis" % "5.0.2",
      "org.scalatest" %% "scalatest" % "3.2.15" % Test
    )
  )
