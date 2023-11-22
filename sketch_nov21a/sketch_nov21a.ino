 /**@brief Arduino code for RFID-based attendance system.
 *
 * This code reads RFID cards using MFRC522 and sends the card information to a Flask server
 * over Wi-Fi using ESP8266.
 *
 * Components:
 * - MFRC522 RFID module
 * - ESP8266 Wi-Fi module
 *
 * Dependencies:
 * - MFRC522 library for RFID: https://github.com/miguelbalboa/rfid
 * - ESP8266_AT library for ESP8266 communication: https://github.com/jandrassy/ESP8266_AT
 */

#include <MFRC522.h>
#include "ESP8266_AT.h"

const char* SSID = "lollollol";
const char* PASSWORD = "00000000";
const char* serverAddress = "your_server_ip"; // Replace with your server's IP address
const char* idsalle = "ST001";

/* Select Demo */
//#define RECEIVE_DEMO			/* Define RECEIVE demo */
#define SEND_DEMO				/* Define SEND demo */
#define SS_PIN 10
#define RST_PIN 9
MFRC522 mfrc522(SS_PIN, RST_PIN);
char _buffer[150];
uint8_t Connect_Status;
#ifdef SEND_DEMO
uint8_t Sample = 0;
#endif

void setup() {
  
  Serial.begin(115200);
  delay(10);
  mfrc522.PCD_Init();

//Connect to Wifi :
     while(!ESP8266_Begin());
    ESP8266_WIFIMode(BOTH_STATION_AND_ACCESPOINT);	/* 3 = Both (AP and STA) */
    ESP8266_ConnectionMode(SINGLE);     			/* 0 = Single; 1 = Multi */
    ESP8266_ApplicationMode(NORMAL);    			/* 0 = Normal Mode; 1 = Transperant Mode */
    if(ESP8266_connected() == ESP8266_NOT_CONNECTED_TO_AP)/*Check WIFI connection*/
    ESP8266_JoinAccessPoint(SSID, PASSWORD);		/*Connect to WIFI*/
    ESP8266_Start(0, serverAddress, 5000);	
}


void readRFID(){
  byte card_ID[10];//card UID size 4byte
  
  if ( ! mfrc522.PICC_IsNewCardPresent()) {//look for new card
    return;//got to start of loop if there is no card present
  }
  if ( ! mfrc522.PICC_ReadCardSerial()) {// Select one of the cards
    return;//if read card serial(0) returns 1, the uid struct contians the ID of the read card.
  }

  for (byte i = 0; i < mfrc522.uid.size; i++) {
    card_ID[i] = mfrc522.uid.uidByte[i];
  }
    #ifdef SEND_DEMO
  memset(_buffer, 0, 150);

  // Construct the JSON data
 String jsonData = "{\"idsalle\":\"" + String(idsalle) + "\",\"cardID\":\"" + String(reinterpret_cast<char*>(card_ID)) + "\"}";

  // Format the HTTP request with the JSON data
  sprintf(_buffer, "POST /get_rfid_data HTTP/1.1\r\n"
                   "Host: %s\r\n"
                   "Content-Type: application/json\r\n"
                   "Content-Length: %d\r\n\r\n"
                   "%s",
          serverAddress, jsonData.length(), jsonData.c_str());

  // Send the HTTP request using AT commands
  ESP8266_Send(_buffer);
  delay(1500); // Delay for server response 
#endif

  delay(2000); //delay 2secs
}


void loop() {
  // Connect to WiFi
  Connect_Status = ESP8266_connected();
  if (Connect_Status == ESP8266_NOT_CONNECTED_TO_AP) {
    ESP8266_JoinAccessPoint(SSID, PASSWORD);
  }

  // Reconnect to the server if disconnected
  if (Connect_Status == ESP8266_TRANSMISSION_DISCONNECTED) {
    ESP8266_Start(0, serverAddress, 80);
  }

  // Read RFID card every 2 secs
  readRFID();


}
