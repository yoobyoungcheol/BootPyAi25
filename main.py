# 터미널에  uvicorn main:app --reload --port 8001 로 실행
# pip install fastapi uvicorn uvicorn
from pydoc import describe

from fastapi import FastAPI         # 파이썬웹 개발 api
from pydantic import BaseModel      # 유효성 검사용 파이단틱
from starlette.middleware.base import BaseHTTPMiddleware
# 요청과 응답 사이에 특정 작업 수행
# 마둘웨어는 모든 요청에 대해 실행되며, 요청을 처리하기 전에 응답을 반환하기 전에 특정 작업을 수행할 수 있음
# 예를 들어 로킹,인증,cors처리,압축등등...
import logging # 로그찍어주는 함수

# return {} : 제이슨 파일 리턴
app = FastAPI(    # 생성자를 통해 포스트맨을 대체하는 문서화 툴
    title="MBC AI 프로젝트 test",        # 내장된 포스트맵 사용후 꼮 주석 달아주기
    description="파이썬을 자바부트를 연동한 AI 앱",
    version="1.0.0",
    doce_url=None,           # http://localhost:8001/docs   # 보안상 none처리 한다
    # redoc_url=None         # http://localhost:8001/redoc  # 보안상 none처리 한다
)                     # FastAPI() : 객체 생성해서 app 에 넣음

class LoggingMiddleware(BaseHTTPMiddleware):    # 로그를 콘솔에 출력하는 용도 1 usage
    logging.basicConfig(level=logging.INFO)     # 로그 출력 추가
    async def dispatch(self, request, call_next):
        logging.info(f"Req : {request.method}{request.url}")
        response = await call_next(request)
        logging.info(f"Status Code : {response.status_code}")
        return response
app.add_middleware(LoggingMiddleware) # 모든 요청에 대해 로그를 남기는 미들웨어 클래스를 사용함

class Item(BaseModel):              # item 객채 생성(BaseModel : 객채 연결 => 상속 개념)
    name : str                      # 상품명 : 문자열
    description : str = None        # 상품 설명 : 문자열(null)
    price : float                   # 가격 : 실수형
    tax : float = None              # 세금 : 실수형(null)

# 컨트롤러 검증은 포스트맨으로 검증해 보았는데 내장된 백검증 툴도 있다

@app.get("/")     # http://주소:포트/ (루트컨텍스트)
async def reed_root():
    return {"HELLO" : "world"}

@app.post("/items/")                # post 매서드 응답
async def create_item(item: Item):  # BaseModel 은 데이터 모델링을 쉽게 도와 주고 유효성 검사를 시행 한다
                                    # 잘못된 데이터가 들어오면 422 오류 코드를 반환 한다
    return item

@app.get("/items/{items.id}") # http://주소:포트/items/1
async def reed_item(item_id: int, q: str = None):
    return {"item_id":item_id,"q":q}
    # item_id : 상품의 번호 -> 경로 매개 변수
    # q : 쿼리 매개 변수 (none)

