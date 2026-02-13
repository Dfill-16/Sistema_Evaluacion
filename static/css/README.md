# Tailwind CSS Setup

Este directorio contiene los archivos CSS para el proyecto.

## Estructura

```
static/css/
├── input.css      # Archivo de entrada con directivas de Tailwind
└── output.css     # Archivo compilado (generado automáticamente)
```

## Comandos disponibles

### Desarrollo (con watch mode)
```bash
npm run dev
```
Este comando ejecuta Tailwind en modo watch, recompilando automáticamente cada vez que detecta cambios en los archivos HTML o CSS.

### Producción (minificado)
```bash
npm run build
```
Este comando genera el CSS optimizado y minificado para producción.

## Notas

- **input.css**: Contiene las directivas de Tailwind (@tailwind base, @tailwind components, @tailwind utilities) y estilos personalizados.
- **output.css**: Es el archivo compilado que debe ser incluido en los templates HTML. Este archivo es generado automáticamente y NO debe editarse manualmente.
- El archivo **tailwind.config.js** en la raíz del proyecto define las rutas de los templates a escanear.

## Personalización

Los estilos personalizados deben agregarse en `input.css` usando las capas de Tailwind:

```css
@layer components {
  .mi-componente {
    @apply bg-blue-500 text-white p-4 rounded;
  }
}
```
