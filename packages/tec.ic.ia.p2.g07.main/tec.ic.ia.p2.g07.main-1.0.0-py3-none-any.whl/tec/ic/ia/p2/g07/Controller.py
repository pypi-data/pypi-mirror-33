from tkinter import END, messagebox
from pyDatalog import pyDatalog
from tec.ic.ia.p2.g07.Queries import *

# Function to clean Textbox of Results
def clean_msg(results):
    results.config(state='normal')
    results.delete(1.0, END)
    results.config(state='disabled')


# Function to handle the answer on Textbox of Results
def response_msg(results, query, result, status, info):
    results.config(state='normal')
    if query in [0, 1, 2, 3, 5]:
        if status == 'good':
            results.insert(END, "\nRespuesta: Si \n\n")
            results.insert(END, "\nRelaciones Usadas: \n")
            results.insert(END, info[0]+"\n\n")
            for i in range(len(result)):
                results.insert(END, str(i+1)+": "+str(result[i])+"\n")
        elif status == 'bad':
            results.insert(END, "\nRespuesta: No \n")
    elif query == 4:
        if status == 'good':
            levels = []
            for i in result:
                levels.append(i[2])
            results.insert(END, "\nRespuesta: Si - Nivel: " +
                           str(min(levels))+"\n\n")
            results.insert(END, "\nRelaciones Usadas: \n")
            results.insert(END, info[0]+"\n\n")
            for i in range(len(result)):
                results.insert(END, str(i+1)+": "+str(result[i])+"\n")
        elif status == 'bad':
            results.insert(END, "\nRespuesta: No \n")
    elif query == 6:
        if status == 'good':
            results.insert(END, "\nRespuesta: Si\n\n")
            results.insert(END, "\nPalabras: \n\n")
            words = []
            for i in range(len(result)):
                phrase = str(result[i][0])
                word = phrase[phrase.index(":")+1:phrase.index(" ")]
                if word == info[2]:
                    word = phrase[phrase.find(":", phrase.find(
                        ":", phrase.find(":") + 1) + 1)+1:]
                if word not in words:
                    words.append(word)
                    results.insert(END, str(i+1)+": "+str(word)+"\n")
            results.insert(END, "\n\nRelaciones Usadas: \n")
            results.insert(END, info[0]+"\n\n")
            for i in range(len(result)):
                results.insert(END, str(i+1)+": "+str(result[i])+"\n")
        elif status == 'bad':
            results.insert(END, "\nRespuesta: No se encontró resultados.\n")
    elif query == 7:
        if status == 'good':
            results.insert(END, "\nRespuesta: Si\n\n")
            results.insert(END, "\nIdiomas: \n\n")
            langs = list(result[0])
            for i in range(len(langs)):
                results.insert(END, str(i+1)+": "+langs[i]+"\n")
            results.insert(END, "\n\nRelaciones Usadas: \n")
            results.insert(END, info[0]+"\n\n")
            for i in range(len(result[1])):
                results.insert(END, str(i+1)+": "+str(result[1][i])+"\n")
        elif status == 'bad':
            results.insert(END, "\nRespuesta: No se encontró resultados.\n")
    elif query == 8:
        if status == 'good':
            results.insert(END, "\nRespuesta: Si\n\n")
            results.insert(END, "\nCantidad: "+str(result[0])+"\n\n")
            results.insert(END, "\nRelaciones Usadas: \n")
            results.insert(END, info[0]+"\n\n")
            for i in range(len(result[1])):
                results.insert(END, str(i+1)+": "+str(result[1][i])+"\n")
        elif status == 'bad':
            results.insert(END, "\nRespuesta: No se encontró resultados.\n")
    elif query == 9:
        if status == 'good':
            results.insert(END, "\nRespuesta: Si\n\n")
            results.insert(END, "\nPalabras: \n\n")
            words = list(result[0])
            for i in range(len(words)):
                results.insert(END, str(i+1)+": "+words[i]+"\n")
            results.insert(END, "\n\nRelaciones Usadas: \n")
            results.insert(END, info[0]+"\n\n")
            for i in range(len(result[1])):
                results.insert(END, str(i+1)+": "+str(result[1][i])+"\n")
        elif status == 'bad':
            results.insert(END, "\nRespuesta: No se encontró resultados.\n")
    elif query == 10:
        if status == 'good':
            results.insert(END, "\nRespuesta: Si\n\n")
            results.insert(
                END, "\nIdioma: "+str(result[0][0])+" con un "+str(result[0][1])+"%\n\n")
            results.insert(END, "\nRelaciones Usadas: \n")
            results.insert(END, info[0]+"\n\n")
            for i in range(len(result[2])):
                results.insert(END, str(i+1)+": "+str(result[2][i])+"\n")
        elif status == 'bad':
            results.insert(END, "\nRespuesta: No se encontró resultados.\n")
    elif query == 11:
        if status == 'good':
            results.insert(END, "\nRespuesta: Si\n\n")
            results.insert(END, "\nPorcentajes: \n\n")
            perc = list(result[0])
            for i in range(len(perc)):
                results.insert(END, str(i+1)+": " +
                               str(perc[i][0])+": "+str(perc[i][1])+"%\n")
            results.insert(END, "\n\nRelaciones Usadas: \n")
            results.insert(END, info[0]+"\n\n")
            for i in range(len(result[1])):
                results.insert(END, str(i+1)+": "+str(result[1][i])+"\n")
        elif status == 'bad':
            results.insert(END, "\nRespuesta: No se encontró resultados.\n")

    results.config(state='disabled')


# Function to ask the query and calls to print handler
def search(input_first_entry, input_second_entry, p_relations, p_query, results, window, possible_querys, possible_relations, Relations):
    first = input_first_entry.get()
    second = input_second_entry.get()
    relations_selected = p_relations.curselection()
    query = p_query.curselection()
    query = query[0]
    if first == "" or (second == "" and query not in [7, 10, 11]) or relations_selected == [] or query == ():
        messagebox.showwarning(
            "Error!", "You have to select at least one relation, one query and fill the textboxes.")
    else: # If all info is available
        clean_msg(results)
        # start = 0
        # end = 1000
        result = []
        info = []
        # knowledge = []
        # for r in relations_selected:
        # while end <= len(Relations[r]):
        # searching_msg(results)
        print('Buscando...')

        # knowledge = []
        # pyDatalog.clear()
        # if end>len(Relations[r]):
        #     end = len(Relations[r])

        # for rel in Relations[r]:
        #     #Carga de datos
        #     child_lang, child, relation, parent_lang, parent = rel
        #     knowledge.append(Relation(child_lang, child, relation, parent_lang, parent))

        # Queries
        if query == 0:  # 'Si dos palabras son heman@s'
            result = siblings_query(first, second)
            info = ["X: Sibling 1\t\t--\tY: Sibling 2", 2]
        elif query == 1:  # 'Si dos palabras son prim@s'
            result = cousins_query(first, second)
            info = ["X: Cousin 1\t\t--\tY: Cousin 2", 2]
        elif query == 2:  # 'Si una palabra es hij@ de otra'
            result = son_query(first, second)
            info = ["X: Child-Parent", 1]
        elif query == 3:  # 'Si una palabra es ti@ de otra'
            result = uncle_query(first, second)
            info = ["X: Uncle\t\t--\tY: Child", 2]
        elif query == 4:  # 'Si dos palabras son prim@s y en que grado'
            result = cousins_query(first, second)
            info = ["X: Cousin 1\t\t--\tY: Cousin 2", 2]
        elif query == 5:  # 'Si una palabra esta relacionada con un idioma'
            result = language_related_query(first, second)
            info = ["X: Language-Word", 1]
        elif query == 6:  # 'Conjunto de todas las palabras en un idioma originadas por una palabra específica'
            result = language_and_origin_query(first, second)
            info = ["X: Language-Word", 1, second]
        elif query == 7:  # 'Idiomas relacionados con una palabra'
            result = list_languages_related_query(first)
            info = ["X: Language-Word", 1]
        elif query == 8:  # 'Contar todas las palabras comunes entre dos idiomas'
            result = cont_common_words_query(first, second)
            info = ["X: Language 1\t\t--\tY: Language 2", 2]
        elif query == 9:  # 'Idiomas relacionados con una palabra'
            result = list_common_words_query(first, second)
            info = ["X: Language 1\t\t--\tY: Language 2", 2]
        elif query == 10:  # 'Idioma que más aportó a otro'
            result = most_relevant_language_query(first)
            info = ["X: Word-Language", 1]
        elif query == 11:  # 'Listar todos los idiomas que aportaron a otro'
            result = percentages_relevant_language_query(first)
            info = ["X: Word-Language", 1]

            # start+=end
            # end+=end
            # if end>len(Relations[r]):
            #     end = len(Relations[r])

        if result != []: # If a result is found
            response_msg(results, query, result, 'good', info)
            # printed = True
            # found = True
            # break
        else:
            response_msg(results, query, result, 'bad', info)
        #     if found:
        #         break
        # if not printed:
        #     response_msg(results, query, result, 'bad')
