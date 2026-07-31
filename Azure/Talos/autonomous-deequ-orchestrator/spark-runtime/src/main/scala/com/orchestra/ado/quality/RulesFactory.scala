package com.orchestra.ado.quality

import org.apache.spark.sql.{DataFrame, functions => F}
import redis.clients.jedis.Jedis
import org.slf4j.LoggerFactory

/**
 * Entidades de Caso de Uso DAMA-DMBOK2 para el Data Plane de Orchestra Labs
 */
case class RuleDefinition(damaDimension: String, ruleName: String, columns: Seq[String], threshold: Double)
case class EvaluationMetrics(dimension: String, rule: String, targetColumn: String, score: Double, passed: Boolean)

object RulesFactory {
  private val logger = LoggerFactory.getLogger("ADO-RulesFactory-Tier1")

  /**
   * Ejecuta perfiles analíticos masivos y agregaciones funcionales nativas sobre la RAM distributiva
   * integrando aprendizaje histórico de cardinalidad a través de la capa cognitiva de Redis.
   */
  def evaluateBudget(df: DataFrame, rules: Seq[RuleDefinition], tenantId: String): Seq[EvaluationMetrics] = {
    logger.info(s"🛡️ [JVM-CORE-ENGINE] Inicializando auditoría analítica para el Tenant: $tenantId")
    val totalRecords = df.count()
    
    if (totalRecords == 0) {
      logger.warn(s"⚠️ [CORE-EMPTY] Lote analítico con 0 registros detectado bajo el tenant: $tenantId")
      return Seq.empty
    }

    val jedis = new Jedis("localhost", 6379)

    val metrics = rules.flatMap { rule =>
      rule.ruleName.toLowerCase match {
        
        case "iscomplete" =>
          rule.columns.map { colName =>
            val nullCount = df.filter(F.col(colName).isNull || F.col(colName) === "").count()
            val validCount = totalRecords - nullCount
            val completenessScore = validCount.toDouble / totalRecords.toDouble
            val isPassed = completenessScore >= rule.threshold
            
            logger.info(s"📊 [DAMA-COMPLETITUD] Atributo: $colName | Score: $completenessScore")
            EvaluationMetrics("Completitud", rule.ruleName, colName, completenessScore, isPassed)
          }

        case "isunique" =>
          rule.columns.map { colName =>
            val distinctCount = df.select(colName).distinct().count()
            val uniquenessScore = distinctCount.toDouble / totalRecords.toDouble
            val isPassed = uniquenessScore >= rule.threshold
            
            // Inyección en caliente de metadatos de cardinalidad en Redis
            jedis.set(s"ado:profile:$tenantId:$colName:cardinality", distinctCount.toString)
            
            logger.info(s"📊 [DAMA-UNICIDAD] Atributo: $colName | Score: $uniquenessScore")
            EvaluationMetrics("Unicidad", rule.ruleName, colName, uniquenessScore, isPassed)
          }

        case "isconsistent" =>
          rule.columns.map { colName =>
            val matchingRecords = df.filter(F.col(colName).isNotNull).count()
            val consistencyScore = matchingRecords.toDouble / totalRecords.toDouble
            val isPassed = consistencyScore >= rule.threshold
            
            EvaluationMetrics("Consistencia", rule.ruleName, colName, consistencyScore, isPassed)
          }

        case _ => 
          Seq.empty
      }
    }

    jedis.close()
    metrics
  }
}
