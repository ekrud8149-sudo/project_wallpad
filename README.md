Smart Wallpad System (Home Assistant 기반 IoT 출입 관리 시스템)
### *🎨 프로젝트 목표 !*
- Raspberry Pi + Touch Display 기반 Wallpad UI 구현
- Raspberry Pi와 7" Touch Display를 사용하여 homeassistant를 활용한 Wallpad 구현
- stm32과 arduino uno 보드를 사용하여 센서값 전달 및 mariaDB 저장


👨‍💻 담당 역할

STM32 보드에 버튼, 부저, 서보모터, LED 연결 및 Raspberry Pi 연동

Flask 기반 실시간 웹캠 스트리밍 및 캡처 시스템 구현

초인종 / 문열림 이벤트 MariaDB 저장

Home Assistant UI에 날짜, 시간, 날씨 표시

🎥 시연 영상
<iframe width="624" height="351" src="https://www.youtube.com/embed/M8JA2rLNz2I" title="통합 설비 관리 터치 월패드 시스템 시연영상" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
👉 https://youtu.be/M8JA2rLNz2I?si=XrtbHMHnrbMkMU0O

🖥️ UI 화면

<img width="803" height="448" alt="image" src="https://github.com/user-attachments/assets/8fc4b7bf-a7f1-4d54-9993-a0a4cba22d7e" />


## 기능

### **A. 제어 및 알림 (STM32 기반)**

- 사용자 인터랙션: 물리 버튼과 부저(Buzzer)를 이용해 초인종 역할
- 서보 모터 제어: 문열림 / 문닫힘 푸시버튼으로 제어
- 사용자 요청 기반 실시간 캡처 시스템  : HA 미디어에 저장
- 구역별 조명 제어: 거실, 안방, 2층 등 각 구역의 LED를 개별 또는 일괄적으로 제어

### **B. 보안 및 인증 (Arduino 기반)**

- RFID 사용자 인증:
사용자가 RFID를 태그할 때마다 집 / 외출 상태가 즉각적으로 토글되도록 로직을 설계
    
     LED / servo moter를 통해 시각적인 인증 피드백을 제공 
    

### **C. 모니터링 및 허브 (Raspberry Pi 4 기반)**

- 중앙 집중 제어: 터치 디스플레이를 통해 전체 시스템을 제어하는 대시보드 역할
- 실시간 영상 스트리밍: Flask 서버(Python) 기반의 웹캠 스트리밍 파이프라인을 구축
- 데이터 통합:
    
    Bridge 서버: STM32/Arduino의 Serial 데이터를 수집하여 MQTT 브로커로 변환 송신하는 Python 브릿지 파일 개발
    
    MariaDB : STM32와 Arduino로부터 받은 데이터를 Home Assistant로 전달하고 로그 기록

### **아키텍쳐**
<img width="1158" height="688" alt="image" src="https://github.com/user-attachments/assets/49691774-2c39-4b2e-9dd8-39367a17d5a7" />


📂 프로젝트 구조

├── cam_server.py
│   └── Flask 기반 웹캠 스트리밍 및 스냅샷 서버
│
├── bridge.py
│   └── Serial ↔ MQTT ↔ MariaDB ↔ Home Assistant 브릿지
│
├── homeassistant/
│   ├── configuration.yaml
│   └── automations.yaml
│
├── firmware/
│   ├── STM32/
│   └── Arduino/
│
└── database/
    └── MariaDB/
        ├── rfid_log    # 유저 재실 상태 로그
        ├── door_bell   # 초인종 이벤트 기록
        └── door_lock   # 도어락 상태 기록

        
🔧 기술 스택

Hardware

Raspberry Pi 4

STM32

Arduino Uno

RFID Module, Servo Motor, LED, Buzzer

Software

Python (Flask)

Home Assistant

MQTT

MariaDB

⚡ 데이터 흐름

STM32 / Arduino → Serial → Raspberry Pi

bridge.py → MQTT → Home Assistant

Home Assistant → 자동화 처리

이벤트 → MariaDB 저장

사용자 → UI (Touch Display)로 제어

🚧 문제 해결 경험
❗ Issue

PC 기반 Qt 환경과 Raspberry Pi 터치스크린 간
버전 불일치로 인해 의존성 문제가 발생

✅ Solution

Home Assistant 기반의 중앙 집중형 아키텍처로 전환

🎯 Result

장치 간 호환성 문제 해결

터치스크린 + 모바일 모두에서 접근 가능한 UI 구축

시스템 확장성 및 유지보수성 향상
