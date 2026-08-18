public class TestJuego {

	private static int iPasados = 0;
	private static int iFallidos = 0;

	public static void main(String[] args) {

		System.out.println("=== Tests de Juego ===\n");

		testGanadorFilas();
		testGanadorColumnas();
		testGanadorDiagonalPrincipal();
		testGanadorDiagonalSecundaria();
		testSinGanador();
		testTableroLleno();
		testTableroNoLleno();
		testJugada();
		testEmpate();

		System.out.println("\n=== Resultado: " + iPasados + " pasados, " + iFallidos + " fallidos ===");

		if (iFallidos > 0) System.exit(1);
	}

	private static void testGanadorFilas() {
		Juego j = new Juego(3);
		j.jugada(0, 0, 1);
		j.jugada(0, 1, 1);
		j.jugada(0, 2, 1);
		j.evaluarJuego(1);
		assertBoolean("Ganador en fila 0", true, j.isbFinJuego());
	}

	private static void testGanadorColumnas() {
		Juego j = new Juego(3);
		j.jugada(0, 1, 2);
		j.jugada(1, 1, 2);
		j.jugada(2, 1, 2);
		j.evaluarJuego(2);
		assertBoolean("Ganador en columna 1", true, j.isbFinJuego());
	}

	private static void testGanadorDiagonalPrincipal() {
		Juego j = new Juego(3);
		j.jugada(0, 0, 1);
		j.jugada(1, 1, 1);
		j.jugada(2, 2, 1);
		j.evaluarJuego(1);
		assertBoolean("Ganador diagonal principal", true, j.isbFinJuego());
	}

	private static void testGanadorDiagonalSecundaria() {
		Juego j = new Juego(3);
		j.jugada(0, 2, 2);
		j.jugada(1, 1, 2);
		j.jugada(2, 0, 2);
		j.evaluarJuego(2);
		assertBoolean("Ganador diagonal secundaria", true, j.isbFinJuego());
	}

	private static void testSinGanador() {
		Juego j = new Juego(3);
		j.jugada(0, 0, 1);
		j.jugada(0, 1, 2);
		j.evaluarJuego(1);
		assertBoolean("Sin ganador parcial", false, j.isbFinJuego());
	}

	private static void testTableroLleno() {
		Juego j = new Juego(2);
		j.jugada(0, 0, 1);
		j.jugada(0, 1, 2);
		j.jugada(1, 0, 2);
		j.jugada(1, 1, 1);
		assertBoolean("Tablero lleno 2x2", true, j.isTableroLleno());
	}

	private static void testTableroNoLleno() {
		Juego j = new Juego(3);
		j.jugada(0, 0, 1);
		assertBoolean("Tablero no lleno", false, j.isTableroLleno());
	}

	private static void testJugada() {
		Juego j = new Juego(3);
		j.jugada(1, 2, 1);
		assertInt("Marca jugada en matriz", 1, j.getmJuego()[1][2]);
	}

	private static void testEmpate() {
		Juego j = new Juego(3);
		// Tablero 3x3 lleno sin ganador
		// X O X
		// X X O
		// O X O
		j.jugada(0, 0, 1);
		j.jugada(0, 1, 2);
		j.jugada(0, 2, 1);
		j.jugada(1, 0, 1);
		j.jugada(1, 1, 1);
		j.jugada(1, 2, 2);
		j.jugada(2, 0, 2);
		j.jugada(2, 1, 1);
		j.jugada(2, 2, 2);
		assertBoolean("Tablero lleno empate", true, j.isTableroLleno());
		j.evaluarJuego(1);
		assertBoolean("Empate sin ganador X", false, j.isbFinJuego());
		j.setbFinJuego(false);
		j.evaluarJuego(2);
		assertBoolean("Empate sin ganador O", false, j.isbFinJuego());
	}

	private static void assertBoolean(String nombre, boolean esperado, boolean actual) {
		if (esperado == actual) {
			System.out.println("  PASS: " + nombre);
			iPasados++;
		} else {
			System.out.println("  FAIL: " + nombre + " (esperado=" + esperado + ", actual=" + actual + ")");
			iFallidos++;
		}
	}

	private static void assertInt(String nombre, int esperado, int actual) {
		if (esperado == actual) {
			System.out.println("  PASS: " + nombre);
			iPasados++;
		} else {
			System.out.println("  FAIL: " + nombre + " (esperado=" + esperado + ", actual=" + actual + ")");
			iFallidos++;
		}
	}

}
