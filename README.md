Instalación y Uso
1. Crear y Activar Entorno Virtual
bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
2. Instalar Dependencias
bash
pip install -r requirements.txt
3. Configurar API Key de Google Gemini
Crea un archivo .env en la raíz del proyecto y agrega tu API Key:

env
GEMINI_API_KEY=tu_api_key_aqui_google_gemini
4. Preparar Archivo de Preguntas
Crea un archivo questions.json con tus preguntas:

json
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
Uso del Script
Ejecutar el Script Principal
bash
python ai_api.py
