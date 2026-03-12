import sounddevice as sd
import numpy as np
import subprocess
import time
import os

# Новый путь
GAME_DIR = r'путь к папке с игрой'  # Укажите полный путь к папке с игрой, например: r'D:\pw'
START_BAT = r'путь к батнику'  # Укажите полный путь к start.bat, например: r'D:\pw\start.bat'

# Configuration
CLAP_DETECT_THRESHOLD = 0.12
SILENCE_THRESHOLD = 0.04
CLAP_DURATION_MIN = 0.015
CLAP_DURATION_MAX = 0.20
CHUNK_SIZE = 1024
CHANNELS = 1
RATE = 44100

class ClapLauncher:
    def __init__(self):
        self.is_clapping = False
        self.clap_start = 0
        self.last_launch = 0

    def launch_game(self):
        try:
            print(f"Проверяем {START_BAT}")
            if os.path.exists(START_BAT):
                print("Запуск start.bat...")
                subprocess.Popen(f'cd /d "{GAME_DIR}" && start.bat', shell=True)
            else:
                print("start.bat не найден!")
                return False
            return True
        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def audio_callback(self, indata, frames, time_info, status):
        audio_data = indata[:, 0] if indata.ndim > 1 else indata.flatten()
        volume = np.sqrt(np.mean((audio_data / 32768.0)**2))

        current_time = time.time()

        if frames % 150 == 0:
            print(f"V={volume:.3f}")

        if current_time - self.last_launch < 2:
            return None, False

        if volume > CLAP_DETECT_THRESHOLD:
            if not self.is_clapping:
                print(f"ХЛОПОК {volume:.3f}")
                self.is_clapping = True
                self.clap_start = current_time
            duration = current_time - self.clap_start
            if duration > CLAP_DURATION_MAX:
                print("*** ЗАПУСК ИГРЫ! ***")
                self.launch_game()
                self.last_launch = current_time
                self.is_clapping = False
        elif self.is_clapping and volume < SILENCE_THRESHOLD:
            duration = current_time - self.clap_start
            if CLAP_DURATION_MIN <= duration <= CLAP_DURATION_MAX:
                print("*** ЗАПУСК ИГРЫ! ***")
                self.launch_game()
                self.last_launch = current_time
            self.is_clapping = False

        return None, False

    def run(self):
        print("=== ХЛОПОК ЛАНЧЕР (D:\\pw\\start.bat) ===")
        print("Хлопок = запуск! Ctrl+C стоп.")
        
        try:
            with sd.InputStream(samplerate=RATE, channels=CHANNELS, dtype=np.int16, blocksize=CHUNK_SIZE, callback=self.audio_callback):
                print("Готов! Хлопни = D:\\pw\\start.bat")
                while True:
                    time.sleep(0.05)
        except KeyboardInterrupt:
            print("Стоп.")

if __name__ == "__main__":
    ClapLauncher().run()
