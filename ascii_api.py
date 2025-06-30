#ascii_api.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from ascii_converter import UnicodeArt

app = FastAPI()

# CORS 설정 (프론트엔드 연결 시 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ascii-art-2elb.onrender.com"],  # 실제 운영 시엔 특정 origin만 허용 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ascii")
async def convert_ascii(
    image: UploadFile = File(...),
    width: int = Form(100) # Form으로 width를 받도록 추가합니다. 기본값은 100
):
    contents = await image.read()
    art = UnicodeArt(lang='ascii')
    img_io = BytesIO(contents)

    # 받은 width 값을 image_to_ascii 함수에 전달합니다.
    ascii_text = art.image_to_ascii(img_io, width=width) # <-- 여기가 변경됩니다.
    result_img = art.ascii_to_image(ascii_text)

    buffer = BytesIO()
    result_img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")
