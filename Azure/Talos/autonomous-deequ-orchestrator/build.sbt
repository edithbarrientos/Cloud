ThisBuild / organization := "com.orchestra.ado"
ThisBuild / version      := "4.0.0"
ThisBuild / scalaVersion := "2.12.18"

val sparkVersion = "3.5.0"

lazy val coreModels = (project in file("core-models"))
  .settings(
    name := "core-models",
    libraryDependencies ++= Seq(
      "com.lihaoyi" %% "upickle" % "3.1.0",
      "com.lihaoyi" %% "ujson"   % "3.1.0"
    )
  )

lazy val sparkRuntime = (project in file("spark-runtime"))
  .dependsOn(coreModels)
  .settings(
    name := "spark-runtime",
    libraryDependencies ++= Seq(
      "org.apache.spark"   %% "spark-core"              % sparkVersion % "provided",
      "org.apache.spark"   %% "spark-sql"               % sparkVersion % "provided",
      "io.delta"           %% "delta-spark"             % "3.0.0",
      "com.microsoft.azure" % "azure-eventhubs-spark_2.12" % "2.3.22",
      "org.apache.spark"   %% "spark-sql-kafka-0-10"           % sparkVersion,
      "javax.mail"          % "javax.mail-api"          % "1.6.2",
      "com.sun.mail"        % "javax.mail"              % "1.6.2",
      "com.softwaremill.sttp.client3" %% "core"          % "3.8.15",
      "redis.clients"       % "jedis"                   % "5.1.0"
    ),
    assembly / assemblyMergeStrategy := {
      case PathList("META-INF", xs @ _*) => MergeStrategy.discard
      case x if x.endsWith("module-info.class") => MergeStrategy.discard
      case _ => MergeStrategy.first
    }
  )

lazy val root = (project in file("."))
  .aggregate(coreModels, sparkRuntime)
  .dependsOn(sparkRuntime)
  .settings(
    name := "autonomous-deequ-orchestrator"
  )
