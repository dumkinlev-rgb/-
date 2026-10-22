[app]
title = Audio Reverb
package.name = audioreverb
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,kivymd,numpy,soundfile,openssl

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# Запрашиваем доступ к чтению и записи медиафайлов в память Android
android.permissions = WRITE_EXTERNAL_STORAGE, 
log_level = 2
