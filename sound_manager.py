"""Procedurally generated sound effects and background music."""
import pygame
import struct
import math
import io
import wave
import os
from constants import MUSIC_DIR


class SoundManager:
    def __init__(self):
        pygame.mixer.init(44100, -16, 1, 512)
        self.enabled = True
        self.music_enabled = True
        self._build_sounds()
        self._generate_music()

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

    # ── Background music generation ────────────────────────────────
    def _generate_music(self):
        """Generate a calm, looping ambient music track for the game."""
        os.makedirs(MUSIC_DIR, exist_ok=True)
        self._music_path = os.path.join(MUSIC_DIR, "ambient.wav")
        if os.path.isfile(self._music_path):
            return  # already generated

        sr = 44100
        # ~30 second loop – calm piano-like arpeggiated chords
        duration = 30.0
        n = int(sr * duration)
        samples = [0.0] * n

        # ── Chord progression (C Am F G — classic calm loop) ───────
        # Each chord lasts ~3.75 seconds (8 chords = 30 sec)
        chords = [
            [261.63, 329.63, 392.00],    # C  major (C E G)
            [261.63, 329.63, 392.00],    # C  major
            [220.00, 261.63, 329.63],    # Am (A C E)
            [220.00, 261.63, 329.63],    # Am
            [349.23, 440.00, 523.25],    # F  major (F A C5)
            [349.23, 440.00, 523.25],    # F  major
            [392.00, 493.88, 587.33],    # G  major (G B D5)
            [392.00, 493.88, 587.33],    # G  major
        ]
        chord_dur = duration / len(chords)
        chord_samples = int(sr * chord_dur)

        # ── Arpeggiate each chord ──────────────────────────────────
        note_dur = chord_dur / 3  # each note rings for 1/3 of chord
        note_samples = int(sr * note_dur)

        for ci, chord in enumerate(chords):
            chord_start = ci * chord_samples
            for ni, freq in enumerate(chord):
                note_start = chord_start + ni * note_samples
                # Each note: soft sine with gentle attack and long release
                note_len = int(note_dur * 2.5 * sr)  # let it ring longer
                for i in range(min(note_len, n - note_start)):
                    t = i / sr
                    # Soft sine + subtle overtone
                    v = 0.6 * math.sin(2 * math.pi * freq * t)
                    v += 0.2 * math.sin(2 * math.pi * freq * 2 * t)
                    v += 0.1 * math.sin(2 * math.pi * freq * 3 * t)
                    # Smooth envelope
                    attack = min(1.0, i / (sr * 0.08))
                    release = min(1.0, (note_len - i) / (sr * 0.6))
                    v *= attack * release * 0.18
                    idx = note_start + i
                    if idx < n:
                        samples[idx] += v

        # ── Add a very soft bass pad underneath ────────────────────
        bass_freqs = [130.81, 130.81, 110.00, 110.00,
                      174.61, 174.61, 196.00, 196.00]
        for ci, bf in enumerate(bass_freqs):
            chord_start = ci * chord_samples
            for i in range(chord_samples):
                t = i / sr
                v = 0.4 * math.sin(2 * math.pi * bf * t)
                attack = min(1.0, i / (sr * 0.3))
                release = min(1.0, (chord_samples - i) / (sr * 0.3))
                v *= attack * release * 0.10
                idx = chord_start + i
                if idx < n:
                    samples[idx] += v

        # ── Normalize and write WAV ────────────────────────────────
        peak = max(abs(x) for x in samples) or 1
        with wave.open(self._music_path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            for s in samples:
                val = int(s / peak * 28000)
                w.writeframes(struct.pack("<h", max(-32768, min(32767, val))))

    # ── Music playback API ─────────────────────────────────────────
    def start_music(self):
        """Start playing background music on loop."""
        if self.music_enabled and os.path.isfile(self._music_path):
            try:
                pygame.mixer.music.load(self._music_path)
                pygame.mixer.music.set_volume(0.25)
                pygame.mixer.music.play(-1)  # loop forever
            except Exception:
                pass

    def stop_music(self):
        """Stop background music."""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def toggle_music(self):
        """Toggle music on/off."""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.start_music()
        else:
            self.stop_music()
        return self.music_enabled

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
