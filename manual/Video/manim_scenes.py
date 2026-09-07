"""Escenas Manim animadas para insertar en el video del Triki.

Uso: manim -qh manim_scenes.py TableroScene  (1920x1080p30)
  luego el ensamblado copia los mp4 a work/clips/manim_s<N>.mp4 para
  sustituir el kenburns estático de los capítulos 14/16/17.
"""
from manim import *


class TableroScene(Scene):
    """El tablero 3x3 con X y O al ritmo de los movimientos."""

    def construct(self):
        bg = Rectangle(width=16, height=9, fill_color=BLUE_E, fill_opacity=1, stroke_opacity=0)
        self.add(bg)
        titulo = Text("El tablero del Triki", font_size=54, color=WHITE).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3))
        grid = VGroup()
        for i in range(3):
            for j in range(3):
                cell = Square(side_length=1.6, color=WHITE, fill_color=DARK_BLUE, fill_opacity=0.35)
                cell.move_to(np.array([(j - 1) * 1.7, (1 - i) * 1.7, 0]))
                grid.add(cell)
        self.play(LaggedStart(*[Create(c) for c in grid], lag_ratio=0.12))
        x = VGroup(
            Line(np.array([-0.6, 0.6, 0]), np.array([0.6, -0.6, 0]), color=RED, stroke_width=14),
            Line(np.array([0.6, 0.6, 0]), np.array([-0.6, -0.6, 0]), color=RED, stroke_width=14),
        )
        x.move_to(grid[0].get_center())
        o = Circle(radius=0.7, color=YELLOW, stroke_width=14).move_to(grid[4].get_center())
        self.play(Write(x), run_time=1.2)
        self.play(Create(o), run_time=1.2)
        linea = Line(grid[0].get_center(), grid[4].get_center(), color=GREEN, stroke_width=12)
        self.play(Create(linea), run_time=0.9)
        self.wait(1.2)


class MinimaxScene(Scene):
    """Árbol de juego reducido: valores minimax que suben hacia la raíz."""

    def construct(self):
        bg = Rectangle(width=16, height=9, fill_color=TEAL_E, fill_opacity=1, stroke_opacity=0)
        self.add(bg)
        titulo = Text("Minimax: la IA piensa el mejor movimiento",
                      font_size=42, color=WHITE).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3))
        # árbol: raíz -> 2 hijos -> 4 hojas con valores
        pos = {
            "r": np.array([0, 1.7, 0]),
            "h1": np.array([-2.6, 0.2, 0]),
            "h2": np.array([2.6, 0.2, 0]),
        }
        hojas = [
            (np.array([-3.9, -1.6, 0]), "3"),
            (np.array([-1.3, -1.6, 0]), "9"),
            (np.array([1.3, -1.6, 0]), "5"),
            (np.array([3.9, -1.6, 0]), "2"),
        ]
        nodos = {}
        raiz = Circle(radius=0.55, color=WHITE, fill_color=DARK_BLUE, fill_opacity=0.9).move_to(pos["r"])
        nodos["r"] = raiz
        for k in ("h1", "h2"):
            c = Circle(radius=0.55, color=WHITE, fill_color=DARK_BLUE, fill_opacity=0.9).move_to(pos[k])
            nodos[k] = c
        crits = {("r", "h1"): Line(pos["r"], pos["h1"], color=GREY_B, stroke_width=8),
                 ("r", "h2"): Line(pos["r"], pos["h2"], color=GREY_B, stroke_width=8)}
        h_objs = []
        for i, (hp, val) in enumerate(hojas):
            circ = Circle(radius=0.42, color=WHITE, fill_color=DARK_BLUE, fill_opacity=0.9).move_to(hp)
            num = Text(val, font_size=30, color=WHITE).move_to(hp)
            h_objs.append((circ, num))
            crits[("h" + ("1" if i < 2 else "2"), f"l{i}")] = Line(
                pos["h1"] if i < 2 else pos["h2"], hp, color=GREY_B, stroke_width=8)
        self.play(LaggedStart(*[Create(c) for c in crits.values()], lag_ratio=0.15), run_time=1.6)
        self.play(LaggedStart(*[Create(r) for r in nodos.values()], lag_ratio=0.3), run_time=1.0)
        self.play(LaggedStart(*[Create(c) for c, _ in h_objs], lag_ratio=0.12), run_time=1.2)
        vals = [t for _, t in h_objs]
        self.play(LaggedStart(*[Write(v) for v in vals], lag_ratio=0.15), run_time=1.2)
        # sube min de cada par -> h1=min(3,9)=3  h2=min(5,2)=2
        for nh, ha, hb in ((nodos["h1"], hojas[0], hojas[1]), (nodos["h2"], hojas[2], hojas[3])):
            etiqueta = Text(str(min(int(ha[1]), int(hb[1]))), font_size=30, color=YELLOW).move_to(
                nh.get_center() + np.array([-0.7, 0.5, 0]))
            self.play(FadeIn(etiqueta, shift=UP * 0.2), run_time=0.7)
        # raíz elige max = 3
        elegida = Text("3", font_size=30, color=GREEN).move_to(
            nodos["r"].get_center() + np.array([0.9, 0.6, 0]))
        flecha = Arrow(raiz.get_center() + np.array([0, 0, 0]),
                       raiz.get_center() + np.array([0, 0.8, 0]), color=GREEN, stroke_width=10)
        self.play(FadeIn(elegida), GrowFromCenter(flecha), run_time=1.0)
        tex = MathTex(r"\max(\min(3,9),\min(5,2)) = 3", font_size=40).to_edge(DOWN)
        self.play(FadeIn(tex), run_time=1.0)
        self.wait(1.6)


class CapasScene(Scene):
    """Las capas: Vista (Swing), Lógica (Juego) e IA (minimax)."""

    def construct(self):
        bg = Rectangle(width=16, height=9, fill_color=PURPLE_E, fill_opacity=1, stroke_opacity=0)
        self.add(bg)
        titulo = Text("Tres capas conectadas", font_size=50, color=WHITE).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3))
        cajas = [
            ("Tablero.java  (vista)", DARK_BLUE),
            ("Juego.java  (lógica)", TEAL_E),
            ("IA.java  (minimax)", MAROON_E),
        ]
        objs = []
        for i, (txt, color) in enumerate(cajas):
            box = RoundedRectangle(width=5.4, height=1.15, corner_radius=0.15,
                                   fill_color=color, fill_opacity=0.95,
                                   stroke_color=WHITE, stroke_width=4)
            lab = Text(txt, font_size=30, color=WHITE)
            g = VGroup(box, lab).move_to(np.array([0, 1.6 - i * 1.9, 0]))
            objs.append(g)
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.4) for g in objs], lag_ratio=0.35), run_time=2.0)
        flechas = [
            Arrow(objs[0].get_bottom(), objs[1].get_top(), color=YELLOW, stroke_width=9),
            Arrow(objs[1].get_bottom(), objs[2].get_top(), color=YELLOW, stroke_width=9),
        ]
        self.play(LaggedStart(*[GrowArrow(a) for a in flechas], lag_ratio=0.4), run_time=1.4)
        nota = Text("El clic llama a la lógica → la IA decide",
                    font_size=30, color=WHITE).to_edge(DOWN)
        self.play(FadeIn(nota), run_time=0.8)
        self.wait(1.6)