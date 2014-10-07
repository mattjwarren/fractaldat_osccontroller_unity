import win32api, win32con
import time

def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def press_back():
    win32api.keybd_event(0x08,0,0,0) #click backspace
    time.sleep(0.1)
    win32api.keybd_event(0x08,0,2,0) #release backspace
    
def rgbint2rgbtuple(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return (red, green, blue)

click(100,200)
press_back()
color = win32gui.GetPixel(win32gui.GetDC(win32gui.GetActiveWindow()), 100 , 200)
