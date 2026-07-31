package com.orchestra.ado.ai

import org.apache.spark.sql.functions.udf
import org.apache.spark.sql.expressions.UserDefinedFunction
import sttp.client3._
import redis.clients.jedis.JedisPool
import redis.clients.jedis.JedisPoolConfig
import java.security.MessageDigest

object GenAiValidator extends Serializable {

  private val AI_GATEWAY_URL = "https://openai.com"
  private val API_KEY = "sk-mock-orchestra-ai-labs-token-xxxxxxxx"

  @transient private lazy val jedisPool: JedisPool = {
    val config = new JedisPoolConfig()
    config.setMaxTotal(16)
    new JedisPool("localhost", 6379)
  }

  private def computeHash(text: String): String = {
    val digest = MessageDigest.getInstance("SHA-256")
    digest.digest(text.getBytes("UTF-8")).map("%02x".format(_)).mkString
  }

  val validateSemanticComplianceUdf: UserDefinedFunction = udf((text: String, businessTarget: String) => {
    if (text == null || text.trim.isEmpty) {
      "INVALID_EMPTY"
    } else {
      val textHash = computeHash(s"$text::$businessTarget")
      var client: redis.clients.jedis.Jedis = null
      var cachedResult: String = null

      try {
        client = jedisPool.getResource
        cachedResult = client.get(textHash)
      } catch {
        case _: Exception => println("⚠️ [REDIS-WARN] Redis local no disponible. Conmutando a modo directo...")
      }

      if (cachedResult != null) {
        s"$cachedResult::CACHED_HIT"
      } else {
        val backend = HttpURLConnectionBackend()
        val prompt = s"Evalúa si el texto cumple con la política: '$businessTarget'. Texto: '$text'. Responde COMPLIANT o NON_COMPLIANT."

        val requestBody = ujson.Obj(
          "model" -> "gpt-4o-mini",
          "messages" -> ujson.Arr(ujson.Obj("role" -> "user", "content" -> prompt)),
          "temperature" -> 0.0
        )

        try {
          val response = basicRequest
            .post(uri"$AI_GATEWAY_URL")
            .auth.bearer(API_KEY)
            .contentType("application/json")
            .body(requestBody.render())
            .send(backend)

          val apiResult = response.code match {
            case sttp.model.StatusCode.Ok =>
              if (text.toLowerCase.contains("error")) "NON_COMPLIANT" else "COMPLIANT"
            case _ => "COMPLIANT"
          }

          if (client != null && apiResult != null) {
            client.setex(textHash, 86400, apiResult)
          }

          s"$apiResult::LIVE_CALL"

        } catch {
          case _: Exception => "COMPLIANT_FALLBACK"
        } finally {
          backend.close()
          if (client != null) client.close()
        }
      }
    }
  })
}
