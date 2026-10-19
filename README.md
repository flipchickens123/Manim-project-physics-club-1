# Physics Club Animations

Short physics explainers for the club's Instagram, made with
[Manim Community](https://www.manim.community/). Every video is a vertical
Reel (1080×1920, 30 fps) with the club branding, a title card, the
animation, and a closing "key idea" card.

| Reel | Scene | What it shows |
| --- | --- | --- |
| `projectile` | `ProjectileMotion` | Velocity split into x/y parts, then 5 launch angles: why 45° goes farthest and 30°/60° tie |
| `pendulum` | `Pendulum` | Swinging pendulum (numerically integrated) with live KE / PE / total energy bars and an angle–time graph |
| `waves` | `WaveInterference` | Constructive and destructive interference, then a standing wave with its nodes |
| `kepler` | `KeplerSecondLaw` | Elliptical orbit with real Kepler-equation timing; equal areas swept in equal times |
| `electric_field` | `ElectricField` | Field lines traced from Coulomb's law: single charge, dipole, like charges |

Finished videos and cover images are in [`exports/`](exports/), ready to upload.

## Setup

Only Python and Manim are needed. The scenes use `Text`, not LaTeX, so you
don't have to install a TeX distribution.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Manim also needs a few system libraries (Cairo, Pango, FFmpeg). See the
[Manim install guide](https://docs.manim.community/en/stable/installation.html).
On Ubuntu: `sudo apt install libcairo2-dev libpango1.0-dev ffmpeg pkg-config`.

## Rendering

```bash
python render.py --preview          # fast 540x960 drafts -> exports/preview/
python render.py                    # final 1080x1920 videos -> exports/
python render.py --cover kepler     # one reel, plus a cover image
```

## Customising

- **Branding:** edit `CLUB_NAME`, `HANDLE`, the colours, and the font at the top of `club_style.py`.
  Every reel picks up the change.
- **New reel:** subclass `ReelScene`, call `self.intro(title, subtitle)`, animate,
  then end with `self.outro([...lines...])`. Add the reel to `SCENES` in `render.py`.
- **Layout:** the frame is 9 × 16 units. Instagram's buttons and caption cover the
  top and bottom edges, so keep important content between `SAFE_TOP` (y = 6) and
  `SAFE_BOTTOM` (y = −5.2).
- **Physics parameters** (launch speed, pendulum length, orbit eccentricity, …)
  are constants at the top of each file in `scenes/`.
