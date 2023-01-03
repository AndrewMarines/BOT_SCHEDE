import multiprocessing

import cv2
import pytesseract
import re
import glob
import pandas as pd
import os
from time import perf_counter

df = pd.read_csv("C:\\Users\\AE\\Downloads\\Lista Draft S9 - Foglio1.csv")
df['Nome'] = df['Nome'].str.upper()
# All files and directories ending with .txt and that don't begin with a dot:
lista = glob.glob("DAVALUTARE/*.jpg")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

ruoli = ["G", "DC", "TERDX", "TERSX", "M", "C", "TC", "PC", "TS", "TD", "TOTALE"]
for ruolo in ruoli:
    if not os.path.isdir(ruolo):
        os.mkdir(ruolo)
        print(f"creata cartella per {ruolo}")


def prepare_image(imgc):
    # nome
    img = cv2.cvtColor(imgc, cv2.COLOR_BGR2GRAY)  # convert to grey
    img = img[15:40, 428:1000]
    # img = cv2.GaussianBlur(img, (5, 5), 3)
    # img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 1, 5)
    return img


def get_text(img):
    txt = pytesseract.image_to_string(img, config='--psm 10')
    txt = " ".join(re.findall("[a-zA-Z]+", txt))
    return txt


def find_n_scheda(txt):
    try:
        index = df.loc[df['Nome'] == txt].index[0]
        n_scheda = int(df['Numero scheda'][index])
    except:
        n_scheda = "NON_IN_LISTA "
    n_scheda = str(n_scheda) + " "
    return n_scheda


def save_based_on_role(imgc, n_scheda, txt):
    # ruolo
    # dc
    cv2.imwrite('TOTALE/' + n_scheda + txt + '.png', imgc)
    if (imgc[339, 415][1] > 200):
        cv2.imwrite('DC/' + n_scheda + txt + '.png', imgc)
        return "DC"
    # terdx
    if (imgc[386, 411][1] > 200 or imgc[386, 444][1] > 200):
        cv2.imwrite('TERDX/' + n_scheda + txt + '.png', imgc)
        return "TERDX"
    # med
    if (imgc[340, 443][1] > 200):
        cv2.imwrite('M/' + n_scheda + txt + '.png', imgc)
        return "M"

    # tc
    if (imgc[339, 515][1] > 200):
        cv2.imwrite('TC/' + n_scheda + txt + '.png', imgc)
        return "TC"

    # pc
    if (imgc[340, 555][1] > 200):
        cv2.imwrite('PC/' + n_scheda + txt + '.png', imgc)
        return "PC"

        # c/ts
    if (imgc[293, 480][1] > 200 or imgc[293, 515][1] > 200):
        cv2.imwrite('TS/' + n_scheda + txt + '.png', imgc)
        return "TS"

    # c/td
    if (imgc[387, 480][1] > 200 or imgc[388, 517][1] > 200):
        cv2.imwrite('TD/' + n_scheda + txt + '.png', imgc)
        return "TD"

    # cc
    if (imgc[340, 483][1] > 200):
        cv2.imwrite('C/' + n_scheda + txt + '.png', imgc)
        return "C"

    # TERSX
    if (imgc[293, 411][1] > 200 or imgc[293, 443][1] > 200):
        cv2.imwrite('TERSX/' + n_scheda + txt + '.png', imgc)
        return "TERSX"

    # G
    if (imgc[340, 364][1] > 200):
        cv2.imwrite('G/' + n_scheda + txt + '.png', imgc)
        return "G"

    return f"NON HO TROVATO"


def analizza(path):
    imgc = cv2.imread(path)
    img = prepare_image(imgc)
    txt = get_text(img)
    n_scheda = find_n_scheda(txt)
    risultato = save_based_on_role(imgc, n_scheda, txt)
    print(f"{txt}: {risultato}")

def main():
    with multiprocessing.Pool() as pool:
        pool.map(analizza, lista)

if __name__ == '__main__':
    t1_start = perf_counter()
    main()
    t1_stop = perf_counter()
    print(f"Impiegato: {t1_stop - t1_start} s")

