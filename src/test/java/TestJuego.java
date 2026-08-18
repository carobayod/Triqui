import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class TestJuego {

    @Test
    public void ganadorEnFila() {
        Juego j = new Juego(3);
        j.jugada(0, 0, 1);
        j.jugada(0, 1, 1);
        j.jugada(0, 2, 1);
        j.evaluarJuego(1);
        assertTrue(j.isbFinJuego());
    }

    @Test
    public void ganadorEnColumna() {
        Juego j = new Juego(3);
        j.jugada(0, 1, 2);
        j.jugada(1, 1, 2);
        j.jugada(2, 1, 2);
        j.evaluarJuego(2);
        assertTrue(j.isbFinJuego());
    }

    @Test
    public void ganadorDiagonalPrincipal() {
        Juego j = new Juego(3);
        j.jugada(0, 0, 1);
        j.jugada(1, 1, 1);
        j.jugada(2, 2, 1);
        j.evaluarJuego(1);
        assertTrue(j.isbFinJuego());
    }

    @Test
    public void ganadorDiagonalSecundaria() {
        Juego j = new Juego(3);
        j.jugada(0, 2, 2);
        j.jugada(1, 1, 2);
        j.jugada(2, 0, 2);
        j.evaluarJuego(2);
        assertTrue(j.isbFinJuego());
    }

    @Test
    public void sinGanadorParcial() {
        Juego j = new Juego(3);
        j.jugada(0, 0, 1);
        j.jugada(0, 1, 2);
        j.evaluarJuego(1);
        assertFalse(j.isbFinJuego());
    }

    @Test
    public void tableroLleno2x2() {
        Juego j = new Juego(2);
        j.jugada(0, 0, 1);
        j.jugada(0, 1, 2);
        j.jugada(1, 0, 2);
        j.jugada(1, 1, 1);
        assertTrue(j.isTableroLleno());
    }

    @Test
    public void tableroNoLleno() {
        Juego j = new Juego(3);
        j.jugada(0, 0, 1);
        assertFalse(j.isTableroLleno());
    }

    @Test
    public void marcaJugadaEnMatriz() {
        Juego j = new Juego(3);
        j.jugada(1, 2, 1);
        assertEquals(1, j.getmJuego()[1][2]);
    }

    @Test
    public void empateSinGanador() {
        Juego j = new Juego(3);
        j.jugada(0, 0, 1);
        j.jugada(0, 1, 2);
        j.jugada(0, 2, 1);
        j.jugada(1, 0, 1);
        j.jugada(1, 1, 1);
        j.jugada(1, 2, 2);
        j.jugada(2, 0, 2);
        j.jugada(2, 1, 1);
        j.jugada(2, 2, 2);
        assertTrue(j.isTableroLleno());
        j.evaluarJuego(1);
        assertFalse(j.isbFinJuego());
        j.setbFinJuego(false);
        j.evaluarJuego(2);
        assertFalse(j.isbFinJuego());
    }

    @Test
    public void ganadorEnFila4x4() {
        Juego j = new Juego(4);
        j.jugada(2, 0, 1);
        j.jugada(2, 1, 1);
        j.jugada(2, 2, 1);
        j.jugada(2, 3, 1);
        j.evaluarJuego(1);
        assertTrue(j.isbFinJuego());
    }

}
