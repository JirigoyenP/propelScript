"""
GENERADOR DE RESPUESTAS IA CON GOOGLE GEMINI
============================================
Script amigable para procesar preguntas y generar respuestas usando IA
Compatible con webhooks para n8n y Zapier
"""

import json
import csv
import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import google.generativeai as genai
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint

# Cargar variables de entorno
load_dotenv()

# Inicializar consola Rich para mejor formato
console = Console()

class AIResponseGenerator:
    """Generador de respuestas usando Google Gemini."""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model_name = os.getenv('MODEL', 'gemini-1.5-flash')
        self.webhook_url = None
        self.webhook_enabled = False
        self.responses_generated = 0
        self.start_time = None
        
        # Configurar el modelo si hay API key
        if self.api_key and self.api_key != 'tu_api_key_aqui':
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
    
    def show_welcome_banner(self):
        """Muestra un banner de bienvenida atractivo."""
        banner = """
╔════════════════════════════════════════════════════════════╗
║     🤖 GENERADOR DE RESPUESTAS IA CON GOOGLE GEMINI 🤖     ║
║                                                            ║
║    Procesa preguntas automáticamente y genera respuestas  ║
║         inteligentes usando IA de última generación       ║
║                                                            ║
║         Compatible con n8n, Zapier y Make.com 🔗          ║
╚════════════════════════════════════════════════════════════╝
        """
        console.print(banner, style="bold cyan")
        time.sleep(1)
    
    def check_configuration(self) -> bool:
        """Verifica la configuración inicial."""
        console.print("\n[bold yellow]📋 Verificando configuración...[/bold yellow]")
        time.sleep(0.5)
        
        issues = []
        
        # Verificar API Key
        if not self.api_key or self.api_key == 'tu_api_key_aqui':
            issues.append("❌ API Key de Gemini no configurada")
        else:
            console.print("✅ API Key encontrada", style="green")
        
        # Verificar archivo .env
        if not os.path.exists('.env'):
            issues.append("❌ Archivo .env no encontrado")
        else:
            console.print("✅ Archivo .env encontrado", style="green")
        
        # Mostrar problemas si existen
        if issues:
            console.print("\n[bold red]⚠️  Problemas encontrados:[/bold red]")
            for issue in issues:
                console.print(f"  {issue}")
            
            console.print("\n[bold yellow]Para configurar tu API Key:[/bold yellow]")
            console.print("1. Ve a: https://makersuite.google.com/app/apikey")
            console.print("2. Crea o copia tu API key")
            console.print("3. Edita el archivo .env y reemplaza 'tu_api_key_aqui'")
            
            if Confirm.ask("\n¿Quieres continuar sin API Key? (modo demo)", default=False):
                return True
            return False
        
        console.print("\n[bold green]✅ Configuración correcta[/bold green]")
        return True
    
    def select_input_file(self) -> Optional[str]:
        """Permite al usuario seleccionar un archivo de entrada."""
        console.print("\n[bold cyan]📂 Buscando archivos de preguntas...[/bold cyan]")
        
        # Buscar archivos compatibles
        valid_extensions = ['.json', '.csv', '.txt']
        files = []
        
        for ext in valid_extensions:
            files.extend(Path('.').glob(f'*{ext}'))
        
        # Filtrar archivos de sistema y de salida
        files = [f for f in files if not str(f).startswith('.') 
                and 'respuestas' not in str(f).lower()
                and 'output' not in str(f).lower()]
        
        if not files:
            console.print("[bold red]❌ No se encontraron archivos de preguntas[/bold red]")
            console.print("\nPuedes crear archivos de ejemplo ejecutando: [bold]python quick_start.py[/bold]")
            return None
        
        # Mostrar tabla de archivos
        table = Table(title="Archivos Disponibles", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Archivo", style="cyan", width=30)
        table.add_column("Tipo", style="green")
        table.add_column("Tamaño", justify="right")
        
        for i, file_path in enumerate(files, 1):
            size = file_path.stat().st_size
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            file_type = file_path.suffix[1:].upper()
            table.add_row(str(i), str(file_path), file_type, size_str)
        
        console.print(table)
        
        # Solicitar selección
        while True:
            choice = Prompt.ask(
                "\n[bold cyan]Selecciona un archivo (número) o 'q' para salir[/bold cyan]",
                default="1"
            )
            
            if choice.lower() == 'q':
                return None
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(files):
                    selected_file = str(files[index])
                    console.print(f"\n[bold green]✅ Archivo seleccionado:[/bold green] {selected_file}")
                    return selected_file
                else:
                    console.print("[red]❌ Número inválido[/red]")
            except ValueError:
                console.print("[red]❌ Por favor ingresa un número válido[/red]")
    
    def load_questions(self, file_path: str) -> List[Dict[str, Any]]:
        """Carga las preguntas desde el archivo."""
        console.print(f"\n[bold yellow]📖 Cargando preguntas desde {file_path}...[/bold yellow]")
        
        questions = []
        file_ext = Path(file_path).suffix.lower()
        
        try:
            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'questions' in data:
                        questions = data['questions']
                    elif isinstance(data, list):
                        questions = data
                    else:
                        questions = [{"question": str(data)}]
            
            elif file_ext == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        questions.append(row)
            
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        if line:
                            questions.append({"question": line})
            
            # Normalizar estructura
            normalized = []
            for q in questions:
                if isinstance(q, str):
                    normalized.append({"question": q, "context": "", "max_tokens": 200})
                else:
                    normalized.append({
                        "question": q.get('question', ''),
                        "context": q.get('context', ''),
                        "max_tokens": int(q.get('max_tokens', 200))
                    })
            
            console.print(f"[bold green]✅ {len(normalized)} preguntas cargadas correctamente[/bold green]")
            return normalized
            
        except Exception as e:
            console.print(f"[bold red]❌ Error cargando archivo: {e}[/bold red]")
            return []
    
    def generate_response(self, question: str, context: str = "", max_tokens: int = 200) -> str:
        """Genera una respuesta usando Gemini."""
        if not self.model:
            # Modo demo sin API key
            return f"[Respuesta de demo] Esta es una respuesta simulada para: '{question}'"
        
        try:
            prompt = f"{context}\n\nPregunta: {question}\n\nRespuesta:" if context else f"Pregunta: {question}\n\nRespuesta:"
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Error generando respuesta: {e}[/yellow]")
            return f"Error al generar respuesta: {str(e)}"
    
    def process_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Procesa todas las preguntas y genera respuestas."""
        self.start_time = time.time()
        results = []
        
        console.print(f"\n[bold cyan]🚀 Procesando {len(questions)} preguntas...[/bold cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("[cyan]Generando respuestas...", total=len(questions))
            
            for i, q in enumerate(questions, 1):
                progress.update(task, description=f"[cyan]Procesando pregunta {i}/{len(questions)}...")
                
                # Generar respuesta
                response = self.generate_response(
                    q['question'],
                    q.get('context', ''),
                    q.get('max_tokens', 200)
                )
                
                # Crear resultado
                result = {
                    "pregunta": q['question'],
                    "contexto": q.get('context', ''),
                    "respuesta": response,
                    "timestamp": datetime.now().isoformat(),
                    "modelo": self.model_name
                }
                
                results.append(result)
                self.responses_generated += 1
                
                # Enviar a webhook si está habilitado
                if self.webhook_enabled and self.webhook_url:
                    self.send_to_webhook(result)
                
                progress.advance(task)
                
                # Pequeña pausa para evitar rate limiting
                if i < len(questions):
                    time.sleep(0.5)
        
        elapsed = time.time() - self.start_time
        console.print(f"\n[bold green]✅ Procesamiento completado en {elapsed:.1f} segundos[/bold green]")
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], input_file: str) -> str:
        """Guarda los resultados en un archivo."""
        # Generar nombre de archivo de salida
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = Path(input_file).stem
        output_file = f"respuestas_{base_name}_{timestamp}.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "total_preguntas": len(results),
                        "archivo_origen": input_file,
                        "fecha_procesamiento": datetime.now().isoformat(),
                        "modelo": self.model_name,
                        "webhook_activado": self.webhook_enabled
                    },
                    "respuestas": results
                }, f, ensure_ascii=False, indent=2)
            
            console.print(f"\n[bold green]💾 Resultados guardados en: {output_file}[/bold green]")
            return output_file
            
        except Exception as e:
            console.print(f"[bold red]❌ Error guardando resultados: {e}[/bold red]")
            return ""
    
    def configure_webhook(self):
        """Configura la integración con webhooks."""
        console.print("\n[bold cyan]🔗 CONFIGURACIÓN DE WEBHOOK[/bold cyan]")
        console.print("Los webhooks permiten enviar respuestas en tiempo real a:")
        console.print("  • n8n")
        console.print("  • Zapier")
        console.print("  • Make.com (Integromat)")
        console.print("  • Cualquier endpoint HTTP")
        
        if Confirm.ask("\n¿Deseas activar el webhook?", default=False):
            self.webhook_url = Prompt.ask(
                "\n[bold cyan]Ingresa la URL del webhook[/bold cyan]",
                default="https://your-n8n-instance.com/webhook/xxx"
            )
            
            # Validar URL
            if self.webhook_url and self.webhook_url.startswith('http'):
                self.webhook_enabled = True
                console.print(f"[bold green]✅ Webhook configurado: {self.webhook_url}[/bold green]")
                
                # Probar webhook
                if Confirm.ask("\n¿Quieres probar el webhook?", default=True):
                    self.test_webhook()
            else:
                console.print("[bold red]❌ URL inválida[/bold red]")
                self.webhook_enabled = False
    
    def test_webhook(self):
        """Prueba la conexión al webhook."""
        console.print("\n[yellow]🔧 Probando webhook...[/yellow]")
        
        test_data = {
            "test": True,
            "message": "Prueba de conexión desde Generador IA",
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=test_data,
                timeout=5,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201, 202, 204]:
                console.print("[bold green]✅ Webhook funcionando correctamente[/bold green]")
            else:
                console.print(f"[yellow]⚠️  Webhook respondió con código: {response.status_code}[/yellow]")
                
        except requests.exceptions.Timeout:
            console.print("[red]❌ Timeout - El webhook no respondió[/red]")
            self.webhook_enabled = False
        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Error conectando al webhook: {e}[/red]")
            self.webhook_enabled = False
    
    def send_to_webhook(self, data: Dict[str, Any]):
        """Envía datos al webhook configurado."""
        if not self.webhook_enabled or not self.webhook_url:
            return
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                timeout=3,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code not in [200, 201, 202, 204]:
                console.print(f"[yellow]⚠️  Webhook error: {response.status_code}[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]⚠️  Error enviando a webhook: {e}[/yellow]")
    
    def show_summary(self, results: List[Dict[str, Any]], output_file: str):
        """Muestra un resumen del procesamiento."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # Crear panel de resumen
        summary = f"""
[bold green]📊 RESUMEN DE PROCESAMIENTO[/bold green]

📝 Preguntas procesadas: {len(results)}
⏱️  Tiempo total: {elapsed:.1f} segundos
📁 Archivo de salida: {output_file}
🤖 Modelo usado: {self.model_name}
🔗 Webhook: {'Activado ✅' if self.webhook_enabled else 'Desactivado ❌'}
        """
        
        console.print(Panel(summary, title="Resultados", border_style="green"))
        
        # Mostrar algunas respuestas de ejemplo
        if results and Confirm.ask("\n¿Quieres ver algunas respuestas de ejemplo?", default=True):
            console.print("\n[bold cyan]📋 Primeras 3 respuestas:[/bold cyan]\n")
            
            for i, result in enumerate(results[:3], 1):
                console.print(f"[bold]Pregunta {i}:[/bold] {result['pregunta'][:100]}...")
                console.print(f"[dim]Respuesta:[/dim] {result['respuesta'][:200]}...")
                console.print("-" * 50)
    
    def run(self):
        """Ejecuta el flujo principal del generador."""
        try:
            # Mostrar banner de bienvenida
            self.show_welcome_banner()
            
            # Verificar configuración
            if not self.check_configuration():
                console.print("\n[bold red]❌ Configuración incompleta. Saliendo...[/bold red]")
                return
            
            # Seleccionar archivo
            input_file = self.select_input_file()
            if not input_file:
                console.print("\n[yellow]👋 Proceso cancelado[/yellow]")
                return
            
            # Cargar preguntas
            questions = self.load_questions(input_file)
            if not questions:
                console.print("\n[bold red]❌ No se pudieron cargar las preguntas[/bold red]")
                return
            
            # Configurar webhook
            self.configure_webhook()
            
            # Procesar preguntas
            results = self.process_questions(questions)
            
            # Guardar resultados
            output_file = self.save_results(results, input_file)
            
            # Mostrar resumen
            self.show_summary(results, output_file)
            
            # Opciones adicionales
            console.print("\n[bold cyan]🎯 SIGUIENTES PASOS:[/bold cyan]")
            console.print("1. Revisa el archivo de respuestas generado")
            console.print("2. Puedes procesarlo con n8n, Zapier o tu herramienta favorita")
            console.print("3. Ejecuta el script nuevamente para procesar más preguntas")
            
            if self.webhook_enabled:
                console.print("\n[green]✅ Las respuestas también fueron enviadas al webhook configurado[/green]")
            
        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠️  Proceso interrumpido por el usuario[/yellow]")
        except Exception as e:
            console.print(f"\n[bold red]❌ Error inesperado: {e}[/bold red]")
            import traceback
            if Confirm.ask("¿Mostrar detalles del error?", default=False):
                console.print(traceback.format_exc())

def main():
    """Función principal."""
    generator = AIResponseGenerator()
    generator.run()

if __name__ == "__main__":
    main()