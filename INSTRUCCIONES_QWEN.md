# Módulos Qwen para Odoo LLM - Instrucciones de Uso

## Resumen

He creado el módulo **llm_qwen** que soporta BOTH:
1. ✅ **Modelos locales de Qwen** (vLLM, Ollama con API compatible OpenAI)
2. ✅ **Modelos grandes de Qwen en la nube** (Alibaba Cloud DashScope)

El módulo es compatible con **Odoo 16, 17 y 18**.

---

## 📁 Estructura del Módulo Creado

```
/workspace/llm_qwen/
├── __init__.py
├── __manifest__.py
├── README.md
├── changelog.rst
├── pyproject.toml
├── data/
│   ├── llm_model.xml       # Modelos preconfigurados
│   ├── llm_provider.xml    # Proveedores (cloud y local)
│   └── llm_publisher.xml   # Información del publisher
├── models/
│   ├── __init__.py
│   ├── mail_message.py     # Formato de mensajes
│   └── qwen_provider.py    # Implementación principal
└── static/description/
    ├── banner.jpeg
    └── qwen_logo.png
```

---

## 🚀 Instalación

### Paso 1: Instalar dependencia Python

```bash
pip install openai
```

### Paso 2: Copiar el módulo a tu instancia Odoo

```bash
cp -r /workspace/llm_qwen /ruta/a/tu/odoo/addons/
```

### Paso 3: Actualizar lista de aplicaciones en Odoo

1. Ir a **Ajustes → Aplicaciones**
2. Click en **Actualizar lista de aplicaciones**
3. Buscar "Qwen"
4. Instalar **"Qwen LLM Integration"**

---

## ⚙️ Configuración

### Opción A: Usar Qwen en la NUBE (Modelos Grandes)

**Recomendado para:** Producción, modelos más potentes (qwen-max, qwen-plus)

#### 1. Obtener API Key de Alibaba Cloud

1. Crear cuenta en: https://www.aliyun.com/
2. Ir a DashScope Console: https://dashscope.console.aliyun.com/apiKey
3. Generar una API Key
4. **¡Importante!** Regístrate para obtener créditos gratuitos iniciales

#### 2. Configurar en Odoo

1. Ir a **LLM → Providers**
2. Editar **"Qwen Cloud (DashScope)"**
3. Pegar tu API Key en el campo **API Key**
4. El API Base ya está configurado: `https://dashscope.aliyuncs.com/compatible-mode/v1`
5. Guardar
6. Activar los modelos que quieras usar en **LLM → Models**

#### Modelos Cloud Disponibles:

| Modelo | Uso | Descripción |
|--------|-----|-------------|
| `qwen-max` | Chat (Default) | Modelo más potente |
| `qwen-plus` | Chat | Balance entre rendimiento y costo |
| `qwen-turbo` | Chat | Rápido y económico |
| `qwen-vl-max` | Chat | Multimodal (imágenes + texto) |
| `text-embedding-v3` | Embedding | Para búsquedas semánticas |

---

### Opción B: Usar Qwen LOCAL (Modelos en tu Servidor)

**Recomendado para:** Desarrollo, privacidad total, sin costos de API

#### Método 1: Con vLLM (Recomendado para producción local)

##### 1. Instalar vLLM

```bash
pip install vllm
```

##### 2. Descargar e iniciar un modelo Qwen

```bash
# Ejemplo con Qwen2.5-7B (requiere ~14GB RAM/VRAM)
python -m vllm.entrypoints.openai_api_server \
    --model Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000
```

**Otros modelos disponibles:**
- `Qwen/Qwen2.5-14B-Instruct` (~28GB)
- `Qwen/Qwen2.5-32B-Instruct` (~64GB)
- `Qwen/Qwen2.5-72B-Instruct` (~144GB, requiere múltiples GPUs)

##### 3. Configurar en Odoo

1. Ir a **LLM → Providers**
2. Editar **"Qwen Local"**
3. Activar el provider (checkbox **Active**)
4. Configurar **API Base**: `http://localhost:8000/v1`
5. Configurar **API Key**: `not-needed`
6. Guardar
7. Ir a **LLM → Models** y activar los modelos locales que quieras usar

#### Método 2: Con Ollama (Más fácil para desarrollo)

##### 1. Instalar Ollama

```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Descargar desde https://ollama.ai/download
```

##### 2. Descargar modelo Qwen

```bash
ollama pull qwen2.5:7b
```

##### 3. Iniciar Ollama (si no está corriendo)

```bash
ollama serve
```

##### 4. Configurar en Odoo

1. Ir a **LLM → Providers**
2. Editar **"Qwen Local"**
3. Activar el provider
4. Configurar **API Base**: `http://localhost:11434/v1`
5. Configurar **API Key**: `not-needed`
6. Guardar

**Nota:** También puedes usar el módulo `llm_ollama` existente si prefieres integración nativa con Ollama.

#### Modelos Locales Preconfigurados:

| Modelo | VRAM Requerida | Uso Recomendado |
|--------|----------------|-----------------|
| `qwen2.5:7b` | ~14GB | Desarrollo, testing |
| `qwen2.5:14b` | ~28GB | Producción ligera |
| `qwen2.5:32b` | ~64GB | Producción media |
| `qwen2.5:72b` | ~144GB | Producción pesada (multi-GPU) |

---

## 🧪 Pruebas y Verificación

### 1. Verificar conexión al proveedor

```python
# En la consola de Odoo (shell)
provider = env['llm.provider'].search([('service', '=', 'qwen')], limit=1)
print(f"Provider: {provider.name}")
print(f"Service: {provider.service}")
print(f"API Base: {provider.api_base}")
```

### 2. Listar modelos disponibles

```python
provider = env['llm.provider'].search([('service', '=', 'qwen'), ('active', '=', True)], limit=1)
models = provider.list_models()
for model in models:
    print(f"Model: {model['name']}")
```

### 3. Probar chat simple

```python
from odoo import api, SUPERUSER_ID

with api.Environment.manage():
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        provider = env['llm.provider'].search([('service', '=', 'qwen'), ('active', '=', True)], limit=1)
        model = env['llm.model'].search([('provider_id', '=', provider.id), ('default', '=', True)], limit=1)
        
        messages = [
            {"role": "user", "content": "Hola, ¿cómo estás?"}
        ]
        
        response = provider.chat(messages, model=model)
        for chunk in response:
            print(chunk.get('content', ''), end='')
```

### 4. Probar desde la interfaz de Odoo

1. Ir a **LLM → Threads**
2. Crear nuevo thread
3. Seleccionar un modelo Qwen
4. Enviar mensaje de prueba

---

## 🔧 Solución de Problemas

### Error: "Connection refused"

**Causa:** El servidor local no está corriendo o el puerto es incorrecto

**Solución:**
```bash
# Verificar si vLLM/Ollama está corriendo
netstat -tlnp | grep 8000  # Para vLLM
netstat -tlnp | grep 11434 # Para Ollama

# Reiniciar el servidor
# vLLM: Volver a ejecutar el comando de inicio
# Ollama: ollama serve
```

### Error: "Invalid API key"

**Causa:** API Key incorrecta o sin créditos

**Solución:**
1. Verificar API Key en DashScope Console
2. Verificar que hay créditos disponibles
3. Regenerar API Key si es necesario

### Error: "Model not found"

**Causa:** El modelo no está disponible en el proveedor

**Solución:**
- **Cloud:** Verificar modelos disponibles en https://dashscope.console.aliyun.com/models
- **Local:** Listar modelos cargados:
  ```bash
  # vLLM
  curl http://localhost:8000/v1/models
  
  # Ollama
  ollama list
  ```

### Error: "Out of memory" (local)

**Causa:** El modelo es muy grande para tu hardware

**Solución:**
1. Usar un modelo más pequeño (ej. 7b en lugar de 72b)
2. Usar cuantización (ej. `qwen2.5:7b-q4_K_M` en Ollama)
3. Añadir más RAM/VRAM

---

## 📊 Comparativa: Cloud vs Local

| Característica | Cloud (DashScope) | Local (vLLM/Ollama) |
|----------------|-------------------|---------------------|
| **Costo** | Pay-per-use | Gratis (solo hardware) |
| **Potencia** | Máxima (qwen-max) | Depende de tu hardware |
| **Privacidad** | Datos en Alibaba Cloud | 100% local |
| **Latencia** | ~200-500ms | ~50-200ms (local) |
| **Setup** | Fácil (solo API key) | Requiere configuración |
| **Escalabilidad** | Automática | Limitada por hardware |
| **Recomendado para** | Producción, modelos grandes | Dev, privacy, testing |

---

## 💡 Mejores Prácticas

### Para Producción

1. **Usar Cloud** para modelos grandes (qwen-max, qwen-plus)
2. **Configurar rate limiting** para evitar costos inesperados
3. **Monitorear uso** en DashScope Console
4. **Tener fallback** a otro proveedor si es crítico

### Para Desarrollo

1. **Usar Local** con modelos pequeños (7b, 14b)
2. **vLLM** para mejor rendimiento que Ollama
3. **Probar en local** antes de desplegar a cloud
4. **Usar quantization** para reducir requerimientos

### Híbrido (Recomendado)

1. **Desarrollo/Testing:** Local con qwen2.5:7b
2. **Staging:** Local con qwen2.5:32b o Cloud con qwen-turbo
3. **Producción:** Cloud con qwen-max/qwen-plus

---

## 📚 Recursos Adicionales

- **Documentación oficial Qwen:** https://help.aliyun.com/zh/dashscope/
- **GitHub Qwen:** https://github.com/QwenLM/Qwen
- **Hugging Face Qwen:** https://huggingface.co/Qwen
- **vLLM Docs:** https://docs.vllm.ai/
- **Ollama Docs:** https://github.com/ollama/ollama

---

## ✅ Checklist de Verificación

Después de instalar y configurar, verifica:

- [ ] Módulo instalado sin errores
- [ ] Provider "Qwen Cloud" o "Qwen Local" aparece en LLM → Providers
- [ ] Provider está activo
- [ ] API Base configurado correctamente
- [ ] API Key configurado (solo cloud)
- [ ] Modelos aparecen en LLM → Models
- [ ] Al menos un modelo está activo y marcado como default
- [ ] Test de chat funciona desde la consola de Odoo
- [ ] Test de chat funciona desde LLM → Threads

---

## 🎯 Siguientes Pasos

Una vez verificado el funcionamiento:

1. **Configurar Knowledge Base** para usar Qwen con RAG
2. **Crear Tools** personalizados para function calling
3. **Integrar con Asistentes** existentes
4. **Configurar automatizaciones** con LLM Automation

---

**¡Listo!** Ya puedes usar modelos Qwen tanto locales como en la nube en tu Odoo.

Si tienes preguntas o problemas, revisa la sección de "Solución de Problemas" o consulta los logs de Odoo (`--log-level=debug` para más detalle).
