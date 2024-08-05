from typing import List
from tkinter import *
from PIL import ImageTk,Image
import tkinter.font as font
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import re
from fpdf import FPDF
import os
import requests

#Function for saving all the pdf's and plots in directory
def init():
    if not os.path.isdir("./data/"):
        os.makedirs("./data/")
    img = requests.get('https://static.spacecrafted.com/f28b97dbc1c84e84a123fcf1d7ad66cc/i/ce141728f0284db9907df6fa8425d146/1/4SoifmQp45JMgBnHm9g4L/bingo-logo.png').content
    with open('./data/bingo.jfif','wb') as handler:
        handler.write(img)

#Funtion to save output in pdf format        
def cards_to_pdf(list_of_cards, simulation_no):
        text = np.asarray(list_of_cards)
        pdf = FPDF()
        # Add a page
        pdf.add_page()
        pdf.set_font("Arial", size=int(18), style="B")
        line = 10
        pdf.cell(200, 10, txt="Cards for Simulation"+str(simulation_no), ln=1, align="C")
        for w in range(len(text)):
                pdf.set_font("Arial", size=int(12), style="U")
                pdf.cell(200, 10, txt="Card" + str(w + 1), ln=1, align="L")
                pdf.set_font("Arial", size=int(10))
                text_out = np.transpose(text[w])
                for i in range(len(text[w])):
                        pdf.cell(10, 10, txt=str(text_out[i]), ln=0, align='L')
                        pdf.ln()
        pdf.output(name=f"./data/Cards_for_Simulation"+str(simulation_no)+".pdf", dest='F')

#Function to draw cards        
def draw_card():
    random_number_list = random.sample((range(1, 76)), 75)

    return random_number_list

#Function to specify rules for player cards
def create_card():
    card = list(list())
    card_range: dict = {1: 15, 16: 30, 31: 45, 46: 60, 61: 75}

    for key, value in card_range.items():
        card.append(random.sample(range(key, value), 5))
    card[2][2] = "X"
    np.array(card).T.tolist()

    return card

#Function to create n cards
def create_n_cards(players: int = 4):
    all_bingo_cards = []

    for player in range(1, players + 1):
        if player > 0:
            player_card = create_card()
            all_bingo_cards.append(player_card)
        else:
            raise Exception("Number of players is not defined!")

    return all_bingo_cards

#Function to check bingo card
def check_bingo_card(drawn_card_number: int, player_card):
    for x in range(0, 5):
        for y in range(0, 5):
            if drawn_card_number == player_card[x][y]:
                 player_card[x][y] = "X"
                 return True
    
    return False

#Function to check bingo per simulation
def check_for_bingo_per_round(player_card):
    for x in range(0, 5):
        count = 0
        for y in range(0, 5):
            if player_card[y][x] != "X":
                break
            else:
                count += 1
        if count == 5:
            return True

    for y in range(0, 5):
        count = 0
        for x in range(0, 5):
            if player_card[y][x] != "X":
                break
            else:
                count += 1
        if count == 5:
            return True

        # check for diagonal - top left to bottom right
    count = 0
    for i in range(0, 5):
        if player_card[i][i] != "X":
            break
        else:
            count += 1
        if count == 5:
            
            return True

        # check for diagnal - top right to bottom left
    count = 0
    for x in range(0, 5):
        if player_card[4 - x][x] != "X":
            break
        else:
            count += 1
    if count == 5:
        
        return True

    return False

#Function to record player's reaching bingo
def celebrate_winner(all_bingo_cards, player_card):
    all_bingo_cards.remove(player_card)

#Function to run simulation
def run_simulation(total_number_of_games,no_of_players):
    all_drawn_numbers = []
    player_stats = []
    final=pd.DataFrame()

    for games in range(1, total_number_of_games + 1):
        wins_count=[]

        #print(f"-------------\n|Game no : {games}|\n-------------")
        initialise_the_players = create_n_cards(players=no_of_players)  # assign cards to player
        cards_to_pdf(initialise_the_players,games)
        counter = 0
        win_counter = 0
        for draw in random.sample((range(1, 76)), 75):
            counter += 1

            if initialise_the_players:
                drawn_number = draw
                for each_player_card in initialise_the_players:
                    check_for_drawn_card = check_bingo_card(
                        drawn_card_number=drawn_number, player_card=each_player_card
                    )
                    if check_for_drawn_card == True:
                        bingo_check = check_for_bingo_per_round(each_player_card)

                        if bingo_check == True:
                            win_counter += 1
                            celebrate_winner(
                                all_bingo_cards=initialise_the_players, player_card=each_player_card
                            )

                total_winner_in_a_round = win_counter
                drawn_number_stats = {
                    "GAME_NO": games,
                    "ROUND": counter,
                    "NUMBER_CALLED": drawn_number,
                    "NO_OF_PLAYER_WON": int(win_counter),
                }
                all_drawn_numbers.append(drawn_number_stats)
                wins_count.append(int(win_counter))
            else:
                last_round = counter - 1
                drawn_number_stats = {
                        "GAME_NO": games,
                        "ROUND": counter,
                        "NUMBER_CALLED": drawn_number,
                        "NO_OF_PLAYER_WON": int(win_counter),
                }
                all_drawn_numbers.append(drawn_number_stats)
                wins_count.append(int(win_counter))
               
        final['simulation_{u}'.format(u=games)]=pd.Series(wins_count)

    df_rounds = pd.DataFrame(all_drawn_numbers)

    df_rounds = df_rounds.dropna(subset=["NO_OF_PLAYER_WON"])
    df_rounds.sort_values(by=["GAME_NO", "ROUND"])



    pd.set_option('display.max_rows',100)
    pd.set_option('display.max_columns',120)
    
    
    return final

#Function to plot graph
def plot(final):
    plt.figure(figsize=(8,6))
    plt.plot(final.mean(axis=1),color='blue', label='Mean')
    plt.fill_between(final.index.values, final.mean(axis=1) - final.std(axis=1), final.mean(axis=1) + final.std(axis=1), color='lightskyblue', alpha=0.4, label='Std')
    plt.plot(final.min(axis=1), linestyle='dashed',color='steelblue', label='Min')
    plt.plot(final.max(axis=1), linestyle='dashed',color='steelblue', label='Max')
    plt.legend()
    plt.title('Number of Winner per Number Called')
    plt.xlabel('Total Number Called')
    plt.ylabel('Winners')
    plt.savefig(f"./data/BingoSimulationPlot.pdf", format="pdf", bbox_inches="tight")
    plt.savefig('./data/plot.png')

#Function to calculate measures of centrality
def measure_of_centrality(final):
    stats = pd.DataFrame()
    stats['Mean'] = final.mean(axis=1)
    stats['Median'] = final.median(axis=1)
    stats['Std'] =  final.std(axis=1)
    stats['Min'] = final.min(axis=1)
    stats['Max'] = final.max(axis=1)
    stats['25%'] =final.quantile(q=0.25, axis=1)
    stats['50%'] =final.quantile(q=0.5, axis=1)
    stats['75%'] =final.quantile(q=0.75, axis=1)
    stats['Skewness'] = final.skew(axis=1)
    
    return stats

#Funtion to save stats in a table
def save_table(stats):
    fig, ax =plt.subplots(figsize=(12,4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=stats.values,colLabels=stats.columns,loc='center')
    pp = PdfPages(f"./data/BingoCentralityTable.pdf")
    pp.savefig(fig, bbox_inches='tight')
    pp.close()


#GUI using tkinter
init()
root = Tk()
root.title('BingoGame')
root.geometry("500x400")

my_img = Image.open("./data/bingo.jfif")
resize_img = my_img.resize((500,200), Image.ANTIALIAS)

new_img = ImageTk.PhotoImage(resize_img)
my_label = Label(image= new_img,background = "red")
my_label.pack(pady=20)

heading_label_font = font.Font(family = 'Times New Roman' , size = 20)
heading_label = Label(root,text="Click Start button to start your Bingo!", background= "yellow",font=heading_label_font)
heading_label.pack()

reg = "[1-9]{1}[0-9]*"
    
def start():
   first = Toplevel()
   first.geometry("500x300")
    
   game_label = Entry(first, width=50, borderwidth=5)
   game_label.pack()
   game_label.insert(0,"Enter total number of games : ")

   player_label = Entry(first, width=50, borderwidth=5)
   player_label.pack()
   player_label.insert(0,"Enter total number of player : ")
    
   def btn_click():
    games_input = re.findall(reg,game_label.get().strip())
    players_input = re.findall(reg,player_label.get().strip())
    
    if len(games_input)== 0 or len(players_input)== 0 :
        error_label_font = font.Font(family = 'Times New Roman' , size = 20)
        error_label = Label(first,text="Invalid Input!!!!!", background= "red",font=error_label_font)
        error_label.pack()
        return
    
    num_of_games = int(games_input[0])
    num_of_players = int(players_input[0])
    
        
    df = run_simulation(num_of_games,num_of_players)
    plot(df)
    
    label1 = Label(first,text=df.shape[0])
    label1.pack()
    
    #label2 = Label(top,text=num_of_players)
    #label2.pack()
    
    first.destroy()
    second = Toplevel()
    global plot_img
    plot_img = ImageTk.PhotoImage(file = "./data/plot.png")
    plot_label = Label(second,image= plot_img)
    plot_label.pack(pady = 20)
    
    stats = measure_of_centrality(df)
    save_table(stats)
            
   btn2_font = font.Font(family = 'Times New Roman' , size = 20, underline =1) 
   btn2 = Button(first,text="Next",command=btn_click, font = btn2_font)
   btn2.pack(pady=50)
   
btn_font = font.Font(family = 'Times New Roman' , size = 20, underline =1)
btn = Button(root,text="Start",command=start, font = btn_font)
btn.pack(pady=20)

root.mainloop()


