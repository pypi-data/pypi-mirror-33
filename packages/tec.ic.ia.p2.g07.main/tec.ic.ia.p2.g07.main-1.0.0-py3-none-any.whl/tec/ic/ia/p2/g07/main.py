from tec.ic.ia.p2.g07.Relation import Relation
from tec.ic.ia.p2.g07.Controller import search
import csv
from tkinter import messagebox, Tk, Label, Entry, Button, StringVar,\
    Listbox, END, EXTENDED, Scrollbar, Text
from pyDatalog import pyDatalog

Relations = []  # knowledge database

# Function to change cursor when program is busy
def busy(window):
    window.config(cursor="wait")


# Function to change cursor when program is free
def notbusy(window):
    window.config(cursor="")


# Function to process input file
def db_input(input, window, possible_relations):
    global Relations
    busy(window)
    inverted = [0, 1, 2, 5]
    Relations = []
    pyDatalog.clear()
    try:  # If file exists
        with open(input.get(), 'r', encoding="utf8") as csvfile:
            spamreader = csv.reader(
                csvfile, delimiter='\t', lineterminator='\n')

            for row in spamreader:
                first_index = row[0].index(":")  # Search first word
                second_index = row[2].index(":")  # Search second word
                relation = row[1]
                # If relation is generator -> generated
                if possible_relations.index(relation) in inverted:
                    child_lang = row[2][0:second_index]
                    child = row[2][second_index+2:]
                    parent_lang = row[0][0:first_index]
                    parent = row[0][first_index+2:]
                # If relation is generated -> generator
                else:
                    child_lang = row[0][0:first_index]
                    child = row[0][first_index+2:]
                    parent_lang = row[2][0:second_index]
                    parent = row[2][second_index+2:]
                # Relations[possible_relations.index(relation)].append(
                #     [child_lang, child, relation, parent_lang, parent])
                # Add to knowledge database
                Relations.append(Relation(child_lang, child,
                                          relation, parent_lang, parent))

        messagebox.showinfo("Let's Continue!", "The upload is done!")
    except:
        messagebox.showwarning("Error!", "The file can't be upload.")

    notbusy(window)


# Function to change Label according to query selected
def onselect(evt, first_entry, second_entry):
    w = evt.widget
    index = int(w.curselection()[0])
    labels = ['First word:', 'Second word:']
    if index == 0:
        labels = ['Sibling 1:', 'Sibling 2:']
    elif index == 1 or index == 4:
        labels = ['Cousin 1:', 'Cousin 2:']
    elif index == 2:
        labels = ['Child:', 'Parent:']
    elif index == 3:
        labels = ['Uncle:', 'Child:']
    elif index == 5 or index == 6:
        labels = ['Language:', 'Word:']
    elif index == 7:
        labels = ['Word:', '']
    elif index == 8 or index == 9:
        labels = ['Language 1:', 'Language 2:']
    elif index == 10 or index == 11:
        labels = ['Language:', '']
    first_entry['text'] = labels[0]
    second_entry['text'] = labels[1]


# Graphic User Interface
def ui():
    # List of possible querys, each query changes the labels for the two words
    possible_querys = ['Si dos palabras son herman@s', 'Si dos palabras son prim@s', 'Si una palabra es hij@ de otra',
                       'Si una palabra es ti@', 'Si son prim@s y en qué grado', 'Si una palabra está relacionada con un idioma',
                       'Palabras en un idioma originadas por una palabra específica', 'Listar los idiomas relacionados con una palabra',
                       'Contar todas las palabras comunes entre dos idiomas', 'Listar todas las palabras comunes entre dos idiomas',
                       'Idioma que más aportó a otro', 'Listar todos los idiomas que aportaron a otro']
    # List of possible relations on knowledge database
    possible_relations = ['rel:derived', 'rel:etymological_origin_of', 'rel:etymologically', 'rel:etymologically_related', 'rel:etymology',
                          'rel:has_derived_form', 'rel:is_derived_from', 'rel:variant:orthography']

    # Window Properties
    window = Tk()
    window.title("Project 2 - Ethymological Relationships")
    window.geometry("1000x800+180+20")

    # Title
    Label(window, text="Ethymological Relationships",
          font="Helvetica 18 bold").place(x=337, y=50)

    # Entry DB
    Label(window, text="Database File:", font="Helvetica 14").place(x=310, y=130)

    input = StringVar()
    Entry(window, font="Helvetica 12", textvariable=input).place(x=445, y=132)

    # Button input database
    enter_db = Button(window, font="Helvetica 12", text="Enter", command=lambda: db_input(
        input, window, possible_relations)).place(x=640, y=125)

    # Relations
    Label(window, text="Relations:", font="Helvetica 12").place(x=30, y=200)
    relations = Listbox(window, height=8, font="Helvetica 12",
                        selectmode=EXTENDED, exportselection=0)
    relations.place(x=30, y=220)

    for item in possible_relations:
        relations.insert(END, item)

    # Results
    Label(window, text="Results:", font="Helvetica 12").place(x=20, y=420)
    results = Text(window, font="Helvetica 12",
                   height=18, width=105, state='disabled')
    results.place(x=20, y=440)

    # Entry
    first_entry = Label(window, text="First word:", font="Helvetica 14")
    first_entry.place(x=550, y=240)
    input_first_entry = StringVar()
    Entry(window, font="Helvetica 12",
          textvariable=input_first_entry).place(x=675, y=242)

    # Entry
    second_entry = Label(window, text="Second word:", font="Helvetica 14")
    second_entry.place(x=550, y=300)
    input_second_entry = StringVar()
    Entry(window, font="Helvetica 12",
          textvariable=input_second_entry).place(x=675, y=302)

    # Querys
    Label(window, text="Querys:", font="Helvetica 12").place(x=240, y=200)
    querys = Listbox(window, height=7, width=30,
                     font="Helvetica 12", exportselection=0)
    querys.place(x=240, y=220)
    scrollbar = Scrollbar(window, orient="horizontal")
    scrollbar.place(x=240, y=360, width=270)
    scrollbar.config(command=querys.xview)

    querys.bind('<<ListboxSelect>>', lambda evt: onselect(
        evt, first_entry, second_entry))

    for item in possible_querys:
        querys.insert(END, item)

    # Button search
    Button(window, font="Helvetica 12", text="Search", command=lambda: search(input_first_entry,
                                                                              input_second_entry, relations, querys, results, window, possible_querys, possible_relations,
                                                                              Relations)).place(x=890, y=270)

    # Ejecuta la ventana
    window.mainloop()


ui()
