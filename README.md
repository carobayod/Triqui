# Triki

Juego de **Triki (tres en línea)** en Java que se juega contra la computadora, con interfaz gráfica **Swing** e **inteligencia artificial basada en minimax**.

## Características

- Tablero de tamaño **N x N** configurable
- Jugador contra la computadora con IA minimax (`IA.java`)
- Interfaz gráfica en Swing (`Tablero.java`)
- Lógica del juego separada y testeable (`Juego.java`)
- Pruebas unitarias con **JUnit 5**

## Compilar y ejecutar

Requisitos: Java 17+ y Maven.

```bash
mvn clean package          # compila y ejecuta las pruebas
java -jar target/triqui-1.0.jar   # ejecuta el juego
```

También puedes iniciarlo directamente con:

```bash
mvn exec:java
```

## Probar

```bash
mvn test
```

Incluye 18 pruebas unitarias para la lógica del juego y la IA.