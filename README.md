# AI API — Instalación y Uso

Instrucciones para configurar y ejecutar el script `ai_api.py` que utiliza la API de Google Gemini.

---

## Requisitos

* Python 3.x
* `pip`
* Archivo `requirements.txt` en la raíz del proyecto

---

## 1. Crear y Activar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows (CMD):
venv\Scripts\activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

---

## 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Configurar API Key de Google Gemini

Crea un archivo `.env` en la raíz del proyecto y agrega tu API Key:

```env
GEMINI_API_KEY=tu_api_key_aqui_google_gemini
```

> **Nota:** Mantén tu `.env` fuera del control de versiones (añádelo a `.gitignore`).

---

## 4. Preparar Archivo de Preguntas

Crea un archivo `questions.json` con tus preguntas. Ejemplo:

```json
[
  {
    "question": "¿Cuáles son las mejores prácticas para el desarrollo de software?",
    "context": "Metodologías ágiles",
    "max_tokens": 200
  },
  {
    "question": "Explica qué es la inteligencia artificial",
    "context": "Para audiencia no técnica",
    "max_tokens": 150
  }
]
```

---

## Uso del Script

### Ejecutar el Script Principal

```bash
python ai_api.py
```

---

## Consejos útiles

* Si usas **PowerShell** y hay restricciones de ejecución, podrías necesitar ejecutar `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` (ejecutar PowerShell como administrador).
* Verifica que la variable `GEMINI_API_KEY` esté bien escrita en `.env` y que el script lea variables de entorno (por ejemplo usando `python-dotenv`).

---

Si quieres, puedo añadir una sección de *Descripción del proyecto*, *Cómo contribuir* o generar directamente un archivo descargable `.md` listo para subir al repositorio.
