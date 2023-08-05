# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 09:33:02 2018

@author: ShashiKant
"""

# Fifteen Puzzle Game
import numpy as game
import random
import os

def Start_Pattern(Operation_List,Check_List):
    os.system('clear')
    f = 0
    l = 4
    for x in range(0,4):
        print('$------$------$------$------$')
        for y in range(f,l):
            print('|{0:^6s}'.format(Operation_List[y]),end = '')
        print('|',end = '')        
        f = l
        l = l + 4    
        print(sep = '\n')       
    print('$------$------$------$------$')
    
def Pattern(Operation_List,Check_List):
    os.system('clear')
    f = 0
    l = 4
    for x in range(0,4):
        print('$------$------$------$------$')
        for y in range(f,l):
            print('|{0:^6s}'.format(Operation_List[y]),end = '')
        print('|',end = '')        
        f = l
        l = l + 4    
        print(sep = '\n')       
    print('$------$------$------$------$')
    if list(Operation_List) == list(Check_List):
        print('Congratulations,You have completed the game')
    else:
        saving = open('save.txt','wt')
        saving_List = 'n'.join(Operation_List)
        saving_List = saving_List + 'n'
        print(saving_List,file = saving)
        saving.close()
        game_play(Operation_List,Check_List)

def game_play(Operation_List,Check_List):
    Chance = input('Enter your step: ')
    if Chance == 'Q' or Chance == 'q':
        exit()
    else:
        Chance = Chance.split(' ')
    for x in range(0,16):
        if Operation_List[x] == Chance[0]:
             if (Chance[-1] == 'W') or (Chance[-1] == 'w'):
                 if Operation_List[x-4] == ' ' and x>3:
                     temp = Operation_List[x]
                     Operation_List[x] = Operation_List[x-4]
                     Operation_List[x-4] = temp
                     Pattern(Operation_List,Check_List)
                 else:
                     Choice = input('Wrong Step. Want to Try Again(Y/N): ')
                     if Choice == 'Y' or Choice == 'y':
                         game_play(Operation_List,Check_List)
                     else:
                         exit()
             elif (Chance[-1] == 'S') or (Chance[-1] == 's'):
                 if Operation_List[x+4] == ' ' and x<12:
                     temp = Operation_List[x]
                     Operation_List[x] = Operation_List[x+4]
                     Operation_List[x+4] = temp
                     Pattern(Operation_List,Check_List)
                 else:
                     Choice = input('Wrong Step. Want to Try Again(Y/N): ')
                     if Choice == 'Y' or Choice == 'y':
                         game_play(Operation_List,Check_List)
                     else:
                         exit()
             elif (Chance[-1] == 'A') or (Chance[-1] == 'a'):
                 if Operation_List[x-1] == ' ' and x>0:
                     temp = Operation_List[x]
                     Operation_List[x] = Operation_List[x-1]
                     Operation_List[x-1] = temp
                     Pattern(Operation_List,Check_List)
                 else:
                     Choice = input('Wrong Step. Want to Try Again(Y/N): ')
                     if Choice == 'Y' or Choice == 'y':
                         game_play(Operation_List,Check_List)
                     else:
                         exit()
             elif (Chance[-1] == 'D') or (Chance[-1] == 'd'):
                 if Operation_List[x+1] == ' ' and x<15:
                     temp = Operation_List[x]
                     Operation_List[x] = Operation_List[x+1]
                     Operation_List[x+1] = temp
                     Pattern(Operation_List,Check_List)
                 else:
                     Choice = input('Wrong Step. Want to Try Again(Y/N): ')
                     if Choice == 'Y' or Choice == 'y':                         
                         game_play(Operation_List,Check_List)
                     else:
                         exit()
             else:
                 Choice = input('Wrong Step. Want to Try Again(Y/N): ')
                 if Choice == 'Y' or Choice == 'y':
                     game_play(Operation_List,Check_List)
                 else:
                     exit()
        #else:
            #Choice = input('Wrong Step. Want to Try Again(Y/N): ')
            #if Choice == 'Y' or Choice == 'y':
            #    game_play(Operation_List,Check_List)
           # else:
            #    exit()


    
def Play():
    game_list = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15',
            ' ']
    game_digits = game.asarray(game_list)
    game_digits_copy = game_digits
    Start_Pattern(game_digits,game_digits_copy)
    Start = input('Press \nN: New Game\nS: Resume Last Game\nQ: Exit\nEnter Choice Here:')
    if Start == 'N' or Start == 'n':
        random.shuffle(game_list)
        game_digits = game.asarray(game_list)
        Pattern(game_digits,game_digits_copy)
    elif Start == 'S' or Start == 's':
     try:
         Resume = open('save.txt','rt')
         Load = Resume.readline()
         Resume.close()
         Load = Load.split('n')
         del Load[-1]
         Pattern(Load,game_digits_copy)
     except:
         print('No Saved File')
         Choice = input('Wrong Step. Want to Try Again(Y/N): ')
         if Choice == 'Y' or Choice == 'y':
             Play()
         else:
             exit()
    else:
        exit()



     
    
    
