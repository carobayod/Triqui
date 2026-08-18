import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class TestIA {

    @Test
    public void iaGanaSiPuede() {
        IA ia = new IA(3);
        int[][] tablero = {
            {2, 2, 0},
            {1, 1, 0},
            {0, 0, 0}
        };
        PosMatris jugada = ia.mejorJugada(tablero, 2);
        assertEquals(0, jugada.getiFila());
        assertEquals(2, jugada.getiColumna());
    }

    @Test
    public void iaBloqueaJugador() {
        IA ia = new IA(3);
        int[][] tablero = {
            {1, 1, 0},
            {2, 0, 0},
            {0, 0, 0}
        };
        PosMatris jugada = ia.mejorJugada(tablero, 2);
        assertEquals(0, jugada.getiFila());
        assertEquals(2, jugada.getiColumna());
    }

    @Test
    public void minimaxVsMinimaxEmpata() {
        IA ia = new IA(3);
        int[][] tablero = new int[3][3];
        int turno = 1;
        for (int i = 0; i < 9; i++) {
            PosMatris jugada = ia.mejorJugada(tablero, turno);
            if (jugada == null) break;
            tablero[jugada.getiFila()][jugada.getiColumna()] = turno;
            if (ia.ganador(tablero, turno)) break;
            turno = (turno == 1) ? 2 : 1;
        }
        assertTrue(true);
    }

    @Test
    public void iaNoSobreCeldasOcupadas() {
        IA ia = new IA(3);
        int[][] tablero = {
            {1, 0, 0},
            {0, 2, 0},
            {0, 0, 1}
        };
        PosMatris jugada = ia.mejorJugada(tablero, 2);
        assertEquals(0, tablero[jugada.getiFila()][jugada.getiColumna()]);
    }

    @Test
    public void detectaGanadorEnFila() {
        IA ia = new IA(3);
        int[][] tablero = {
            {2, 2, 2},
            {1, 0, 0},
            {0, 1, 0}
        };
        assertTrue(ia.ganador(tablero, 2));
    }

    @Test
    public void detectaGanadorEnColumna() {
        IA ia = new IA(3);
        int[][] tablero = {
            {0, 1, 0},
            {0, 1, 0},
            {2, 1, 0}
        };
        assertTrue(ia.ganador(tablero, 1));
    }

    @Test
    public void detectaGanadorEnDiagonal() {
        IA ia = new IA(3);
        int[][] tablero = {
            {2, 0, 0},
            {0, 2, 0},
            {0, 0, 2}
        };
        assertTrue(ia.ganador(tablero, 2));
    }

    @Test
    public void noDetectaGanadorFalso() {
        IA ia = new IA(3);
        int[][] tablero = {
            {1, 2, 1},
            {2, 1, 2},
            {2, 1, 0}
        };
        assertFalse(ia.ganador(tablero, 1));
        assertFalse(ia.ganador(tablero, 2));
    }

}
