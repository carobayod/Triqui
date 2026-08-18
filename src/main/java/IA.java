public class IA {

	private int iTamanio;

	public IA(int iTamanio) {
		this.iTamanio = iTamanio;
	}

	/**
	 * Retorna la mejor jugada para la computadora usando minimax
	 */
	public PosMatris mejorJugada(int[][] tablero, int turnoComputador) {
		int turnoHumano = (turnoComputador == 1) ? 2 : 1;
		int mejorPuntaje = Integer.MIN_VALUE;
		PosMatris mejorPosicion = null;

		for (int fila = 0; fila < iTamanio; fila++) {
			for (int columna = 0; columna < iTamanio; columna++) {
				if (tablero[fila][columna] == 0) {
					tablero[fila][columna] = turnoComputador;
					int puntaje = minimax(tablero, 0, false, turnoComputador, turnoHumano);
					tablero[fila][columna] = 0;

					if (puntaje > mejorPuntaje) {
						mejorPuntaje = puntaje;
						mejorPosicion = new PosMatris(fila, columna);
					}
				}
			}
		}
		return mejorPosicion;
	}

	/**
	 * Algoritmo minimax con poda alfa-beta
	 * +10 = gana computadora, -10 = gana humano, 0 = empate
	 */
	private int minimax(int[][] tablero, int profundidad, boolean esMaximizando, int turnoComputador, int turnoHumano) {

		if (ganador(tablero, turnoComputador)) return 10 - profundidad;
		if (ganador(tablero, turnoHumano)) return profundidad - 10;
		if (tableroLleno(tablero)) return 0;

		if (esMaximizando) {
			int mejorPuntaje = Integer.MIN_VALUE;
			for (int fila = 0; fila < iTamanio; fila++) {
				for (int columna = 0; columna < iTamanio; columna++) {
					if (tablero[fila][columna] == 0) {
						tablero[fila][columna] = turnoComputador;
						int puntaje = minimax(tablero, profundidad + 1, false, turnoComputador, turnoHumano);
						tablero[fila][columna] = 0;
						mejorPuntaje = Math.max(puntaje, mejorPuntaje);
					}
				}
			}
			return mejorPuntaje;
		} else {
			int mejorPuntaje = Integer.MAX_VALUE;
			for (int fila = 0; fila < iTamanio; fila++) {
				for (int columna = 0; columna < iTamanio; columna++) {
					if (tablero[fila][columna] == 0) {
						tablero[fila][columna] = turnoHumano;
						int puntaje = minimax(tablero, profundidad + 1, true, turnoComputador, turnoHumano);
						tablero[fila][columna] = 0;
						mejorPuntaje = Math.min(puntaje, mejorPuntaje);
					}
				}
			}
			return mejorPuntaje;
		}
	}

	/**
	 * Verifica si un jugador ganó
	 */
	public boolean ganador(int[][] tablero, int turno) {
		return ganadorFilas(tablero, turno) || ganadorColumnas(tablero, turno) || ganadorDiagonales(tablero, turno);
	}

	private boolean ganadorFilas(int[][] tablero, int turno) {
		for (int fila = 0; fila < iTamanio; fila++) {
			int count = 0;
			for (int columna = 0; columna < iTamanio; columna++) {
				if (tablero[fila][columna] == turno) count++;
			}
			if (count == iTamanio) return true;
		}
		return false;
	}

	private boolean ganadorColumnas(int[][] tablero, int turno) {
		for (int columna = 0; columna < iTamanio; columna++) {
			int count = 0;
			for (int fila = 0; fila < iTamanio; fila++) {
				if (tablero[fila][columna] == turno) count++;
			}
			if (count == iTamanio) return true;
		}
		return false;
	}

	private boolean ganadorDiagonales(int[][] tablero, int turno) {
		int count1 = 0;
		int count2 = 0;
		for (int i = 0; i < iTamanio; i++) {
			if (tablero[i][i] == turno) count1++;
			if (tablero[(iTamanio - 1) - i][i] == turno) count2++;
		}
		return count1 == iTamanio || count2 == iTamanio;
	}

	private boolean tableroLleno(int[][] tablero) {
		for (int fila = 0; fila < iTamanio; fila++) {
			for (int columna = 0; columna < iTamanio; columna++) {
				if (tablero[fila][columna] == 0) return false;
			}
		}
		return true;
	}

	public int getiTamanio() {
		return iTamanio;
	}

}
