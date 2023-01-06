import multiprocessing
import time

import cv2
import pytesseract
import re
import glob
import  csv
import os
from time import perf_counter

Giocatori = []
class Giocatore:
    def __init__(self, nome, ruolo, n_scheda):
        self.nome = nome
        self.ruolo = ruolo
        self.n_scheda = n_scheda

# All files and directories ending with .txt and that don't begin with a dot:
extensions = ("*.png", "*.jpg")
lista = []
for extension in extensions:
    lista.extend(glob.glob("DAVALUTARE/" + extension))
print(len(lista))


ruoli = ["G", "DC", "TERDX", "TERSX", "M", "C", "TC", "PC", "TS", "TD", "TOTALE"]
for ruolo in ruoli:
    if not os.path.isdir(ruolo):
        os.mkdir(ruolo)
        print(f"creata cartella per {ruolo}")



with open("Lista Draft S9 - Foglio1.csv") as csv_file:
    csv_f = csv.reader(csv_file, delimiter=',')

    for row in csv_f:
        row[1] = " ".join(re.findall("[a-zA-Z ']+", row[1]))
        row[1] = re.sub(" / ", "/", row[1])
        Giocatori.append(Giocatore(row[1].upper(), row[3], row[0]))

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

def prepare_image(imgc):
    # nome
    img = cv2.cvtColor(imgc, cv2.COLOR_BGR2GRAY)  # convert to grey
    #img = img[15:40, 428:1000]
    img = img[0:30, 195:600]

    # img = cv2.GaussianBlur(img, (5, 5), 3)
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 1, 5)
    return img


def get_text(img):
    txt = pytesseract.image_to_string(img, config='--psm 10')
    txt = " ".join(re.findall("[a-zA-Z ']+", txt))
    txt = txt.replace("REGEN", "").replace("RINATO", "").replace("PG", "")
    txt = txt.strip()

    return txt


def find_n_scheda(txt):
    trovato = False
    for index, x in enumerate(Giocatori):
        if x.nome == txt:
            n_scheda = x.n_scheda
            ruolo = x.ruolo
            trovato = True
    if not trovato:
        n_scheda = "NON_IN_LISTA "
        ruolo = "NO_RUOLO"
    n_scheda = str(n_scheda) + " "

    return n_scheda, ruolo


def save_based_on_role(n_scheda, ruolo, txt, imgc):
    cv2.imwrite('TOTALE/' + n_scheda + " - " + txt + '.png', imgc)
    if "GK" in ruolo:
        cv2.imwrite('G/' + n_scheda +" - "+ txt + '.png', imgc)

    if "D" in ruolo and "C"  in ruolo:
        cv2.imwrite('DC/' + n_scheda + " - " + txt + '.png', imgc)

    if ("D" in ruolo or "WB" in ruolo) and "L" in ruolo:
        cv2.imwrite('TERSX/' + n_scheda + " - " + txt + '.png', imgc)

    if ("D" in ruolo or "WB" in ruolo) and "R" in ruolo:
        cv2.imwrite('TERDX/' + n_scheda + " - " + txt + '.png', imgc)

    if "DM" in ruolo:
        cv2.imwrite('M/' + n_scheda + " - " + txt + '.png', imgc)

    if "M" in ruolo.replace("DM","").replace("AM","") and "C"  in ruolo:
        cv2.imwrite('C/' + n_scheda + " - " + txt + '.png', imgc)

    if "AM" in ruolo and "C" in ruolo:
        cv2.imwrite('TC/' + n_scheda + " - " + txt + '.png', imgc)

    if "S" in ruolo:
        cv2.imwrite('PC/' + n_scheda + " - " + txt + '.png', imgc)

    if ("AM" in ruolo or "M" in ruolo.replace("DM","").replace("AM",""))  and "L" in ruolo:
        cv2.imwrite('TS/' + n_scheda + " - " + txt + '.png', imgc)

    if ("AM" in ruolo or "M" in ruolo.replace("DM", "").replace("AM", "")) and "R" in ruolo:
        cv2.imwrite('TD/' + n_scheda +" - "+ txt + '.png', imgc)

def analizza(path):
    imgc = cv2.imread(path)
    img = prepare_image(imgc)
    txt = get_text(img)
    n_scheda, ruolo = find_n_scheda(txt)

    save_based_on_role(n_scheda, ruolo, txt, imgc)
    print(f"{txt}({ruolo}): {ruolo}")

def main():
    with multiprocessing.Pool() as pool:
        pool.map(analizza, lista)
if __name__ == '__main__':
    t1_start = perf_counter()

    main()
    t1_stop = perf_counter()
    print(f"Impiegato: {t1_stop - t1_start} s")

