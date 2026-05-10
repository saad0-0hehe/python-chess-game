"""Procedurally generated sound effects – no external audio files needed."""
import pygame
import struct
import math
import io
import wave


class SoundManager:
    def __init__(self):
        pygame.mixer.init(44100, -16, 1, 512)
        self.enabled = True
        self._build_sounds()

    # ── helpers ─────────────────────────────────────────────────────
    @staticmethod
    def _make_wave(freq, dur, vol=0.5, wtype="sine", fade_out=True):
        sr = 44100
        n = int(sr * dur)
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            for i in range(n):
                t = i / sr
                if wtype == "sine":
                    v = math.sin(2 * math.pi * freq * t)
                elif wtype == "square":
                    v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
                else:
                    v = math.sin(2 * math.pi * freq * t)
                # envelope
                attack = min(1.0, i / 300)
                release = min(1.0, (n - i) / (n * 0.4)) if fade_out else 1.0
                s = int(v * vol * 32767 * attack * release)
                w.writeframes(struct.pack("<h", max(-32768, min(32767, s))))
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    @staticmethod
    def _make_compound(specs):
        """Mix several tones together."""
        sr = 44100
        max_n = max(int(sr * d) for _, d, _, _ in specs)
        mixed = [0.0] * max_n
        for freq, dur, vol, wtype in specs:
            n = int(sr * dur)
            for i in range(n):
                t = i / sr
                if wtype == "sine":
                    v = math.sin(2 * math.pi * freq * t)
                else:
                    v = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
                env = min(1.0, i / 300) * min(1.0, (n - i) / (n * 0.4))
                mixed[i] += v * vol * env
        peak = max(abs(x) for x in mixed) or 1
        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            for s in mixed:
                w.writeframes(struct.pack("<h", int(s / peak * 30000)))
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _build_sounds(self):
        self.snd_move      = self._make_wave(700, 0.07, 0.30)
        self.snd_capture   = self._make_compound([
            (250, 0.14, 0.5, "sine"), (500, 0.10, 0.3, "sine")
        ])
        self.snd_check     = self._make_compound([
            (1100, 0.10, 0.4, "sine"), (1400, 0.08, 0.3, "sine")
        ])
        self.snd_mate      = self._make_compound([
            (523, 0.25, 0.45, "sine"), (659, 0.25, 0.40, "sine"),
            (784, 0.35, 0.50, "sine"),
        ])
        self.snd_illegal   = self._make_wave(180, 0.18, 0.25, "square")
        self.snd_menu      = self._make_wave(600, 0.04, 0.15)
        self.snd_game_over = self._make_compound([
            (350, 0.4, 0.4, "sine"), (280, 0.5, 0.35, "sine"),
        ])

    # ── public API ──────────────────────────────────────────────────
    def _play(self, snd):
        if self.enabled:
            snd.play()

    def play_move(self):      self._play(self.snd_move)
    def play_capture(self):   self._play(self.snd_capture)
    def play_check(self):     self._play(self.snd_check)
    def play_mate(self):      self._play(self.snd_mate)
    def play_illegal(self):   self._play(self.snd_illegal)
    def play_menu(self):      self._play(self.snd_menu)
    def play_game_over(self): self._play(self.snd_game_over)

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled
