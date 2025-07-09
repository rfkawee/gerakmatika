import cvzone
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import google.generativeai as genai
from PIL import Image
import streamlit as st

# Custom CSS for background and style
st.markdown("""
    <style>
    body, .main {
        background: #f8fafc;
    }
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
    .stButton>button {
        color: white;
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        border-radius: 8px;
        font-weight: bold;
    }
    .stCheckbox>div {
        color: #2575fc;
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

# Main title and description (tanpa sidebar)
st.markdown("""
<div class="header-box">
    <div class="header-title">AI Math Gesture Recognition</div>
    <div class="header-desc">
        Gambarkan soal matematika dengan tangan di depan kamera,<br>
        dan dapatkan jawabannya secara otomatis!
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3,2], gap="large")
with col1:
    run = st.checkbox('Aktifkan Kamera', value=True, help="Aktifkan kamera untuk mulai menggambar soal matematika.")
    FRAME_WINDOW = st.image([])
with col2:
    st.markdown("### Jawaban AI")
    output_placeholder = st.empty()

genai.configure(api_key="AIzaSyCTRpz_zZWDiu6I1AZqKMRJDGVYYmnOefs")
model = genai.GenerativeModel('gemini-1.5-flash')

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

detector = HandDetector(staticMode=False, maxHands=1, modelComplexity=1, detectionCon=0.7, minTrackCon=0.5)

def getHandInfo(img):
    hands, img = detector.findHands(img, draw=False, flipType=True)
    if hands:
        hand = hands[0]
        lmList = hand["lmList"]
        fingers = detector.fingersUp(hand)
        print(fingers)
        return fingers, lmList
    else:
        return None

def draw(info,prev_pos,canvas):
    fingers, lmList = info
    current_pos= None
    if fingers == [0, 1, 0, 0, 0]:
        current_pos = lmList[8][0:2]
        if prev_pos is None: prev_pos = current_pos
        cv2.line(canvas,current_pos,prev_pos,(255,0,255),10)
    elif fingers == [1, 0, 0, 0, 0]:
        canvas = np.zeros_like(img)
    return current_pos, canvas

def sendToAI(model,canvas,fingers):
    if fingers == [1,1,0,0,1]:
        pil_image = Image.fromarray(canvas)
        # response = model.generate_content(["Solve this math problem", pil_image])
        response = model.generate_content(["Selesaikan soal matematika ini", pil_image])
        return response.text

prev_pos= None
canvas=None
image_combined = None
output_text= ""
while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    if canvas is None:
        canvas = np.zeros_like(img)

    info = getHandInfo(img)
    if info:
        fingers, lmList = info
        prev_pos,canvas = draw(info, prev_pos,canvas)
        output_text = sendToAI(model,canvas,fingers)

    image_combined= cv2.addWeighted(img,0.7,canvas,0.3,0)
    FRAME_WINDOW.image(image_combined,channels="BGR")

    if output_text:
        output_placeholder.markdown(
            f"<div class='answer-box'>{output_text}</div>", unsafe_allow_html=True
        )

    cv2.waitKey(1)