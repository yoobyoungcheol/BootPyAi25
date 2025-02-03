package edu.mbcai.pybootai.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.client.MultipartBodyBuilder;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.BodyInserters;
import org.springframework.web.reactive.function.client.WebClient;

@RestController             // 파이썬과 통신하는 비동기화 컨트롤러 역할 할당
public class RestReqController {

    @Autowired      // 생성자 자동 주입 (객체사용)
    private WebClient webClient;    // 방금 생성한 config 컨트롤러 객체 생성

    @PostMapping("/java_service")
    public String serviceRequest(MultipartFile file, String message){

        MultipartBodyBuilder bodyBuilder = new MultipartBodyBuilder(); // 멀티파트 폼 데이터를 구조
        bodyBuilder.part("message",message);                    // 폼데이터
        bodyBuilder.part("file",file.getResource());            // 폼데이터, 파일
        String result = webClient.post().uri("/detect")//POST 방식으로 요청, 엔드포인트는 /detect
                .contentType(MediaType.MULTIPART_FORM_DATA) // 파일이 전송되므로
                .body(BodyInserters.fromMultipartData(bodyBuilder.build()))//폼데이터를 요청 본문으로
                .retrieve()// 요청을 실행하고 응답을 받음
                .bodyToMono(String.class)   // 본문을 String 타입으로 변환
                .block();                   // 비동기처리를 동기적으로 블록해서 결과를 반환

        return result;

    } // http://localhost:80/java_service 요청 post 맵핑

    // 1. 자바 rest 컨트롤러로 텍스트와 이미지를 비동기 방식으로 전송
    // 2. ai 서버에서 이미지를 받아 객체 탐지를 수행
    // 3. ai 서버에서 이미지를 base64 인코딩 문자열로 변환
    // 4. rest 컨트롤러에서 비동기 방식으로 텍스트와 이미지를 변환
    // 5. 비동기 요청한 뷰 페이지에서 결과를 화면에 출력
}
