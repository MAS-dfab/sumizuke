import sensor
from machine import ADC
from pyb import LED
import time
from ssd1306 import write_text, intro, write_text_center
from mqtt_as import MQTTClient
from mqtt_local import wifi_led, blue_led, config
import uasyncio as asyncio
import json
import gc

MQTT_SERVER = "test.mosquitto.org"
MQTT_PORT = 1883
MODE_TOPIC = "craftsx/mode"
ID_TOPIC = "craftsx/id"
IMAGE_TOPIC = "craftsx/img"
TCP_TOPIC = "craftsx/tcp"
text = None
old_text = None
long_click_tcp = 0
parallel_click = 0
align_number = 0
mode_message = 0
free_pin = ADC("PC4")
tcp_pin = ADC("PF3")
redLED = LED(1)
greenLED = LED(2)
blueLED = LED(3)
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.HVGA)
sensor.ioctl(sensor.IOCTL_SET_FOV_WIDE, True)
sensor.set_windowing((320, 320))
sensor.skip_frames(time=500)


def sub_cb(topic, msg, retained):
    global text
    global old_text
    text = msg.decode("utf-8")
    if text:
        write_text_center(text)
        old_text = text
        text = None


async def heartbeat():
    s = True
    while True:
        message = decide_mode()
        print(message)
        await client.publish(MODE_TOPIC, json.dumps(message), qos=0)
        await asyncio.sleep_ms(500)
        blue_led(s)
        s = not s


async def wifi_han(state):
    wifi_led(not state)
    await asyncio.sleep(1)


async def conn_han(client):
    await client.subscribe(ID_TOPIC, 1)


def pinvalue(pinout):
    if pinout.read_u16() > 53000:
        return 0
    else:
        return 1


def decide_mode():
    global mode_message
    if parallel_click:
        mode_message = 3
    else:
        mode_message = 2
    return mode_message


async def take_a_pic():
    redLED.on
    greenLED.on
    blueLED.on
    img = sensor.snapshot()
    img = img.compress(quality=35)
    await client.publish(IMAGE_TOPIC, bytearray(img.to_jpeg()))
    del img
    gc.collect()
    await asyncio.sleep_ms(500)


async def main(client):
    global old_text
    global long_click_tcp
    global parallel_click
    global align_number
    try:
        await client.connect()
    except OSError as e:
        print("Connection failed.", e)
        return
    while True:
        await asyncio.sleep_ms(500)
        if pinvalue(tcp_pin):
            start = time.ticks_ms()
            while pinvalue(tcp_pin):
                if time.ticks_diff(time.ticks_ms(), start) > 2000:
                    if pinvalue(free_pin):
                        parallel_click = (parallel_click - 1) * -1
                        if parallel_click:
                            long_click_tcp = 0
                            write_text_center("designit!")
                            await asyncio.sleep_ms(2000)
                        else:
                            long_click_tcp = 1
                            await client.publish(
                                TCP_TOPIC, json.dumps("RESET_ALIGNMENT"), qos=0
                            )
                            write_text_center("alignit!")
                            await asyncio.sleep_ms(2000)
                            align_number = 0

            if long_click_tcp == 0:
                # Design mode
                if old_text != None:
                    id = "3" + "," + old_text
                    await client.publish(TCP_TOPIC, json.dumps(id), qos=0)
                    write_text_center("ID sent !")
                    await asyncio.sleep_ms(2000)
                    old_text = None
                    del id
                    gc.collect()
                else:
                    write_text_center("no marker")
                    await asyncio.sleep_ms(1000)
            else:
                if old_text != None:
                    # Align mode
                    id = "2" + "," + old_text
                    await client.publish(TCP_TOPIC, json.dumps(id), qos=0)
                    write_text_center("ID sent !")
                    await asyncio.sleep_ms(2000)
                    align_number += 1
                    if align_number == 3:
                        write_text_center("aligned")
                        await asyncio.sleep_ms(2000)
                        long_click_tcp = 0
                        align_number = 0
                    old_text = None
                    del id
                    gc.collect()
                else:
                    write_text_center("no marker")
                    await asyncio.sleep_ms(1000)
        asyncio.create_task(take_a_pic())
        gc.collect()
        await asyncio.sleep_ms(100)
        if old_text == None:
            write_text_center("marker?")
            await asyncio.sleep_ms(100)
        elif pinvalue(free_pin):
            write_text_center("lock " f"{old_text}")
            await asyncio.sleep_ms(100)


write_text("")
intro("***GKR***")
time.sleep(0.5)
write_text("")
time.sleep(0.5)
write_text_center("KR_CraftX")
time.sleep(1.5)
write_text("")
time.sleep(0.5)
print("initialize")
config["subs_cb"] = sub_cb
config["wifi_coro"] = wifi_han
config["connect_coro"] = conn_han
config["clean"] = True
MQTTClient.DEBUG = True
client = MQTTClient(config)
asyncio.create_task(heartbeat())
gc.collect()
try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()
