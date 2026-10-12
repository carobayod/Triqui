"""Contenido curado para el video v3 (estructura reorganizada del libro):
títulos cortos, 3 puntos clave por escena y narración redactada para las
secciones (partes / intro / glosario). Re-mapeado tras la reorganización:
Parte Cero + Parte I "Prepara el taller" + Parte III "Cómo está construido".
SIN regenerar el video v2: este archivo queda listo para futuros renders.
"""
from pathlib import Path

# Diagramas del libro, que el video antes no usaba en ninguna diapositiva.
ASSETS = Path(__file__).resolve().parents[1] / "assets"
DATA = {
    0: dict(
        title="Introducción",
        section="Aprende Java Jugando",
        points=["Java desde cero sin experiencia",
                "Aprenderás haciendo un juego",
                "Retos y código real"],
        narr="Este curso te enseña a programar en Java creando un juego de Triki con "
             "inteligencia artificial. No necesitas experiencia previa: se comienza "
             "desde cero y se avanza paso a paso."),
    1: dict(
        title="Parte Cero · El juego, para todos",
        section="Parte Cero · El Juego, para Todos",
        points=["Las reglas del tres en raya",
                "Entender el juego antes de programar",
                "Traducir reglas a código"],
        narr="Antes de programar, entendemos el juego: sus reglas, cómo se gana y "
             "cómo se traduce cada regla a código."),
    2: dict(
        title="Las reglas del Triki",
        section="Parte Cero · El Juego, para Todos",
        points=["Tablero de tres por tres",
                "Tres en línea para ganar",
                "Empate si se llena"],
        narr="El Triki se juega en un tablero de tres por tres. Gana quien junte "
             "tres marcas en línea y hay empate si el tablero se llena."),
    3: dict(
        title="Una partida bajo el microscopio",
        section="Parte Cero · El Juego, para Todos",
        points=["Cada jugada tiene su porqué",
                "Amenazas y bloqueos",
                "De las reglas al código"],
        narr="Analizamos una partida movimiento por movimiento: cada jugada es una "
             "decisión que el código aprenderá a tomar solo."),
    4: dict(
        title="Parte Uno · Prepara el taller",
        section="Parte Uno · Prepara el Taller",
        points=["Instalar las herramientas",
                "Un editor para escribir código",
                "Ejecutar el juego temprano"],
        narr="Antes de escribir código preparamos nuestra computadora: instalamos "
             "Java, un editor y ejecutamos el Triki por primera vez."),
    5: dict(
        title="Configuración paso a paso",
        section="Parte Uno · Prepara el Taller",
        points=["Java y kit de desarrollo",
                "Editor de código recomendado",
                "Comprobar que todo funciona"]),
    6: dict(
        title="Compilar y ejecutar el Triki",
        section="Parte Uno · Prepara el Taller",
        points=["Compilar con javac",
                "Ejecutar la clase Tablero",
                "Tu juego ya corre"],
        narr="Compilamos el proyecto y ejecutamos el Triki: el código pasa de texto "
             "a la ventana del juego por primera vez."),
    7: dict(
        title="Parte Dos · Los fundamentos",
        section="Parte Dos · Fundamentos",
        points=["Qué es programar",
                "Las piezas esenciales de Java",
                "Tu primer código"],
        narr="Entramos en la programación: qué significa programar, cómo piensa una "
             "computadora y cuáles son las piezas esenciales de Java."),
    8: dict(
        title="¿Qué es programar?",
        section="Parte Dos · Fundamentos",
        points=["Dar instrucciones a la computadora",
                "Se repiten sin cansarse",
                "Resolver problemas paso a paso"]),
    9: dict(
        title="¿Qué es Java?",
        section="Parte Dos · Fundamentos",
        points=["Uno de los lenguajes más usados",
                "Compatible con muchas plataformas",
                "Ideal para empezar a aprender"]),
    10: dict(
        title="Ciclo de vida de un programa",
        section="Parte Dos · Fundamentos",
        points=["Escribir el código fuente",
                "Compilar el programa",
                "La máquina virtual lo ejecuta"],
        narr="Un programa Java pasa por varias etapas: escribimos el código, lo compilamos "
             "y luego la máquina virtual lo ejecuta. Veámoslo paso a paso."),
    11: dict(
        title="Palabras básicas de Java",
        section="Parte Dos · Fundamentos",
        points=["Palabras reservadas del lenguaje",
                "Su significado en Java",
                "Clases, paquetes y más"]),
    12: dict(
        title="Variables y tipos de datos",
        section="Parte Dos · Fundamentos",
        points=["Guardar valores en memoria",
                "Tipos: entero, texto, booleano",
                "El nombre describe al dato"]),
    13: dict(
        title="Estructuras condicionales",
        section="Parte Dos · Fundamentos",
        points=["El programa toma decisiones",
                "if y else en acción",
                "Comparar valores y actuar"]),
    14: dict(
        title="Ciclos · repetir acciones",
        section="Parte Dos · Fundamentos",
        points=["Repetir una acción varias veces",
                "Recorrer listas fácilmente",
                "Menos trabajo manual"]),
    15: dict(
        title="Métodos y funciones",
        section="Parte Dos · Fundamentos",
        points=["Bloques de código con nombre",
                "Se llaman cuando se necesitan",
                "Reutilizar sin repetir"]),
    16: dict(
        title="POO y encapsulamiento",
        section="Parte Dos · Fundamentos",
        points=["Clases y objetos",
                "El objeto protege su estado",
                "Encapsular para simplificar"]),
    17: dict(
        title="Parte Tres · Cómo está construido",
        section="Parte Tres · Cómo Está Construido",
        points=["El mapa del código",
                "La interfaz con Swing",
                "La lógica y la IA"],
        narr="Ahora abrimos el juego por dentro: recorremos el mapa del código, la "
             "interfaz gráfica, la lógica y la inteligencia artificial."),
    18: dict(
        title="El mapa del código",
        section="Parte Tres · Cómo Está Construido",
        points=["Dónde vive cada clase",
                "Responsabilidades claras",
                "De la pantalla a la IA"],
        narr="Antes de ver el código, miramos el mapa del proyecto: qué archivos hay "
             "y qué hace cada uno."),
    19: dict(
        title="Swing: interfaz gráfica",
        section="Parte Tres · Cómo Está Construido",
        points=["Ventanas y botones en Java",
                "Adiós a la consola",
                "Componentes visuales listos"]),
    20: dict(
        title="Componentes Swing del Triki",
        section="Parte Tres · Cómo Está Construido",
        points=["JFrame: la ventana",
                "Botones para cada casilla",
                "Etiquetas y textos"]),
    21: dict(
        title="Layout: distribución",
        section="Parte Tres · Cómo Está Construido",
        points=["Organizar los componentes",
                "GridLayout: tablero de tres por tres",
                "El orden dentro de la ventana"]),
    22: dict(
        title="Eventos: reacción al clic",
        section="Parte Tres · Cómo Está Construido",
        points=["El programa reacciona al clic",
                "ActionListener escucha",
                "Cada botón tiene su respuesta"]),
    23: dict(
        title="Tablero.java · la pantalla",
        section="Parte Tres · Cómo Está Construido",
        points=["Ventana con nueve botones",
                "Cada botón es una casilla",
                "Dibuja y escucha los clics"]),
    24: dict(
        title="Juego.java · la lógica",
        section="Parte Tres · Cómo Está Construido",
        points=["Guarda el estado del tablero",
                "Comprueba filas y diagonales",
                "Las reglas del Triki"]),
    25: dict(
        title="IA.java · minimax",
        section="Parte Tres · Cómo Está Construido",
        points=["La máquina piensa las jugadas",
                "Simula jugadas por adelantado",
                "Elige la mejor opción"]),
    26: dict(
        title="Conexión de las capas",
        section="Parte Tres · Cómo Está Construido",
        points=["La vista llama a la lógica",
                "La lógica consulta a la IA",
                "Todo conectado"]),
    27: dict(
        title="Parte Cuatro · Herramientas",
        section="Parte Cuatro · Herramientas",
        points=["Línea de comandos",
                "Maven: construir proyectos",
                "Git y pruebas con JUnit"],
        narr="Para terminar, vemos las herramientas de los programadores profesionales: "
             "la línea de comandos, Maven para construir, Git para versionar y JUnit "
             "para probar."),
    28: dict(
        title="Línea de comandos",
        section="Parte Cuatro · Herramientas",
        points=["Una ventana para escribir órdenes",
                "Comandos básicos",
                "Navegar entre carpetas"]),
    29: dict(
        title="Maven · el asistente",
        section="Parte Cuatro · Herramientas",
        points=["Automatiza la compilación",
                "Organiza las librerías",
                "Comandos sencillos"]),
    30: dict(
        title="Git y GitHub",
        section="Parte Cuatro · Herramientas",
        points=["Historial de cambios",
                "Guardar versiones que funcionan",
                "Compartir con GitHub"]),
    31: dict(
        title="¿Por qué pruebas unitarias?",
        section="Parte Cuatro · Herramientas",
        points=["Verificar cada función",
                "Detectar errores pronto",
                "Confianza al cambiar código"]),
    32: dict(
        title="JUnit 5 · la librería",
        section="Parte Cuatro · Herramientas",
        points=["La librería estándar de pruebas",
                "Escribir tests con anotaciones",
                "Afirmaciones que comprueban"]),
    33: dict(
        title="Pruebas en la práctica",
        section="Parte Cuatro · Herramientas",
        points=["TestJuego: las reglas",
                "TestIA: el minimax",
                "Pruebas reales del proyecto"]),
    34: dict(
        title="Las librerías en general",
        section="Parte Cuatro · Herramientas",
        points=["Código ya escrito por otros",
                "Reutilizar sin reinventar",
                "Como piezas de un set"]),
    35: dict(
        title="Glosario final",
        section="Glosario",
        points=["Repaso de conceptos clave",
                "Vocabulario del curso",
                "Para consultar después"],
        narr="Terminamos con un glosario: un repaso rápido de las palabras y conceptos "
             "más importantes del curso."),
    36: dict(
        title="Apéndice · referencia rápida",
        section="Apéndice",
        points=["Cuatro clases, un trabajo cada una",
                "Juego decide quién ganó",
                "IA elige la mejor jugada"],
        extra=dict(diagrama=ASSETS / "mapa_clases_archify.png",
                   alt="Diagrama de las cuatro clases del Triki y cómo se hablan entre sí",
                   lado="lado"),
        narr="Como apéndice, un mapa de referencia rápida del código del Triki, "
             "organizado por archivos, para consultar cuando quieras."),
    37: dict(
        title="PosMatris.java · guardar una posición",
        section="Apéndice",
        points=["Un contenedor de datos",
                "Guarda fila y columna",
                "Simple y reutilizable"],
        # Codigo real tomado del apendice del libro (linea 1327). Antes esta
        # escena decia solo "Simple y reutilizable", que no explica nada.
        #
        # Se recorta a 7 lineas: el original tiene 9 y con la glosa se pasaba
        # del limite de la diapositiva (medido: el contenido llegaba a y=1046
        # de 1080 y montaba sobre el pie, que empieza en y=1010). Con 7 lineas
        # entra lo esencial: los dos campos, el constructor con parametros y
        # un getter. El libro conserva la version completa.
        extra=dict(codigo="public class PosMatris {\n"
                          "    private int iFila;    // fila\n"
                          "    private int iColumna; // columna\n"
                          "    public PosMatris(int iFila, int iColumna) {\n"
                          "        this.iFila = iFila;\n"
                          "        this.iColumna = iColumna;\n"
                          "    }\n"
                          "    public int getiFila() { return iFila; }\n"
                          "}",
                  glosa="new PosMatris(1, 2) crea la posición fila 1, "
                        "columna 2.")),
    38: dict(
        title="Juego.java · la lógica del juego",
        section="Apéndice",
        points=["La matriz del tablero",
                "Turnos y verificaciones",
                "Quién gana cada partida"],
        extra=dict(codigo="// Convención: 0 = vacío, 1 = X, 2 = O\n"
                          "jugada(fila, columna, turno)   // marca\n"
                          "evaluarJuego(turno)            // revisa\n"
                          "isTableroLleno()              // empate\n"
                          "jugadaMaquinaInteligente(...)  // delega en IA",
                  glosa="Juego guarda el tablero en una matriz de enteros "
                        "y decide quién ganó. Lo explica a fondo el capítulo 20.")),
    39: dict(
        title="IA.java · el algoritmo minimax",
        section="Apéndice",
        points=["Recorre cada casilla libre",
                "Evalúa jugadas ganadoras",
                "Busca la mejor jugada con minimax"],
        # El arbol de minimax ya existe en el libro (assets/minimax_tree.png) y
        # no se estaba usando en ningun lado del video.
        extra=dict(diagrama=ASSETS / "minimax_tree.png",
                   alt="Árbol de decisión del minimax con los puntajes de cada jugada",
                   lado="lado")),
    40: dict(
        title="Tablero.java · la interfaz gráfica",
        section="Apéndice",
        points=["La ventana principal",
                "Nueve botones conectados",
                "Une todo el juego"],
        extra=dict(diagrama=ASSETS / "flujo_turno_video.png",
                   alt="Flujo de un turno: del clic del jugador a la respuesta de la máquina",
                   lado="abajo")),
}

SECTIONS_N = 41


def get(idx, fallback_title="", fallback_banner="Curso Java"):
    d = DATA.get(idx, {})
    title = d.get("title") or fallback_title
    section = d.get("section") or fallback_banner
    points = d.get("points", [])
    narr = d.get("narr")
    # Quinto valor: el contenido visual de la diapositiva (diagrama o bloque de
    # codigo). Las escenas del apendice lo usan; las demas lo traen vacio.
    return title, section, points, narr, d.get("extra")