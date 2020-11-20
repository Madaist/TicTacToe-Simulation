import time

ADANCIME_MAX = 6
NR_COLOANE = 3
POZITIE_X = 5

NR_CASTIG_X = 0
NR_CASTIG_0 = 0
NR_REMIZE = 0


# verifica daca lista data ca parametru contine elemente identice
# (in acest caz: o linie/coloana/diagonala a tablei de x si 0
def elem_identice(lista):
    mt = set(lista)  # converteste lista in set
    if len(mt) == 1:  # daca toate elementele sunt identice, lungimea setului va fi 1
        castigator = list(mt)[0]  # luam elementul din set
        if castigator != Joc.GOL:  # daca e diferit de '#', adica de pozitia goala, inseamna ca avem un castigator (x sau 0)
            return castigator
        else:
            return False
    else:
        return False


class Joc:
    JMIN = None
    JMAX = None
    GOL = '#'

    def __init__(self, tabla=None):
        self.matr = tabla or [self.__class__.GOL] * NR_COLOANE ** 2

    def final(self):
        n = NR_COLOANE
        rez = (elem_identice(self.matr[0: n])  # prima linie
               or elem_identice(self.matr[n: 2 * n])  # a doua linie
               or elem_identice(self.matr[2 * n: 3 * n])  # a treia linie
               or elem_identice(self.matr[0: n * n: n])  # prima coloana
               or elem_identice(self.matr[1: n * n: n])  # a doua coloana
               or elem_identice(self.matr[2: n * n: n])  # a treia coloana
               or elem_identice(self.matr[0: n * n: (n + 1)])  # diagonala principala
               or elem_identice(self.matr[(n - 1): (n * n - 1): (n - 1)]))  # diagonala secundara
        if NR_COLOANE >= 4:
            rez = rez or elem_identice(self.matr[3 * n: 4 * n]) \
                  or elem_identice(self.matr[3: n * n: n])
        if NR_COLOANE == 5:
            rez = rez or elem_identice(self.matr[4 * n: 5 * n]) \
                  or elem_identice(self.matr[4: n * n: n])

        if rez:  # daca aveam vreo linie/coloana/diagonala identica, avem castigator
            return rez
        elif self.__class__.GOL not in self.matr:  # daca nu mai avem spatii goale, inseamna ca toate pozitiile sunt completate si avem remiza
            return 'remiza'
        else:
            return False  # altfel, inseamna ca nu am ajuns inca la finalul jocului

    def mutari(self, jucator_opus):  # succesori
        l_mutari = []
        for i in range(len(self.matr)):
            if self.matr[i] == self.__class__.GOL:
                matr_tabla_noua = list(self.matr)
                matr_tabla_noua[i] = jucator_opus
                l_mutari.append(Joc(matr_tabla_noua))
        return l_mutari

    # linie deschisa inseamna linie pe care jucatorul mai poate forma o configuratie castigatoare
    def linie_deschisa(self, lista, jucator):
        # obtin multimea simbolurilor de pe linie
        mt = set(lista)
        # verific daca sunt maxim 2 simboluri
        if len(mt) <= 2:
            # daca multimea simbolurilor nu are alte simboluri decat pentru cel de "gol" si jucatorul curent
            if mt <= {self.__class__.GOL, jucator}:
                # inseamna ca linia este deschisa
                return 1
            else:
                return 0
        else:
            return 0

    def linii_deschise(self, jucator):
        nr_linii_deschise = 0
        n = NR_COLOANE
        nr_linii_deschise += self.linie_deschisa(self.matr[0: n], jucator) \
                             + self.linie_deschisa(self.matr[n: 2 * n], jucator) \
                             + self.linie_deschisa(self.matr[2 * n: 3 * n], jucator) \
                             + self.linie_deschisa(self.matr[0: n * n: n], jucator) \
                             + self.linie_deschisa(self.matr[1: n * n: n], jucator) \
                             + self.linie_deschisa(self.matr[2: n * n: n], jucator) \
                             + self.linie_deschisa(self.matr[0: n * n: (n + 1)], jucator) \
                             + self.linie_deschisa(self.matr[(n - 1): (n * n - 1): (n - 1)], jucator)
        if n >= 4:
            nr_linii_deschise += self.linie_deschisa(self.matr[3 * n: 4 * n], jucator) \
                                 + self.linie_deschisa(self.matr[3: n * n: n], jucator)
        if n == 5:
            nr_linii_deschise += self.linie_deschisa(self.matr[4 * n: 5 * n], jucator) \
                                 + self.linie_deschisa(self.matr[4: n * n: n], jucator)
        return nr_linii_deschise

    def estimeaza_scor(self, adancime):
        t_final = self.final()
        # if (adancime==0):
        if t_final == self.__class__.JMAX:
            return 99 + adancime
        elif t_final == self.__class__.JMIN:
            return -99 - adancime
        elif t_final == 'remiza':
            return 0
        else:
            return self.linii_deschise(self.__class__.JMAX) - self.linii_deschise(self.__class__.JMIN)

    def __str__(self):
        n = NR_COLOANE
        sir = (" ".join([str(x) for x in self.matr[0: n]]) + "\n" +
               " ".join([str(x) for x in self.matr[n: 2 * n]]) + "\n" +
               " ".join([str(x) for x in self.matr[2 * n: 3 * n]]) + "\n")
        if n >= 4:
            sir += (" ".join([str(x) for x in self.matr[3 * n: 4 * n]]) + "\n")
        if n == 5:
            sir += (" ".join([str(x) for x in self.matr[4 * n: 5 * n]]) + "\n")
        return sir


class Stare:

    def __init__(self, tabla_joc, j_curent, adancime, parinte=None, scor=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent

        # adancimea in arborele de stari
        self.adancime = adancime

        # scorul starii (daca e finala) sau al celei mai bune stari-fiice (pentru jucatorul curent)
        self.scor = scor

        # lista de mutari posibile din starea curenta
        self.mutari_posibile = []

        # cea mai buna mutare din lista de mutari posibile pentru jucatorul curent
        self.stare_aleasa = None

    def jucator_opus(self):
        if self.j_curent == Joc.JMIN:
            return Joc.JMAX
        else:
            return Joc.JMIN

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        juc_opus = self.jucator_opus()
        l_stari_mutari = [Stare(mutare, juc_opus, self.adancime - 1, parinte=self) for mutare in l_mutari]

        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Juc curent:" + self.j_curent + ")\n"
        return sir


def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # este intr-un interval invalid deci nu o mai procesez

    stare.mutari_posibile = stare.mutari()

    if stare.j_curent == Joc.JMAX:
        scor_curent = float('-inf')

        for mutare in stare.mutari_posibile:
            # calculeaza scorul
            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent < stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor
            if alpha < stare_noua.scor:
                alpha = stare_noua.scor
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        scor_curent = float('inf')

        for mutare in stare.mutari_posibile:

            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent > stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if beta > stare_noua.scor:
                beta = stare_noua.scor
                if alpha >= beta:
                    break
    stare.scor = stare.stare_aleasa.scor

    return stare


def afis_daca_final(stare_curenta):
    global NR_REMIZE, NR_CASTIG_0, NR_CASTIG_X
    final = stare_curenta.tabla_joc.final()
    if final:
        if final == "remiza":
            #########print("Remiza!")
            NR_REMIZE += 1
        else:
            if final == Joc.JMAX:
                NR_CASTIG_X += 1
            else:
                NR_CASTIG_0 += 1
            ########## print("A castigat " + final)
        return True

    return False


def main():
    Joc.JMAX = 'x'
    Joc.JMIN = '0'

    # initializare tabla
    tabla_curenta = Joc()
    tabla_curenta.matr[POZITIE_X] = 'x'
    #########print("Tabla initiala")
    #########print(str(tabla_curenta))

    # creare stare initiala
    stare_curenta = Stare(tabla_curenta, '0', ADANCIME_MAX)

    while True:
        if stare_curenta.j_curent == Joc.JMIN:
            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = float(round(time.time() * 1000))
            stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
            #########print("Tabla dupa mutarea calculatorului")
            #########print(str(stare_curenta))

            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            #########print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")

            if afis_daca_final(stare_curenta):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.j_curent = stare_curenta.jucator_opus()

        else:  # jucatorul e JMAX
            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = float(round(time.time() * 1000))
            stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc
            #######print("Tabla dupa mutarea calculatorului")
            #######print(str(stare_curenta))

            # preiau timpul in milisecunde de dupa mutare
            t_dupa = float(round(time.time() * 1000))
            #######print("Calculatorul a \"gandit\" timp de " + str(t_dupa - t_inainte) + " milisecunde.")

            if afis_daca_final(stare_curenta):
                break

            # S-a realizat o mutare. Schimb jucatorul cu cel opus
            stare_curenta.j_curent = stare_curenta.jucator_opus()


if __name__ == "__main__":
    for pozitie in range(NR_COLOANE ** 2):
        POZITIE_X = pozitie
        print("Pentru pozitia ", POZITIE_X, " a lui x: ")
        main()
        print("X a castigat de ", NR_CASTIG_X, " ori")
        print("0 a castigat de ", NR_CASTIG_0, " ori")
        print("Remize: ", NR_REMIZE)
        print()
        NR_CASTIG_X = 0
        NR_CASTIG_0 = 0
        NR_REMIZE = 0
