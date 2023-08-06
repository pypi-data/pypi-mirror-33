import os
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication
import sys
from typing import List

from . import entree, calcul, erreur

HERE = os.path.abspath(os.path.dirname(__file__))


def _format_number(number: int) -> str:
    return "{:,}".format(number).replace(',', "'")


class Fenetre(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi(os.path.join(HERE, 'fenetre.ui'), self)
        self._set_colonnes(entree.fichier(os.path.join(HERE, 'aleatoire1M.txt.gz')))


    @pyqtSlot(bool)
    def on_fichierRandom1m_toggled(self, enabled: bool) -> None:
        if enabled:
            self._set_colonnes(entree.aleatoire(333333))

    @pyqtSlot(bool)
    def on_fichierAleatoire1m_toggled(self, enabled: bool) -> None:
        if enabled:
            self._set_colonnes(entree.fichier(os.path.join(HERE, 'aleatoire1M.txt.gz')))

    @pyqtSlot(int)
    def on_secteurBaseMax_valueChanged(self, valeur: int) -> None:
        self.secteurBaseMin.setMaximum(valeur - 1)

    @pyqtSlot(int)
    def on_comparoMax_valueChanged(self, valeur: int) -> None:
        self.comparoMin.setMaximum(valeur - 1)

    @pyqtSlot(int)
    def on_formuleDelta1_valueChanged(self, valeur: int) -> None:
        self.formuleDelta2.setMinimum(valeur + 1)

    @pyqtSlot(int)
    def on_formuleDelta2_valueChanged(self, valeur: int) -> None:
        self.formuleDelta3.setMinimum(valeur + 1)

    @pyqtSlot(int)
    def on_formuleDelta3_valueChanged(self, valeur: int) -> None:
        self.formuleDelta4.setMinimum(valeur + 1)

    @pyqtSlot()
    def on_execute_clicked(self) -> None:
        plus = [0, 0, 0]
        moins = [0, 0, 0]
        try:
            for i, valeurs in enumerate(self._colonnes):
                plus[i], moins[i] = calcul.calcul(valeurs, self.secteurBaseMin.value(), self.secteurBaseMax.value(),
                                                  self.comparoMin.value(), self.comparoMax.value(),
                                                  [
                                                      self.formuleDelta1.value(),
                                                      self.formuleDelta2.value(),
                                                      self.formuleDelta3.value(),
                                                      self.formuleDelta4.value()
                                                  ])
            for i, plus_texte, moins_texte in [(0, self.plusA, self.moinsA),
                                               (1, self.plusB, self.moinsB),
                                               (2, self.plusC, self.moinsC)]:
                plus_texte.setText(_format_number(plus[i]))
                moins_texte.setText(_format_number(moins[i]))
                plus_texte.setStyleSheet("QLabel { color: black; }")
                moins_texte.setStyleSheet("QLabel { color: black; }")
                if plus[i] > moins[i]:
                    plus_texte.setStyleSheet("QLabel { color: red; }")
                elif moins[i] > plus[i]:
                    moins_texte.setStyleSheet("QLabel { color: red; }")

            self.statusbar.showMessage("Calcul effectué", 1000)
        except erreur.Erreur as e:
            self.statusbar.showMessage(f"Erreur: {e}", 5000)

    def _set_colonnes(self, colonnes: entree.Entrees) -> None:
        self._colonnes = colonnes
        for widget in (self.secteurBaseMin, self.secteurBaseMax):
            widget.setMaximum(len(colonnes[0]))


def main() -> None:
    app = QApplication(sys.argv)
    fenetre = Fenetre()
    fenetre.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
