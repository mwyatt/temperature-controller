import RPi.GPIO as GPIO
GPIO_PIN = 8

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
#if GPIO.input(GPIO_PIN) == 1:
GPIO.setup(GPIO_PIN, GPIO.OUT)
GPIO.output(GPIO_PIN, False)
print(GPIO.input(GPIO_PIN))

if GPIO.input(GPIO_PIN) == 0:
    GPIO.cleanup()
