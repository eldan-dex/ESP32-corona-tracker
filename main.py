from machine import Pin, SPI
import st7789py as st7789
#import random

#Connects to the network
def netConnect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)

    sta_if.active(True)
    sta_if.connect('{ESSID}', '{PASSWORD}') #Fill in your wifi network name and password
    while not sta_if.isconnected():
            pass

#Retrieves JSON data from the web and returns them as a JSON object. Does not support any server-side compression.
def getWebData():
    import urequest
    import json

    url = "{YOUR JSON API URL}"
    data = urequest.urlopen(url).read().decode('utf-8', 'ignore')

    return json.loads(data)

#Aligns a numeric value to a given length
#pos -1: align left, pos 0: align center, pos 1: align right
def alignValue(value, desiredLen, pos):
    text = str(value)
    if pos == -1:
        return text + ' ' * (desiredLen - len(text))
    elif pos == 0:
        appended = False
        while len(text) < desiredLen:
            if appended:
                text = " " + text
            else:
                text = text + " "
            appended = not appended
        return text
    else:
        return ' ' * (desiredLen - len(text)) + text

def main():
    #Import fonts we'll be using
    from fonts import vga2_8x8 as smallfont
    from fonts import vga2_bold_16x16 as bigfont
    from fonts import vga2_bold_16x32 as biggestfont

    #Initialize the display
    tft = st7789.ST7789(
        SPI(2, baudrate=30000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(19)),
        135,
        240,
        reset=Pin(23, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(16, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=1)

    #Print init message to serial and display
    print("Corona tracker v1.1, Dex&Delly&Meow&jklk 03/2020")
    tft.text(smallfont, "Corona tracker v1.1", 5, 5,
        st7789.color565(255, 255, 255),
        st7789.color565(0, 0, 0)
    )
    tft.text(smallfont, "Dex&Delly&Meow&jklk 03/2020", 5, 20,
        st7789.color565(255, 255, 255),
        st7789.color565(0, 0, 0)
    )

    #Connect to WLAN
    netConnect()
    print("Connected to WLAN!")

    #Display loop
    import time
    bigDisplay = False
    apiUpdateIn = 0
    while True:
        if apiUpdateIn == 0:
             #Get API data (only once every 10 refreshes)
            inJson = getWebData()
            print("API Data retrieved!")

            #Keys and values might differ based on which API is used
            countTested = inJson['totalTested']
            countInfected = inJson['infected']
            countRecovered = inJson['recovered']
            countDead = 0 #TODO add proper readout once the API changes
            lastUpdate = inJson['lastUpdatedAtSource'].replace("T", " ").replace("Z", "")
            infectedPrague = inJson['infectedPrague']
            inJson = 0
            apiUpdateIn = 10

        else:
            apiUpdateIn = apiUpdateIn - 1

        #Clear the screen
        tft.fill(0)

        #Basic info
        if bigDisplay:
            #Only numbers (better visibility)
            tft.text(biggestfont, alignValue(countInfected, 5, -1), 5, 5,
                st7789.color565(255, 255, 255),
                st7789.color565(170, 170, 0)
            )

            tft.text(biggestfont, alignValue(countDead, 4, 0), 95, 5,
                st7789.color565(255, 255, 255),
                st7789.color565(170, 0, 0)
            )

            tft.text(biggestfont, alignValue(countRecovered, 4, 1), 170, 5,
                st7789.color565(255, 255, 255),
                st7789.color565(0, 170, 0)
            )

            tft.text(biggestfont, alignValue(infectedPrague, 5, -1), 5, 35,
                st7789.color565(255, 255, 255),
                st7789.color565(150, 140, 0)
            )

        else:
            #Full description (smaller text)
            tft.text(bigfont, "Infected: " + str(countInfected), 5, 5,
                st7789.color565(255, 255, 255),
                st7789.color565(170, 170, 0)
            )

            #tft.text(bigfont, "Prg: " + str(countInfected), 5, 25,
            #    st7789.color565(255, 255, 255),
            #    st7789.color565(170, 170, 0)
            #)

            tft.text(bigfont, "Dead: " + str(countDead), 5, 25,
                st7789.color565(255, 255, 255),
                st7789.color565(170, 0, 0)
            )

            tft.text(bigfont, "Recovered: " + str(countRecovered), 5, 45,
                st7789.color565(255, 255, 255),
                st7789.color565(0, 170, 0)
            )

        #Other info
        tft.text(bigfont, "Tested: " + str(countTested), 5, 65,
            st7789.color565(255, 255, 255),
            st7789.color565(0, 0, 170)
        )

        tft.text(smallfont, "Last Update: " + str(lastUpdate), 5, 90,
            st7789.color565(255, 255, 255),
            st7789.color565(0, 0, 0)
        )

        tft.text(smallfont, "Dex&Delly&Meow&jklk 03/2020", 5, 105,
            st7789.color565(255, 255, 255),
            st7789.color565(0, 0, 0)
        )

        #Sitch display style every 10s
        bigDisplay = not bigDisplay
        time.sleep(10)

main()
