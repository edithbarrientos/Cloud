/**
 * 🪐 COMPLEMENTOS DE COMPILACIÓN DISTRIBUIDA (SBT PLUGINS)
 * Define las herramientas de infraestructura necesarias para el empaquetado,
 * sombreado de dependencias y ensamble del Fat JAR del submódulo Flink.
 */

// Plugin oficial para la generación de archivos binarios consolidados (Fat JARs)
addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "2.1.5")
