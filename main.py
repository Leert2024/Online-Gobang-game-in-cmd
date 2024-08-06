from socket import *
mysocket = socket(AF_INET,SOCK_STREAM)

if_server = 0

import keyboard
from time import sleep

#引入fprint.py文件以方便进行指定位置、指定颜色输出
import fprint

import sys
from os import system
from random import randint
from setup import *
if HEIGHT < 5 :
    HEIGHT =5
if WIDTH < 5:
    WIDTH = 5

from sys import stdout
status = 2
#status状态：2为等待，1为游戏进行中且可落子，3为等待对方落子，0为游戏结束但未退出，-1为退出

recent_x = int((WIDTH-1)/2)
recent_y = int((HEIGHT-1)/2)
board = []
chess_type = 0

def call(x):
    global status,recent_x,recent_y,chess_type,data,if_server

    #游戏开始前的等待阶段
    if status == 2:
        if x.event_type == 'down' and x.name == 's':
            if_server = 1
            IP = str(input("Input your IP address:"))
            PORT = int(input("Input your port:"))
            mysocket.bind((IP,PORT))
            mysocket.listen(1)
            print("New game started at "+IP+" on port "+str(PORT)+".")
            print("Waiting for an opponent...")
            data, addr = mysocket.accept()
            print("A player at "+str(addr)+" joined the game.")

            #server随机确定执子类型，并发送给client
            chess_type = randint(0,1)
            data.send((str(chess_type)).encode())
            if chess_type:
                print("You are the defensive.")
            else:
                print("You are the offensive.")
            
            print("GAME STARTS!")
            sleep(3)
            print_board()
            if chess_type:
                status = 3
            else:
                status = 1
                potential_place(recent_x, recent_y)
                fprint.goto_x_y(0,HEIGHT+1)
                fprint.set_color(0x0a)
                print("your turn             ")
            
        elif x.event_type == 'down' and x.name == 'j':
            IP = str(input("Input the IP address of a server:"))
            PORT = int(input("Input the port:"))
            mysocket.connect((IP,PORT))

            #接收server的执子类型，则己方类型为其相反类型
            chess_type = int(1 - int((mysocket.recv(512)).decode()))
            if chess_type:
                print("You are the defensive.")
            else:
                print("You are the offensive.")
            
            print("GAME STARTS!")
            sleep(3)
            print_board()
            if chess_type:
                status = 3
            else:
                status = 1
                potential_place(recent_x, recent_y)
                fprint.goto_x_y(0,HEIGHT+1)
                fprint.set_color(0x0a)
                print("your turn             ")
                
    #游戏结束，按任意键退出窗口     
    elif status == 0:
        status = -1

    #轮到己方落子
    elif status == 1:
        if x.event_type == 'down' and x.name == 'o':#如果退出游戏
            send_msg("o")
            game_win()
            accident("You exit the game!")
            return

        #移动控制，调用move_away()和potential_place()
        elif x.event_type == 'down' and x.name == 'left':
            if recent_x > 0:
                move_away(recent_x, recent_y)
                recent_x -= 1
                potential_place(recent_x, recent_y)
        elif x.event_type == 'down' and x.name == 'right':
            if recent_x < WIDTH-1:
                move_away(recent_x, recent_y)
                recent_x += 1
                potential_place(recent_x, recent_y)
        elif x.event_type == 'down' and x.name == 'up':
            if recent_y > 0:
                move_away(recent_x, recent_y)
                recent_y -= 1
                potential_place(recent_x, recent_y)
        elif x.event_type == 'down' and x.name == 'down':
            if recent_y < HEIGHT-1:
                move_away(recent_x, recent_y)
                recent_y += 1
                potential_place(recent_x, recent_y)

        #尝试落子，能落子则调用set_chess()
        elif x.event_type == 'down' and x.name == 's':
            if board[recent_y][recent_x] <= 8:
                set_chess(chess_type)
                move_away(recent_x, recent_y)
                send_msg((str(recent_y)+' '+str(recent_x)))
                status = 3
                if if_over():
                    game_win()
            
    elif status == 3:
        if x.event_type == 'down' and x.name == 'o':
            send_msg("o")
            game_win()
            accident("You exit the game!")
            return

#接受字符串
def send_msg(msg):
    global mysocket,data,if_server
    if if_server:
        data.send(msg.encode())
    else:
        mysocket.send(msg.encode())

def move_away(x, y):
    fprint.goto_x_y(x*2, y)
    fprint.set_color(0x0f)
    print(ICONS[board[y][x]])

def potential_place(x, y):
    fprint.goto_x_y(x*2, y)
    fprint.set_color(0xcf)
    print(ICONS[board[y][x]])

#set_chess更新游戏面板
def set_chess(what_chess):
    board[recent_y][recent_x] = what_chess+9
    fprint.goto_x_y(recent_x*2,recent_y)
    print(ICONS[what_chess+9])

def if_over():
    #检测行内有无五子连线
    for i in range(HEIGHT):
        num = 1
        for j in range(WIDTH-1):
            if board[i][j+1] >= 9 and board[i][j+1] == board[i][j]:
                num += 1
            else:
                num = 1
            if num >= 5:
                return 1

    #检测列内有无五子连线
    for i in range(WIDTH):
        num = 1
        for j in range(HEIGHT-1):
            if board[j][i] >= 9 and board[j+1][i] == board[j][i]:
                num += 1
            else:
                num = 1
            if num >= 5:
                return 1

    #检测西南-东北方向有无五子连线
    for i in range(4,HEIGHT+WIDTH-5):
        num = 1;
        for j in range(i):
            if i-j < HEIGHT and j+1 < WIDTH and board[i-j][j] >= 9 and board[i-j][j] == board[i-j-1][j+1]:
                num += 1
                if num >= 5:
                    return 1
            else:
                num = 1

    #检测西北-东南方向有无五子连线
    for i in range(5-WIDTH,HEIGHT-4):
        num = 1;
        for j in range(HEIGHT-i-1):
            if i+j >= 0 and j+1 < WIDTH and board[i+j][j] >= 9 and board[i+j+1][j+1] == board[i+j][j]:
                num += 1
                if num >= 5:
                    return 1
            else:
                num = 1
    
    return 0

def init_board():
    layer = [0]
    for i in range(WIDTH-2):
        layer.append(1)
    layer.append(2)
    board.append(layer)
    
    for i in range(HEIGHT-2):
        layer = []
        layer.append(3)
        for i in range(WIDTH-2):
            layer.append(4)
        layer.append(5)
        board.append(layer)
        
    layer = [6]
    for i in range(WIDTH-2):
        layer.append(7)
    layer.append(8)
    board.append(layer)

def print_board():
    system("cls")
    fprint.set_color(0x0f)
    for i in range(HEIGHT):
        for j in range(WIDTH):
            stdout.write(ICONS[board[i][j]])
        stdout.write("\n")

#游戏结束（某方获得无字连线、某方退出游戏活某方断开连接时调用）
def game_win():
    global status
    status = 0
    
    #关闭套接字
    mysocket.close()
    if if_server:
        data.close()

    #输出游戏结果
    fprint.goto_x_y(0, HEIGHT+1)
    fprint.set_color(0x0f)
    print("GAME ENDS!            ")
    if chess_type == 1:
        print("● WON THE GAME!")
    else:
        print("○ WON THE GAME!")
    print("Press any key to exit the game.")

def welcome():
    fprint.goto_x_y(0, 0)
    fprint.set_color(0x0f)
    print("Welcome to Gobang game.")
    print("Press s for starting a new game.")
    print("Press j for joining other's game.")

def what_chess():
    if chess_type:
        print("You are "+str(ICONS[10])+"(defensive)")
    else:
        print("You are "+str(ICONS[9])+"(offensive)")

#接收到对方的落子信息时调用，作用为更新己方游戏面板
def recv_pos(pos):
    global status,recent_x,recent_y    
    recent_y = int(pos[0])
    recent_x = int(pos[1])
    set_chess(1-chess_type)
    if if_over():
        game_win()
        return
    potential_place(recent_x, recent_y)
    status = 1
    fprint.goto_x_y(0,HEIGHT+1)
    fprint.set_color(0x0a)
    print("your turn             ")

def accident(msg):
    fprint.goto_x_y(0,HEIGHT+2)
    fprint.set_color(0x0e)
    print(msg)

if __name__ == "__main__":
    keyboard.on_press(call)
    init_board()
    welcome()
    while status != -1:
        if status == 3:
            fprint.goto_x_y(0,HEIGHT+1)
            fprint.set_color(0x0c)
            print("your opponent's turn")
            try:
                if if_server:
                    reception = data.recv(512)
                else:
                    reception = mysocket.recv(512)
            except ConnectionResetError:
                game_win()
                accident("Your opponent went offline!")
                continue
            if not reception:#如果对方掉线
                game_win()
                accident("Your opponent went offline!")
            elif reception.decode() == "o":
                game_win()
                accident("Your opponent exited the game!")
            else:
                recv_pos((reception.decode()).split(' '))
            
