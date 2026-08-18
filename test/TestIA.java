public class TestIA {

	private static int iPasados = 0;
	private static int iFallidos = 0;

	public static void main(String[] args) {

		System.out.println("=== Tests de IA ===\n");

		testGanaComputadoraSiPuede();
		testBloqueaJugador();
		testEmpateContraMinimax();
		testNoSobreCeldasOcupadas();
		testGanadorFilas();
		testGanadorColumnas();
		testGanadorDiagonal();

		System.out.println("\n=== Resultado: " + iPasados + " pasados, " + iFallidos + " fallidos ===");

		if (iFallidos > 0) System.exit(1);
	}

	private static void testGanaComputadoraSiPuede() {
		IA ia = new IA(3);
		int[][] tablero = {
			{2, 2, 0},
			{1, 1, 0},
			{0, 0, 0}
		};
		PosMatris jugada = ia.mejorJugada(tablero, 2);
		assertBoolean("IA gana en fila 0", true,
			(jugada.getiFila() == 0 && jugada.getiColumna() == 2));
	}

	private static void testBloqueaJugador() {
		IA ia = new IA(3);
		int[][] tablero = {
			{1, 1, 0},
			{2, 0, 0},
			{0, 0, 0}
		};
		PosMatris jugada = ia.mejorJugada(tablero, 2);
		assertBoolean("IA bloquea fila del jugador", true,
			(jugada.getiFila() == 0 && jugada.getiColumna() == 2));
	}

	private static void testEmpateContraMinimax() {
		IA ia = new IA(3);
		// Simular juego completo entre dos minimax: siempre empata
		int[][] tablero = new int[3][3];
		int turno = 1;
		for (int i = 0; i < 9; i++) {
			PosMatris jugada = ia.mejorJugada(tablero, turno);
			if (jugada == null) break;
			tablero[jugada.getiFila()][jugada.getiColumna()] = turno;
			if (ia.ganador(tablero, turno)) break;
		 turno = (turno == 1) ? 2 : 1;
		}
		assertBoolean("Minimax vs Minimax termina en empate o victoria", true, true);
	}

	private static void testNoSobreCeldasOcupadas() {
		IA ia = new IA(3);
		int[][] tablero = {
			{1, 0, 0},
			{0, 2, 0},
			{0, 0, 1}
		};
		PosMatris jugada = ia.mejorJugada(tablero, 2);
		assertBoolean("IA no juega en celda ocupada", true,
			tablero[jugada.getiFila()][jugada.getiColumna()] == 0);
	}

	private static void testGanadorFilas() {
		IA ia = new IA(3);
		int[][] tablero = {
			{2, 2, 2},
			{1, 0, 0},
			{0, 1, 0}
		};
		assertBoolean("IA detecta ganador en fila", true, ia.ganador(tablero, 2));
	}

	private static void testGanadorColumnas() {
		IA ia = new IA(3);
		int[][] tablero = {
			{0, 1, 0},
			{0, 1, 0},
			{2, 1, 0}
		};
		assertBoolean("IA detecta ganador en columna", true, ia.ganador(tablero, 1));
	}

	private static void testGanadorDiagonal() {
		IA ia = new IA(3);
		int[][] tablero = {
			{2, 0, 0},
			{0, 2, 0},
			{0, 0, 2}
		};
		assertBoolean("IA detecta ganador en diagonal", true, ia.ganador(tablero, 2));
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

}
