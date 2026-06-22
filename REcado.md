// ============================================================
//  ARDUINO UNO - CHRONOS EXPRESS CONTROLLER v2.0
//  Com suporte a BUZZER para feedback sonoro
// ============================================================

const int joystickX = A0;    // Eixo X do joystick
const int joystickY = A1;    // Eixo Y do joystick
const int buttonPin = 2;     // Botão do joystick (Dash)
const int buzzerPin = 8;     // Buzzer para efeitos sonoros
const int ledPin = 13;       // LED interno para feedback

// Variáveis para controle
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

// Variáveis para controle do buzzer
bool buzzerActive = false;
unsigned long buzzerStartTime = 0;
int buzzerDuration = 0;
int buzzerFrequency = 0;

void setup() {
  // Inicializa comunicação serial
  Serial.begin(115200);
  
  // Configura pinos
  pinMode(joystickX, INPUT);
  pinMode(joystickY, INPUT);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(buzzerPin, OUTPUT);
  pinMode(ledPin, OUTPUT);
  
  // Toca um som de inicialização
  playTone(880, 100);  // Bip agudo curto
  delay(100);
  playTone(660, 100);
  
  Serial.println("READY"); // Sinaliza que o Arduino está pronto
}

void loop() {
  // ============================================================
  // 1. LEITURA DO JOYSTICK
  // ============================================================
  int x = analogRead(joystickX);
  int y = analogRead(joystickY);
  
  // Aplica filtro para evitar ruído
  x = smoothReading(x, joystickX);
  y = smoothReading(y, joystickY);
  
  // ============================================================
  // 2. LEITURA DO BOTÃO (com debounce)
  // ============================================================
  int buttonState = digitalRead(buttonPin);
  int buttonPressed = 0; // 0 = não pressionado, 1 = pressionado
  
  if (buttonState != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (buttonState == LOW) {
      buttonPressed = 1;
    }
  }
  lastButtonState = buttonState;
  
  // ============================================================
  // 3. ENVIA DADOS PARA O PC
  // ============================================================
  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.println(buttonPressed);
  
  // ============================================================
  // 4. FEEDBACK COM O LED (pisca quando o botão é pressionado)
  // ============================================================
  if (buttonPressed == 1) {
    digitalWrite(ledPin, HIGH);
    // Toca um som curto para feedback do dash
    if (buzzerActive == false) {
      playTone(1200, 80);
    }
  } else {
    digitalWrite(ledPin, LOW);
  }
  
  // ============================================================
  // 5. GERENCIAMENTO DO BUZZER
  // ============================================================
  if (buzzerActive) {
    unsigned long currentTime = millis();
    if (currentTime - buzzerStartTime >= buzzerDuration) {
      noTone(buzzerPin);
      buzzerActive = false;
    }
  }
  
  // ============================================================
  // 6. ESCUTA COMANDOS DO PC (para tocar sons sob demanda)
  // ============================================================
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "HIT") {
      // Toca som de impacto!
      playTone(200, 300);   // Tom grave
      delay(100);
      playTone(150, 250);   // Tom mais grave
    }
    else if (command == "SHIELD") {
      // Toca som de escudo ativado
      playTone(880, 150);
      delay(100);
      playTone(1100, 150);
    }
    else if (command == "POWERUP") {
      // Toca som de power-up coletado
      playTone(660, 100);
      delay(80);
      playTone(880, 100);
      delay(80);
      playTone(1100, 150);
    }
    else if (command == "DELIVERY") {
      // Toca som de entrega
      playTone(523, 100);
      delay(100);
      playTone(659, 100);
      delay(100);
      playTone(784, 150);
    }
    else if (command == "GAMEOVER") {
      // Toca som de game over (triste)
      playTone(440, 400);
      delay(300);
      playTone(349, 500);
    }
    else if (command == "VICTORY") {
      // Toca som de vitória (feliz)
      playTone(523, 150);
      delay(100);
      playTone(659, 150);
      delay(100);
      playTone(784, 150);
      delay(100);
      playTone(1047, 300);
    }
  }
  
  delay(5); // Pequeno delay para estabilidade
}

// ============================================================
// FUNÇÕES AUXILIARES
// ============================================================

/**
 * Toca um tom no buzzer
 * @param frequency - Frequência em Hz (ex: 440 = Lá)
 * @param duration - Duração em milissegundos
 */
void playTone(int frequency, int duration) {
  if (buzzerActive) {
    noTone(buzzerPin); // Para o som atual
    delay(10);
  }
  tone(buzzerPin, frequency, duration);
  buzzerActive = true;
  buzzerStartTime = millis();
  buzzerDuration = duration;
  buzzerFrequency = frequency;
}

/**
 * Filtro para suavizar a leitura do joystick
 */
int smoothReading(int currentValue, int pin) {
  static int lastValue = 512;
  int newValue = (lastValue * 3 + currentValue) / 4; // Média móvel
  lastValue = newValue;
  return newValue;
}
