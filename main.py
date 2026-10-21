import os
import threading
import numpy as np
import soundfile as sf

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.slider import MDSlider

class AudioReverbApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Dark"
        
        self.selected_file = None
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_path,
            preview=False
        )

        layout = MDBoxLayout(orientation='vertical', spacing="15dp")
        toolbar = MDTopAppBar(title="Audio Reverb Studio")
        layout.add_widget(toolbar)
        
        content = MDBoxLayout(orientation='vertical', spacing="15dp", padding="20dp")
        
        # Статус
        self.status_label = MDLabel(
            text="Файл не выбран\nВыберите диктофонную запись (.mp3, .m4a, .wav)",
            halign="center", theme_text_color="Secondary"
        )
        content.add_widget(self.status_label)
        
        # Кнопка выбора
        select_btn = MDRaisedButton(
            text="ВЫБРАТЬ АУДИОФАЙЛ", pos_hint={"center_x": 0.5},
            on_release=self.open_file_manager
        )
        content.add_widget(select_btn)
        
        # Слайдер размера комнаты (Задержка эха)
        content.add_widget(MDLabel(text="Размер комнаты (Задержка эха):", theme_text_color="Hint"))
        self.delay_slider = MDSlider(min=50, max=300, value=150, step=10)
        content.add_widget(self.delay_slider)
        
        # Слайдер затухания (Отражение стен)
        content.add_widget(MDLabel(text="Поглощение звука (Длина эха):", theme_text_color="Hint"))
        self.decay_slider = MDSlider(min=0.1, max=0.8, value=0.45, step=0.05)
        content.add_widget(self.decay_slider)
        
        # Кнопка обработки
        self.process_btn = MDRaisedButton(
            text="ПРИМЕНИТЬ ЭФФЕКТ И СОХРАНИТЬ", pos_hint={"center_x": 0.5},
            disabled=True, on_release=self.start_processing_thread
        )
        content.add_widget(self.process_btn)
        
        layout.add_widget(content)
        return layout

    def open_file_manager(self, instance):
        path = "/storage/emulated/0/Download"
        if not os.path.exists(path):
            path = "/storage/emulated/0"
        self.file_manager.show(path)

    def select_path(self, path):
        self.exit_file_manager()
        if path.lower().endswith(('.mp3', '.m4a', '.wav', '.ogg', '.flac')):
            self.selected_file = path
            self.status_label.text = f"Выбран файл:\n{os.path.basename(path)}"
            self.process_btn.disabled = False
        else:
            self.status_label.text = "Ошибка: Выберите аудиофайл!"
            self.process_btn.disabled = True

    def exit_file_manager(self, *args):
        self.file_manager.close()

    def start_processing_thread(self, instance):
        if not self.selected_file: return
        self.status_label.text = "Обработка звука... Пожалуйста, подождите."
        self.process_btn.disabled = True
        threading.Thread(target=self.process_audio, daemon=True).start()

    def process_audio(self):
        try:
            output_path = "/storage/emulated/0/Download/reverb_result.wav"
            
            data, sample_rate = sf.read(self.selected_file)
            if len(data.shape) > 1: data = data[:, 0]
            samples = data.astype(np.float32)
            
            # Берем настройки прямо с экрана из ползунков!
            delay_ms = self.delay_slider.value
            decay = self.decay_slider.value
            num_reflections = 5
            
            extra_samples = int(sample_rate * (delay_ms / 1000.0) * num_reflections)
            output_samples = np.zeros(len(samples) + extra_samples, dtype=np.float32)
            output_samples[:len(samples)] = samples
            
            delay_samples = int(sample_rate * (delay_ms / 1000.0))
            for i in range(1, num_reflections + 1):
                shift = delay_samples * i
                current_decay = decay ** i
                output_samples[shift:shift + len(samples)] += samples * current_decay
                
            max_val = np.max(np.abs(output_samples))
            if max_val > 0:
                output_samples = (output_samples / max_val) * np.max(np.abs(data))
                
            sf.write(output_path, output_samples, sample_rate, format='WAV', subtype='PCM_16')
            self.status_label.text = f"Готово!\nФайл 'reverb_result.wav'\nсохранен в папку Загрузки!"
        except Exception as e:
            self.status_label.text = f"Ошибка:\n{str(e)}"
        finally:
            self.process_btn.disabled = False

if __name__ == '__main__':
    AudioReverbApp().run()
