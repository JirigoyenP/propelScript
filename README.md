# Instalación y Uso

## 1. Crear y Activar Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
2. Instalar Dependencias
bash
Copiar código
pip install -r requirements.txt
3. Configurar API Key de Google Gemini
Crea un archivo .env en la raíz del proyecto y agrega tu API Key:

env
Copiar código
GEMINI_API_KEY=tu_api_key_aqui_google_gemini

Uso del Script
Ejecutar el Script Principal
bash
Copiar código
python ai_api.py
arduino
Copiar código
