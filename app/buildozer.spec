[app]
title           = KalamAI
package.name    = kalamAI
package.domain  = ai.kalam
source.dir      = .
source.include_exts = py,png,jpg,kv,atlas,json
version         = 1.0.0
entrypoint      = main.py
requirements = python3,kivy==2.3.0,numpy,requests,pillow
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE
android.minapi  = 21
android.api     = 33
android.ndk     = 25b
android.sdk     = 33
android.archs   = arm64-v8a
android.accept_sdk_license = True
orientation     = portrait
fullscreen       = 0
android.presplash_color = #7C3AED

[buildozer]
log_level = 2
warn_on_root = 1
