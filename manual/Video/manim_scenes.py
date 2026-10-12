"""Escenas Manim animadas para insertar en el video del Triki.

  Uso: manim -qh manim_scenes.py Clase  (1920x1080p30)
  luego el ensamblado copia los mp4 a work/clips/manim_s<N>.mp4 para
  sustituir el kenburns de las escenas indicadas en ANIMACIONES.

  Colocacion (ver ANIMACIONES): cada animacion va en la escena cuya
  narracion termina en dos puntos, porque el "invita" a ver algo.
"""
from manim import *

ANIMACIONES = {
    "manim_s03": "TableroScene",   # una partida bajo el microscopio
    "manim_s18": "CapasScene",     # el mapa del codigo
    "manim_s20": "SwingScene",     # componentes Swing
    "manim_s21": "LayoutScene",    # distribucion de los componentes
    "manim_s25": "MinimaxScene",   # la IA: minimax
}

FONDO = "#10194a"
ACENTO = "#26C6DA"
ACENTO2 = "#7ce3ee"
TEXTO = "#ffffff"
TENUE = "#c9d6ff"


class _Base(Scene):
    def setup(self):
        self.camera.background_color = FONDO

    def titulo(self, txt, size=50):
        t = Text(txt, font_size=size, color=TEXTO).to_edge(UP, buff=0.5)
        self.play(FadeIn(t, shift=DOWN * 0.3), run_time=0.8)
        return t


class TableroScene(_Base):
    """Una jugada: se marca X y la maquina responde con O."""

    def construct(self):
        self.titulo("Una jugada en el tablero", 52)

        filas, cols, lado = 3, 3, 1.5
        grid = VGroup()
        for f in range(filas):
            for c in range(cols):
                sq = Square(side_length=lado, stroke_color=ACENTO,
                            stroke_width=3).move_to(
                    [c * lado * 1.15, -f * lado * 1.15, 0])
                sq.set_fill(ACENTO, opacity=0.06)
                grid.add(sq)
        grid.move_to(ORIGIN)
        self.play(LaggedStart(*[Create(s) for s in grid], lag_ratio=0.1), run_time=1.6)

        # jugada humana: (1,0)
        x = Text("X", font_size=64, color=ACENTO2).move_to(grid[0].get_center())
        self.play(FadeIn(x, scale=1.6), run_time=0.9)
        # la maquina responde: (2,2)
        o = Text("O", font_size=64, color="#FFA600")
        o.move_to(grid[8].get_center())
        self.play(FadeIn(o, scale=1.6), run_time=0.9)

        # tres en linea
        linea = Line(grid[0].get_center(), grid[4].get_center(),
                     grid[8].get_center(), color="#7CFC00", stroke_width=8)
        msg = Text("tres en linea", font_size=38, color="#7CFC00").to_edge(DOWN, buff=0.8)
        self.play(Create(linea), run_time=1.2)
        self.play(FadeIn(msg), run_time=0.8)
        self.wait(0.6)


class CapasScene(_Base):
    """El mapa del codigo: tres capas que se hablan entre si."""

    def construct(self):
        self.titulo("El mapa del codigo", 54)

        capas = [
            ("Tablero", "ventana y clics", "#4a6fa5"),
            ("Juego", "reglas y ganador", "#2e7d32"),
            ("IA", "minimax", "#ef6c00"),
        ]
        cajas = VGroup()
        for i, (nombre, rol, color) in enumerate(capas):
            caja = VGroup(
                RoundedRectangle(width=4.6, height=1.5, corner_radius=0.18,
                                 stroke_width=3).set_stroke(color=color),
                Text(nombre, font_size=34, color=TEXTO).shift(UP * 0.22),
                Text(rol, font_size=20, color=TENUE).shift(DOWN * 0.32),
            )
            caja[0].set_fill(color, opacity=0.18)
            caja.move_to([0, -1.7 * i, 0])
            cajas.add(caja)
        cajas.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.5) for c in cajas],
                              lag_ratio=0.45), run_time=2.2)

        flechas = VGroup(
            Arrow(cajas[0].get_bottom(), cajas[1].get_top(), buff=0.12,
                  color=ACENTO, stroke_width=5, max_tip_length_to_length_ratio=0.15),
            Arrow(cajas[1].get_bottom(), cajas[2].get_top(), buff=0.12,
                  color=ACENTO, stroke_width=5, max_tip_length_to_length_ratio=0.15),
        )
        self.play(LaggedStart(*[GrowArrow(a) for a in flechas], lag_ratio=0.5),
                  run_time=1.6)
        self.wait(0.5)


class SwingScene(_Base):
    """Los componentes Swing que usa el Triki."""

    def construct(self):
        self.titulo("Los componentes Swing del Triki", 48)

        ventana = RoundedRectangle(width=7.4, height=4.6, corner_radius=0.2,
                                   stroke_color=ACENTO, stroke_width=4)
        ventana.set_fill("#0d1330", opacity=0.85)
        tit = Text("JFrame", font_size=26, color=TEXTO)
        tit.move_to(ventana.get_corner(UL) + RIGHT * 0.5 + DOWN * 0.4)
        self.play(Create(ventana), run_time=1.2)
        self.play(FadeIn(tit), run_time=0.5)

        # botonera 3x3, como el tablero del juego
        botones = VGroup()
        for f in range(3):
            for c in range(3):
                b = Square(side_length=0.82, stroke_color=ACENTO2, stroke_width=2.5)
                b.set_fill(ACENTO, opacity=0.12)
                b.move_to(ventana.get_center() + [c * 0.95 - 0.95, -f * 0.95 + 0.95, 0])
                botones.add(b)
        self.play(LaggedStart(*[Create(b) for b in botones], lag_ratio=0.08),
                  run_time=1.8)

        rotulos = VGroup(
            Text("JButton", font_size=26, color=ACENTO2),
            Text("una casilla", font_size=19, color=TENUE),
        ).arrange(DOWN, buff=0.15).next_to(botones, RIGHT, buff=0.7)
        linea = Arrow(botones.get_right(), rotulos.get_left(), buff=0.12,
                      color=ACENTO, stroke_width=3,
                      max_tip_length_to_length_ratio=0.2)
        self.play(GrowArrow(linea), FadeIn(rotulos), run_time=1.2)
        self.wait(0.5)


class LayoutScene(_Base):
    """GridLayout: como Swing reparte los componentes."""

    def construct(self):
        self.titulo("GridLayout: uno por celda", 50)

        marco = RoundedRectangle(width=7.6, height=4.8, corner_radius=0.2,
                                 stroke_color=TENUE, stroke_width=3)
        marco.set_fill("#0d1330", opacity=0.8)
        self.play(Create(marco), run_time=1.0)

        celdas = VGroup()
        for f in range(3):
            for c in range(3):
                r = Square(side_length=1.3, stroke_color=ACENTO, stroke_width=2.5)
                r.set_fill(ACENTO, opacity=0.14 if (f + c) % 2 == 0 else 0.05)
                r.move_to(marco.get_center() +
                          [c * 1.45 - 1.45, -f * 1.45 + 1.45, 0])
                celdas.add(r)
        self.play(LaggedStart(*[Create(r) for r in celdas], lag_ratio=0.12),
                  run_time=1.9)

        # una pieza cae en la celda central
        p = Square(side_length=1.3, stroke_color="#FFA600", stroke_width=4)
        p.set_fill("#FFA600", opacity=0.3)
        p.move_to(celdas[1].get_center())
        self.play(FadeIn(p, scale=1.4), run_time=0.9)

        txt = Text("una fila y una columna por componente",
                   font_size=26, color=TENUE).to_edge(DOWN, buff=0.7)
        self.play(FadeIn(txt), run_time=0.8)
        self.wait(0.5)


class MinimaxScene(_Base):
    """El arbol minimax: la IA prueba jugadas y puntua."""

    def construct(self):
        self.titulo("Minimax: la IA piensa el mejor movimiento", 46)

        nodos = {
            "raiz": (0, 2.3),
            "izq": (-2.9, 0.7),
            "der": (2.9, 0.7),
            "i1": (-3.9, -1.1),
            "i2": (-1.9, -1.1),
            "d1": (1.9, -1.1),
            "d2": (3.9, -1.1),
        }
        objs, crits = {}, {}
        for k, (x, y) in nodos.items():
            r = Circle(radius=0.44, stroke_color=ACENTO, stroke_width=3)
            r.set_fill(ACENTO, opacity=0.12)
            r.move_to([x, y, 0])
            objs[k] = r
            crits[k] = r

        self.play(LaggedStart(*[Create(c) for c in crits.values()], lag_ratio=0.14),
                  run_time=1.6)

        aristas = VGroup(
            Line(objs["raiz"].get_center(), objs["izq"].get_center(),
                 color=TENUE, stroke_width=3),
            Line(objs["raiz"].get_center(), objs["der"].get_center(),
                 color=TENUE, stroke_width=3),
            Line(objs["izq"].get_center(), objs["i1"].get_center(),
                 color=TENUE, stroke_width=3),
            Line(objs["izq"].get_center(), objs["i2"].get_center(),
                 color=TENUE, stroke_width=3),
            Line(objs["der"].get_center(), objs["d1"].get_center(),
                 color=TENUE, stroke_width=3),
            Line(objs["der"].get_center(), objs["d2"].get_center(),
                 color=TENUE, stroke_width=3),
        )
        self.play(LaggedStart(*[Create(a) for a in aristas], lag_ratio=0.18),
                  run_time=1.7)

        # puntajes de las hojas
        for k, v in [("i1", 3), ("i2", -1), ("d1", 5), ("d2", 2)]:
            num = Text(str(v), font_size=30, color=TEXTO).move_to(objs[k].get_center())
            self.play(FadeIn(num, scale=0.6), run_time=0.35)

        # el nodo toma el maximo de sus hijos
        for k, v in [("izq", 3), ("der", 5), ("raiz", 5)]:
            num = Text(str(v), font_size=34, color="#FFA600")
            num.move_to(objs[k].get_center())
            self.play(Transform(objs[k], num), run_time=0.7)

        elegida = Text("5", font_size=34, color="#7CFC00")
        elegida.move_to(objs["d1"].get_center())
        flecha = Arrow(objs["raiz"].get_center(), objs["d1"].get_center(),
                       buff=0.5, color="#7CFC00", stroke_width=5,
                       max_tip_length_to_length_ratio=0.12)
        self.play(Transform(objs["d1"], elegida), GrowFromCenter(flecha),
                  run_time=1.1)
        self.wait(0.6)