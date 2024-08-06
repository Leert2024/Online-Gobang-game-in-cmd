import ctypes
from sys import stdout
STD_OUTPUT_HANDLE = -11
handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

class COORD(ctypes.Structure):
    _fields_ = [("X",ctypes.c_short),("Y",ctypes.c_short)]

def goto_x_y(x, y):
    coord = COORD(x, y)
    ctypes.windll.kernel32.SetConsoleCursorPosition(handle, coord)

def set_color(color):
    ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)

if __name__ == "__main__":
    goto_x_y(10,10)
    set_color(0x0a)
    print("我阐述你的梦！")
    goto_x_y(10,10)
    set_color(0x0b)
    print("我吃柠檬！")
    input()
    
