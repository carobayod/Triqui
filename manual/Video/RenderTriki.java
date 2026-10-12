import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import javax.swing.JButton;
import javax.swing.SwingUtilities;
import java.util.ArrayList;
import java.util.List;

/**
 * Renderiza una partida real del Triki a imagenes, sin capturar la pantalla.
 *
 * Capturar la pantalla no funciona en WSLg (devuelve negro tanto con x11grab
 * como con Robot). En cambio se pide al propio componente Swing que se pinte
 * sobre un BufferedImage: es exacto, nitido y reproducible.
 *
 * Cada jugada (humano + respuesta de la maquina) produce un PNG.
 */
public class RenderTriki {

    static final String OUT = "/tmp/opencode/grab/frames";
    static JButton[] casillas;
    static Component ventana;
    static int n = 0;

    public static void main(String[] args) throws Exception {
        int tamano = args.length > 0 ? Integer.parseInt(args[0]) : 3;

        new File(OUT).mkdirs();
        for (File f : new File(OUT).listFiles()) f.delete();
        casillas = new JButton[tamano * tamano];

        SwingUtilities.invokeAndWait(() -> {
            Tablero t = new Tablero(tamano);
            t.setVisible(true);
            ventana = t;
        });

        esperar(2500);
        SwingUtilities.invokeAndWait(() -> buscarCasillas(ventana, tamano));
        System.err.println("casillas: " + cuenta() + "  ventana: " + ventana.getWidth()
                + "x" + ventana.getHeight());

        // estado inicial (el tablero recien creado)
        SwingUtilities.invokeAndWait(() -> guardar("inicio"));

        // Secuencia de jugadas del humano: se recorre el tablero en diagonal
        // alterna, que reparte las X y deja jugar mas turnos antes de que
        // alguien gane. Las casillas ya ocupadas se saltan.
        List<int[]> orden = new ArrayList<>();
        for (int d = 0; d < tamano; d++) {
            if (d % 2 == 0) {
                for (int f = 0; f < tamano; f++) {
                    int c = (d - f + tamano) % tamano;
                    orden.add(new int[]{f, c});
                }
            } else {
                for (int f = tamano - 1; f >= 0; f--) {
                    int c = (d - f + tamano) % tamano;
                    orden.add(new int[]{f, c});
                }
            }
        }

        int idx = 0;
        for (int[] j : orden) {
            if (idx >= casillas.length) break;
            int i = j[0] * tamano + j[1];
            if (casillas[i] == null) continue;
            final int k = i;
            String t = texto(k);
            if (!t.isEmpty()) continue;
            SwingUtilities.invokeAndWait(() -> casillas[k].doClick());
            esperar(1300);                 // la maquina responde
            final String et = "j" + (idx + 1);
            idx++;
            SwingUtilities.invokeAndWait(() -> guardar(et));
        }

        esperar(1200);
        SwingUtilities.invokeAndWait(() -> guardar("final"));
        System.err.println("frames escritos: " + n);
        System.exit(0);
    }

    static void guardar(String etiqueta) {
        try {
            BufferedImage img = new BufferedImage(
                    Math.max(ventana.getWidth(), 1), Math.max(ventana.getHeight(), 1),
                    BufferedImage.TYPE_INT_RGB);
            Graphics2D g = img.createGraphics();
            ventana.printAll(g);
            g.dispose();
            File f = new File(String.format("%s/f%02d_%s.png", OUT, n, etiqueta));
            ImageIO.write(img, "png", f);
            n++;
        } catch (Exception e) {
            System.err.println("render fallo: " + e);
        }
    }

    static int cuenta() {
        int k = 0;
        for (JButton b : casillas) if (b != null) k++;
        return k;
    }

    static void buscarCasillas(Component c, int T) {
        List<JButton> todas = new ArrayList<>();
        recorrer(c, todas);
        List<JButton> grandes = new ArrayList<>();
        for (JButton b : todas) if (b.getWidth() >= 40 && b.getHeight() >= 40) grandes.add(b);
        grandes.sort((p, q) -> {
            int dy = p.getY() - q.getY();
            if (Math.abs(dy) > 15) return dy;
            return Integer.compare(p.getX(), q.getX());
        });
        for (int i = 0; i < casillas.length && i < grandes.size(); i++) casillas[i] = grandes.get(i);
    }

    static void recorrer(Component c, List<JButton> out) {
        if (c instanceof Container) {
            for (Component ch : ((Container) c).getComponents()) {
                if (ch instanceof JButton) out.add((JButton) ch);
                recorrer(ch, out);
            }
        }
    }

    static String texto(int i) {
        if (casillas[i] == null) return "x";
        String t = casillas[i].getText();
        return t == null ? "" : t.trim();
    }

    static void esperar(int ms) {
        try { Thread.sleep(ms); } catch (InterruptedException e) { }
    }
}