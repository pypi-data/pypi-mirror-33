import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRunnable, QThreadPool, QObject
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
import sys
from typing import List

from . import entree, calcul, erreur

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, 'VERSION')) as version:
    VERSION = version.read().strip()


def _format_number(number: int) -> str:
    return "{:,}".format(number).replace(',', "'")


class CalculateurSignals(QObject):
    fini = pyqtSignal()


class Calculateur(QRunnable):
    def __init__(self, parent: QMainWindow, base: List[int], secteur_debut: int, secteur_fin: int,
                 comparo_debut: int, comparo_fin: int,
                 formule_delta: List[int], plus_texte: QLabel, moins_texte: QLabel) -> None:
        super().__init__()
        self.parent = parent
        self.base = base
        self.secteur_debut = secteur_debut
        self.secteur_fin = secteur_fin
        self.comparo_debut = comparo_debut
        self.comparo_fin = comparo_fin
        self.formule_delta = formule_delta
        self.plus_texte = plus_texte
        self.moins_texte = moins_texte
        self.signaux = CalculateurSignals()

    @pyqtSlot()
    def run(self) -> None:
        try:
            plus, moins = calcul.calcul(self.base, self.secteur_debut, self.secteur_fin,
                                        self.comparo_debut, self.comparo_fin, self.formule_delta)
            self.plus_texte.setText(_format_number(plus))
            self.moins_texte.setText(_format_number(moins))
            if plus > moins:
                self.plus_texte.setStyleSheet("QLabel { color: red; }")
            elif moins > plus:
                self.moins_texte.setStyleSheet("QLabel { color: red; }")
            self.signaux.fini.emit()
        except erreur.Erreur as e:
            self.parent.statusbar.showMessage(f"Erreur: {e}", 5000)


class Fenetre(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(os.path.join(HERE, 'fenetre.ui'), self)
        self.setWindowTitle(self.windowTitle() + " " + VERSION)
        self._set_colonnes(entree.fichier(os.path.join(HERE, 'aleatoire1M.txt.gz')))
        self.threads = QThreadPool(self)
        self.a_faire = 0


    @pyqtSlot(bool)
    def on_fichierRandom1m_toggled(self, enabled: bool) -> None:
        if enabled:
            self._set_colonnes(entree.aleatoire(333333))

    @pyqtSlot(bool)
    def on_fichierAleatoire300k_toggled(self, enabled: bool) -> None:
        if enabled:
            self._set_colonnes(entree.fichier(os.path.join(HERE, 'aleatoire300K.txt.gz')))

    @pyqtSlot(bool)
    def on_fichierAleatoire1m_toggled(self, enabled: bool) -> None:
        if enabled:
            self._set_colonnes(entree.fichier(os.path.join(HERE, 'aleatoire1M.txt.gz')))

    @pyqtSlot(int)
    def on_secteurBaseMin_valueChanged(self, valeur: int) -> None:
        self.pasBaseValeur.setValue(self.secteurBaseMax.value() - valeur + 1)

    @pyqtSlot(int)
    def on_secteurBaseMax_valueChanged(self, valeur: int) -> None:
        self.secteurBaseMin.setMaximum(valeur - 1)
        self.pasBaseValeur.setValue(valeur - self.secteurBaseMin.value() + 1)

    @pyqtSlot(int)
    def on_comparoMin_valueChanged(self, valeur: int) -> None:
        self.pasComparosValeur.setValue(self.comparoMax.value() - valeur + 1)

    @pyqtSlot(int)
    def on_comparoMax_valueChanged(self, valeur: int) -> None:
        self.comparoMin.setMaximum(valeur)
        self.pasComparosValeur.setValue(valeur - self.comparoMin.value() + 1)

    @pyqtSlot(int)
    def on_formuleDelta1_valueChanged(self, valeur: int) -> None:
        self.formuleDelta2.setMinimum(valeur + 1)

    @pyqtSlot(int)
    def on_formuleDelta2_valueChanged(self, valeur: int) -> None:
        self.formuleDelta3.setMinimum(valeur + 1)

    @pyqtSlot(int)
    def on_formuleDelta3_valueChanged(self, valeur: int) -> None:
        self.formuleDelta4.setMinimum(valeur + 1)

    @pyqtSlot(bool)
    def on_pasComparos_toggled(self, valeur: bool) -> None:
        self.pasComparosValeur.setEnabled(valeur)
        self.pasBaseValeur.setEnabled(not valeur)

    @pyqtSlot()
    def on_execute_clicked(self) -> None:
        if self.a_faire != 0:
            return

        for texte in (self.plusA, self.moinsA, self.plusB, self.moinsB, self.plusC, self.moinsC):
            texte.setText("")
            texte.setStyleSheet("QLabel { color: black; }")
        self.execute.setEnabled(False)

        labels = [
            (self.plusA, self.moinsA),
            (self.plusB, self.moinsB),
            (self.plusC, self.moinsC)
        ]
        self.a_faire = 3
        for i, valeurs in enumerate(self._colonnes):
            plus_texte, moins_texte = labels[i]
            calculateur = Calculateur(self, valeurs, self.secteurBaseMin.value(), self.secteurBaseMax.value(),
                                      self.comparoMin.value(), self.comparoMax.value(),
                                      [self.formuleDelta1.value(), self.formuleDelta2.value(),
                                       self.formuleDelta3.value(), self.formuleDelta4.value()], plus_texte,
                                      moins_texte)
            calculateur.signaux.fini.connect(self.fait)
            self.threads.start(calculateur)

    @pyqtSlot()
    def fait(self) -> None:
        self.a_faire -= 1
        if self.a_faire != 0:
            return
        self.statusbar.showMessage("Calcul effectué", 1000)

        if self.pasBase.isChecked():
            max_texte = self.secteurBaseMax
            min_texte = self.secteurBaseMin
        elif self.pasComparos.isChecked():
            max_texte = self.comparoMax
            min_texte = self.comparoMin
        else:
            return

        delta = max_texte.value() - min_texte.value() + 1
        for texte in (max_texte, min_texte):
            texte.setValue(texte.value() + delta)

        self.execute.setEnabled(True)

    def _set_colonnes(self, colonnes: entree.Entrees) -> None:
        self._colonnes = colonnes
        for widget in (self.secteurBaseMin, self.secteurBaseMax, self.comparoMax, self.comparoMin,
                       self.pasBaseValeur, self.pasComparosValeur):
            widget.setMaximum(len(colonnes[0]))


def main() -> None:
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    fenetre.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
