#include <SPI.h>
#include <MFRC522.h>
//#include <Servo.h>   
 
#define RST_PIN   9
#define SS_PIN    10
#define LED1   4
#define LED2   3



//Servo SG90; 
MFRC522 rc522(SS_PIN, RST_PIN);

// int sg90 = 6;
// int i=0;

void setup(){
  Serial.begin(115200);
  SPI.begin();
  rc522.PCD_Init();
  
  //SG90.attach(sg90);          ++
  pinMode(LED1, OUTPUT);    
  pinMode(LED2, OUTPUT); 

  Serial.println("RFID Reader Initialized...");     
  rc522.PCD_DumpVersionToSerial();         
}

void loop(){
  digitalWrite(LED1, LOW);   
  digitalWrite(LED2, LOW);   

  if ( !rc522.PICC_IsNewCardPresent() || !rc522.PICC_ReadCardSerial() ) { 
    //카드 또는 ID 가 읽히지 않으면 return을 통해 다시 시작하게 됩니다.
    delay(500);
    return;
  }
  
  Serial.print("Card UID:");
  
  for (byte i = 0; i < 4; i++) {
    Serial.print(rc522.uid.uidByte[i]);
    Serial.print(" ");
  }
  Serial.println(" ");

  if(rc522.uid.uidByte[0]==227  && rc522.uid.uidByte[1]==81 && rc522.uid.uidByte[2]==77 
    && rc522.uid.uidByte[3]==5) {  // 여기에 CARD UID 를 자신의 카드에 맞는 값으로 변경해주세요
    
    Serial.println("<< OK !!! >>  Registered card...");
    Serial.println("USER1_TAGGED");

    digitalWrite(LED2, HIGH);
    delay(2000);              // 2초 동안 켜진 상태 유지
    digitalWrite(LED2, LOW);  // 2초 후 끔
    
    // for(i=0; i<=180; i++){        //0부터 180까지 1씩 증가
    //   SG90.write(i);
    //   delay(10);
    // }
    // for(i=180; i>0; i--){         //180부터 0까지 1씩 감소
    //   SG90.write(i);
    // delay(10);
    // }
    // delay(500);
  }

    else if(rc522.uid.uidByte[0]==222  && rc522.uid.uidByte[1]==55 && rc522.uid.uidByte[2]==77 
    && rc522.uid.uidByte[3]==5) {  // 여기에 CARD UID 를 자신의 카드에 맞는 값으로 변경해주세요
    
    Serial.println("<< OK !!! >>  Registered card...");
    Serial.println("USER2_TAGGED");

    digitalWrite(LED2, HIGH);
    delay(2000);              // 2초 동안 켜진 상태 유지
    digitalWrite(LED2, LOW);  // 2초 후 끔
    
  }

  else{
    
    Serial.println("<< WARNING !!! >>  This card is not registered");
    digitalWrite(LED1, HIGH);
    delay(2000);              // 2초 동안 켜진 상태 유지
    digitalWrite(LED1, LOW);  // 2초 후 끔
  }

  delay(100);
}