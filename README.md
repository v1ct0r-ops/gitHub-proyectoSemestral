# Sistema de Gestión de Órdenes de Compra

## Descripción del Proyecto

Este sistema permite gestionar órdenes de compra para una empresa de gas licuado. La aplicación cuenta con un módulo de autenticación seguro, registro de órdenes de compra y un menú principal para navegar entre las diferentes funcionalidades.

El proyecto está desarrollado como parte de la Experiencia de Aprendizaje 2 y representa el primer Sprint de un sistema empresarial completo.

### Funcionalidades Principales

- **Login seguro**: Autenticación de usuarios con contraseñas encriptadas
- **Gestión de órdenes**: Registro completo de órdenes de compra con validación de datos
- **Catálogo de productos**: Sistema de galones de gas con precios actualizados
- **Consulta de órdenes**: Visualización de órdenes almacenadas con filtros
- **Navegación intuitiva**: Menú principal con opciones claras

## Integrantes del Grupo

- **Victor Garces** - Desarrollador principal

## Requerimientos Técnicos

### Software necesario
- Python 3.8 o superior
- Visual Studio Code (recomendado)
- Git para control de versiones

### Librerías utilizadas
- **tkinter**: Interfaz gráfica de usuario (incluida en Python)
- **sqlite3**: Base de datos (incluida en Python)
- **hashlib**: Encriptación de contraseñas (incluida en Python)
- **datetime**: Manejo de fechas (incluida en Python)
- **os**: Operaciones del sistema (incluida en Python)

*Nota: Todas las librerías son estándar de Python, no requieren instalación adicional.*

## Estructura del Proyecto

```
gitHub-proyectoSemestral/
├── src/
│   ├── app.py              # Punto de entrada principal
│   ├── login.py            # Módulo de autenticación
│   ├── menu.py             # Menú principal
│   └── orden_compra.py     # Gestión de órdenes
├── database/
│   ├── database.py         # Conexión y configuración BD
│   └── proyecto.db         # Base de datos SQLite
├── evidencias/
│   ├── commits.png         # Historial de commits
│   ├── ramas.png           # Estructura de ramas
│   ├── merge.png           # Procesos de merge
│   └── kanban.png          # Tablero de seguimiento
└── README.md
```

## Instrucciones de Ejecución

### 1. Clonar el repositorio
```bash
git clone https://github.com/v1ct0r-ops/gitHub-proyectoSemestral.git
cd gitHub-proyectoSemestral
```

### 2. Ejecutar la aplicación
```bash
python src/app.py
```

### 3. Credenciales de acceso
- **Usuario**: admin
- **Contraseña**: admin123

### 4. Uso del sistema
1. Ingresar credenciales en la ventana de login
2. Navegar por el menú principal
3. Crear nuevas órdenes desde "Crear nueva orden"
4. Consultar órdenes guardadas desde "Listar órdenes guardadas"
5. Cerrar sesión de forma segura

## Base de Datos

El sistema utiliza SQLite con las siguientes tablas:

- **usuarios**: Almacena credenciales de acceso
- **productos**: Catálogo de galones de gas con precios
- **ordenes_compra**: Registro completo de órdenes

## Desarrollo y Control de Versiones

Este proyecto utiliza Git Flow con las siguientes ramas:
- `main`: Rama principal estable
- `dev`: Desarrollo e integración
- `qa`: Control de calidad
- `feature/*`: Ramas para funcionalidades específicas

## Estado del Proyecto

✅ **Completado**: 
- Módulo de login (RF2)
- Gestión de órdenes (RF1) 
- Menú principal (RF3)
- Integración completa del sistema
- Base de datos funcional