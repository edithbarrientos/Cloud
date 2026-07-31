package com.orchestra.ado

import org.apache.spark.sql.{SparkSession, DataFrame, SaveMode}
import redis.clients.jedis.{JedisPool, JedisPoolConfig}
import org.slf4j.LoggerFactory
import com.orchestra.ado.quality.{RulesFactory, RuleDefinition, AiStorageOptimizer}
import java.io.File
import scala.io.Source
import java.util.Properties
import java.time.Instant
import java.util.logging.{Logger => JLogger, FileHandler, SimpleFormatter}
import javax.mail._
import javax.mail.internet._
import javax.activation._
import scala.util.{Try, Success, Failure}

case class UniversalAuditRecord(
  timestamp: String,
  tenant_id: String,
  execution_id: String,
  component_name: String,
  log_level: String,
  action_performed: String,
  status: String,
  payload_telemetry: String
)

object Main {
  private val logger = LoggerFactory.getLogger("ADO-Main-Production-Tier1")

  private lazy val jedisPool: JedisPool = {
    val poolConfig = new JedisPoolConfig()
    poolConfig.setMaxTotal(8)
    poolConfig.setMaxIdle(4)
    new JedisPool(poolConfig, sys.env.getOrElse("REDIS_HOST", "localhost"), sys.env.getOrElse("REDIS_PORT", "6379").toInt, 2000)
  }

  def sendUniversalAuditEmail(
    smtpHost: String,
    smtpPort: String,
    emailFrom: String,
    emailPassword: String,
    emailTo: String,
    tenantId: String,
    executionId: String,
    attachmentPath: String,
    telemetry: String
  ): Unit = {
    logger.info(s"📬 [UNIVERSAL-SMTP] Intentando handshake TLS seguro con $smtpHost:$smtpPort...")
    
    val props = new Properties()
    props.put("mail.smtp.host", smtpHost)
    props.put("mail.smtp.port", smtpPort)
    props.put("mail.smtp.auth", "true")
    props.put("mail.smtp.starttls.enable", "true")
    props.put("mail.smtp.ssl.protocols", "TLSv1.2")

    val auth = new Authenticator() {
      override protected def getPasswordAuthentication: PasswordAuthentication = {
        new PasswordAuthentication(emailFrom, emailPassword)
      }
    }
    
    val session = Session.getInstance(props, auth)
    val message = new MimeMessage(session)
    message.setFrom(new InternetAddress(emailFrom))
    message.addRecipient(Message.RecipientType.TO, new InternetAddress(emailTo))
    message.setSubject(s"🛡️ [ADO-AUDIT] Consolidación de Bitácora y Traza | Tenant: $tenantId")

    val messageBodyPart = new MimeBodyPart()
    messageBodyPart.setContent(
      s"""<h2>Orchestra Data Labs - Autonomous Data Engine</h2>
         |<p>Se ha consolidado con éxito el rastro analítico del Data Plane.</p>
         |<ul>
         |  <li><b>Tenant ID:</b> $tenantId</li>
         |  <li><b>Execution ID:</b> $executionId</li>
         |  <li><b>Métricas Inferencia:</b> $telemetry</li>
         |</ul>
      """.stripMargin, "text/html"
    )

    val multipart = new MimeMultipart()
    multipart.addBodyPart(messageBodyPart)

    val file = new File(attachmentPath)
    if (file.exists()) {
      val attachPart = new MimeBodyPart()
      val source = new FileDataSource(attachmentPath)
      attachPart.setDataHandler(new DataHandler(source))
      attachPart.setFileName(file.getName)
      multipart.addBodyPart(attachPart)
    }

    message.setContent(multipart)
    Transport.send(message)
    logger.info(s"✅ [EMAIL-SUCCESS] Bitácora enviada de forma segura por correo hacia: $emailTo")
  }

  def main(args: Array[String]): Unit = {
    val isEmailOptionActive = args.contains("--send-email")
    
    val homeDir = sys.env.getOrElse("HOME", "/root")
    val targetDeltaTablePath = s"$homeDir/data_lake/metadata/universal_audit_bitacora"
    val logFilePath = s"$homeDir/spark_execution.log"
    
    val fh = new FileHandler(logFilePath, true)
    fh.setFormatter(new SimpleFormatter())
    JLogger.getLogger("").addHandler(fh)
    
    logger.info(s"🎻 [STARTUP-JVM] Inicializando ADO Core Seguro. ¿Capacidad de correo solicitada?: $isEmailOptionActive")

    val spark = SparkSession.builder()
      .appName("Autonomous-Data-Engine-ADO-Local")
      .master("local[*]")
      .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
      .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
      .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
      .getOrCreate()

    import spark.implicits._

    val contractPath = s"$homeDir/contract_test.json"
    val fileObj = new File(contractPath)

    if (fileObj.exists()) {
      val bufferedSource = Source.fromFile(fileObj)
      val jsonPayload = bufferedSource.getLines().mkString
      bufferedSource.close()

      val parsedJson = ujson.read(jsonPayload)
      val metadataBlock = parsedJson("metadata")

      // ⚡ REPARACIÓN BLINDAJE TIER-1: Se usa el método elástico .get con fallback seguro para mitigar NoSuchElementException [DAMA]
      val targetNotificationEmail = metadataBlock.obj.get("notificationEmailTo").map(_.str).getOrElse("none@orchestralabs.io")
      val tenantId = metadataBlock.obj.get("tenantId").map(_.str).getOrElse("tenant-orchestra-poc-01")
      val executionId = metadataBlock.obj.get("executionId").map(_.str).getOrElse("7c4b08e8-1f24-49b2-889e-1abd52cb510f")
      val datasetName = metadataBlock.obj.get("datasetName").map(_.str).getOrElse("Core_Transactions")

      logger.info(s"📥 [DYNAMIC-CONTRACT] Extrayendo metadatos conformes. Inquilino actual asignado: $tenantId")

      val df = Seq(("tx-001", "user1@orchestra.com", 150.50)).toDF("transaction_id", "customer_email", "amount")
      val rules = Seq(RuleDefinition("Completitud", "iscomplete", Seq("customer_email"), 0.75))

      val jedis = jedisPool.getResource
      try {
        val metrics = RulesFactory.evaluateBudget(df, rules, tenantId)
        val totalRows = df.count()
        val optimalCodec = AiStorageOptimizer.inferOptimalCodec(jedis, tenantId, datasetName, "transaction_id", totalRows)
        val metricsSummary = s"""{"total_records": $totalRows, "calculated_codec": "$optimalCodec"}"""

        logger.info(s"📤 [DATA-LAKE-PERSIST] Insertando fila relacional en la tabla Delta unificada...")
        val record = Seq(UniversalAuditRecord(
          timestamp = Instant.now().toString,
          tenant_id = tenantId,
          execution_id = executionId,
          component_name = "SPARK_ANALYTICS_ENGINE",
          log_level = "INFO",
          action_performed = "RUN_DAMA_INFERENCE_CYCLE",
          status = "SUCCESS",
          payload_telemetry = metricsSummary
        )).toDS()

        record.write.format("delta").mode(SaveMode.Append).partitionBy("tenant_id").save(targetDeltaTablePath)
        logger.info("✅ [ENGINE-SUCCESS] Registro de bitácora polimórfico guardado con éxito en el Data Lake.")
        
        fh.close()

        if (isEmailOptionActive) {
          logger.info("📡 [FEATURE-FLAG-ACTIVE] Procesando envío opcional de correo analítico...")
          val smtpHost = sys.env.getOrElse("SMTP_HOST", "://gmail.com")
          val smtpPort = sys.env.getOrElse("SMTP_PORT", "587")
          val emailFrom = sys.env.getOrElse("SMTP_USER_FROM", "ado-engine@orchestralabs.io")
          val emailPass = sys.env.getOrElse("SMTP_PASSWORD", "secret")

          Try(sendUniversalAuditEmail(smtpHost, smtpPort, emailFrom, emailPass, targetNotificationEmail, tenantId, executionId, logFilePath, metricsSummary)) match {
            case Success(_) => logger.info("📧 [NOTIFICACIÓN] Alerta electrónica entregada.")
            case Failure(e) => logger.warn(s"⚠️ [NOTIFICACIÓN-REBOTE] Correo omitido, datos salvados: ${e.getMessage}")
          }
        } else {
          logger.info("⏭️ [FEATURE-FLAG-SKIP] Capacidad de correo omitida de forma conforme.")
        }

      } catch {
        case e: Exception => 
          logger.error(s"🚨 Fallo crítico en el procesamiento: ${e.getMessage}")
          fh.close()
          val recordFail = Seq(UniversalAuditRecord(timestamp = Instant.now().toString, tenant_id = tenantId, execution_id = executionId, component_name = "SPARK_ANALYTICS_ENGINE", log_level = "FATAL", action_performed = "RUN_DAMA_INFERENCE_CYCLE", status = "FAILED", payload_telemetry = s"""{"error_message": "${e.getMessage}"}""")).toDS()
          recordFail.write.format("delta").mode(SaveMode.Append).partitionBy("tenant_id").save(targetDeltaTablePath)
      } finally {
        jedis.close()
      }
    } else {
      logger.error(s"❌ [LOCAL-ENGINE-ERROR] Manifiesto declarativo no encontrado.")
    }
    spark.stop()
    jedisPool.destroy()
  }
}
