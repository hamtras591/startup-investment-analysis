# 📋 Guía de Configuración

## 🎯 Archivo: `project_config.json`

Este archivo contiene toda la configuración del proyecto. **NO es necesario tocar código Python** para cambiar rutas o archivos.

---

## 📝 Cómo Editar

### ✅ Ejemplo 1: Agregar un Nuevo Archivo de Entrada

Si tienes un archivo `nuevos_datos.csv` en `data/raw/`:
```json
"input_files": {
  "startups": "crunchbase_startups.csv",
  "mis_datos": "nuevos_datos.csv"    ← AGREGAR AQUÍ
}
```

### ✅ Ejemplo 2: Agregar un Dataset de Kaggle

Para descargar un nuevo dataset:

1. Ve al dataset en Kaggle (ej: https://www.kaggle.com/datasets/usuario/nombre)
2. Copia el identificador: `usuario/nombre`
3. Agrégalo:
```json
"kaggle_datasets": {
  "startups": "yanmaksi/big-startup-secsees-fail-dataset-from-crunchbase",
  "mi_dataset": "usuario/nombre-del-dataset"    ← AGREGAR AQUÍ
}
```

---

## ⚠️ Reglas Importantes

1. **Comillas dobles** siempre: `"clave": "valor"`
2. **Comas entre elementos**, pero NO en el último
3. **No usar tildes** en las claves (nombres cortos)
4. **Mantener el formato JSON** (validar en: https://jsonlint.com)

---

## 🔧 Validar el JSON

Antes de guardar cambios, verifica en:
- https://jsonlint.com
- O ejecuta: `python -m json.tool config/project_config.json`

---

## 📞 ¿Problemas?

Si el programa da error después de editar:
1. Verifica que no falten comas
2. Verifica que todas las comillas estén cerradas
3. Usa un validador JSON online