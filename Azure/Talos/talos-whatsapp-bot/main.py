from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Mi API con Granian",
    description="Interfaz de desarrollo activa"
)

# Definimos la estructura del mensaje que vamos a recibir
class Mensaje(BaseModel):
    saludo: str

# Endpoint GET actual
@app.get("/")
def read_root():
    return {"status": "Servidor corriendo en Granian con Rust"}

# NUEVO: Endpoint POST para recibir y procesar tu simulación
@app.post("/")
def recibir_mensaje(data: Mensaje):
    # Aquí puedes procesar el saludo recibido
    return {
        "status": "Mensaje recibido con éxito",
        "tu_mensaje_fue": data.saludo
    }
