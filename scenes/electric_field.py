"""Electric field lines: opposite charges vs like charges."""

import numpy as np
from manim import *

from club_style import *

BOUNDS = (4.4, 4.8, -3.6)  # |x| limit, top y, bottom y of the field region
FIELD_CENTER = UP * 0.6
R = 0.3  # charge radius


def field(p, charges):
    e = np.zeros(3)
    for q, c in charges:
        d = p - c
        e += q * d / max(np.linalg.norm(d), 1e-3) ** 3
    return e


def trace(start, charges, sign=1, ds=0.03, steps=600):
    """Follow E (sign=+1) or -E from start. Returns (points, hit_charge_index or None)."""
    pts = [start]
    p = start.copy()
    for _ in range(steps):
        # midpoint (RK2) step along the unit field direction
        e = field(p, charges)
        mid = p + sign * 0.5 * ds * e / np.linalg.norm(e)
        e = field(mid, charges)
        p = p + sign * ds * e / np.linalg.norm(e)
        pts.append(p.copy())
        for i, (_, c) in enumerate(charges):
            if np.linalg.norm(p - c) < R * 0.9:
                return pts, i
        if abs(p[0]) > BOUNDS[0] or p[1] > BOUNDS[1] or p[1] < BOUNDS[2]:
            return pts, None
    return pts, None


def field_lines(charges, n=16, color=CYAN):
    lines = VGroup()
    for idx, (q, c) in enumerate(charges):
        for k in range(n):
            a = 2 * PI * (k + 0.5) / n
            start = c + R * np.array([np.cos(a), np.sin(a), 0])
            pts, hit = trace(start, charges, sign=1 if q > 0 else -1)
            # A line joining a + and a - charge is drawn once, from the + side.
            if q < 0 and hit is not None and charges[hit][0] > 0:
                continue
            if q < 0:
                pts = pts[::-1]
            line = VMobject(stroke_color=color, stroke_width=3).set_points_smoothly(pts[::3] + [pts[-1]])
            lines.add(line)
    return lines


def charge(q, pos):
    color = PINK if q > 0 else CYAN
    glow = Dot(pos, radius=R * 1.6, color=color).set_opacity(0.25)
    body = Dot(pos, radius=R, color=color)
    sign = txt("+" if q > 0 else "−", 40, BG, weight="BOLD").move_to(pos)
    return VGroup(glow, body, sign)


def arrowheads(lines, color):
    """Small arrows halfway along each line, pointing along the field."""
    heads = VGroup()
    for line in lines:
        p = line.point_from_proportion(0.5)
        q = line.point_from_proportion(0.52)
        if np.linalg.norm(q - p) > 1e-4:
            heads.add(Arrow(p - (q - p) * 4, q, buff=0, color=color, stroke_width=3,
                            max_tip_length_to_length_ratio=0.9, max_stroke_width_to_length_ratio=1))
    return heads


class ElectricField(ReelScene):
    def construct(self):
        self.intro("Electric Fields", "The invisible lines between charges")

        pos_l = FIELD_CENTER + LEFT * 1.8
        pos_r = FIELD_CENTER + RIGHT * 1.8

        # ---- single charge -----------------------------------------------
        single = [(1, FIELD_CENTER)]
        c0 = charge(1, FIELD_CENTER)
        l0 = field_lines(single, color=PINK)
        h0 = arrowheads(l0, PINK)
        cap = self.caption("A positive charge: field points outward", y=-4.4, size=32)
        self.play(FadeIn(c0, scale=0.3))
        self.play(LaggedStart(*[Create(l) for l in l0], lag_ratio=0.05), FadeIn(cap), run_time=2)
        self.play(FadeIn(h0))
        self.wait(2)

        # ---- dipole -------------------------------------------------------
        dipole = [(1, pos_l), (-1, pos_r)]
        cl, cr = charge(1, pos_l), charge(-1, pos_r)
        l1 = field_lines(dipole, n=18, color=PURPLE)
        h1 = arrowheads(l1, PURPLE)
        new = self.caption("Opposite charges: lines connect", y=-4.4, size=32, color=PURPLE, weight="BOLD")
        self.play(FadeOut(l0), FadeOut(h0), ReplacementTransform(c0, cl), FadeIn(cr, scale=0.3),
                  FadeTransform(cap, new))
        cap = new
        self.play(LaggedStart(*[Create(l) for l in l1], lag_ratio=0.04), run_time=2.5)
        self.play(FadeIn(h1))
        self.wait(1)

        # A small positive test charge rides along a field line.
        path = min(l1, key=lambda l: abs(l.point_from_proportion(0.5)[1] - (FIELD_CENTER[1] + 1.4)))
        test = Dot(path.get_start(), radius=0.12, color=ACCENT)
        tlabel = txt("test charge", 24, ACCENT).next_to(test, UP + LEFT, 0.1)
        hint = self.caption("A + charge follows the arrows", y=-5.0, size=28, color=ACCENT)
        self.play(FadeIn(test, scale=2), FadeIn(tlabel), FadeIn(hint))
        self.play(FadeOut(tlabel), MoveAlongPath(test, path), run_time=3, rate_func=smooth)
        self.play(FadeOut(test), FadeOut(hint))
        self.wait(0.5)

        # ---- like charges ------------------------------------------------
        like = [(1, pos_l), (1, pos_r)]
        cr2 = charge(1, pos_r)
        l2 = field_lines(like, n=16, color=PINK)
        h2 = arrowheads(l2, PINK)
        new = self.caption("Like charges: lines push apart", y=-4.4, size=32, color=PINK, weight="BOLD")
        self.play(FadeOut(l1), FadeOut(h1), ReplacementTransform(cr, cr2), FadeTransform(cap, new))
        cap = new
        self.play(LaggedStart(*[Create(l) for l in l2], lag_ratio=0.04), run_time=2.5)
        self.play(FadeIn(h2))
        mid = Dot(FIELD_CENTER, radius=0.08, color=ACCENT)
        mlabel = txt("field = 0 here", 26, ACCENT).next_to(mid, DOWN, 0.25)
        mlabel.add_background_rectangle(color=BG, opacity=0.85, buff=0.08)
        self.play(FadeIn(mid, scale=3), FadeIn(mlabel))
        self.wait(2.5)

        self.outro([
            "Field lines start on + charges",
            "and end on − charges.",
            "Closer lines = stronger field.",
        ])
