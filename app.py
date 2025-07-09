import streamlit as st
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration
import av
from cvzone.HandTrackingModule import HandDetector
import google.generativeai as genai
from PIL import Image
import threading

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f7faff 60%, #b3c6ff 100%);
    }
    .header-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 24px 32px 16px 32px;
        margin-bottom: 18px;
        box-shadow: 0 4px 16px rgba(37,117,252,0.10);
    }
    .header-title {
        color: #fff;
        font-size: 2.5em;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 0;
    }
    .header-desc {
        color: #e0e7ff;
        font-size: 1.2em;
        margin-top: 8px;
    }
    .answer-box {
        background: #fff;
        border-left: 8px solid #2575fc;
        border-radius: 12px;
        padding: 24px 20px;
        margin-top: 16px;
        font-size: 1.2em;
        color: #111;
        box-shadow: 0 2px 12px rgba(37,117,252,0.08);
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide", page_title="AI Math Gesture", page_icon="🖐️")

# Header
st.markdown("""
<div class="header-box">
    <div class="header-title">AI Math Gesture Recognition</div>
    <div class="header-desc">
        Gambarkan soal matematika dengan tangan di depan kamera,<br>
        dan dapatkan jawabannya secara otomatis!
    </div>
</div>
""", unsafe_allow_html=True)

# Konfigurasi Gemini API
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("API Key Gemini tidak ditemukan. Tambahkan ke secrets.toml")
    st.stop()

# RTC Configuration untuk deployment
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
    ]
})

class MathGestureTransformer(VideoTransformerBase):
    def __init__(self):
        self.detector = HandDetector(
            staticMode=False, 
            maxHands=1, 
            modelComplexity=1, 
            detectionCon=0.7, 
            minTrackCon=0.5
        )
        self.canvas = None
        self.prev_pos = None
        self.lock = threading.Lock()
        
    def getHandInfo(self, img):
        hands, img = self.detector.findHands(img, draw=False, flipType=True)
        if hands:
            hand = hands[0]
            lmList = hand["lmList"]
            fingers = self.detector.fingersUp(hand)
            return fingers, lmList
        return None

    def draw(self, info, img):
        if self.canvas is None:
            self.canvas = np.zeros_like(img)
            
        fingers, lmList = info
        current_pos = None
        
        # Jari telunjuk untuk menggambar
        if fingers == [0, 1, 0, 0, 0]:
            current_pos = lmList[8][0:2]
            if self.prev_pos is None:
                self.prev_pos = current_pos
            cv2.line(self.canvas, tuple(current_pos), tuple(self.prev_pos), (255, 0, 255), 10)
            self.prev_pos = current_pos
        
        # Jempol untuk menghapus
        elif fingers == [1, 0, 0, 0, 0]:
            self.canvas = np.zeros_like(img)
            self.prev_pos = None
        
        # Gesture untuk mengirim ke AI (thumb + index + pinky)
        elif fingers == [1, 1, 0, 0, 1]:
            self.sendToAI()
        
        else:
            self.prev_pos = None
        
        return current_pos

    def sendToAI(self):
        if self.canvas is not None:
            try:
                # Convert canvas to PIL Image
                pil_image = Image.fromarray(self.canvas)
                response = model.generate_content(["Selesaikan soal matematika ini", pil_image])
                
                # Store result in session state
                st.session_state.ai_result = response.text
            except Exception as e:
                st.session_state.ai_result = f"Error: {str(e)}"

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        with self.lock:
            info = self.getHandInfo(img)
            if info:
                self.draw(info, img)
            
            # Overlay canvas on image
            if self.canvas is not None:
                img = cv2.addWeighted(img, 0.7, self.canvas, 0.3, 0)
        
        return img

# Layout
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.markdown("### 📹 Kamera")
    st.markdown("""
    **Instruksi:**
    - ✋ **Jari telunjuk** = Menggambar
    - 👍 **Jempol** = Menghapus canvas
    - 🤟 **Jempol + Telunjuk + Kelingking** = Kirim ke AI
    """)
    
    # WebRTC Streamer
    webrtc_ctx = webrtc_streamer(
        key="math-gesture",
        mode="send-channel",
        rtc_configuration=RTC_CONFIGURATION,
        video_transformer_factory=MathGestureTransformer,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

with col2:
    st.markdown("### 🤖 Jawaban AI")
    
    # Display AI result
    if hasattr(st.session_state, 'ai_result') and st.session_state.ai_result:
        st.markdown(
            f"<div class='answer-box'>{st.session_state.ai_result}</div>", 
            unsafe_allow_html=True
        )
    else:
        st.info("Gambar soal matematika dengan gesture tangan, lalu gunakan gesture kirim untuk mendapatkan jawaban.")

# Instructions
st.markdown("""
---
### 📋 Cara Menggunakan:

1. **Izinkan akses kamera** ketika browser meminta
2. **Gambar soal matematika** dengan menggunakan jari telunjuk
3. **Hapus gambar** dengan menunjukkan jempol
4. **Kirim ke AI** dengan gesture jempol + telunjuk + kelingking
5. **Lihat hasil** di panel sebelah kanan

### ⚠️ Catatan Penting:
- Aplikasi ini memerlukan **HTTPS** untuk akses kamera
- Pastikan **pencahayaan cukup** untuk deteksi tangan yang optimal
- **Gesture harus jelas** dan stabil
""")

# Footer
st.markdown("""
---
<div style="text-align: center; color: #666; margin-top: 20px;">
    Powered by Streamlit WebRTC + Gemini AI + CVZone
</div>
""", unsafe_allow_html=True)