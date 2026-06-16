# Hasta el Último Cartucho

Es un simulador táctico de artillería por turnos en **2D** fuertemente inspirado en el clásico *Gunbound*. El juego cuenta con generación procedimental de entornos destruibles, física balística determinista y adaptación dinámica de los tanques al relieve del mapa. Fue desarrollado bajo la metodología **TDD (Desarrollo Guiado por Pruebas)** para el curso de Testing, Implantación y Mantenimiento de Sistemas.

---

## 🔧 Manual de Instalación y Despliegue

### Requisitos Previos
* **Python 3.8 o superiores antes de 3.14r** instalado en el sistema.
* La librería gráfica **Pygame**.

### Pasos para la Ejecución

1. **Instalar Dependencias:**
   Abre una terminal o consola de comandos y ejecuta el siguiente comando para instalar Pygame:
   ```bash
   pip install pygame
   ```

2. **Estructura del Proyecto:**
   Asegúrate de que todos los módulos estén guardados en la misma carpeta raíz:

   ProyectoTesting/
   ├── constants.py
   ├── utils.py
   ├── weapons.py
   ├── effects.py
   ├── entities.py
   ├── terrain.py
   └── main.py
   

3. **Lanzar el Juego:**
   Ejecuta el archivo principal (`main.py`) desde tu terminal:
   ```bash
   python main.py
   ```

*(Nota: El sistema cuenta con un mecanismo de **contingencia pasiva**; si no encuentra imágenes en una carpeta `assets/`, autogenerará un entorno geométrico procedural vectorizado para evitar que el programa falle).*

## 📜 Reglas del Juego

- **Regla 1 (Límite 1v1):** Solo se permite el enfrentamiento cerrado entre **2 jugadores** en tiempo real.
- **Regla 2 (Temporizador Táctico):** Cada jugador dispone de exactamente **30 segundos** por turno para moverse, apuntar y disparar. Si el tiempo expira, el turno se transfiere automáticamente al rival.
- **Regla 3 (Límite de Combustible):** Los desplazamientos horizontales consumen una barra de combustible finita. Al agotarse, el tanque queda inmovilizado hasta la siguiente ronda.
- **Regla 4 (Sector de Apuntado Corto):** El radar de asistencia está limitado a un cuadrante de **90°** relativo a la dirección de la mirada del chasis. Debes orientar el tanque hacia tu objetivo para poder apuntarle.
- **Regla 5 (Física Balística y Viento):** Los proyectiles se rigen bajo una gravedad fija (g = 0.22) y la fricción del aire. Las corrientes de viento cambian de fuerza y dirección de forma aleatoria **al inicio de cada turno**.
- **Regla 6 (Condición de Victoria):** La partida concluye inmediatamente si la salud de un competidor se reduce a **0**, o si el terreno bajo sus pies es completamente destruido y **cae al vacío** (límite inferior de la pantalla).
- **Regla 7 (Criterio de Empate):** Si ambos tanques se quedan sin salud o caen al abismo simultáneamente en el mismo turno, se declara **Empate Táctico**.

## 🎮 Controles y Cómo Jugar

Al iniciar, el sistema les permitirá pasar por fases consecutivas para elegir uno de los **4 tanques disponibles** (Knight, Mage, Dragon, Heavy), cada uno con estadísticas y un set de **5 armas exclusivas**.  

### Mandos del Teclado
- **Teclas `A` / `D` :** Mover el tanque hacia la izquierda o derecha (consume combustible).
- **Teclas `W` / `S` :** Ajustar de forma milimétrica la inclinación del cañón.
- **Teclas `1` a `5` :** Seleccionar el tipo de proyectil del catálogo exclusivo de tu tanque.
- **Barra Espaciadora (`SPACE`):**
  - **Mantener presionada:** Carga de forma progresiva la barra de fuerza en la interfaz inferior.
  - **Soltar:** Dispara el proyectil con la potencia acumulada.

*(Nota: Si la barra se llena al 100%, la computadora ejecutará un **auto-disparo** inmediato por seguridad)*