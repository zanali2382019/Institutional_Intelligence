import os
import json
import base64
import requests
import subprocess
from pathlib import Path

proxy_url = "https://cxl-services.appspot.com/proxy?url=https://texttospeech.googleapis.com/v1beta1/text:synthesize&token=0cAFcWeA7rNbGGYI0Lhmdiax3ftJAFxOLK3yvtsso2ueQje30gJHvOux3Kbh4SbbMfLuSgm00MspAIXHo9JzXSS5YZmICBLVeFJOqjI1NfFsTmNEesE_HXjh3V2b7iHmZ2wQPWpM1PeOeS07bdzyQCsqbpjO3bUj9mqWSmHOJxjj0u4GTiK5MhF2EIDaNIIrnGUOsdJUBJyVeWIejlQhNh4Ib8I7nD2S2Ub89L16xqUdOph0imhJGVydqhUGiieYrKu25oFfGEzGjwQW_5ioZDIOTl-OOETbjToc_cXC4G_bu4kJ9YM1O7J07pdlFEZkulxb7RG0NcNJv8LOvrLFrcckyl1FMMV-K9K91qSkAUVZcJctbnsuLYodWJheb2sNsEGWLs85egvBZdL8bzVfimHbha8Wvu8fyqDWsGenzmrFSbKSb5Ibr3uBfk0IaSG3DdiNS92ZJCx7U1cIQbJvO-uvKwYpX-BhDO4igmDKAQ_Z2u1Hs3dcjrwa-HUZdTYb5RkAZYWDr4iOy0yLlihPQJJqDDVmx6c8zNH2qRUNAdS2ZtIfnhBe6HWix0ujVV6-7qFINg5XvuP1oj4IbcjvxC2HHY_tzn8ip8KiMszFPCOuLUe82yolqXJIV9vhhKBLG9hyWHOsua8Z6AtpIBisjBAYcyCLPF0qDmQpWE3VL4bA5mdClMUd70xZjWDccozZeKeuNNfqbq7RSHmTiJR9g07G8lXivtkQJICp8dE0x4DTZ142vA6K8h3rP_s9ui1JHG3Z3aLm0BeCWXpQ8gjsjjsslQsETxOKy9lSpliia6BzR3xztvZjOMbsI4ctyN5CAcuYfdMC_NRhp5Tp5ypW0cHwaZWFABmSPEaD814_vSGn65Mg1zL8KEF6TXpNR-sTOLy23BglIJG1EBqCGoqA3RjxqevNx5qX4NdIIXM_nfHPb9eQrFNADQYy1ZyYVzn6cFgxwXOIZvDCGVVFWiTTYNgObS8oVkE6fjhE7OFJHDDsG8io78X3Hoy6xndypquDViyrJGNfihiBzYHzE2T8RasHoRPrHUP3oVMcoq_uEHR-S15hmYwZWfzZe_97LVfj8SjnqrYiL1SQGq8oFGf5jbyvrGKr8Zfo135ekhZwMEkm4yJ5v28dY_eS4JE53T4PusedcVfDeExavfOVuuX_D02fJUAmRs8KkbgiKqo5pl9QrAA6eLkm4vEpNxPm1BVmgv1uXDEiw8XRp2NzCZO0jvDITTfTJ0f4Ge2cWlZjR0XBEJVu-cE7XTjljRKI4-F_u8Kf1ly---vccqwSePPzM9BHFJUi3IukVK343Mgl2wThaaFwQOpGip57BK4Q40ZrcHZrcNkE42P-yr6bH_pBCoQppUoj6rtg48k74GzvYqtFu7NngS37AKbhvXqI2Ui-a6P8GZsi9mtRtMfpbgIttoAW9X0wEc8onkRBUSIGdTSGD-YjlA1nqBi5qkFkoxiJNLag7pe1GDvgwhktrYaDqbgAPYep0rD44LLsfGAx0tsIp3qcLVOrNqWdqkN2bDF4kE8d64oddbLXCrI7rTH5HGehWmeGmgEPy6gmzBCLmeKNsJEZEhGLl9VnnKA2UBP05fOFkTfhQULO2l9TY_8A63uhCiJDcOH6mzzt-Hx2farxevnUb6QWsU2_aeaIyxpS2UTwIfeaQGVgdmnAOALOMc5MyZA2S7F4dmvCCNCfwzM8ElHOkDhHLv_8PEmuV6Be-s-YeGORlBy96fXq2icCstOchM-c3v3p98kUejbzIs6Qeh6Poozbrs8Yy7tdbgz2xf80zzQcCsRgQXfzdY7BZKy83WLczuR9WiwPQh6CXjUfETVXXOf8ils9GtYTX53EtXHH9FXeskaByRsXRQHv6jW10SZZbY_t7r7ITJY2hSveLtgB5SAp_MG0o_iXqeFKPyWFJpJZ3x8VSjVnPxy_UDNbzhJ9rvtKG-WOW_3GxhgbDeM20zf-a3JSuvy0BslS2agzTLB--9-ru-SJ_Mx8frYiYN1rHjZBNls0SZuu052XqoLW1O1R2rjAx9TU0WcukqTF-JHVr2IagAskLBznI2_g8HClJ6-8Zj9axobFphFGqIZLs8vi91AJkyyaFTM9vAv_ZeArsNjNm4Yv9YtEyjrcWeKNdLGZaLwCd6IliaQJWKMWegmBjJZ4jx-R81UtYvXVH8cSUXbH1N8Aas-tz3Tyy36OMINHYXsQiaGB9-SJ-p4MP4D7T-yVZrrLZlm_PIeQdrsgFAhHAhQNPlneaS361vCwYhiqnWQa94K1cx6N7-f_PKWYDg0joDv7vFW4i_PJiMSxgTYjhGKouxU91O8LDrHRdEXzUNd7rUZ9PPHKbGC1GiZjpNfag"

headers = {
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://www.gstatic.com",
    "Referer": "https://www.gstatic.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
}

out_dir = Path(r"e:\my Office\youtube channel\قناة الذكاء المؤسسي\03_الفيديوهات_الطويلة_والشروحات\حلقات_الموسم_الأول\حلقة_تحديثات_ERPNext_v16_60")

# Regenerate p1a with ERP capital letters and نكست
p1a_text = """في عالمِ الأعمالِ الحديث، لم تعدِ المعركةُ تدورُ حولَ مَن يمتلكُ نظامَ ERP تقليدي... بل مَن يمتلكُ نظاماً يفكرُ ويتنبأُ قبلَ الجميع! أطلقتْ مجتمعاتُ فرابي، و ERP نكست، تحديثَها الأضخمَ لهذا العام: الإصدارَ السادسَ عشر، النسخةَ ستين. تحديثٌ لا يكتفي بإصلاحِ الأخطاء، بل يعيدُ كتابةَ قواعدِ إدارةِ المؤسساتِ إلى الأبد. أهلاً بكم في قناةِ إتقان — الذكاءُ المؤسسي. رحلتُكم نحو إدارةِ الأعمالِ الذكيةِ والتحولِ الرقمي."""

out_wav = out_dir / "v3_p1a_raw.wav"
payload = {
    "input": {"text": p1a_text},
    "voice": {
        "languageCode": "ar-XA",
        "name": "ar-XA-Chirp3-HD-Charon"
    },
    "audioConfig": {
        "audioEncoding": "LINEAR16",
        "pitch": 0,
        "speakingRate": 1.04
    }
}

print(f"[*] Re-synthesizing p1a with English letters ERP + نكست...")
r = requests.post(proxy_url, headers=headers, json=payload, timeout=60)
print(f"[*] Response status: {r.status_code}")
if r.status_code != 200:
    print(f"[!] Error: {r.text[:500]}")
    exit(1)

data = r.json()
b64_audio = data.get("audioContent")
raw_wav = base64.b64decode(b64_audio)
out_wav.write_bytes(raw_wav)
print(f"[OK] Saved {out_wav} ({len(raw_wav)/1024:.1f} KB)")

# Concat p1a + p1b + v2_p2 + v2_p3 + v2_p4
all_parts = ["v3_p1a_raw.wav", "v3_p1b_raw.wav", "v2_p2_raw.wav", "v2_p3_raw.wav", "v2_p4_raw.wav"]
concat_file = out_dir / "concat_charon_v5.txt"
with open(concat_file, "w", encoding="utf-8") as f:
    for w in all_parts:
        f.write(f"file '{w}'\n")

final_mp3 = out_dir / "voiceover_v16_chirp3_charon_master.mp3"
final_wav = out_dir / "voiceover_v16_chirp3_charon_master.wav"

ffmpeg_exe = r"C:\Users\96777\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.2-full_build\bin\ffmpeg.exe"
if not os.path.exists(ffmpeg_exe):
    ffmpeg_exe = "ffmpeg"

print("[*] Rebuilding Master MP3 & WAV with 'ERP نكست'...")
cmd_mp3 = [
    ffmpeg_exe, "-y",
    "-f", "concat", "-safe", "0",
    "-i", str(concat_file),
    "-c:a", "libmp3lame", "-b:a", "192k",
    "-ar", "48000",
    str(final_mp3)
]
subprocess.run(cmd_mp3, check=True)

cmd_wav = [
    ffmpeg_exe, "-y",
    "-f", "concat", "-safe", "0",
    "-i", str(concat_file),
    "-c:a", "pcm_s16le",
    str(final_wav)
]
subprocess.run(cmd_wav, check=True)

print(f"[SUCCESS] Perfect Charon Master saved to: {final_mp3} ({final_mp3.stat().st_size/1024:.1f} KB)")
