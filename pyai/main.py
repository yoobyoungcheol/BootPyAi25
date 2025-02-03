# pip install fastapi uvicorn pydantic Pillow numpy requests
# pip install ultralytics opencv-python python-multipart

# fastapi : 비동기 웹 프레임워크 자동으로 openapi 문서 생성
# uvicorn : 고성능 비동기 서버, ASGI 표준 지원
# pydantic : 데이터 검증 직렬화, 타입 힌팅 설정관리
# pillow : 이미지 열기, 저장, 반환, 다양한 이미지 처리용
# numpy : 수치계산, 배열 및 행렬 연산, 다양한 수학함수
# requests : 간단한 http 요청 및 응답 처리
# ultralytics : YOLOS 객체 탐지 모델 제공
# opencv-python : 이미지 및 비디오 처리 컴퓨터비젼 기능 (roboflow 대체)
# python-multipart : 멀티파트 폼 데이터를 파싱하기 위함

# uvicorn main:app --reload 로 실행

#######################################
# post 요청을 통해 이미지가 전송되면 인공지능 객체 탐지 모델을 이용해서 객체를 탐지하고
# 그결과 이미지를 base64 인코딩된 문자열로 반환하는 서비스를 만들어보자


# from fastapi import FastAPI
from fastapi import FastAPI, UploadFile, File, Form
# 라우팅, 파일 업로드, 폼데이터처리

from pydantic import BaseModel  # pydantic의 데이터 모델을 정의
import io                       # 파일 입출력을 위한 모델
import base64                   # 데이터를 Base64로 인코딩, 디코딩
# https://ko.wikipedia.org/wiki/%EB%B2%A0%EC%9D%B4%EC%8A%A464
from PIL import Image           # Pillow 이미지 처리 라이브러리
import numpy as np              # 배열 및 행렬 연산을 위한 라이브러리
from ultralytics import YOLO    # yolo8 모델 사용 울트라 리텍스
import cv2                      # 컴퓨터 비전 작업을 위한 라이브러리

app = FastAPI()

model = YOLO("yolov8n.pt")
# YOLOv8 모델 로드 (yolov8n.pt 모델의 가중치파일)

class DetectionResult(BaseModel):   # pydantic을 사용하여 데이터 모델을 정의 (응답 데이터 구조화)
    message: str                   # 클라이언트가 보낸 메세지
    image: str                     # Base64로 인코딩된 탐지 결과 이미지

# 객체 탐지 함수
# 객체 탐지를 위한 함수 정의로 모델에 이미지를 넣어 객체를 탐지하고
# 그 결과에서 바운딩 박스 정보를 추출한 후 이미지에 바인딩 박스와 클래스 이름, 신뢰도를 표시한 후 반환
def detect_objects(image: Image):
    img = np.array(image)                   # 이미지를 numpy 배열로 변환
    results = model(img)                    # 객체 탐지
    class_names = model.names               # 클래스 이름 저장

    #  결과를 바운딩 박스, 클래스이름, 정확도로 이미지에 표시
    for result in results:
        boxes = result.boxes.xyxy               # 바운딩 박스
        confidences = result.boxes.conf         # 신뢰도
        class_ids = result.boxes.cls            # 클래스 이름

        for box, confidences, class_ids in zip(boxes, confidences, class_ids):
            x1,y1,x2,y2= map(int,box)               # 좌표를 정수로 변환
            label = class_names[int(class_ids)]     # 클래스 이름
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(img,f'{label} {confidences:.2f}', (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)


    result_image = Image.fromarray(img)             # 결과 이미지를 PIL로 변환
    return result_image
    # 결론 : YOLO 모델로 객체 탐지 수행
    # 탐지된 객체에 대해 바운딩 박스를 그리고 정확도 점수를 이미지에 표시
    # 결과 이미지를 PIL 이미지로 변환하여 반환


@app.get("/") # get방식의 요청 테스트용 메시지를 json 형식으로 반환
async def need_root():
    return {"message":"Hello FastAPI"}

# 객체 탐지 엔드 포인트
@app.post("/detect",response_model=DetectionResult)
# async def detect_service(message: str = Form(...), file: UploadFile = File(...)):
async def detect_service(message: str = Form(...), file: UploadFile = File(...)):
    # 이미지를 읽어서 PIL 이미지로 변환
    image = Image.open(io.BytesIO(await file.read()))

    # 알파 채널 제거하고 GRB로 변환
    if image.mode == "RGBA" :
        image = image.convert('RGB')
    elif image.mode != 'RGB':
        image = image.convert('RGB')

    # 객체 탐지 수행
    result_image = detect_objects(image)

    # 이미지 결과를 base64로 인코딩
    buffered = io.BytesIO()
    result_image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return DetectionResult(message=message, image=img_str)
    # 결론 : http://localhost:8001/detect 경로에 post 요청 처리
    # 클라이언트로 업로드된 이미지를 읽고 PIL 이미지로 변환하고, 알파 채널이 있으면 알파 채널을 제거
    # https://developer.mozilla.org/ko/docs/Glossary/Alpha
    # 객체 탐지 함수를 호출하면 탐지 결과 이미지를 얻는다
    # 탐지 결과 이미지를 base64 문자열로 인코딩
    # DetectionResult 모델을 사용하여 메시지와 인코딩된 이미지를 json 응답으로 반환


# .py에 작성해서 실행하는 법
if __name__=="__main__":  # uvicorn main:app 인 경우 포트와 uvicorn 실행
    import uvicorn
    uvicorn.run(app,host="0.0.0.0", port=8001)

# 터미널에 작성 :  uvicorn main:app --reload

