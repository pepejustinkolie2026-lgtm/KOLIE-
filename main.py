# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
import random
import time
import os
import json

# =========================================================
# REGLAGES DE LA BANQUE DE QUIZ
# =========================================================
NB_QUESTIONS_PAR_QUIZ = 20
NB_QUESTIONNAIRES_PAR_CLASSE = 400

# Reglages de l'EXAMEN (different du quiz : toutes les matieres
# de la classe, questions de niveau intermediaire, classement IA).
NB_QUESTIONS_PAR_MATIERE_EXAMEN = 10
TEMPS_PAR_QUESTION_EXAMEN = 25  # secondes
NB_CANDIDATS_IA = 220
MOYENNE_ADMISSION = 10.00

# Effectifs des personnages IA presents dans les classements
# apres un examen, selon l'echelle consultee.
NB_IA_ECOLE = 50
NB_IA_REGIONAL = 600
NB_IA_NATIONAL = 1500

# Duree (en secondes) de la "correction" simulee d'un examen avant
# que les resultats ne deviennent consultables.
DUREE_CORRECTION_SECONDES = 30

NOM_CORRECTEUR = "BLACK M"


def formater_duree(secondes):
    """Formate un nombre de secondes en texte lisible (secondes ou
    minutes selon la duree), pour l'attente des resultats d'examen."""
    secondes = max(1, int(secondes))
    if secondes < 60:
        return str(secondes) + " seconde(s)"
    minutes = (secondes // 60) + (1 if secondes % 60 else 0)
    return str(minutes) + " minute(s)"

Window.clearcolor = (0.94, 0.96, 1, 1)


# =========================================================
# OUTILS
# =========================================================

BLUE = (0.08, 0.35, 0.75, 1)
DARK = (0.12, 0.14, 0.18, 1)
GREY = (0.35, 0.38, 0.45, 1)
GREEN = (0.10, 0.55, 0.25, 1)
RED = (0.75, 0.15, 0.15, 1)
ORANGE = (0.85, 0.45, 0.08, 1)


def bouton(text, action=None, couleur=BLUE, hauteur=55):
    b = Button(
        text=text,
        font_size=dp(17),
        size_hint_y=None,
        height=dp(hauteur),
        background_normal="",
        background_color=couleur
    )
    if action:
        b.bind(on_release=action)
    return b


def titre(text, taille=28):
    return Label(
        text=text,
        markup=True,
        font_size=dp(taille),
        color=BLUE,
        halign="center",
        valign="middle",
        size_hint_y=None,
        height=dp(65)
    )


# =========================================================
# BANQUE DE 20 QUESTIONS
# Chaque question : question, 4 choix, bonne réponse
# =========================================================

QUESTIONS = [
    {
        "matiere": "Sciences",
        "question": "Quel organe pompe le sang dans le corps humain ?",
        "choix": ["Le poumon", "Le coeur", "Le foie", "L'estomac"],
        "bonne": 1,
        "explication": "Le coeur est un muscle qui se contracte pour "
                        "envoyer le sang dans tout le corps."
    },
    {
        "matiere": "Sciences",
        "question": "Quelle est la formule chimique de l'eau ?",
        "choix": ["CO2", "O2", "H2O", "NaCl"],
        "bonne": 2,
        "explication": "L'eau est composee de 2 atomes d'hydrogene et "
                        "1 atome d'oxygene, d'ou H2O."
    },
    {
        "matiere": "Sciences",
        "question": "Quelle planète est la plus proche du Soleil ?",
        "choix": ["Mars", "Mercure", "Jupiter", "Vénus"],
        "bonne": 1,
        "explication": "Mercure est la premiere planete du systeme "
                        "solaire, juste apres le Soleil."
    },
    {
        "matiere": "Sciences",
        "question": "Combien de pattes possède normalement un insecte ?",
        "choix": ["4", "6", "8", "10"],
        "bonne": 1,
        "explication": "Un insecte possede 3 paires de pattes, "
                        "soit 6 pattes au total."
    },
    {
        "matiere": "Sciences",
        "question": "Quel gaz les humains utilisent-ils principalement pour respirer ?",
        "choix": ["Oxygène", "Azote", "Hydrogène", "Hélium"],
        "bonne": 0,
        "explication": "Le corps utilise l'oxygene de l'air pour "
                        "produire de l'energie."
    },
    {
        "matiere": "Sciences",
        "question": "Quel organe permet de voir ?",
        "choix": ["Le nez", "L'oeil", "L'oreille", "La bouche"],
        "bonne": 1,
        "explication": "L'oeil est l'organe de la vue, il capte "
                        "la lumiere."
    },
    {
        "matiere": "Sciences",
        "question": "Quel organe filtre le sang et produit l'urine ?",
        "choix": ["Le foie", "Le rein", "Le coeur", "L'estomac"],
        "bonne": 1,
        "explication": "Les reins filtrent le sang et eliminent "
                        "les dechets sous forme d'urine."
    },
    {
        "matiere": "Sciences",
        "question": "Combien d'os compte environ le squelette d'un adulte ?",
        "choix": ["106", "206", "306", "406"],
        "bonne": 1,
        "explication": "Le squelette humain adulte compte environ "
                        "206 os."
    },
    {
        "matiere": "Sciences",
        "question": "Quelle vitamine le corps produit-il grâce au soleil ?",
        "choix": ["Vitamine A", "Vitamine C", "Vitamine D", "Vitamine K"],
        "bonne": 2,
        "explication": "La peau produit de la vitamine D sous "
                        "l'effet des rayons du soleil."
    },
    {
        "matiere": "Sciences",
        "question": "Comment appelle-t-on la transformation de l'eau liquide en vapeur ?",
        "choix": ["Condensation", "Evaporation", "Solidification", "Fusion"],
        "bonne": 1,
        "explication": "L'evaporation transforme l'eau liquide "
                        "en vapeur d'eau."
    },
    {
        "matiere": "Sciences",
        "question": "Quel est le plus grand organe du corps humain ?",
        "choix": ["Le foie", "Le coeur", "La peau", "Le cerveau"],
        "bonne": 2,
        "explication": "La peau est le plus grand organe du corps "
                        "humain, elle protege l'organisme."
    },
    {
        "matiere": "Sciences",
        "question": "Quelle partie de la plante absorbe l'eau et les minéraux du sol ?",
        "choix": ["La feuille", "La tige", "La racine", "La fleur"],
        "bonne": 2,
        "explication": "Les racines absorbent l'eau et les "
                        "mineraux necessaires a la plante."
    },
    {
        "matiere": "Sciences",
        "question": "Quel gaz les plantes rejettent-elles pendant la photosynthèse ?",
        "choix": ["Dioxyde de carbone", "Azote", "Oxygène", "Hydrogène"],
        "bonne": 2,
        "explication": "Pendant la photosynthese, les plantes "
                        "absorbent le CO2 et rejettent de l'oxygene."
    },
    {
        "matiere": "Sciences",
        "question": "Combien de temps la lumière du Soleil met-elle environ pour atteindre la Terre ?",
        "choix": ["8 secondes", "8 minutes", "8 heures", "8 jours"],
        "bonne": 1,
        "explication": "La lumiere du Soleil met environ 8 minutes "
                        "pour parcourir la distance jusqu'a la Terre."
    },
    {
        "matiere": "Sciences",
        "question": "Quel sens permet de percevoir les sons ?",
        "choix": ["La vue", "L'ouïe", "Le toucher", "L'odorat"],
        "bonne": 1,
        "explication": "L'ouie est le sens qui permet de percevoir "
                        "les sons grace aux oreilles."
    },
    {
        "matiere": "Sciences",
        "question": "Quel est le nom du muscle qui permet la respiration en se contractant sous les poumons ?",
        "choix": ["Le biceps", "Le diaphragme", "Le triceps", "Le mollet"],
        "bonne": 1,
        "explication": "Le diaphragme est un muscle situe sous "
                        "les poumons qui permet la respiration."
    },
    {
        "matiere": "Sciences",
        "question": "Quel est l'état de la matière de la glace ?",
        "choix": ["Liquide", "Gazeux", "Solide", "Plasma"],
        "bonne": 2,
        "explication": "La glace est de l'eau a l'etat solide."
    },
    {
        "matiere": "Sciences",
        "question": "Quel astre est principalement responsable des marées sur Terre ?",
        "choix": ["Le Soleil", "La Lune", "Mars", "Vénus"],
        "bonne": 1,
        "explication": "L'attraction de la Lune est la principale "
                        "cause des marees."
    },
    {
        "matiere": "Sciences",
        "question": "Combien de temps dure environ une grossesse humaine ?",
        "choix": ["6 mois", "9 mois", "12 mois", "3 mois"],
        "bonne": 1,
        "explication": "Une grossesse humaine dure en moyenne "
                        "environ 9 mois."
    },
    {
        "matiere": "Sciences",
        "question": "Comment appelle-t-on l'étude des êtres vivants ?",
        "choix": ["Geologie", "Chimie", "Biologie", "Physique"],
        "bonne": 2,
        "explication": "La biologie est la science qui etudie "
                        "les etres vivants."
    },

    {
        "matiere": "Histoire",
        "question": "En quelle année Christophe Colomb arrive-t-il en Amérique ?",
        "choix": ["1492", "1789", "1914", "1453"],
        "bonne": 0,
        "explication": "Christophe Colomb atteint les Ameriques "
                        "en 1492, en cherchant une route vers l'Asie."
    },
    {
        "matiere": "Histoire",
        "question": "Quelle civilisation a construit les pyramides de Gizeh ?",
        "choix": ["Romaine", "Égyptienne", "Maya", "Grecque"],
        "bonne": 1,
        "explication": "Les pyramides de Gizeh ont ete construites "
                        "par les anciens Egyptiens."
    },
    {
        "matiere": "Histoire",
        "question": "Qui est souvent considéré comme le fondateur de l'Empire du Mali ?",
        "choix": ["Soundiata Keita", "Askia Mohammed", "Shaka Zulu", "Hannibal"],
        "bonne": 0,
        "explication": "Soundiata Keita a fonde l'Empire du Mali "
                        "au 13e siecle."
    },
    {
        "matiere": "Histoire",
        "question": "La Première Guerre mondiale commence en quelle année ?",
        "choix": ["1905", "1914", "1918", "1939"],
        "bonne": 1,
        "explication": "La Premiere Guerre mondiale a debute en 1914 "
                        "et s'est terminee en 1918."
    },
    {
        "matiere": "Histoire",
        "question": "La Révolution française commence en quelle année ?",
        "choix": ["1776", "1789", "1804", "1815"],
        "bonne": 1,
        "explication": "La Revolution française commence en 1789 "
                        "avec la prise de la Bastille."
    },
    {
        "matiere": "Histoire",
        "question": "Qui fut le premier président des Etats-Unis ?",
        "choix": ["Abraham Lincoln", "George Washington", "Thomas Jefferson", "John Adams"],
        "bonne": 1,
        "explication": "George Washington est devenu le premier "
                        "president des Etats-Unis en 1789."
    },
    {
        "matiere": "Histoire",
        "question": "En quelle année la Guinée a-t-elle obtenu son indépendance ?",
        "choix": ["1945", "1958", "1960", "1962"],
        "bonne": 1,
        "explication": "La Guinee a obtenu son independance de "
                        "la France le 2 octobre 1958."
    },
    {
        "matiere": "Histoire",
        "question": "Qui a lutté contre l'apartheid et est devenu président d'Afrique du Sud ?",
        "choix": ["Nelson Mandela", "Kwame Nkrumah", "Julius Nyerere", "Patrice Lumumba"],
        "bonne": 0,
        "explication": "Nelson Mandela a lutte contre l'apartheid "
                        "et est devenu president en 1994."
    },
    {
        "matiere": "Histoire",
        "question": "Quelle guerre a opposé le Nord et le Sud des Etats-Unis ?",
        "choix": ["La guerre d'Indépendance", "La guerre de Sécession", "La guerre froide", "La guerre du Vietnam"],
        "bonne": 1,
        "explication": "La guerre de Secession (1861-1865) opposait "
                        "les Etats du Nord et du Sud."
    },
    {
        "matiere": "Histoire",
        "question": "Quel empereur français est né en Corse ?",
        "choix": ["Louis XIV", "Napoléon Bonaparte", "Charlemagne", "Louis XVI"],
        "bonne": 1,
        "explication": "Napoleon Bonaparte est ne a Ajaccio, "
                        "en Corse, en 1769."
    },
    {
        "matiere": "Histoire",
        "question": "En quelle année le mur de Berlin est-il tombé ?",
        "choix": ["1979", "1989", "1991", "1999"],
        "bonne": 1,
        "explication": "Le mur de Berlin est tombe en novembre 1989."
    },
    {
        "matiere": "Histoire",
        "question": "Qui fut le premier président de la République de Guinée ?",
        "choix": ["Ahmed Sékou Touré", "Lansana Conté", "Alpha Condé", "Sékouba Konaté"],
        "bonne": 0,
        "explication": "Ahmed Sekou Toure fut le premier president "
                        "de la Guinee independante."
    },
    {
        "matiere": "Histoire",
        "question": "Quelle civilisation antique a inventé l'écriture cunéiforme ?",
        "choix": ["Les Egyptiens", "Les Sumériens", "Les Romains", "Les Grecs"],
        "bonne": 1,
        "explication": "Les Sumeriens, en Mesopotamie, ont invente "
                        "l'ecriture cuneiforme."
    },
    {
        "matiere": "Histoire",
        "question": "Quelle bataille marque la défaite finale de Napoléon ?",
        "choix": ["Austerlitz", "Waterloo", "Trafalgar", "Verdun"],
        "bonne": 1,
        "explication": "Napoleon est definitivement vaincu a la "
                        "bataille de Waterloo en 1815."
    },
    {
        "matiere": "Histoire",
        "question": "Quel traité met fin à la Première Guerre mondiale ?",
        "choix": ["Le traité de Versailles", "Le traité de Rome", "Le traité de Paris", "Le traité de Vienne"],
        "bonne": 0,
        "explication": "Le traite de Versailles, signe en 1919, "
                        "met officiellement fin a la Premiere Guerre mondiale."
    },
    {
        "matiere": "Histoire",
        "question": "Quelle organisation internationale est créée en 1945 pour maintenir la paix ?",
        "choix": ["L'ONU", "L'Union Africaine", "L'OTAN", "L'Union Européenne"],
        "bonne": 0,
        "explication": "L'Organisation des Nations unies (ONU) "
                        "est fondee en 1945."
    },
    {
        "matiere": "Histoire",
        "question": "Quel roi de France est surnommé le « Roi Soleil » ?",
        "choix": ["Louis XIII", "Louis XIV", "Louis XV", "Louis XVI"],
        "bonne": 1,
        "explication": "Louis XIV, qui regna tres longtemps, est "
                        "surnomme le « Roi Soleil »."
    },
    {
        "matiere": "Histoire",
        "question": "Quel navigateur portugais a ouvert la route maritime vers l'Inde en contournant l'Afrique ?",
        "choix": ["Vasco de Gama", "Christophe Colomb", "Magellan", "Marco Polo"],
        "bonne": 0,
        "explication": "Vasco de Gama a atteint l'Inde en 1498 "
                        "en contournant l'Afrique."
    },
    {
        "matiere": "Histoire",
        "question": "Quel événement a déclenché la Seconde Guerre mondiale en 1939 ?",
        "choix": ["L'invasion de la Pologne", "La crise de 1929", "L'assassinat à Sarajevo", "La chute de Rome"],
        "bonne": 0,
        "explication": "L'invasion de la Pologne par l'Allemagne, "
                        "le 1er septembre 1939, declenche la guerre."
    },
    {
        "matiere": "Histoire",
        "question": "Quel empereur du Mali est célèbre pour son immense richesse en or ?",
        "choix": ["Kankou Moussa", "Soundiata Keita", "Askia Mohammed", "Chaka Zoulou"],
        "bonne": 0,
        "explication": "Kankou Moussa (Mansa Moussa) etait un "
                        "empereur du Mali reputee pour son immense fortune."
    },

    {
        "matiere": "Français",
        "question": "Quel est le synonyme de « rapide » ?",
        "choix": ["Lent", "Vif", "Faible", "Triste"],
        "bonne": 1,
        "explication": "« Vif » signifie egalement rapide, agile."
    },
    {
        "matiere": "Français",
        "question": "Quel est le contraire de « difficile » ?",
        "choix": ["Compliqué", "Dur", "Facile", "Fort"],
        "bonne": 2,
        "explication": "« Facile » est le contraire de « difficile »."
    },
    {
        "matiere": "Français",
        "question": "Dans « Les élèves travaillent », quel est le verbe ?",
        "choix": ["Les", "Élèves", "Travaillent", "Les élèves"],
        "bonne": 2,
        "explication": "« Travaillent » est le verbe conjugue de "
                        "la phrase."
    },
    {
        "matiere": "Français",
        "question": "Quel mot est un adjectif qualificatif ?",
        "choix": ["Maison", "Courir", "Grand", "Rapidement"],
        "bonne": 2,
        "explication": "« Grand » decrit une qualite, c'est un "
                        "adjectif qualificatif."
    },
    {
        "matiere": "Français",
        "question": "Quel est le pluriel de « cheval » ?",
        "choix": ["Chevals", "Chevaux", "Chevales", "Chevaus"],
        "bonne": 1,
        "explication": "Les mots en « -al » font leur pluriel en "
                        "« -aux » : cheval -> chevaux."
    },
    {
        "matiere": "Français",
        "question": "Quel est le contraire de « grand » ?",
        "choix": ["Petit", "Large", "Long", "Haut"],
        "bonne": 0,
        "explication": "« Petit » est l'antonyme de « grand »."
    },
    {
        "matiere": "Français",
        "question": "Quel est le synonyme de « content » ?",
        "choix": ["Triste", "Heureux", "Fâché", "Fatigué"],
        "bonne": 1,
        "explication": "« Heureux » a le meme sens que « content »."
    },
    {
        "matiere": "Français",
        "question": "Quel est le féminin du mot « acteur » ?",
        "choix": ["Acteure", "Actrice", "Actoresse", "Acteuse"],
        "bonne": 1,
        "explication": "Le feminin de « acteur » est « actrice »."
    },
    {
        "matiere": "Français",
        "question": "Combien de voyelles compte l'alphabet français ?",
        "choix": ["5", "6", "7", "8"],
        "bonne": 1,
        "explication": "L'alphabet francais compte 6 voyelles : "
                        "a, e, i, o, u, y."
    },
    {
        "matiere": "Français",
        "question": "Quel est le temps du verbe dans « il mangea » ?",
        "choix": ["Le present", "L'imparfait", "Le passe simple", "Le futur"],
        "bonne": 2,
        "explication": "« Il mangea » est conjugue au passe simple."
    },
    {
        "matiere": "Français",
        "question": "Quel signe de ponctuation marque une question ?",
        "choix": ["Le point", "La virgule", "Le point d'interrogation", "Le point d'exclamation"],
        "bonne": 2,
        "explication": "Le point d'interrogation se place a la "
                        "fin d'une phrase interrogative."
    },
    {
        "matiere": "Français",
        "question": "Quel est l'antonyme du verbe « monter » ?",
        "choix": ["Descendre", "Sortir", "Entrer", "Tomber"],
        "bonne": 0,
        "explication": "« Descendre » est le contraire de « monter »."
    },
    {
        "matiere": "Français",
        "question": "Comment appelle-t-on un mot qui a le même sens qu'un autre ?",
        "choix": ["Un homonyme", "Un synonyme", "Un antonyme", "Un paronyme"],
        "bonne": 1,
        "explication": "Un synonyme est un mot de sens proche ou "
                        "identique a un autre."
    },
    {
        "matiere": "Français",
        "question": "Quel est le sujet dans la phrase « Le chat dort » ?",
        "choix": ["Le chat", "Dort", "Le", "Chat dort"],
        "bonne": 0,
        "explication": "« Le chat » est le groupe sujet de la phrase."
    },
    {
        "matiere": "Français",
        "question": "Quel est le pluriel de « journal » ?",
        "choix": ["Journals", "Journaux", "Journales", "Journaus"],
        "bonne": 1,
        "explication": "Les mots en « -al » font souvent leur "
                        "pluriel en « -aux »."
    },
    {
        "matiere": "Français",
        "question": "Qui est l'auteur du roman « Les Misérables » ?",
        "choix": ["Victor Hugo", "Emile Zola", "Molière", "Voltaire"],
        "bonne": 0,
        "explication": "« Les Miserables » est un roman ecrit "
                        "par Victor Hugo en 1862."
    },
    {
        "matiere": "Français",
        "question": "Quelle figure de style compare deux éléments à l'aide de « comme » ?",
        "choix": ["La metaphore", "La comparaison", "L'hyperbole", "La personnification"],
        "bonne": 1,
        "explication": "La comparaison relie deux elements a "
                        "l'aide d'un mot comme « comme »."
    },
    {
        "matiere": "Français",
        "question": "Quel est le participe passé du verbe « faire » ?",
        "choix": ["Fais", "Fait", "Faisant", "Ferai"],
        "bonne": 1,
        "explication": "Le participe passe du verbe « faire » "
                        "est « fait »."
    },
    {
        "matiere": "Français",
        "question": "Comment appelle-t-on une phrase qui exprime un ordre ?",
        "choix": ["Une phrase declarative", "Une phrase imperative", "Une phrase interrogative", "Une phrase exclamative"],
        "bonne": 1,
        "explication": "La phrase imperative exprime un ordre "
                        "ou un conseil."
    },
    {
        "matiere": "Français",
        "question": "Quel est le complément d'objet direct dans « Marie lit un livre » ?",
        "choix": ["Marie", "Lit", "Un livre", "Marie lit"],
        "bonne": 2,
        "explication": "« Un livre » repond a la question « lit "
                        "quoi ? », c'est le COD."
    },

    {
        "matiere": "Géographie",
        "question": "Quel est le plus grand océan du monde ?",
        "choix": ["Atlantique", "Indien", "Pacifique", "Arctique"],
        "bonne": 2,
        "explication": "L'ocean Pacifique est le plus vaste et le "
                        "plus profond des oceans."
    },
    {
        "matiere": "Géographie",
        "question": "Quelle est la capitale de la Guinée ?",
        "choix": ["Kankan", "Labé", "Conakry", "Kindia"],
        "bonne": 2,
        "explication": "Conakry est la capitale et la plus grande "
                        "ville de la Guinee."
    },
    {
        "matiere": "Géographie",
        "question": "Quel continent est le plus vaste ?",
        "choix": ["Europe", "Afrique", "Asie", "Océanie"],
        "bonne": 2,
        "explication": "L'Asie est le plus grand continent en "
                        "superficie et en population."
    },
    {
        "matiere": "Géographie",
        "question": "Le Sahara se trouve principalement sur quel continent ?",
        "choix": ["Afrique", "Asie", "Europe", "Amérique"],
        "bonne": 0,
        "explication": "Le Sahara est un grand desert situe en "
                        "Afrique du Nord."
    },
    {
        "matiere": "Géographie",
        "question": "Quel est le plus long fleuve d'Afrique ?",
        "choix": ["Niger", "Congo", "Nil", "Sénégal"],
        "bonne": 2,
        "explication": "Le Nil est le plus long fleuve d'Afrique, "
                        "traversant notamment l'Egypte."
    },
    {
        "matiere": "Géographie",
        "question": "Quelle est la plus haute montagne du monde ?",
        "choix": ["Le Kilimandjaro", "L'Everest", "Le Mont Blanc", "L'Aconcagua"],
        "bonne": 1,
        "explication": "L'Everest, dans l'Himalaya, culmine a "
                        "plus de 8 800 metres."
    },
    {
        "matiere": "Géographie",
        "question": "Quel est le plus grand pays du monde par sa superficie ?",
        "choix": ["Le Canada", "La Chine", "La Russie", "Le Brésil"],
        "bonne": 2,
        "explication": "La Russie est le plus vaste pays du monde "
                        "par sa superficie."
    },
    {
        "matiere": "Géographie",
        "question": "Quel est le plus grand désert froid du monde ?",
        "choix": ["Le Sahara", "Le Gobi", "L'Antarctique", "Le Kalahari"],
        "bonne": 2,
        "explication": "L'Antarctique est considere comme le plus "
                        "grand desert froid du monde."
    },
    {
        "matiere": "Géographie",
        "question": "Quelle mer borde le Maroc et l'Algérie au nord ?",
        "choix": ["La Mer Rouge", "La Méditerranée", "La Mer Noire", "La Mer Caspienne"],
        "bonne": 1,
        "explication": "La Mediterranee borde le nord du Maroc "
                        "et de l'Algerie."
    },
    {
        "matiere": "Géographie",
        "question": "Quel fleuve traverse la ville de Paris ?",
        "choix": ["La Loire", "Le Rhône", "La Seine", "La Garonne"],
        "bonne": 2,
        "explication": "La Seine est le fleuve qui traverse Paris."
    },
    {
        "matiere": "Géographie",
        "question": "Quelle est la capitale du Sénégal ?",
        "choix": ["Thiès", "Dakar", "Saint-Louis", "Touba"],
        "bonne": 1,
        "explication": "Dakar est la capitale du Senegal."
    },
    {
        "matiere": "Géographie",
        "question": "Quel océan sépare l'Afrique de l'Amérique ?",
        "choix": ["L'ocean Pacifique", "L'ocean Atlantique", "L'ocean Indien", "L'ocean Arctique"],
        "bonne": 1,
        "explication": "L'ocean Atlantique separe le continent "
                        "africain du continent americain."
    },
    {
        "matiere": "Géographie",
        "question": "Quel pays est surnommé le « pays du Soleil levant » ?",
        "choix": ["La Chine", "Le Japon", "La Corée", "La Thaïlande"],
        "bonne": 1,
        "explication": "Le Japon est surnomme le « pays du "
                        "Soleil levant »."
    },
    {
        "matiere": "Géographie",
        "question": "Quelle chaîne de montagnes sépare traditionnellement l'Europe de l'Asie ?",
        "choix": ["Les Alpes", "L'Oural", "Les Andes", "L'Himalaya"],
        "bonne": 1,
        "explication": "La chaine de l'Oural marque la limite "
                        "traditionnelle entre l'Europe et l'Asie."
    },
    {
        "matiere": "Géographie",
        "question": "Quelle est la capitale du Mali ?",
        "choix": ["Ségou", "Bamako", "Sikasso", "Mopti"],
        "bonne": 1,
        "explication": "Bamako est la capitale du Mali."
    },
    {
        "matiere": "Géographie",
        "question": "Quel est le plus petit continent du monde ?",
        "choix": ["L'Europe", "L'Océanie", "L'Antarctique", "L'Amerique du Sud"],
        "bonne": 1,
        "explication": "L'Oceanie est le plus petit continent "
                        "en superficie."
    },
    {
        "matiere": "Géographie",
        "question": "Quel pays est traversé par la Grande Muraille ?",
        "choix": ["Le Japon", "La Chine", "La Mongolie", "La Corée"],
        "bonne": 1,
        "explication": "La Grande Muraille se trouve en Chine."
    },
    {
        "matiere": "Géographie",
        "question": "Quelle ville est la capitale politique de la Côte d'Ivoire ?",
        "choix": ["Abidjan", "Yamoussoukro", "Bouaké", "San-Pédro"],
        "bonne": 1,
        "explication": "Yamoussoukro est la capitale politique "
                        "de la Cote d'Ivoire, meme si Abidjan reste "
                        "le plus grand centre economique."
    },
    {
        "matiere": "Géographie",
        "question": "Quel type de climat caractérise la forêt équatoriale ?",
        "choix": ["Froid et sec", "Chaud et humide", "Tempere", "Polaire"],
        "bonne": 1,
        "explication": "Le climat equatorial est chaud et tres "
                        "humide toute l'annee."
    },
    {
        "matiere": "Géographie",
        "question": "Quel est le point culminant du continent africain ?",
        "choix": ["Le mont Kenya", "Le Kilimandjaro", "Le mont Cameroun", "Le Toubkal"],
        "bonne": 1,
        "explication": "Le Kilimandjaro, en Tanzanie, est le "
                        "plus haut sommet d'Afrique."
    },

    {
        "matiere": "Maths",
        "question": "Quelle est la valeur de π (pi) arrondie à 2 décimales ?",
        "choix": ["3.14", "3.41", "2.71", "3.10"],
        "bonne": 0,
        "explication": "Pi vaut environ 3,14159, soit 3,14 arrondi "
                        "a 2 decimales."
    },
    {
        "matiere": "Maths",
        "question": "Quelle est la racine carrée de 64 ?",
        "choix": ["6", "7", "8", "9"],
        "bonne": 2,
        "explication": "8 x 8 = 64, donc la racine carree de 64 est 8."
    },
    {
        "matiere": "Maths",
        "question": "Comment appelle-t-on un triangle ayant un angle de 90° ?",
        "choix": ["Equilateral", "Isocele", "Rectangle", "Scalene"],
        "bonne": 2,
        "explication": "Un triangle rectangle possede un angle droit "
                        "de 90 degres."
    },
    {
        "matiere": "Maths",
        "question": "Quelle est la solution de l'équation 2x + 4 = 10 ?",
        "choix": ["2", "3", "4", "5"],
        "bonne": 1,
        "explication": "2x = 10 - 4 = 6, donc x = 3."
    },
    {
        "matiere": "Maths",
        "question": "Quelle est la dérivée de x² ?",
        "choix": ["x", "2x", "x²", "2"],
        "bonne": 1,
        "explication": "La derivee de x^n est n.x^(n-1), donc la "
                        "derivee de x² est 2x."
    },
    {
        "matiere": "Maths",
        "question": "Combien font 7 x 8 ?",
        "choix": ["54", "56", "58", "64"],
        "bonne": 1,
        "explication": "7 multiplie par 8 est egal a 56."
    },
    {
        "matiere": "Maths",
        "question": "Combien font 15% de 200 ?",
        "choix": ["15", "20", "30", "40"],
        "bonne": 2,
        "explication": "15% de 200 = 0,15 x 200 = 30."
    },
    {
        "matiere": "Maths",
        "question": "Quelle est l'aire d'un carré de côté 5 ?",
        "choix": ["10", "15", "20", "25"],
        "bonne": 3,
        "explication": "L'aire d'un carre est cote x cote, "
                        "soit 5 x 5 = 25."
    },
    {
        "matiere": "Maths",
        "question": "Combien de côtés possède un hexagone ?",
        "choix": ["5", "6", "7", "8"],
        "bonne": 1,
        "explication": "Un hexagone possede 6 cotes."
    },
    {
        "matiere": "Maths",
        "question": "Quelle est la somme des angles d'un triangle ?",
        "choix": ["90°", "180°", "270°", "360°"],
        "bonne": 1,
        "explication": "La somme des angles d'un triangle vaut "
                        "toujours 180 degres."
    },
    {
        "matiere": "Maths",
        "question": "Quel est le résultat de 9 au carré ?",
        "choix": ["18", "72", "81", "90"],
        "bonne": 2,
        "explication": "9² = 9 x 9 = 81."
    },
    {
        "matiere": "Maths",
        "question": "Comment appelle-t-on un nombre divisible seulement par 1 et par lui-même ?",
        "choix": ["Un nombre pair", "Un nombre premier", "Un nombre impair", "Un nombre compose"],
        "bonne": 1,
        "explication": "Un nombre premier n'a que deux diviseurs : "
                        "1 et lui-meme."
    },
    {
        "matiere": "Maths",
        "question": "Quelle fraction est équivalente à 0,5 ?",
        "choix": ["1/3", "1/2", "1/4", "2/3"],
        "bonne": 1,
        "explication": "0,5 correspond exactement a la fraction 1/2."
    },
    {
        "matiere": "Maths",
        "question": "Quelle est la formule du périmètre d'un cercle de rayon r ?",
        "choix": ["πr²", "2πr", "πr", "πr/2"],
        "bonne": 1,
        "explication": "Le perimetre (circonference) d'un cercle "
                        "est 2πr."
    },
    {
        "matiere": "Maths",
        "question": "Combien font (-3) multiplié par (-4) ?",
        "choix": ["-12", "-7", "7", "12"],
        "bonne": 3,
        "explication": "Le produit de deux nombres negatifs est "
                        "positif : (-3) x (-4) = 12."
    },
    {
        "matiere": "Maths",
        "question": "Quelle est la valeur de 10 puissance 3 ?",
        "choix": ["100", "1000", "10000", "30"],
        "bonne": 1,
        "explication": "10³ = 10 x 10 x 10 = 1000."
    },
    {
        "matiere": "Maths",
        "question": "Combien font 100 divisé par 4 ?",
        "choix": ["20", "25", "30", "40"],
        "bonne": 1,
        "explication": "100 divise par 4 est egal a 25."
    },
    {
        "matiere": "Maths",
        "question": "Comment appelle-t-on une équation du second degré ?",
        "choix": ["Une equation lineaire", "Une equation quadratique", "Une equation cubique", "Une inequation"],
        "bonne": 1,
        "explication": "Une equation du second degre est aussi "
                        "appelee equation quadratique."
    },
    {
        "matiere": "Maths",
        "question": "Quelle est la moyenne des nombres 4, 8 et 12 ?",
        "choix": ["6", "7", "8", "9"],
        "bonne": 2,
        "explication": "(4 + 8 + 12) / 3 = 24 / 3 = 8."
    },
    {
        "matiere": "Maths",
        "question": "Quel est le volume d'un cube d'arête 3 ?",
        "choix": ["9", "18", "27", "36"],
        "bonne": 2,
        "explication": "Le volume d'un cube est arete³, soit "
                        "3³ = 27."
    },

    {
        "matiere": "Physique",
        "question": "Quelle est l'unité de mesure de la force ?",
        "choix": ["Watt", "Joule", "Newton", "Pascal"],
        "bonne": 2,
        "explication": "La force se mesure en Newton (N) dans le "
                        "systeme international."
    },
    {
        "matiere": "Physique",
        "question": "Quelle est la vitesse de la lumière dans le vide (environ) ?",
        "choix": ["300 000 km/s", "150 000 km/s", "3 000 km/s", "30 000 km/s"],
        "bonne": 0,
        "explication": "La lumiere se deplace a environ "
                        "300 000 km par seconde dans le vide."
    },
    {
        "matiere": "Physique",
        "question": "Quelle grandeur mesure-t-on en volts ?",
        "choix": ["Intensite", "Tension", "Resistance", "Puissance"],
        "bonne": 1,
        "explication": "Le volt (V) est l'unite de la tension "
                        "electrique."
    },
    {
        "matiere": "Physique",
        "question": "Quelle loi relie tension, intensité et résistance ?",
        "choix": ["Loi de Newton", "Loi d'Ohm", "Loi de Coulomb", "Loi de Boyle"],
        "bonne": 1,
        "explication": "La loi d'Ohm s'ecrit U = R x I."
    },
    {
        "matiere": "Physique",
        "question": "Quelle est l'accélération de la pesanteur sur Terre (environ) ?",
        "choix": ["5,8 m/s²", "9,8 m/s²", "12,8 m/s²", "15 m/s²"],
        "bonne": 1,
        "explication": "Sur Terre, l'acceleration de la pesanteur "
                        "vaut environ 9,8 m/s²."
    },
    {
        "matiere": "Physique",
        "question": "Quelle est l'unité de mesure de l'énergie ?",
        "choix": ["Le watt", "Le joule", "Le newton", "Le volt"],
        "bonne": 1,
        "explication": "L'energie se mesure en joules (J) dans "
                        "le systeme international."
    },
    {
        "matiere": "Physique",
        "question": "Quelle est l'unité de mesure de la puissance électrique ?",
        "choix": ["Le watt", "L'ampere", "Le volt", "L'ohm"],
        "bonne": 0,
        "explication": "La puissance electrique se mesure en "
                        "watts (W)."
    },
    {
        "matiere": "Physique",
        "question": "Comment appelle-t-on le passage de l'état solide à l'état liquide ?",
        "choix": ["L'evaporation", "La fusion", "La sublimation", "La condensation"],
        "bonne": 1,
        "explication": "La fusion est le passage de l'etat "
                        "solide a l'etat liquide."
    },
    {
        "matiere": "Physique",
        "question": "Quelle grandeur mesure-t-on en ampères ?",
        "choix": ["La tension", "L'intensite du courant", "La resistance", "La puissance"],
        "bonne": 1,
        "explication": "L'ampere (A) est l'unite de l'intensite "
                        "du courant electrique."
    },
    {
        "matiere": "Physique",
        "question": "Quel scientifique a formulé la loi de la gravitation universelle ?",
        "choix": ["Albert Einstein", "Isaac Newton", "Galilee", "Archimede"],
        "bonne": 1,
        "explication": "Isaac Newton a formule la loi de la "
                        "gravitation universelle au 17e siecle."
    },
    {
        "matiere": "Physique",
        "question": "Comment appelle-t-on un matériau qui laisse passer le courant électrique ?",
        "choix": ["Un isolant", "Un conducteur", "Un semi-conducteur", "Un aimant"],
        "bonne": 1,
        "explication": "Un conducteur laisse circuler le courant "
                        "electrique, contrairement a un isolant."
    },
    {
        "matiere": "Physique",
        "question": "Quelle est l'unité de mesure de la pression ?",
        "choix": ["Le pascal", "Le newton", "Le joule", "Le watt"],
        "bonne": 0,
        "explication": "La pression se mesure en pascals (Pa)."
    },
    {
        "matiere": "Physique",
        "question": "Comment appelle-t-on le phénomène de réflexion de la lumière sur un miroir ?",
        "choix": ["La refraction", "La reflexion", "La diffraction", "La dispersion"],
        "bonne": 1,
        "explication": "La reflexion est le renvoi de la lumiere "
                        "par une surface comme un miroir."
    },
    {
        "matiere": "Physique",
        "question": "Quelle grandeur physique se mesure en hertz ?",
        "choix": ["La frequence", "La vitesse", "La masse", "La force"],
        "bonne": 0,
        "explication": "Le hertz (Hz) est l'unite de mesure "
                        "de la frequence."
    },
    {
        "matiere": "Physique",
        "question": "Quel est le nom de la force qui attire les objets vers le centre de la Terre ?",
        "choix": ["La gravite", "Le magnetisme", "La friction", "La pression"],
        "bonne": 0,
        "explication": "La gravite (ou pesanteur) attire les "
                        "objets vers le centre de la Terre."
    },
    {
        "matiere": "Physique",
        "question": "Comment appelle-t-on un circuit électrique où le courant suit un seul chemin ?",
        "choix": ["Un circuit en serie", "Un circuit en parallele", "Un circuit ouvert", "Un circuit court"],
        "bonne": 0,
        "explication": "Dans un circuit en serie, le courant "
                        "suit un seul et unique chemin."
    },
    {
        "matiere": "Physique",
        "question": "Quelle énergie provient du mouvement d'un objet ?",
        "choix": ["L'energie potentielle", "L'energie cinetique", "L'energie thermique", "L'energie chimique"],
        "bonne": 1,
        "explication": "L'energie cinetique est l'energie liee "
                        "au mouvement d'un objet."
    },
    {
        "matiere": "Physique",
        "question": "Quel instrument sert à mesurer la température ?",
        "choix": ["Le barometre", "Le thermometre", "L'hygrometre", "Le manometre"],
        "bonne": 1,
        "explication": "Le thermometre est l'instrument utilise "
                        "pour mesurer la temperature."
    },
    {
        "matiere": "Physique",
        "question": "Comment appelle-t-on le son émis par un objet qui vibre trop vite pour l'oreille humaine ?",
        "choix": ["Un infrason", "Un ultrason", "Un echo", "Une resonance"],
        "bonne": 1,
        "explication": "Un ultrason est un son de frequence "
                        "trop elevee pour etre entendu par l'oreille "
                        "humaine."
    },
    {
        "matiere": "Physique",
        "question": "Quelle est l'unité de mesure de la résistance électrique ?",
        "choix": ["L'ohm", "Le volt", "L'ampere", "Le watt"],
        "bonne": 0,
        "explication": "La resistance electrique se mesure en "
                        "ohms (Ω)."
    },

    {
        "matiere": "Chimie",
        "question": "Quel est le symbole chimique du fer ?",
        "choix": ["Fe", "Fr", "Fi", "F"],
        "bonne": 0,
        "explication": "Le symbole chimique du fer est Fe, du latin "
                        "« ferrum »."
    },
    {
        "matiere": "Chimie",
        "question": "Combien de protons possède l'atome d'hydrogène ?",
        "choix": ["0", "1", "2", "3"],
        "bonne": 1,
        "explication": "L'atome d'hydrogene possede 1 seul proton."
    },
    {
        "matiere": "Chimie",
        "question": "Quel est le pH d'une solution neutre ?",
        "choix": ["0", "7", "14", "10"],
        "bonne": 1,
        "explication": "Une solution neutre (comme l'eau pure) a "
                        "un pH de 7."
    },
    {
        "matiere": "Chimie",
        "question": "Quel gaz est produit lors de la respiration ?",
        "choix": ["Oxygène", "Azote", "Dioxyde de carbone", "Hydrogène"],
        "bonne": 2,
        "explication": "La respiration rejette du dioxyde de "
                        "carbone (CO2)."
    },
    {
        "matiere": "Chimie",
        "question": "Comment appelle-t-on la réaction entre un acide et une base ?",
        "choix": ["Oxydation", "Neutralisation", "Combustion", "Fusion"],
        "bonne": 1,
        "explication": "La reaction acide-base est appelee une "
                        "neutralisation."
    },
    {
        "matiere": "Chimie",
        "question": "Quel est le symbole chimique de l'or ?",
        "choix": ["Or", "Au", "Ag", "O"],
        "bonne": 1,
        "explication": "Le symbole chimique de l'or est Au, "
                        "du latin « aurum »."
    },
    {
        "matiere": "Chimie",
        "question": "Quel est le symbole chimique de l'oxygène ?",
        "choix": ["O", "Ox", "Og", "Oy"],
        "bonne": 0,
        "explication": "Le symbole chimique de l'oxygene est "
                        "simplement O."
    },
    {
        "matiere": "Chimie",
        "question": "Comment appelle-t-on un mélange homogène d'un solide dissous dans un liquide ?",
        "choix": ["Une suspension", "Une solution", "Une emulsion", "Un colloide"],
        "bonne": 1,
        "explication": "Une solution est un melange homogene, "
                        "comme le sel dissous dans l'eau."
    },
    {
        "matiere": "Chimie",
        "question": "Quel est le nombre d'électrons d'un atome de carbone neutre ?",
        "choix": ["4", "6", "8", "12"],
        "bonne": 1,
        "explication": "L'atome de carbone possede 6 protons "
                        "et donc 6 electrons a l'etat neutre."
    },
    {
        "matiere": "Chimie",
        "question": "Quel gaz est le plus abondant dans l'atmosphère terrestre ?",
        "choix": ["L'oxygene", "L'azote", "Le dioxyde de carbone", "L'argon"],
        "bonne": 1,
        "explication": "L'azote represente environ 78% de "
                        "l'atmosphere terrestre."
    },
    {
        "matiere": "Chimie",
        "question": "Comment appelle-t-on la plus petite particule d'un élément chimique ?",
        "choix": ["La molecule", "L'atome", "L'ion", "Le noyau"],
        "bonne": 1,
        "explication": "L'atome est la plus petite unite d'un "
                        "element chimique."
    },
    {
        "matiere": "Chimie",
        "question": "Quel est le symbole chimique du sodium ?",
        "choix": ["So", "Sd", "Na", "Sn"],
        "bonne": 2,
        "explication": "Le symbole chimique du sodium est Na, "
                        "du latin « natrium »."
    },
    {
        "matiere": "Chimie",
        "question": "Comment appelle-t-on la transformation d'un solide directement en gaz ?",
        "choix": ["La fusion", "La sublimation", "La condensation", "L'evaporation"],
        "bonne": 1,
        "explication": "La sublimation est le passage direct "
                        "de l'etat solide a l'etat gazeux."
    },
    {
        "matiere": "Chimie",
        "question": "Quel type de liaison unit les atomes dans une molécule d'eau ?",
        "choix": ["Une liaison ionique", "Une liaison covalente", "Une liaison metallique", "Une liaison hydrogene"],
        "bonne": 1,
        "explication": "Les atomes d'hydrogene et d'oxygene sont "
                        "lies par des liaisons covalentes dans l'eau."
    },
    {
        "matiere": "Chimie",
        "question": "Quel est le nom donné à une substance qui accélère une réaction chimique sans être consommée ?",
        "choix": ["Un reactif", "Un catalyseur", "Un solvant", "Un produit"],
        "bonne": 1,
        "explication": "Un catalyseur accelere une reaction "
                        "chimique sans etre consomme lui-meme."
    },
    {
        "matiere": "Chimie",
        "question": "Quel est le symbole chimique du potassium ?",
        "choix": ["K", "P", "Po", "Pt"],
        "bonne": 0,
        "explication": "Le symbole chimique du potassium est K, "
                        "du latin « kalium »."
    },
    {
        "matiere": "Chimie",
        "question": "Comment appelle-t-on une réaction qui dégage de la chaleur ?",
        "choix": ["Une reaction endothermique", "Une reaction exothermique", "Une reaction reversible", "Une reaction lente"],
        "bonne": 1,
        "explication": "Une reaction exothermique libere de la "
                        "chaleur vers l'exterieur."
    },
    {
        "matiere": "Chimie",
        "question": "Quel métal est liquide à température ambiante ?",
        "choix": ["Le fer", "Le mercure", "L'aluminium", "Le zinc"],
        "bonne": 1,
        "explication": "Le mercure est le seul metal liquide "
                        "a temperature ambiante."
    },
    {
        "matiere": "Chimie",
        "question": "Comment appelle-t-on l'étude des réactions et transformations de la matière ?",
        "choix": ["La physique", "La chimie", "La biologie", "La geologie"],
        "bonne": 1,
        "explication": "La chimie est la science qui etudie "
                        "la composition et les transformations de "
                        "la matiere."
    },
    {
        "matiere": "Chimie",
        "question": "Quel est le symbole chimique de l'azote ?",
        "choix": ["Az", "N", "A", "At"],
        "bonne": 1,
        "explication": "Le symbole chimique de l'azote est N, "
                        "du latin « nitrogenium »."
    },

    {
        "matiere": "Anglais",
        "question": "Comment dit-on « bonjour » (le matin) en anglais ?",
        "choix": ["Good night", "Good morning", "Good evening", "Goodbye"],
        "bonne": 1,
        "explication": "« Good morning » signifie bonjour, utilise "
                        "le matin."
    },
    {
        "matiere": "Anglais",
        "question": "Quel est le pluriel de « child » en anglais ?",
        "choix": ["Childs", "Children", "Childes", "Childrens"],
        "bonne": 1,
        "explication": "« Child » a un pluriel irregulier : "
                        "« children »."
    },
    {
        "matiere": "Anglais",
        "question": "Comment traduit-on « livre » en anglais ?",
        "choix": ["Book", "Table", "Pen", "Chair"],
        "bonne": 0,
        "explication": "« Book » signifie livre en anglais."
    },
    {
        "matiere": "Anglais",
        "question": "Quel est le passé du verbe « go » ?",
        "choix": ["Goed", "Gone", "Went", "Going"],
        "bonne": 2,
        "explication": "Le preterit du verbe irregulier « go » est "
                        "« went »."
    },
    {
        "matiere": "Anglais",
        "question": "Comment dit-on « merci » en anglais ?",
        "choix": ["Please", "Sorry", "Thank you", "Welcome"],
        "bonne": 2,
        "explication": "« Thank you » signifie merci en anglais."
    },
    {
        "matiere": "Anglais",
        "question": "Comment dit-on « au revoir » en anglais ?",
        "choix": ["Hello", "Goodbye", "Please", "Sorry"],
        "bonne": 1,
        "explication": "« Goodbye » signifie au revoir en anglais."
    },
    {
        "matiere": "Anglais",
        "question": "Quel est le pluriel de « mouse » (souris) ?",
        "choix": ["Mouses", "Mice", "Mices", "Mousies"],
        "bonne": 1,
        "explication": "« Mouse » a un pluriel irregulier : « mice »."
    },
    {
        "matiere": "Anglais",
        "question": "Comment traduit-on « maison » en anglais ?",
        "choix": ["House", "Car", "Tree", "Road"],
        "bonne": 0,
        "explication": "« House » signifie maison en anglais."
    },
    {
        "matiere": "Anglais",
        "question": "Quel est le passé du verbe « eat » ?",
        "choix": ["Eated", "Ate", "Eaten", "Eating"],
        "bonne": 1,
        "explication": "Le preterit du verbe irregulier « eat » "
                        "est « ate »."
    },
    {
        "matiere": "Anglais",
        "question": "Comment dit-on « s'il vous plaît » en anglais ?",
        "choix": ["Sorry", "Please", "Thanks", "Welcome"],
        "bonne": 1,
        "explication": "« Please » signifie s'il vous plait "
                        "en anglais."
    },
    {
        "matiere": "Anglais",
        "question": "Quel mot signifie « école » en anglais ?",
        "choix": ["School", "Book", "Teacher", "Class"],
        "bonne": 0,
        "explication": "« School » signifie ecole en anglais."
    },
    {
        "matiere": "Anglais",
        "question": "Comment dit-on « je m'appelle » en anglais ?",
        "choix": ["I am", "My name is", "I have", "I like"],
        "bonne": 1,
        "explication": "« My name is » signifie je m'appelle."
    },
    {
        "matiere": "Anglais",
        "question": "Quel est le comparatif de supériorité de « good » ?",
        "choix": ["Gooder", "Better", "Best", "More good"],
        "bonne": 1,
        "explication": "« Good » a un comparatif irregulier : "
                        "« better »."
    },
    {
        "matiere": "Anglais",
        "question": "Comment traduit-on « chien » en anglais ?",
        "choix": ["Cat", "Dog", "Bird", "Fish"],
        "bonne": 1,
        "explication": "« Dog » signifie chien en anglais."
    },
    {
        "matiere": "Anglais",
        "question": "Quel est le présent continu du verbe « to run » à la 3e personne du singulier ?",
        "choix": ["He run", "He is running", "He runs", "He running"],
        "bonne": 1,
        "explication": "Le present continu se forme avec « be "
                        "+ verbe-ing » : « he is running »."
    },
    {
        "matiere": "Anglais",
        "question": "Comment dit-on « combien » en anglais ?",
        "choix": ["How many", "How much", "How long", "How far"],
        "bonne": 1,
        "explication": "« How much » s'utilise pour demander une "
                        "quantite non comptable ou un prix."
    },
    {
        "matiere": "Anglais",
        "question": "Quel est l'opposé de « hot » en anglais ?",
        "choix": ["Warm", "Cold", "Cool", "Fresh"],
        "bonne": 1,
        "explication": "« Cold » (froid) est le contraire de "
                        "« hot » (chaud)."
    },
    {
        "matiere": "Anglais",
        "question": "Comment traduit-on « professeur » en anglais ?",
        "choix": ["Student", "Teacher", "Doctor", "Farmer"],
        "bonne": 1,
        "explication": "« Teacher » signifie professeur en anglais."
    },
    {
        "matiere": "Anglais",
        "question": "Quel pronom personnel remplace « the students » (les étudiants) ?",
        "choix": ["He", "She", "They", "It"],
        "bonne": 2,
        "explication": "« They » remplace un groupe de personnes "
                        "ou de choses au pluriel."
    },
    {
        "matiere": "Anglais",
        "question": "Comment dit-on « aujourd'hui » en anglais ?",
        "choix": ["Yesterday", "Tomorrow", "Today", "Now"],
        "bonne": 2,
        "explication": "« Today » signifie aujourd'hui en anglais."
    },

    {
        "matiere": "Philosophie",
        "question": "Qui est l'auteur du « Discours de la méthode » ?",
        "choix": ["Platon", "Descartes", "Kant", "Socrate"],
        "bonne": 1,
        "explication": "Rene Descartes est l'auteur du « Discours "
                        "de la methode » (1637)."
    },
    {
        "matiere": "Philosophie",
        "question": "Que signifie le mot « philosophie » en grec ?",
        "choix": ["Amour de la sagesse", "Science de la nature", "Etude du passe", "Art de convaincre"],
        "bonne": 0,
        "explication": "« Philosophie » vient du grec « philo » "
                        "(amour) et « sophia » (sagesse)."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe est connu pour « Je pense donc je suis » ?",
        "choix": ["Aristote", "Descartes", "Nietzsche", "Rousseau"],
        "bonne": 1,
        "explication": "Cette formule celebre vient de Descartes."
    },
    {
        "matiere": "Philosophie",
        "question": "Qui a écrit « La République » ?",
        "choix": ["Platon", "Aristote", "Socrate", "Epicure"],
        "bonne": 0,
        "explication": "« La Republique » est une oeuvre majeure "
                        "de Platon."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel courant défend que le bonheur est le bien suprême ?",
        "choix": ["Stoïcisme", "Eudémonisme", "Scepticisme", "Nihilisme"],
        "bonne": 1,
        "explication": "L'eudemonisme place le bonheur (eudaimonia) "
                        "au sommet des biens."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe grec fut le maître d'Alexandre le Grand ?",
        "choix": ["Platon", "Aristote", "Socrate", "Epicure"],
        "bonne": 1,
        "explication": "Aristote fut le precepteur d'Alexandre "
                        "le Grand."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe a été condamné à boire la cigüe à Athènes ?",
        "choix": ["Platon", "Aristote", "Socrate", "Diogène"],
        "bonne": 2,
        "explication": "Socrate fut condamne a mort et but la "
                        "cigue en 399 av. J.-C."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel courant philosophique prêche la maîtrise de soi face aux émotions ?",
        "choix": ["Le stoicisme", "L'hedonisme", "Le scepticisme", "L'existentialisme"],
        "bonne": 0,
        "explication": "Le stoicisme enseigne la maitrise des "
                        "passions et l'acceptation du destin."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe allemand est l'auteur de « Ainsi parlait Zarathoustra » ?",
        "choix": ["Kant", "Hegel", "Nietzsche", "Marx"],
        "bonne": 2,
        "explication": "« Ainsi parlait Zarathoustra » est une "
                        "oeuvre majeure de Friedrich Nietzsche."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe est associé au concept du « contrat social » ?",
        "choix": ["Voltaire", "Rousseau", "Montesquieu", "Diderot"],
        "bonne": 1,
        "explication": "Jean-Jacques Rousseau a developpe la "
                        "theorie du contrat social."
    },
    {
        "matiere": "Philosophie",
        "question": "Quelle branche de la philosophie étudie la connaissance et sa validité ?",
        "choix": ["L'ethique", "L'epistemologie", "L'esthetique", "La metaphysique"],
        "bonne": 1,
        "explication": "L'epistemologie est l'etude de la "
                        "connaissance et de sa validite."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe a écrit « Critique de la raison pure » ?",
        "choix": ["Emmanuel Kant", "Hegel", "Spinoza", "Leibniz"],
        "bonne": 0,
        "explication": "« Critique de la raison pure » est une "
                        "oeuvre majeure d'Emmanuel Kant."
    },
    {
        "matiere": "Philosophie",
        "question": "Comment appelle-t-on le doute systématique utilisé par Descartes ?",
        "choix": ["Le doute methodique", "Le scepticisme absolu", "Le nihilisme", "L'agnosticisme"],
        "bonne": 0,
        "explication": "Descartes utilise un doute methodique "
                        "pour parvenir a des certitudes."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe est considéré comme le fondateur du marxisme ?",
        "choix": ["Karl Marx", "Friedrich Engels", "Hegel", "Proudhon"],
        "bonne": 0,
        "explication": "Karl Marx est le principal fondateur "
                        "de la pensee marxiste."
    },
    {
        "matiere": "Philosophie",
        "question": "Que signifie « ex nihilo » en philosophie ?",
        "choix": ["A partir de rien", "Vers l'infini", "Selon la nature", "Par necessite"],
        "bonne": 0,
        "explication": "« Ex nihilo » signifie « a partir de "
                        "rien », souvent employe pour la creation."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe grec enseignait en marchant, d'où le nom d'école « péripatéticienne » ?",
        "choix": ["Platon", "Aristote", "Socrate", "Zenon"],
        "bonne": 1,
        "explication": "Aristote enseignait en marchant, donnant "
                        "naissance a l'ecole peripateticienne."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel courant remet en question la possibilité d'atteindre une vérité certaine ?",
        "choix": ["Le scepticisme", "Le dogmatisme", "Le rationalisme", "L'empirisme"],
        "bonne": 0,
        "explication": "Le scepticisme doute de la possibilite "
                        "d'atteindre une connaissance certaine."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe français est associé à l'existentialisme et à l'oeuvre « L'Être et le Néant » ?",
        "choix": ["Albert Camus", "Jean-Paul Sartre", "Michel Foucault", "Simone de Beauvoir"],
        "bonne": 1,
        "explication": "« L'Etre et le Neant » est une oeuvre "
                        "majeure de Jean-Paul Sartre."
    },
    {
        "matiere": "Philosophie",
        "question": "Que signifie « logos » en grec ancien ?",
        "choix": ["La raison", "La force", "Le temps", "Le hasard"],
        "bonne": 0,
        "explication": "« Logos » signifie la raison, la parole "
                        "ou le discours en grec ancien."
    },
    {
        "matiere": "Philosophie",
        "question": "Quel philosophe est célèbre pour l'allégorie de la caverne ?",
        "choix": ["Platon", "Aristote", "Epicure", "Zenon"],
        "bonne": 0,
        "explication": "L'allegorie de la caverne est un texte "
                        "celebre de Platon, tire de « La Republique »."
    },

    {
        "matiere": "Biologie",
        "question": "Quelle est l'unité de base du vivant ?",
        "choix": ["L'organe", "La cellule", "Le tissu", "L'atome"],
        "bonne": 1,
        "explication": "La cellule est l'unite structurale et "
                        "fonctionnelle de base du vivant."
    },
    {
        "matiere": "Biologie",
        "question": "Quel organite produit l'énergie dans la cellule ?",
        "choix": ["Noyau", "Ribosome", "Mitochondrie", "Appareil de Golgi"],
        "bonne": 2,
        "explication": "La mitochondrie produit l'energie (ATP) "
                        "de la cellule."
    },
    {
        "matiere": "Biologie",
        "question": "Quel est le rôle de l'ADN ?",
        "choix": ["Produire de l'energie", "Transporter l'oxygene", "Porter l'information genetique", "Digerer les aliments"],
        "bonne": 2,
        "explication": "L'ADN porte l'information genetique "
                        "necessaire au fonctionnement des cellules."
    },
    {
        "matiere": "Biologie",
        "question": "Comment appelle-t-on la division cellulaire qui produit des cellules identiques ?",
        "choix": ["Meiose", "Mitose", "Fecondation", "Mutation"],
        "bonne": 1,
        "explication": "La mitose produit deux cellules filles "
                        "identiques a la cellule mere."
    },
    {
        "matiere": "Biologie",
        "question": "Quel système transporte le sang dans le corps ?",
        "choix": ["Systeme nerveux", "Systeme digestif", "Systeme circulatoire", "Systeme respiratoire"],
        "bonne": 2,
        "explication": "Le systeme circulatoire transporte le sang "
                        "grace au coeur et aux vaisseaux."
    },
    {
        "matiere": "Biologie",
        "question": "Quel organe assure la respiration chez l'homme ?",
        "choix": ["Le coeur", "Les poumons", "Le foie", "Les reins"],
        "bonne": 1,
        "explication": "Les poumons permettent les echanges "
                        "gazeux necessaires a la respiration."
    },
    {
        "matiere": "Biologie",
        "question": "Comment appelle-t-on la reproduction sans fécondation ?",
        "choix": ["La reproduction sexuee", "La reproduction asexuee", "La meiose", "La fecondation"],
        "bonne": 1,
        "explication": "La reproduction asexuee ne necessite pas "
                        "la fusion de deux cellules sexuelles."
    },
    {
        "matiere": "Biologie",
        "question": "Quel est le rôle des globules rouges ?",
        "choix": ["Combattre les infections", "Transporter l'oxygene", "Coaguler le sang", "Digerer les aliments"],
        "bonne": 1,
        "explication": "Les globules rouges transportent l'oxygene "
                        "dans tout le corps grace a l'hemoglobine."
    },
    {
        "matiere": "Biologie",
        "question": "Quel processus permet aux plantes de fabriquer leur propre nourriture ?",
        "choix": ["La respiration", "La photosynthese", "La transpiration", "La digestion"],
        "bonne": 1,
        "explication": "La photosynthese permet aux plantes de "
                        "produire de la matiere organique grace "
                        "a la lumiere."
    },
    {
        "matiere": "Biologie",
        "question": "Comment appelle-t-on l'ensemble des espèces vivant dans un même milieu ?",
        "choix": ["Une population", "Un ecosysteme", "Une biosphere", "Un habitat"],
        "bonne": 1,
        "explication": "Un ecosysteme regroupe les etres vivants "
                        "et leur environnement dans un meme milieu."
    },
    {
        "matiere": "Biologie",
        "question": "Quel organe produit l'insuline dans le corps humain ?",
        "choix": ["Le foie", "Le pancreas", "La rate", "La vesicule biliaire"],
        "bonne": 1,
        "explication": "Le pancreas produit l'insuline, qui "
                        "regule le taux de sucre dans le sang."
    },
    {
        "matiere": "Biologie",
        "question": "Comment appelle-t-on la division cellulaire qui produit les cellules reproductrices ?",
        "choix": ["La mitose", "La meiose", "La fecondation", "La mutation"],
        "bonne": 1,
        "explication": "La meiose est la division cellulaire "
                        "qui produit les gametes (cellules "
                        "reproductrices)."
    },
    {
        "matiere": "Biologie",
        "question": "Quel est le rôle des globules blancs ?",
        "choix": ["Transporter l'oxygene", "Defendre l'organisme", "Coaguler le sang", "Produire de l'energie"],
        "bonne": 1,
        "explication": "Les globules blancs protegent l'organisme "
                        "contre les infections."
    },
    {
        "matiere": "Biologie",
        "question": "Quel groupe d'animaux comprend les êtres à sang chaud qui allaitent leurs petits ?",
        "choix": ["Les reptiles", "Les mammiferes", "Les amphibiens", "Les oiseaux"],
        "bonne": 1,
        "explication": "Les mammiferes sont des animaux a sang "
                        "chaud qui allaitent leurs petits."
    },
    {
        "matiere": "Biologie",
        "question": "Comment appelle-t-on une modification permanente de l'ADN ?",
        "choix": ["Une meiose", "Une mutation", "Une mitose", "Une fecondation"],
        "bonne": 1,
        "explication": "Une mutation est un changement permanent "
                        "dans la sequence de l'ADN."
    },
    {
        "matiere": "Biologie",
        "question": "Quel organe du corps humain est responsable de la digestion des graisses grâce à la bile ?",
        "choix": ["Le foie", "Le pancreas", "L'estomac", "L'intestin grele"],
        "bonne": 0,
        "explication": "Le foie produit la bile qui aide a "
                        "digerer les graisses."
    },
    {
        "matiere": "Biologie",
        "question": "Comment appelle-t-on les organismes capables de produire leur propre matière organique ?",
        "choix": ["Des heterotrophes", "Des autotrophes", "Des decomposeurs", "Des parasites"],
        "bonne": 1,
        "explication": "Les autotrophes, comme les plantes, "
                        "produisent leur propre matiere organique."
    },
    {
        "matiere": "Biologie",
        "question": "Quel est le rôle principal du système nerveux ?",
        "choix": ["Transporter le sang", "Transmettre les informations", "Digerer les aliments", "Produire des hormones"],
        "bonne": 1,
        "explication": "Le systeme nerveux transmet les "
                        "informations entre le cerveau et le "
                        "reste du corps."
    },
    {
        "matiere": "Biologie",
        "question": "Comment appelle-t-on l'étude des relations entre les êtres vivants et leur milieu ?",
        "choix": ["La genetique", "L'ecologie", "La physiologie", "L'anatomie"],
        "bonne": 1,
        "explication": "L'ecologie etudie les relations entre "
                        "les etres vivants et leur environnement."
    },
    {
        "matiere": "Biologie",
        "question": "Quel est le rôle des enzymes dans l'organisme ?",
        "choix": ["Accelerer les reactions chimiques", "Transporter l'oxygene", "Produire des anticorps", "Stocker l'energie"],
        "bonne": 0,
        "explication": "Les enzymes accelerent les reactions "
                        "chimiques necessaires au fonctionnement "
                        "de l'organisme."
    },

    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on les couches successives de roches ?",
        "choix": ["Strates", "Failles", "Plaques", "Cratons"],
        "bonne": 0,
        "explication": "Les strates sont les couches de roches "
                        "empilees au fil du temps."
    },
    {
        "matiere": "Géologie",
        "question": "Quel phénomène est dû au mouvement des plaques tectoniques ?",
        "choix": ["Maree", "Seisme", "Eclipse", "Ouragan"],
        "bonne": 1,
        "explication": "Les seismes sont souvent dus aux mouvements "
                        "des plaques tectoniques."
    },
    {
        "matiere": "Géologie",
        "question": "Quelle roche se forme par refroidissement du magma ?",
        "choix": ["Sedimentaire", "Metamorphique", "Magmatique", "Calcaire"],
        "bonne": 2,
        "explication": "Une roche magmatique se forme par "
                        "refroidissement du magma."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on l'étude de l'âge des roches ?",
        "choix": ["Geochronologie", "Meteorologie", "Astrologie", "Climatologie"],
        "bonne": 0,
        "explication": "La geochronologie etudie l'age des roches "
                        "et des formations geologiques."
    },
    {
        "matiere": "Géologie",
        "question": "Quel est le nom de la couche externe de la Terre ?",
        "choix": ["Noyau", "Manteau", "Croute", "Atmosphere"],
        "bonne": 2,
        "explication": "La croute terrestre est la couche externe "
                        "et rigide de la Terre."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on le point de départ d'un séisme en profondeur ?",
        "choix": ["L'epicentre", "Le foyer", "La faille", "La croute"],
        "bonne": 1,
        "explication": "Le foyer (ou hypocentre) est le point "
                        "en profondeur ou nait le seisme."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on le point à la surface juste au-dessus du foyer d'un séisme ?",
        "choix": ["L'epicentre", "Le foyer", "La faille", "Le magma"],
        "bonne": 0,
        "explication": "L'epicentre est le point de la surface "
                        "terrestre situe a la verticale du foyer."
    },
    {
        "matiere": "Géologie",
        "question": "Quelle roche se forme par accumulation et compression de sédiments ?",
        "choix": ["Une roche magmatique", "Une roche sedimentaire", "Une roche metamorphique", "Une roche volcanique"],
        "bonne": 1,
        "explication": "Les roches sedimentaires se forment par "
                        "accumulation de sediments compresses."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on la matière en fusion à l'intérieur de la Terre ?",
        "choix": ["La lave", "Le magma", "Le basalte", "Le granite"],
        "bonne": 1,
        "explication": "Le magma est la roche en fusion presente "
                        "sous la surface terrestre."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on le magma une fois qu'il atteint la surface lors d'une éruption ?",
        "choix": ["Le magma", "La lave", "Le basalte", "Le cratere"],
        "bonne": 1,
        "explication": "La lave est le nom donne au magma "
                        "lorsqu'il sort a la surface."
    },
    {
        "matiere": "Géologie",
        "question": "Quelle est la couche la plus interne de la Terre ?",
        "choix": ["La croute", "Le manteau", "Le noyau", "L'asthenosphere"],
        "bonne": 2,
        "explication": "Le noyau est la couche la plus profonde "
                        "et la plus chaude de la Terre."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on une fracture de l'écorce terrestre le long de laquelle des blocs se déplacent ?",
        "choix": ["Une strate", "Une faille", "Une plaque", "Un cratere"],
        "bonne": 1,
        "explication": "Une faille est une cassure de la croute "
                        "terrestre le long de laquelle des roches "
                        "se deplacent."
    },
    {
        "matiere": "Géologie",
        "question": "Quel type de roche se forme sous l'effet de la chaleur et de la pression sans fusion complète ?",
        "choix": ["Une roche sedimentaire", "Une roche magmatique", "Une roche metamorphique", "Une roche volcanique"],
        "bonne": 2,
        "explication": "Les roches metamorphiques se transforment "
                        "sous l'effet de la chaleur et de la "
                        "pression."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on l'instrument qui mesure l'intensité des séismes ?",
        "choix": ["Le barometre", "Le sismographe", "Le thermometre", "L'hygrometre"],
        "bonne": 1,
        "explication": "Le sismographe enregistre les vibrations "
                        "du sol lors d'un seisme."
    },
    {
        "matiere": "Géologie",
        "question": "Quel phénomène géologique forme les chaînes de montagnes par collision de plaques ?",
        "choix": ["L'erosion", "L'orogenese", "La sedimentation", "La subduction"],
        "bonne": 1,
        "explication": "L'orogenese est le processus de formation "
                        "des montagnes, souvent par collision de "
                        "plaques."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on l'usure progressive des roches par le vent, l'eau ou la glace ?",
        "choix": ["L'erosion", "La sedimentation", "La fusion", "La subduction"],
        "bonne": 0,
        "explication": "L'erosion use progressivement les roches "
                        "sous l'effet des agents naturels."
    },
    {
        "matiere": "Géologie",
        "question": "Quel type de volcan a une forme conique très pentue due à des éruptions explosives ?",
        "choix": ["Un volcan bouclier", "Un stratovolcan", "Un maar", "Un dyke"],
        "bonne": 1,
        "explication": "Un stratovolcan a une forme conique "
                        "formee par des couches successives de "
                        "lave et de cendres."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on le phénomène où une plaque tectonique s'enfonce sous une autre ?",
        "choix": ["La collision", "La subduction", "La divergence", "L'accretion"],
        "bonne": 1,
        "explication": "La subduction se produit lorsqu'une "
                        "plaque oceanique s'enfonce sous une autre "
                        "plaque."
    },
    {
        "matiere": "Géologie",
        "question": "Quelle échelle mesure la magnitude d'un séisme ?",
        "choix": ["L'echelle de Richter", "L'echelle de Beaufort", "L'echelle de Mercalli", "L'echelle Celsius"],
        "bonne": 0,
        "explication": "L'echelle de Richter mesure la magnitude, "
                        "c'est-a-dire l'energie liberee par un "
                        "seisme."
    },
    {
        "matiere": "Géologie",
        "question": "Comment appelle-t-on l'étude scientifique des volcans ?",
        "choix": ["La sismologie", "La volcanologie", "La mineralogie", "La petrologie"],
        "bonne": 1,
        "explication": "La volcanologie est la science qui "
                        "etudie les volcans et leur activite."
    },
]


# =========================================================
# GROUPES DE CLASSES ET MATIERES PAR SERIE
# =========================================================

DEFAULT_MATIERES = ["Sciences", "Histoire", "Français", "Géographie"]

MATIERES_PAR_SERIE = {
    "SM": ["Maths", "Physique", "Chimie", "Français"],
    "SS": ["Français", "Géographie", "Histoire", "Philosophie", "Anglais"],
    "SE": ["Biologie", "Géologie", "Maths", "Physique", "Chimie"],
}

CLASSES_PRIMAIRE = [
    "1ere A", "2eme A", "3eme A", "4eme A", "5eme A", "6eme A"
]

CLASSES_COLLEGE = [
    "7eme A", "8eme A", "9eme A", "10eme A"
]

CLASSES_LYCEE = ["11eme", "12eme", "Terminale"]


def matieres_pour_classe(app):
    """Renvoie la liste des matieres disponibles selon la serie
    choisie (au lycee) ou la liste par defaut (primaire/college)."""
    if app.serie in MATIERES_PAR_SERIE:
        return MATIERES_PAR_SERIE[app.serie]
    return DEFAULT_MATIERES


# =========================================================
# COEFFICIENTS DES MATIERES (POUR L'EXAMEN)
# =========================================================
# Primaire : toutes les matieres sont coefficient 1.
# College  : Français = coefficient 2, les autres = 1.
# Lycee    : coefficients propres a chaque serie.

COEFFICIENTS_LYCEE = {
    "SM": {"Maths": 4, "Physique": 3, "Chimie": 3, "Français": 2},
    "SS": {"Français": 4, "Philosophie": 3, "Anglais": 3,
           "Histoire": 2, "Géographie": 2},
    "SE": {"Biologie": 4, "Géologie": 3, "Physique": 3,
           "Maths": 2, "Chimie": 2},
}

COEFFICIENTS_COLLEGE = {"Français": 2}


def coefficients_pour_classe(app):
    """Renvoie le dictionnaire {matiere: coefficient} qui s'applique
    a la classe/serie actuelle. Toute matiere absente du dictionnaire
    vaut coefficient 1 par defaut (utiliser .get(matiere, 1))."""
    if app.serie in COEFFICIENTS_LYCEE:
        return COEFFICIENTS_LYCEE[app.serie]
    if app.classe in CLASSES_COLLEGE:
        return COEFFICIENTS_COLLEGE
    return {}


# =========================================================
# BANQUE DE QUESTIONS DE L'EXAMEN
# Niveau intermediaire, distincte de la banque du quiz.
# Meme structure que QUESTIONS : matiere, question, choix,
# bonne, explication.
# =========================================================

EXAMEN_QUESTIONS = [
    # ---------------- SCIENCES ----------------
    {"matiere": "Sciences",
     "question": "Comment appelle-t-on le processus par lequel les plantes perdent de l'eau sous forme de vapeur par leurs feuilles ?",
     "choix": ["La transpiration", "La photosynthèse", "La respiration", "La condensation"],
     "bonne": 0,
     "explication": "La transpiration vegetale permet a la plante d'evacuer l'exces d'eau par de petits pores des feuilles."},
    {"matiere": "Sciences",
     "question": "Comment appelle-t-on la couche de gaz qui protège la Terre des rayons ultraviolets ?",
     "choix": ["La couche d'ozone", "La troposphère", "L'ionosphère", "La stratosphère basse"],
     "bonne": 0,
     "explication": "La couche d'ozone, situee dans la stratosphere, filtre une grande partie des UV nocifs du Soleil."},
    {"matiere": "Sciences",
     "question": "Quel type de vaisseau sanguin transporte le sang du coeur vers les organes ?",
     "choix": ["Les veines", "Les artères", "Les capillaires", "Les valves"],
     "bonne": 1,
     "explication": "Les arteres transportent le sang riche en oxygene du coeur vers les organes."},
    {"matiere": "Sciences",
     "question": "Comment appelle-t-on le phénomène par lequel un animal change totalement de forme au cours de sa vie (ex : chenille puis papillon) ?",
     "choix": ["La mue", "La métamorphose", "La croissance", "La régénération"],
     "bonne": 1,
     "explication": "La metamorphose est une transformation profonde de la forme d'un animal durant son developpement."},
    {"matiere": "Sciences",
     "question": "Quelle glande, située dans le cou, régule le métabolisme du corps ?",
     "choix": ["L'hypophyse", "La thyroïde", "Le pancréas", "Les surrénales"],
     "bonne": 1,
     "explication": "La thyroide produit des hormones qui regulent le metabolisme et la croissance."},
    {"matiere": "Sciences",
     "question": "Comment appelle-t-on la maladie causée par un manque ou une mauvaise utilisation de l'insuline ?",
     "choix": ["L'anémie", "Le diabète", "L'hypertension", "L'asthme"],
     "bonne": 1,
     "explication": "Le diabete est lie a un probleme de production ou d'utilisation de l'insuline, hormone qui regule le sucre sanguin."},
    {"matiere": "Sciences",
     "question": "Quel groupe sanguin est considéré comme donneur universel ?",
     "choix": ["AB positif", "A négatif", "O négatif", "B positif"],
     "bonne": 2,
     "explication": "Le groupe O negatif peut etre transfuse a la plupart des patients, quel que soit leur groupe sanguin."},
    {"matiere": "Sciences",
     "question": "Comment appelle-t-on le tissu qui relie les muscles aux os ?",
     "choix": ["Le ligament", "Le cartilage", "Le tendon", "Le nerf"],
     "bonne": 2,
     "explication": "Le tendon est une bande de tissu resistant qui attache le muscle a l'os pour permettre le mouvement."},
    {"matiere": "Sciences",
     "question": "Quel organe stocke la bile produite par le foie ?",
     "choix": ["Le pancréas", "La vésicule biliaire", "La rate", "L'intestin grêle"],
     "bonne": 1,
     "explication": "La vesicule biliaire stocke et concentre la bile avant de la liberer dans l'intestin."},
    {"matiere": "Sciences",
     "question": "Comment appelle-t-on la cellule reproductrice mâle chez l'être humain ?",
     "choix": ["L'ovule", "Le spermatozoïde", "Le zygote", "L'embryon"],
     "bonne": 1,
     "explication": "Le spermatozoide est la cellule reproductrice masculine, produite par les testicules."},

    # ---------------- HISTOIRE ----------------
    {"matiere": "Histoire",
     "question": "Quelles expéditions militaires du Moyen Âge visaient à reprendre Jérusalem aux musulmans ?",
     "choix": ["Les croisades", "La Reconquista", "La conquête normande", "Les invasions barbares"],
     "bonne": 0,
     "explication": "Les croisades etaient des expeditions religieuses et militaires organisees par les Etats chretiens d'Europe."},
    {"matiere": "Histoire",
     "question": "Quelle conférence de 1885 a organisé le partage colonial de l'Afrique entre puissances européennes ?",
     "choix": ["La Conférence de Berlin", "Le Congrès de Vienne", "La Conférence de Yalta", "Le Traité de Versailles"],
     "bonne": 0,
     "explication": "La Conference de Berlin de 1885 a fixe les regles du partage colonial du continent africain."},
    {"matiere": "Histoire",
     "question": "Quel pays fut le premier d'Afrique subsaharienne à obtenir son indépendance, en 1957 ?",
     "choix": ["Le Nigeria", "Le Ghana", "Le Sénégal", "Le Kenya"],
     "bonne": 1,
     "explication": "Le Ghana, dirige par Kwame Nkrumah, obtient son independance en 1957, le premier d'Afrique noire."},
    {"matiere": "Histoire",
     "question": "En quelle année la Côte d'Ivoire a-t-elle obtenu son indépendance ?",
     "choix": ["1958", "1960", "1962", "1965"],
     "bonne": 1,
     "explication": "La Côte d'Ivoire a proclame son independance le 7 aout 1960."},
    {"matiere": "Histoire",
     "question": "Qui fut le premier président de la Côte d'Ivoire indépendante ?",
     "choix": ["Laurent Gbagbo", "Félix Houphouët-Boigny", "Henri Konan Bédié", "Alassane Ouattara"],
     "bonne": 1,
     "explication": "Felix Houphouet-Boigny a dirige la Côte d'Ivoire de 1960 a sa mort en 1993."},
    {"matiere": "Histoire",
     "question": "Quel empire ouest-africain a succédé à l'Empire du Mali aux XVe-XVIe siècles ?",
     "choix": ["L'Empire Songhaï", "L'Empire Ashanti", "L'Empire du Ghana", "L'Empire Zoulou"],
     "bonne": 0,
     "explication": "L'Empire Songhai a domine l'Afrique de l'Ouest apres le declin de l'Empire du Mali."},
    {"matiere": "Histoire",
     "question": "Dans quel pays a débuté la première révolution industrielle au XVIIIe siècle ?",
     "choix": ["La France", "L'Allemagne", "L'Angleterre", "Les Etats-Unis"],
     "bonne": 2,
     "explication": "L'Angleterre est le berceau de la revolution industrielle grace notamment a la machine a vapeur."},
    {"matiere": "Histoire",
     "question": "En quelle année la France abolit-elle définitivement l'esclavage ?",
     "choix": ["1794", "1815", "1848", "1900"],
     "bonne": 2,
     "explication": "L'esclavage est aboli definitivement en France et ses colonies en 1848, sous l'impulsion de Victor Schoelcher."},
    {"matiere": "Histoire",
     "question": "Quelle organisation régionale africaine fut créée en 1963 pour favoriser l'unité du continent ?",
     "choix": ["L'Union Africaine", "L'Organisation de l'Unité Africaine (OUA)", "La CEDEAO", "L'ONU"],
     "bonne": 1,
     "explication": "L'OUA a ete fondee en 1963 a Addis-Abeba, avant de devenir l'Union Africaine en 2002."},
    {"matiere": "Histoire",
     "question": "Quelle guerre a opposé les Etats-Unis et l'URSS sans affrontement armé direct après 1945 ?",
     "choix": ["La guerre froide", "La guerre de Corée", "La guerre du Vietnam", "La guerre du Golfe"],
     "bonne": 0,
     "explication": "La guerre froide designe la rivalite politique et ideologique entre les Etats-Unis et l'URSS de 1947 a 1991."},

    # ---------------- FRANÇAIS ----------------
    {"matiere": "Français",
     "question": "Comment appelle-t-on une figure de style qui consiste à exagérer pour produire un effet ?",
     "choix": ["La métaphore", "L'hyperbole", "L'euphémisme", "La litote"],
     "bonne": 1,
     "explication": "L'hyperbole est une exageration destinee a frapper l'esprit du lecteur ou de l'auditeur."},
    {"matiere": "Français",
     "question": "Quel est le mode du verbe dans « Que vous réussissiez ! » ?",
     "choix": ["L'indicatif", "Le conditionnel", "Le subjonctif", "L'impératif"],
     "bonne": 2,
     "explication": "Le subjonctif exprime ici un souhait, ce qui est l'un de ses emplois les plus frequents."},
    {"matiere": "Français",
     "question": "Comment appelle-t-on un texte dans lequel une personne raconte elle-même sa propre vie ?",
     "choix": ["La biographie", "L'autobiographie", "Le roman", "L'essai"],
     "bonne": 1,
     "explication": "Dans l'autobiographie, l'auteur raconte sa propre existence, contrairement a la biographie ecrite par un tiers."},
    {"matiere": "Français",
     "question": "Comment appelle-t-on un groupe de vers formant une unité dans un poème ?",
     "choix": ["Un hémistiche", "Une strophe", "Une rime", "Une syllabe"],
     "bonne": 1,
     "explication": "Une strophe regroupe plusieurs vers separes des autres par un blanc typographique."},
    {"matiere": "Français",
     "question": "Quelle est la nature grammaticale du mot « rapidement » dans une phrase ?",
     "choix": ["Un adjectif", "Un nom", "Un adverbe", "Un pronom"],
     "bonne": 2,
     "explication": "« Rapidement » est un adverbe de maniere, il modifie generalement un verbe."},
    {"matiere": "Français",
     "question": "Comment appelle-t-on une phrase qui ne contient pas de verbe conjugué ?",
     "choix": ["Une phrase simple", "Une phrase nominale", "Une phrase complexe", "Une phrase interrogative"],
     "bonne": 1,
     "explication": "Une phrase nominale est construite autour d'un nom, sans verbe conjugue (ex : « Quelle belle journee ! »)."},
    {"matiere": "Français",
     "question": "Quel est le complément circonstanciel de lieu dans « Il travaille à Abidjan » ?",
     "choix": ["Il", "Travaille", "À Abidjan", "Aucun"],
     "bonne": 2,
     "explication": "« À Abidjan » precise le lieu ou se deroule l'action, c'est un complement circonstanciel de lieu."},
    {"matiere": "Français",
     "question": "Comment appelle-t-on un récit imaginaire mettant en scène des animaux et se terminant par une morale ?",
     "choix": ["Un conte", "Une fable", "Une légende", "Une nouvelle"],
     "bonne": 1,
     "explication": "La fable, comme celles de Jean de La Fontaine, met en scene des animaux pour illustrer une morale."},
    {"matiere": "Français",
     "question": "Qui est l'auteur du roman « Le Petit Prince » ?",
     "choix": ["Victor Hugo", "Antoine de Saint-Exupéry", "Albert Camus", "Jean-Paul Sartre"],
     "bonne": 1,
     "explication": "« Le Petit Prince » a ete ecrit par Antoine de Saint-Exupery, publie en 1943."},
    {"matiere": "Français",
     "question": "Quel est l'homophone de « ver » qui désigne une couleur ?",
     "choix": ["Vert", "Verre", "Vers", "Vair"],
     "bonne": 0,
     "explication": "« Vert » est l'homophone de « ver » qui designe une couleur, celle du feuillage par exemple."},

    # ---------------- GEOGRAPHIE ----------------
    {"matiere": "Géographie",
     "question": "Quel est le plus grand pays d'Afrique par sa superficie ?",
     "choix": ["Le Nigeria", "L'Algérie", "La RD Congo", "L'Egypte"],
     "bonne": 1,
     "explication": "L'Algerie est le plus vaste pays d'Afrique par sa superficie, en grande partie occupee par le Sahara."},
    {"matiere": "Géographie",
     "question": "Quel est le fleuve le plus long du monde ?",
     "choix": ["L'Amazone", "Le Nil", "Le Mississippi", "Le Congo"],
     "bonne": 1,
     "explication": "Le Nil, avec environ 6 650 km, est generalement considere comme le plus long fleuve du monde."},
    {"matiere": "Géographie",
     "question": "Quelle capitale, traversée par le fleuve Niger, se trouve au Mali ?",
     "choix": ["Bamako", "Niamey", "Ouagadougou", "Conakry"],
     "bonne": 0,
     "explication": "Bamako, capitale du Mali, est situee sur les rives du fleuve Niger."},
    {"matiere": "Géographie",
     "question": "Comment appelle-t-on la ligne imaginaire qui divise la Terre en hémisphère nord et hémisphère sud ?",
     "choix": ["Le méridien de Greenwich", "L'équateur", "Le tropique du Cancer", "Le cercle polaire"],
     "bonne": 1,
     "explication": "L'equateur est le cercle imaginaire situe a egale distance des deux poles."},
    {"matiere": "Géographie",
     "question": "Quelle mer est bordée par l'Egypte, l'Arabie Saoudite et Djibouti ?",
     "choix": ["La mer Noire", "La mer Rouge", "La mer Méditerranée", "La mer Caspienne"],
     "bonne": 1,
     "explication": "La mer Rouge separe l'Afrique de la peninsule Arabique."},
    {"matiere": "Géographie",
     "question": "Quel est le plus grand lac d'Afrique ?",
     "choix": ["Le lac Victoria", "Le lac Tchad", "Le lac Malawi", "Le lac Tanganyika"],
     "bonne": 0,
     "explication": "Le lac Victoria, partage entre le Kenya, l'Ouganda et la Tanzanie, est le plus grand lac d'Afrique."},
    {"matiere": "Géographie",
     "question": "Quelle chaîne de montagnes traverse l'Amérique du Sud du nord au sud ?",
     "choix": ["Les Rocheuses", "La cordillère des Andes", "L'Himalaya", "Les Alpes"],
     "bonne": 1,
     "explication": "La cordillere des Andes est la plus longue chaine de montagnes du monde, le long de l'Amerique du Sud."},
    {"matiere": "Géographie",
     "question": "Quel pays est surnommé le « pays des mille collines » ?",
     "choix": ["Le Burundi", "Le Rwanda", "L'Ouganda", "Le Malawi"],
     "bonne": 1,
     "explication": "Le Rwanda est surnomme ainsi en raison de son relief tres vallonne."},
    {"matiere": "Géographie",
     "question": "Quel océan borde la côte est des Etats-Unis ?",
     "choix": ["L'océan Pacifique", "L'océan Atlantique", "L'océan Indien", "L'océan Arctique"],
     "bonne": 1,
     "explication": "La côte est des Etats-Unis, comme New York, est bordee par l'ocean Atlantique."},
    {"matiere": "Géographie",
     "question": "Quel pays est actuellement le plus peuplé du monde ?",
     "choix": ["La Chine", "L'Inde", "Les Etats-Unis", "L'Indonésie"],
     "bonne": 1,
     "explication": "L'Inde a depasse la Chine et est devenue le pays le plus peuple du monde."},

    # ---------------- MATHS ----------------
    {"matiere": "Maths",
     "question": "Quelle est la valeur de (2/3) + (1/6), sous forme de fraction simplifiée ?",
     "choix": ["1/2", "5/6", "3/9", "7/6"],
     "bonne": 1,
     "explication": "En mettant au meme denominateur (6), on obtient 4/6 + 1/6 = 5/6."},
    {"matiere": "Maths",
     "question": "Comment appelle-t-on un nombre qui ne peut pas s'écrire sous forme de fraction, comme π ?",
     "choix": ["Un nombre entier", "Un nombre rationnel", "Un nombre irrationnel", "Un nombre décimal"],
     "bonne": 2,
     "explication": "Un nombre irrationnel ne peut pas s'exprimer comme le quotient de deux entiers."},
    {"matiere": "Maths",
     "question": "Quelle est la formule de l'aire d'un triangle de base b et de hauteur h ?",
     "choix": ["b × h", "(b × h) / 2", "2 × (b + h)", "b² + h²"],
     "bonne": 1,
     "explication": "L'aire d'un triangle se calcule en multipliant la base par la hauteur puis en divisant par 2."},
    {"matiere": "Maths",
     "question": "Quel est le résultat de 3² + 4² ?",
     "choix": ["7", "12", "25", "49"],
     "bonne": 2,
     "explication": "3² = 9 et 4² = 16, donc 9 + 16 = 25."},
    {"matiere": "Maths",
     "question": "Comment appelle-t-on deux droites qui ne se croisent jamais, quelle que soit leur longueur ?",
     "choix": ["Des droites sécantes", "Des droites perpendiculaires", "Des droites parallèles", "Des droites confondues"],
     "bonne": 2,
     "explication": "Deux droites paralleles gardent toujours le meme ecart et ne se rencontrent jamais."},
    {"matiere": "Maths",
     "question": "Quelle est la somme des angles intérieurs d'un quadrilatère ?",
     "choix": ["180°", "270°", "360°", "400°"],
     "bonne": 2,
     "explication": "Un quadrilatere peut se decomposer en deux triangles de 180° chacun, soit 360° au total."},
    {"matiere": "Maths",
     "question": "Quel est le plus grand commun diviseur (PGCD) de 12 et 18 ?",
     "choix": ["3", "6", "9", "12"],
     "bonne": 1,
     "explication": "6 est le plus grand nombre qui divise a la fois 12 et 18."},
    {"matiere": "Maths",
     "question": "Comment appelle-t-on une suite où chaque terme s'obtient en ajoutant toujours le même nombre au terme précédent ?",
     "choix": ["Une suite géométrique", "Une suite arithmétique", "Une suite constante", "Une suite alternée"],
     "bonne": 1,
     "explication": "Dans une suite arithmetique, on passe d'un terme au suivant en ajoutant une raison constante."},
    {"matiere": "Maths",
     "question": "Quelle est la valeur de log(100) en base 10 ?",
     "choix": ["1", "2", "10", "100"],
     "bonne": 1,
     "explication": "Comme 10² = 100, le logarithme decimal de 100 vaut 2."},
    {"matiere": "Maths",
     "question": "Quel est le résultat de 5! (factorielle de 5) ?",
     "choix": ["25", "60", "120", "720"],
     "bonne": 2,
     "explication": "5! = 5 × 4 × 3 × 2 × 1 = 120."},

    # ---------------- PHYSIQUE ----------------
    {"matiere": "Physique",
     "question": "Quel principe énonce que tout corps plongé dans un fluide reçoit une poussée verticale vers le haut ?",
     "choix": ["Le principe d'Archimède", "La loi de Newton", "La loi d'Ohm", "Le principe de Pascal"],
     "bonne": 0,
     "explication": "Le principe d'Archimede explique pourquoi certains objets flottent grace a la poussee du fluide."},
    {"matiere": "Physique",
     "question": "Quelle est l'unité de mesure de la fréquence ?",
     "choix": ["Le watt", "Le hertz", "Le joule", "Le newton"],
     "bonne": 1,
     "explication": "Le hertz (Hz) mesure le nombre d'oscillations ou de cycles par seconde."},
    {"matiere": "Physique",
     "question": "Comment appelle-t-on l'énergie stockée par un objet en raison de sa position (par exemple en hauteur) ?",
     "choix": ["L'énergie cinétique", "L'énergie potentielle", "L'énergie thermique", "L'énergie chimique"],
     "bonne": 1,
     "explication": "L'energie potentielle depend de la position de l'objet, par exemple sa hauteur par rapport au sol."},
    {"matiere": "Physique",
     "question": "Quel scientifique a énoncé les trois lois fondamentales du mouvement en mécanique classique ?",
     "choix": ["Albert Einstein", "Isaac Newton", "Galilée", "Nikola Tesla"],
     "bonne": 1,
     "explication": "Isaac Newton a formule les trois lois du mouvement dans ses Principia Mathematica."},
    {"matiere": "Physique",
     "question": "Quelle est l'unité de mesure de la charge électrique ?",
     "choix": ["Le volt", "L'ampère", "Le coulomb", "L'ohm"],
     "bonne": 2,
     "explication": "Le coulomb (C) est l'unite de mesure de la charge electrique dans le systeme international."},
    {"matiere": "Physique",
     "question": "Comment appelle-t-on le phénomène de déviation de la lumière en passant d'un milieu à un autre ?",
     "choix": ["La réflexion", "La diffraction", "La réfraction", "La dispersion"],
     "bonne": 2,
     "explication": "La refraction est le changement de direction de la lumiere lorsqu'elle change de milieu."},
    {"matiere": "Physique",
     "question": "Quelle grandeur physique traduit la quantité de matière contenue dans un volume donné ?",
     "choix": ["La densité", "La masse volumique", "Le poids", "La pression"],
     "bonne": 1,
     "explication": "La masse volumique est le rapport entre la masse d'un corps et son volume."},
    {"matiere": "Physique",
     "question": "Quel appareil sert à mesurer l'intensité d'un courant électrique ?",
     "choix": ["Le voltmètre", "L'ampèremètre", "L'ohmmètre", "Le wattmètre"],
     "bonne": 1,
     "explication": "L'amperemetre se branche en serie dans un circuit pour mesurer l'intensite du courant."},
    {"matiere": "Physique",
     "question": "Comment appelle-t-on l'ensemble des ondes électromagnétiques visibles par l'oeil humain ?",
     "choix": ["Les rayons X", "La lumière visible", "Les infrarouges", "Les ondes radio"],
     "bonne": 1,
     "explication": "La lumiere visible est la partie du spectre electromagnetique que l'oeil humain peut percevoir."},
    {"matiere": "Physique",
     "question": "Quelle formule relie la puissance électrique (P), la tension (U) et l'intensité (I) ?",
     "choix": ["P = U + I", "P = U × I", "P = U / I", "P = U − I"],
     "bonne": 1,
     "explication": "La puissance electrique se calcule en multipliant la tension par l'intensite du courant."},

    # ---------------- CHIMIE ----------------
    {"matiere": "Chimie",
     "question": "Comment appelle-t-on une substance qui ne peut pas être décomposée en substances plus simples par des moyens chimiques ?",
     "choix": ["Un mélange", "Un élément chimique", "Un composé", "Une solution"],
     "bonne": 1,
     "explication": "Un element chimique est une substance pure formee d'un seul type d'atome."},
    {"matiere": "Chimie",
     "question": "Quel est, environ, le nombre d'Avogadro utilisé en chimie ?",
     "choix": ["3,14", "6,022 × 10²³", "9,8", "1,6 × 10⁻¹⁹"],
     "bonne": 1,
     "explication": "Le nombre d'Avogadro indique le nombre d'entites (atomes, molecules) presentes dans une mole de matiere."},
    {"matiere": "Chimie",
     "question": "Comment appelle-t-on le passage direct de l'état gazeux à l'état solide ?",
     "choix": ["La sublimation", "La condensation", "La solidification", "La fusion"],
     "bonne": 1,
     "explication": "La condensation (ou condensation solide) est le passage direct de l'etat gazeux a l'etat solide."},
    {"matiere": "Chimie",
     "question": "Quel est le symbole chimique du calcium ?",
     "choix": ["Ca", "C", "Cl", "K"],
     "bonne": 0,
     "explication": "Le symbole chimique du calcium est Ca."},
    {"matiere": "Chimie",
     "question": "Comment appelle-t-on une solution dont le pH est supérieur à 7 ?",
     "choix": ["Une solution acide", "Une solution neutre", "Une solution basique", "Une solution saturée"],
     "bonne": 2,
     "explication": "Une solution est dite basique (ou alcaline) lorsque son pH est superieur a 7."},
    {"matiere": "Chimie",
     "question": "Quel gaz est libéré, avec l'eau, lors de la combustion complète d'un hydrocarbure ?",
     "choix": ["Le dioxygène", "Le dioxyde de carbone", "L'azote", "L'hydrogène"],
     "bonne": 1,
     "explication": "La combustion complete d'un hydrocarbure produit du dioxyde de carbone (CO2) et de l'eau."},
    {"matiere": "Chimie",
     "question": "Quelle unité mesure la quantité de matière en chimie ?",
     "choix": ["Le gramme", "Le litre", "La mole", "Le kelvin"],
     "bonne": 2,
     "explication": "La mole est l'unite de mesure de la quantite de matiere dans le systeme international."},
    {"matiere": "Chimie",
     "question": "Quel est le nombre de nucléons (masse) d'un atome qui possède 6 protons et 6 neutrons ?",
     "choix": ["6", "12", "18", "24"],
     "bonne": 1,
     "explication": "Le nombre de masse est la somme des protons et des neutrons, soit 6 + 6 = 12."},
    {"matiere": "Chimie",
     "question": "Comment appelle-t-on deux atomes du même élément possédant un nombre de neutrons différent ?",
     "choix": ["Des isomères", "Des isotopes", "Des ions", "Des allotropes"],
     "bonne": 1,
     "explication": "Les isotopes d'un element ont le meme nombre de protons mais un nombre de neutrons different."},
    {"matiere": "Chimie",
     "question": "Quel type de réaction chimique correspond au schéma A + B → AB ?",
     "choix": ["Une réaction de décomposition", "Une réaction de synthèse", "Une réaction de substitution", "Une réaction acido-basique"],
     "bonne": 1,
     "explication": "Une reaction de synthese (ou combinaison) associe deux especes chimiques pour en former une nouvelle."},

    # ---------------- ANGLAIS ----------------
    {"matiere": "Anglais",
     "question": "Which tense is used in the sentence: \"I have finished my homework\" ?",
     "choix": ["Simple past", "Present perfect", "Past perfect", "Present continuous"],
     "bonne": 1,
     "explication": "« Have + participe passe » correspond au present perfect, utilise ici pour une action recente."},
    {"matiere": "Anglais",
     "question": "What is the comparative form of \"bad\" ?",
     "choix": ["Badder", "More bad", "Worse", "Baddest"],
     "bonne": 2,
     "explication": "« Bad » est un adjectif irregulier : son comparatif est « worse »."},
    {"matiere": "Anglais",
     "question": "Choose the correct question tag: \"She is coming, ___ ?\"",
     "choix": ["isn't she", "doesn't she", "is she", "does she"],
     "bonne": 0,
     "explication": "Avec « is », le question tag correspondant est « isn't she »."},
    {"matiere": "Anglais",
     "question": "What is the past participle of the verb \"write\" ?",
     "choix": ["Wrote", "Writed", "Written", "Writing"],
     "bonne": 2,
     "explication": "« Write » est un verbe irregulier : write - wrote - written."},
    {"matiere": "Anglais",
     "question": "Which word means the opposite of \"generous\" ?",
     "choix": ["Stingy", "Kind", "Happy", "Brave"],
     "bonne": 0,
     "explication": "« Stingy » signifie avare, c'est le contraire de « generous » (genereux)."},
    {"matiere": "Anglais",
     "question": "Complete the sentence: \"If it rains, I ___ stay home.\"",
     "choix": ["will", "would", "am", "was"],
     "bonne": 0,
     "explication": "Dans une phrase conditionnelle de type 1 (probable), on utilise « will » dans la proposition principale."},
    {"matiere": "Anglais",
     "question": "What is the plural form of \"foot\" ?",
     "choix": ["Foots", "Feets", "Feet", "Footes"],
     "bonne": 2,
     "explication": "« Foot » a un pluriel irregulier : « feet »."},
    {"matiere": "Anglais",
     "question": "Which preposition completes: \"She is afraid ___ spiders.\"",
     "choix": ["of", "for", "with", "at"],
     "bonne": 0,
     "explication": "On dit « to be afraid of something », d'ou « afraid of spiders »."},
    {"matiere": "Anglais",
     "question": "What is the English word for « bibliothèque » ?",
     "choix": ["Bookshop", "Library", "Book", "Office"],
     "bonne": 1,
     "explication": "« Library » signifie bibliotheque en anglais, a ne pas confondre avec « bookshop » (librairie)."},
    {"matiere": "Anglais",
     "question": "Choose the correct passive form of: \"They built the house.\"",
     "choix": ["The house built them", "The house was built", "The house is building", "The house builds"],
     "bonne": 1,
     "explication": "A la voix passive, on utilise « be + participe passe » : « The house was built »."},

    # ---------------- PHILOSOPHIE ----------------
    {"matiere": "Philosophie",
     "question": "Quel philosophe italien est l'auteur du « Prince », traité sur l'exercice du pouvoir politique ?",
     "choix": ["Machiavel", "Montesquieu", "Voltaire", "Hobbes"],
     "bonne": 0,
     "explication": "Nicolas Machiavel a ecrit « Le Prince » au XVIe siecle, ouvrage fondateur de la pensee politique moderne."},
    {"matiere": "Philosophie",
     "question": "Comment appelle-t-on la doctrine selon laquelle tout événement a une cause qui le détermine ?",
     "choix": ["Le déterminisme", "Le relativisme", "L'idéalisme", "Le nihilisme"],
     "bonne": 0,
     "explication": "Le determinisme affirme que chaque evenement est la consequence necessaire de causes anterieures."},
    {"matiere": "Philosophie",
     "question": "Quel philosophe grec est considéré comme le fondateur de la logique formelle ?",
     "choix": ["Socrate", "Platon", "Aristote", "Epicure"],
     "bonne": 2,
     "explication": "Aristote a systematise les regles du raisonnement logique dans ses traites d'Organon."},
    {"matiere": "Philosophie",
     "question": "Que désigne, en philosophie, le terme « éthique » ?",
     "choix": ["L'étude de la connaissance", "L'étude de la morale et des valeurs", "L'étude de l'être", "L'étude du langage"],
     "bonne": 1,
     "explication": "L'ethique est la branche de la philosophie qui etudie la morale, les valeurs et le bien agir."},
    {"matiere": "Philosophie",
     "question": "Quel philosophe est associé à l'utilitarisme et à la recherche du plus grand bonheur du plus grand nombre ?",
     "choix": ["Jeremy Bentham", "Emmanuel Kant", "Aristote", "Platon"],
     "bonne": 0,
     "explication": "Jeremy Bentham est le fondateur de l'utilitarisme, courant developpe ensuite par John Stuart Mill."},
    {"matiere": "Philosophie",
     "question": "Quel philosophe français est l'auteur de « Émile ou De l'éducation » ?",
     "choix": ["Voltaire", "Jean-Jacques Rousseau", "Diderot", "Montesquieu"],
     "bonne": 1,
     "explication": "Jean-Jacques Rousseau expose dans « Emile » sa conception de l'education naturelle de l'enfant."},
    {"matiere": "Philosophie",
     "question": "Comment appelle-t-on la branche de la philosophie qui étudie la beauté et l'art ?",
     "choix": ["La métaphysique", "L'esthétique", "L'épistémologie", "La logique"],
     "bonne": 1,
     "explication": "L'esthetique est la discipline philosophique consacree a l'etude du beau et de l'art."},
    {"matiere": "Philosophie",
     "question": "Quel courant philosophique affirme que la connaissance provient principalement de l'expérience sensible ?",
     "choix": ["Le rationalisme", "L'empirisme", "L'idéalisme", "Le dogmatisme"],
     "bonne": 1,
     "explication": "Pour l'empirisme, defendu notamment par Locke et Hume, toute connaissance vient de l'experience."},
    {"matiere": "Philosophie",
     "question": "Quel philosophe français, associé à l'existentialisme, a écrit que « l'enfer, c'est les autres » ?",
     "choix": ["Albert Camus", "Jean-Paul Sartre", "Michel Foucault", "Henri Bergson"],
     "bonne": 1,
     "explication": "Cette phrase celebre est tiree de la piece « Huis clos » de Jean-Paul Sartre."},
    {"matiere": "Philosophie",
     "question": "Comment appelle-t-on la branche de la philosophie qui étudie l'être en tant qu'être ?",
     "choix": ["L'ontologie", "La logique", "L'esthétique", "L'anthropologie"],
     "bonne": 0,
     "explication": "L'ontologie s'interesse a la nature de l'etre et de l'existence en general."},

    # ---------------- BIOLOGIE ----------------
    {"matiere": "Biologie",
     "question": "Comment appelle-t-on l'ensemble des caractères héréditaires portés par les gènes d'un individu ?",
     "choix": ["Le phénotype", "Le génotype", "Le caryotype", "L'allèle"],
     "bonne": 1,
     "explication": "Le genotype represente l'ensemble de l'information genetique portee par les genes d'un individu."},
    {"matiere": "Biologie",
     "question": "Quel est le rôle principal des stomates chez les plantes ?",
     "choix": ["Absorber l'eau du sol", "Permettre les échanges gazeux", "Produire les fleurs", "Stocker les réserves"],
     "bonne": 1,
     "explication": "Les stomates, situes sur les feuilles, permettent les echanges de gaz necessaires a la photosynthese et a la respiration."},
    {"matiere": "Biologie",
     "question": "Quel organe filtre l'air et permet l'échange de l'oxygène contre le dioxyde de carbone chez l'humain ?",
     "choix": ["Le coeur", "Les poumons", "Le foie", "La rate"],
     "bonne": 1,
     "explication": "Les poumons assurent les echanges gazeux entre l'air inspire et le sang."},
    {"matiere": "Biologie",
     "question": "Comment appelle-t-on la nutrition des champignons, qui absorbent la matière organique en décomposition ?",
     "choix": ["La nutrition autotrophe", "La nutrition saprophyte", "La photosynthèse", "La chimiosynthèse"],
     "bonne": 1,
     "explication": "Les champignons sont saprophytes : ils se nourrissent de matiere organique morte en decomposition."},
    {"matiere": "Biologie",
     "question": "Comment appelle-t-on la relation où deux espèces vivent ensemble et en tirent toutes deux un bénéfice ?",
     "choix": ["Le parasitisme", "Le mutualisme", "La compétition", "Le commensalisme"],
     "bonne": 1,
     "explication": "Le mutualisme (ou symbiose) est une association durable et benefique pour les deux especes."},
    {"matiere": "Biologie",
     "question": "Quel est le rôle principal des anticorps dans l'organisme ?",
     "choix": ["Transporter l'oxygène", "Défendre l'organisme contre les agents pathogènes", "Digérer les aliments", "Transmettre les gènes"],
     "bonne": 1,
     "explication": "Les anticorps sont des proteines produites par le systeme immunitaire pour neutraliser les agents pathogenes."},
    {"matiere": "Biologie",
     "question": "Comment appelle-t-on le processus de fabrication des protéines à partir de l'ARN messager ?",
     "choix": ["La transcription", "La traduction", "La réplication", "La mutation"],
     "bonne": 1,
     "explication": "La traduction est l'etape ou les ribosomes lisent l'ARN messager pour fabriquer une proteine."},
    {"matiere": "Biologie",
     "question": "Quel organite cellulaire contient le matériel génétique dans une cellule eucaryote ?",
     "choix": ["La mitochondrie", "Le noyau", "Le ribosome", "Le chloroplaste"],
     "bonne": 1,
     "explication": "Le noyau abrite l'ADN qui porte l'information genetique de la cellule eucaryote."},
    {"matiere": "Biologie",
     "question": "Comment appelle-t-on la théorie selon laquelle les espèces évoluent au fil du temps par sélection naturelle ?",
     "choix": ["La théorie de l'évolution", "La théorie cellulaire", "La théorie germinale", "La théorie de l'hérédité"],
     "bonne": 0,
     "explication": "La theorie de l'evolution, developpee par Charles Darwin, explique la diversite des especes par la selection naturelle."},
    {"matiere": "Biologie",
     "question": "Quel groupe d'animaux respire principalement par des branchies ?",
     "choix": ["Les mammifères", "Les oiseaux", "Les poissons", "Les reptiles"],
     "bonne": 2,
     "explication": "Les poissons respirent grace a leurs branchies, qui extraient l'oxygene dissous dans l'eau."},

    # ---------------- GEOLOGIE ----------------
    {"matiere": "Géologie",
     "question": "Comment appelle-t-on le supercontinent qui regroupait toutes les terres émergées il y a environ 300 millions d'années ?",
     "choix": ["La Laurasia", "La Pangée", "Le Gondwana", "L'Eurasie"],
     "bonne": 1,
     "explication": "La Pangee etait l'unique supercontinent avant que la derive des plaques ne le fragmente."},
    {"matiere": "Géologie",
     "question": "Comment appelle-t-on une roche formée à partir de cendres volcaniques compactées ?",
     "choix": ["Le tuf volcanique", "Le granite", "Le marbre", "Le calcaire"],
     "bonne": 0,
     "explication": "Le tuf volcanique se forme par compaction et cimentation de cendres et debris projetes par un volcan."},
    {"matiere": "Géologie",
     "question": "Quel est le minéral naturel le plus dur connu, utilisé notamment pour rayer le verre ?",
     "choix": ["Le quartz", "Le diamant", "Le mica", "Le calcaire"],
     "bonne": 1,
     "explication": "Le diamant occupe le degre 10, le maximum, sur l'echelle de durete de Mohs."},
    {"matiere": "Géologie",
     "question": "Comment appelle-t-on la science qui étudie la composition, la structure et la formation des minéraux ?",
     "choix": ["La sismologie", "La minéralogie", "La volcanologie", "La géomorphologie"],
     "bonne": 1,
     "explication": "La mineralogie est la branche de la geologie consacree a l'etude des mineraux."},
    {"matiere": "Géologie",
     "question": "Quel type de volcan a une forme large et aplatie due à une lave très fluide (comme à Hawaï) ?",
     "choix": ["Le stratovolcan", "Le volcan bouclier", "Le maar", "Le volcan gris"],
     "bonne": 1,
     "explication": "Le volcan bouclier resulte d'ecoulements de lave fluide qui s'etalent sur de grandes distances."},
    {"matiere": "Géologie",
     "question": "Comment appelle-t-on un fossile qui permet de dater précisément une couche géologique ?",
     "choix": ["Un fossile guide", "Un fossile vivant", "Un moulage", "Un géode"],
     "bonne": 0,
     "explication": "Un fossile guide (ou stratigraphique) a existe peu de temps mais etait tres repandu, ce qui permet de dater les couches."},
    {"matiere": "Géologie",
     "question": "Quelle échelle classe la dureté des minéraux de 1 à 10 ?",
     "choix": ["L'échelle de Richter", "L'échelle de Mohs", "L'échelle de Beaufort", "L'échelle de Kelvin"],
     "bonne": 1,
     "explication": "L'echelle de Mohs mesure la resistance des mineraux a la rayure, de 1 (talc) a 10 (diamant)."},
    {"matiere": "Géologie",
     "question": "Comment appelle-t-on le mouvement lent des continents à la surface du globe au cours des temps géologiques ?",
     "choix": ["La subduction", "La dérive des continents", "L'érosion", "La sédimentation"],
     "bonne": 1,
     "explication": "La derive des continents decrit le deplacement progressif des masses continentales sur des millions d'annees."},
    {"matiere": "Géologie",
     "question": "Comment appelle-t-on un affaissement brutal du sol formant une dépression, parfois un lac ?",
     "choix": ["Une doline", "Un geyser", "Un glacier", "Un delta"],
     "bonne": 0,
     "explication": "Une doline est une depression du sol due a l'effondrement d'une cavite souterraine, souvent dans les roches calcaires."},
    {"matiere": "Géologie",
     "question": "Quelle énergie fossile se forme à partir de la décomposition d'organismes marins sur des millions d'années ?",
     "choix": ["Le charbon", "Le pétrole", "Le gaz naturel", "L'uranium"],
     "bonne": 1,
     "explication": "Le petrole se forme par la transformation de matiere organique marine accumulee et enfouie sur de tres longues periodes."},
]


# =========================================================
# BANQUE COMBINEE (QUIZ + EXAMEN) ET ROTATION DES QUESTIONS
# =========================================================
# Pour eviter qu'un eleve retrouve exactement les memes questions
# d'une partie a l'autre (quiz ou examen), les banques QUESTIONS et
# EXAMEN_QUESTIONS sont fusionnees par matiere. On y puise en
# excluant en priorite les questions deja vues recemment, jusqu'a
# epuisement du reservoir, avant de recommencer un nouveau cycle.

BANQUE_PAR_MATIERE = {}
for _q in QUESTIONS + EXAMEN_QUESTIONS:
    BANQUE_PAR_MATIERE.setdefault(_q["matiere"], []).append(_q)


def selectionner_questions(matiere, nb, deja_vues, rng=None):
    """Choisit `nb` questions pour une matiere, en evitant en
    priorite celles deja presentes dans `deja_vues` (un set
    d'identifiants). Met a jour `deja_vues` avec les questions
    choisies. Si le reservoir de questions inedites ne suffit pas,
    complete avec des questions deja vues puis relance un nouveau
    cycle, pour qu'un eleve ne retombe pas systematiquement sur les
    memes questions d'une partie a l'autre."""
    if rng is None:
        rng = random.Random()

    banque = BANQUE_PAR_MATIERE.get(matiere, [])
    if not banque:
        return []

    non_vues = [q for q in banque if id(q) not in deja_vues]
    rng.shuffle(non_vues)

    selection = non_vues[:nb]

    if len(selection) < nb:
        deja_vues.clear()
        ids_selection = {id(q) for q in selection}
        complement = [q for q in banque if id(q) not in ids_selection]
        rng.shuffle(complement)
        selection.extend(complement[: nb - len(selection)])

    for q in selection:
        deja_vues.add(id(q))

    # Si toutes les questions de la matiere viennent d'etre vues,
    # on relance directement un nouveau cycle pour la prochaine fois.
    if len(deja_vues) >= len(banque):
        deja_vues.clear()

    rng.shuffle(selection)
    return selection


# =========================================================
# CANDIDATS IA POUR L'EXAMEN (CLASSEMENT)
# =========================================================

PRENOMS_IA = [
    "Fatou", "Aminata", "Mariam", "Awa", "Adjoua", "Aya", "Akissi", "Affoué",
    "Ama", "Nina", "Grace", "Sarah", "Chantal", "Christelle", "Rokia",
    "Kadiatou", "Mamadou", "Ibrahim", "Souleymane", "Abou", "David", "Daniel",
    "Emmanuel", "Franck", "Serge", "Yao", "Koffi", "Konan", "Kouadio", "Jean",
    "Paul", "Moussa", "Issa", "Bakary", "Salif", "Aicha", "Kadidia",
    "Nafissatou", "Hawa", "Djeneba",
]

NOMS_FAMILLE_IA = [
    "Kouassi", "Kouadio", "Konan", "N'Guessan", "Yao", "Koffi", "Traoré",
    "Coulibaly", "Ouattara", "Bamba", "Fofana", "Koné", "Diallo", "Bakayoko",
    "Touré", "Camara", "Cissé", "Kouamé", "Diabaté", "Sanogo", "Kamara",
    "Sylla", "Doumbia", "Keita", "Sangaré", "Yeo", "Angoua", "Assamoi",
    "Aka", "Amani",
]


def _generer_nom_ia(rng, deja_utilises):
    """Genere un nom d'IA unique parmi ceux deja attribues."""
    for _ in range(60):
        nom = rng.choice(PRENOMS_IA) + " " + rng.choice(NOMS_FAMILLE_IA)
        if nom not in deja_utilises:
            deja_utilises.add(nom)
            return nom
    suffixe = 1
    while True:
        nom = (rng.choice(PRENOMS_IA) + " " + rng.choice(NOMS_FAMILLE_IA)
               + " " + str(suffixe))
        if nom not in deja_utilises:
            deja_utilises.add(nom)
            return nom
        suffixe += 1


def generer_candidats_ia(n=NB_CANDIDATS_IA):
    """Genere une liste de n candidats IA (nom + moyenne/20) pour le
    classement de l'examen. Le premier de la liste (une fois triee)
    varie a chaque examen, entre 17.00 et 18.50 de moyenne. Certains
    candidats IA echouent, comme un vrai groupe d'eleves."""
    rng = random.Random()
    deja_utilises = set()

    moyennes = []
    for _ in range(n):
        brute = rng.gauss(11.5, 3.4)
        moyennes.append(max(1.0, min(20.0, brute)))

    moyennes.sort(reverse=True)

    premier = round(rng.uniform(17.0, 18.5), 2)
    moyennes[0] = premier
    if len(moyennes) > 1:
        moyennes[1] = round(premier - rng.uniform(0.2, 1.0), 2)
    if len(moyennes) > 2:
        moyennes[2] = round(premier - rng.uniform(1.0, 2.2), 2)

    plafond_reste = moyennes[2] if len(moyennes) > 2 else premier
    for i in range(3, len(moyennes)):
        if moyennes[i] >= plafond_reste:
            moyennes[i] = round(plafond_reste - rng.uniform(0.1, 4.0), 2)
        moyennes[i] = max(1.0, round(moyennes[i], 2))

    rng.shuffle(moyennes)

    candidats = []
    for moyenne in moyennes:
        nom = _generer_nom_ia(rng, deja_utilises)
        candidats.append({
            "nom": nom,
            "moyenne": round(moyenne, 2),
            "admis": moyenne >= MOYENNE_ADMISSION,
            "est_utilisateur": False,
        })

    return candidats


def construire_classement_niveau(moyenne_utilisateur, admis_utilisateur, n):
    """Construit un classement complet (candidats IA + utilisateur)
    pour une echelle donnee (ecole, regional ou national) et renvoie
    un dictionnaire pret a etre stocke dans la session d'examen."""
    candidats_ia = generer_candidats_ia(n)
    classement = list(candidats_ia)
    classement.append({
        "nom": "TOI",
        "moyenne": moyenne_utilisateur,
        "admis": admis_utilisateur,
        "est_utilisateur": True,
    })
    classement.sort(key=lambda c: c["moyenne"], reverse=True)

    rang = 1
    for i, c in enumerate(classement, start=1):
        if c.get("est_utilisateur"):
            rang = i
            break

    nb_admis = sum(1 for c in classement if c["admis"])

    return {
        "classement": classement,
        "rang": rang,
        "total_participants": len(classement),
        "nb_admis": nb_admis,
    }


# =========================================================
# BADGES
# =========================================================
# Chaque badge : identifiant, nom, description et condition
# (fonction qui recoit l'objet app et renvoie True/False)

BADGES = [
    {
        "id": "premier_quiz",
        "nom": "Premier pas",
        "description": "Termine ton premier quiz.",
        "condition": lambda app: app.quiz_joues >= 1
    },
    {
        "id": "cinq_quiz",
        "nom": "Habitue",
        "description": "Termine 5 quiz.",
        "condition": lambda app: app.quiz_joues >= 5
    },
    {
        "id": "dix_quiz",
        "nom": "Assidu",
        "description": "Termine 10 quiz.",
        "condition": lambda app: app.quiz_joues >= 10
    },
    {
        "id": "bon_score",
        "nom": "Bon eleve",
        "description": "Obtiens 75% ou plus a un quiz.",
        "condition": lambda app: app.meilleur_pourcentage >= 75
    },
    {
        "id": "score_parfait",
        "nom": "Sans faute",
        "description": "Obtiens 100% (sans faute) a un quiz.",
        "condition": lambda app: app.meilleur_pourcentage == 100
    },
    {
        "id": "expert_sciences",
        "nom": "Expert Sciences",
        "description": "15 bonnes reponses en Sciences (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Sciences", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_histoire",
        "nom": "Expert Histoire",
        "description": "15 bonnes reponses en Histoire (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Histoire", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_francais",
        "nom": "Expert Français",
        "description": "15 bonnes reponses en Français (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Français", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_geographie",
        "nom": "Expert Géographie",
        "description": "15 bonnes reponses en Geographie (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Géographie", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_maths",
        "nom": "Expert Maths",
        "description": "15 bonnes reponses en Maths (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Maths", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_physique",
        "nom": "Expert Physique",
        "description": "15 bonnes reponses en Physique (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Physique", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_chimie",
        "nom": "Expert Chimie",
        "description": "15 bonnes reponses en Chimie (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Chimie", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_anglais",
        "nom": "Expert Anglais",
        "description": "15 bonnes reponses en Anglais (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Anglais", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_philosophie",
        "nom": "Expert Philosophie",
        "description": "15 bonnes reponses en Philosophie (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Philosophie", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_biologie",
        "nom": "Expert Biologie",
        "description": "15 bonnes reponses en Biologie (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Biologie", {}).get("bonnes", 0) >= 15
    },
    {
        "id": "expert_geologie",
        "nom": "Expert Géologie",
        "description": "15 bonnes reponses en Geologie (cumule).",
        "condition": lambda app: app.stats_matieres.get(
            "Géologie", {}).get("bonnes", 0) >= 15
    },
]


# =========================================================
# ACCUEIL
# =========================================================

class Accueil(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        principal.add_widget(
            Label(
                text="KOLIE QUIZ",
                font_size=dp(34),
                bold=True,
                color=BLUE,
                size_hint_y=None,
                height=dp(70)
            )
        )

        compte = getattr(app, "compte", None)
        if compte and compte.get("prenom"):
            sous_texte = "Bienvenue, " + compte.get("prenom", "") + " !"
        else:
            sous_texte = "Apprends, entraine-toi et teste tes connaissances."

        principal.add_widget(
            Label(
                text=sous_texte,
                font_size=dp(18),
                color=DARK,
                halign="center"
            )
        )

        principal.add_widget(
            bouton(
                "COMMENCER LE QUIZ",
                lambda x: self.choisir_mode("quiz")
            )
        )

        principal.add_widget(
            bouton(
                "EXAMEN",
                lambda x: self.choisir_mode("examen")
            )
        )

        principal.add_widget(
            bouton(
                "MES RESULTATS",
                lambda x: self.manager.__setattr__("current", "resultats")
            )
        )

        principal.add_widget(
            bouton(
                "MON EXAMEN",
                lambda x: self.manager.__setattr__("current", "examen_resultat"),
                couleur=ORANGE
            )
        )

        principal.add_widget(
            bouton(
                "MON PROFIL",
                lambda x: self.manager.__setattr__("current", "profil")
            )
        )

        principal.add_widget(
            bouton(
                "PARAMETRES",
                lambda x: self.manager.__setattr__("current", "parametres"),
                couleur=GREY
            )
        )

        principal.add_widget(
            bouton(
                "AIDE / INFORMATIONS",
                lambda x: self.manager.__setattr__("current", "aide"),
                couleur=GREY
            )
        )

        principal.add_widget(
            Label(
                text="Primaire, College, Lycee (SM, SS, SE)",
                font_size=dp(13),
                color=GREY,
                size_hint_y=None,
                height=dp(40)
            )
        )

        self.add_widget(principal)

    def choisir_mode(self, mode):
        """Prepare la navigation : 'quiz' passe par le choix de la
        matiere, 'examen' va directement a l'examen complet de la
        classe une fois le niveau choisi."""
        app = App.get_running_app()
        app.mode_navigation = mode
        self.manager.current = "classes"


# =========================================================
# CLASSES
# =========================================================

class Classes(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(14)
        )

        principal.add_widget(titre("[b]CHOISIS TON NIVEAU[/b]", 27))

        principal.add_widget(
            bouton(
                "PRIMAIRE",
                lambda x: self.manager.__setattr__("current", "primaire"),
                hauteur=60
            )
        )

        principal.add_widget(
            bouton(
                "COLLEGE",
                lambda x: self.manager.__setattr__("current", "college"),
                hauteur=60
            )
        )

        principal.add_widget(
            bouton(
                "LYCEE",
                lambda x: self.manager.__setattr__("current", "lycee"),
                hauteur=60
            )
        )

        principal.add_widget(
            bouton(
                "RETOUR",
                lambda x: self.manager.__setattr__("current", "accueil"),
                couleur=GREY
            )
        )

        self.add_widget(principal)


# =========================================================
# PRIMAIRE
# =========================================================

class Primaire(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10)
        )

        principal.add_widget(titre("[b]PRIMAIRE[/b]\nChoisis ta classe", 24))

        grille = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None
        )
        grille.bind(minimum_height=grille.setter("height"))

        for classe in CLASSES_PRIMAIRE:
            b = bouton(classe)
            b.bind(
                on_release=lambda btn, c=classe: self.choisir(c)
            )
            grille.add_widget(b)

        principal.add_widget(grille)

        principal.add_widget(
            bouton(
                "RETOUR",
                lambda x: self.manager.__setattr__("current", "classes"),
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def choisir(self, classe):
        app = App.get_running_app()
        app.classe = classe
        app.serie = ""
        if app.mode_navigation == "examen":
            self.manager.current = "examen"
        else:
            self.manager.current = "matieres"


# =========================================================
# COLLEGE
# =========================================================

class College(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10)
        )

        principal.add_widget(titre("[b]COLLEGE[/b]\nChoisis ta classe", 24))

        grille = GridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None
        )
        grille.bind(minimum_height=grille.setter("height"))

        for classe in CLASSES_COLLEGE:
            b = bouton(classe)
            b.bind(
                on_release=lambda btn, c=classe: self.choisir(c)
            )
            grille.add_widget(b)

        principal.add_widget(grille)

        principal.add_widget(
            bouton(
                "RETOUR",
                lambda x: self.manager.__setattr__("current", "classes"),
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def choisir(self, classe):
        app = App.get_running_app()
        app.classe = classe
        app.serie = ""
        if app.mode_navigation == "examen":
            self.manager.current = "examen"
        else:
            self.manager.current = "matieres"


# =========================================================
# LYCEE (choix de la serie : SM, SS, SE)
# =========================================================

class Lycee(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(14)
        )

        principal.add_widget(titre("[b]LYCEE[/b]\nChoisis ta serie", 24))

        principal.add_widget(
            bouton(
                "SM",
                lambda x, s="SM": self.choisir(s),
                hauteur=60
            )
        )

        principal.add_widget(
            bouton(
                "SS",
                lambda x, s="SS": self.choisir(s),
                hauteur=60
            )
        )

        principal.add_widget(
            bouton(
                "SE",
                lambda x, s="SE": self.choisir(s),
                hauteur=60
            )
        )

        principal.add_widget(
            bouton(
                "RETOUR",
                lambda x: self.manager.__setattr__("current", "classes"),
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def choisir(self, serie):
        App.get_running_app().serie = serie
        self.manager.get_screen("niveau_lycee").serie = serie
        self.manager.current = "niveau_lycee"


# =========================================================
# NIVEAU LYCEE (11eme, 12eme, Terminale pour la serie choisie)
# =========================================================

class NiveauLycee(Screen):
    serie = ""

    def on_pre_enter(self):
        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10)
        )

        principal.add_widget(
            titre("[b]LYCEE - " + self.serie + "[/b]\nChoisis ta classe", 22)
        )

        for classe in CLASSES_LYCEE:
            b = bouton(classe)
            b.bind(
                on_release=lambda btn, c=classe: self.choisir(c)
            )
            principal.add_widget(b)

        principal.add_widget(
            bouton(
                "CHANGER DE SERIE",
                lambda x: self.manager.__setattr__("current", "lycee"),
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def choisir(self, classe):
        app = App.get_running_app()
        app.classe = classe + " " + self.serie
        app.serie = self.serie
        if app.mode_navigation == "examen":
            self.manager.current = "examen"
        else:
            self.manager.current = "matieres"


# =========================================================
# MATIERES
# =========================================================

class Matieres(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        principal.add_widget(
            titre("[b]" + app.classe + "[/b]\nChoisis une matiere", 24)
        )

        for matiere in matieres_pour_classe(app):
            b = bouton(matiere)
            b.bind(
                on_release=lambda btn, m=matiere: self.choisir(m)
            )
            principal.add_widget(b)

        principal.add_widget(
            bouton(
                "CHANGER DE CLASSE",
                lambda x: self.manager.__setattr__("current", "classes"),
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def choisir(self, matiere):
        app = App.get_running_app()
        app.matiere = matiere
        # Une nouvelle matiere commence a son questionnaire n°1.
        quiz = self.manager.get_screen("quiz")
        quiz.numero_questionnaire = 0
        quiz.derniere_signature = None
        self.manager.current = "quiz"


# =========================================================
# QUIZ
# =========================================================

TEMPS_PAR_QUESTION = 20  # secondes


class Quiz(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = []
        self.index = 0
        self.score = 0
        self.total_questions = NB_QUESTIONS_PAR_QUIZ
        self.repondu = False
        self.chrono_event = None
        self.temps_restant = TEMPS_PAR_QUESTION
        self.serie_actuelle = 0
        self.meilleure_serie = 0
        self.numero_questionnaire = 0
        self.derniere_signature = None
        self.suivant_event = None
        self.boutons_choix = []

    def on_pre_enter(self):
        self.demarrer_quiz()

    def on_leave(self):
        self.arreter_chrono()
        if self.suivant_event:
            self.suivant_event.cancel()
            self.suivant_event = None

    def demarrer_quiz(self):
        app = App.get_running_app()

        # Chaque classe possede 400 numeros de questionnaires.
        # REJOUER passe automatiquement au suivant et recommence
        # au questionnaire 1 apres le 400e.
        self.numero_questionnaire = (self.numero_questionnaire % NB_QUESTIONNAIRES_PAR_CLASSE) + 1

        # Graine aleatoire (basee sur l'horloge systeme) : garantit que
        # chaque partie melange les questions differemment, meme si on
        # rejoue tout de suite sur le meme numero de questionnaire.
        rng = random.Random()

        deja_vues = app.quiz_questions_vues.setdefault(app.matiere, set())
        selection = selectionner_questions(
            app.matiere, NB_QUESTIONS_PAR_QUIZ, deja_vues, rng
        )

        # Evite qu'un nouveau questionnaire soit exactement identique
        # au precedent, meme avec une petite banque de questions.
        signature = tuple(id(q) for q in selection)
        if signature == self.derniere_signature and len(selection) > 1:
            rng.shuffle(selection)
        self.derniere_signature = tuple(id(q) for q in selection)

        self.questions = selection
        self.total_questions = len(selection)
        self.index = 0
        self.score = 0
        self.repondu = False
        self.serie_actuelle = 0
        self.meilleure_serie = 0
        self.afficher_question()

    def afficher_question(self):
        self.clear_widgets()

        if self.index >= len(self.questions):
            self.terminer()
            return

        q = self.questions[self.index]

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12)
        )

        principal.add_widget(
            Label(
                text="KOLIE QUIZ",
                font_size=dp(28),
                bold=True,
                color=BLUE,
                size_hint_y=None,
                height=dp(50)
            )
        )

        principal.add_widget(
            Label(
                text="Question " + str(self.index + 1) + " / "
                     + str(self.total_questions)
                     + "\n" + q["matiere"]
                     + "  |  Questionnaire " + str(self.numero_questionnaire)
                     + " / " + str(NB_QUESTIONNAIRES_PAR_CLASSE),
                font_size=dp(17),
                color=GREY,
                halign="center",
                size_hint_y=None,
                height=dp(60)
            )
        )

        self.temps_restant = TEMPS_PAR_QUESTION
        self.timer_label = Label(
            text="Temps restant : " + str(self.temps_restant) + " s",
            font_size=dp(16),
            bold=True,
            color=BLUE,
            halign="center",
            size_hint_y=None,
            height=dp(35)
        )
        principal.add_widget(self.timer_label)

        question_label = Label(
            text=q["question"],
            font_size=dp(22),
            bold=True,
            color=DARK,
            halign="center",
            valign="middle",
            text_size=(Window.width - dp(35), None)
        )
        question_label.bind(
            texture_size=lambda instance, value:
            setattr(instance, "height", max(dp(90), value[1] + dp(20)))
        )
        principal.add_widget(question_label)

        grille = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None
        )
        grille.bind(minimum_height=grille.setter("height"))

        self.boutons_choix = []
        for i, choix in enumerate(q["choix"]):
            b = bouton(
                chr(65 + i) + ". " + choix,
                hauteur=58
            )
            b.bind(
                on_release=lambda btn, choix_index=i:
                self.verifier(choix_index)
            )
            grille.add_widget(b)
            self.boutons_choix.append(b)

        principal.add_widget(grille)

        self.message = Label(
            text="Choisis une réponse.",
            font_size=dp(16),
            color=GREY,
            halign="center",
            size_hint_y=None,
            height=dp(45)
        )
        principal.add_widget(self.message)

        self.explication_label = Label(
            text="",
            font_size=dp(14),
            color=GREY,
            halign="center",
            valign="middle",
            text_size=(Window.width - dp(40), None),
            size_hint_y=None,
            height=dp(0)
        )
        principal.add_widget(self.explication_label)

        self.suivant = bouton(
            "QUESTION SUIVANTE",
            self.question_suivante,
            couleur=GREY
        )
        self.suivant.disabled = True
        principal.add_widget(self.suivant)

        principal.add_widget(
            bouton(
                "QUITTER LE QUIZ",
                lambda x: self.manager.__setattr__("current", "accueil"),
                couleur=(0.40, 0.40, 0.44, 1),
                hauteur=48
            )
        )

        self.add_widget(principal)
        self.demarrer_chrono()

    def demarrer_chrono(self):
        self.arreter_chrono()
        self.chrono_event = Clock.schedule_interval(self.tic_tac, 1)

    def arreter_chrono(self):
        if self.chrono_event:
            self.chrono_event.cancel()
            self.chrono_event = None

    def tic_tac(self, dt):
        self.temps_restant -= 1

        if self.temps_restant <= 0:
            self.timer_label.text = "Temps ecoule !"
            self.arreter_chrono()
            if not self.repondu:
                self.verifier(-1)
            return

        self.timer_label.text = "Temps restant : " + str(self.temps_restant) + " s"
        if self.temps_restant <= 5:
            self.timer_label.color = RED

    def verifier(self, choix_index):
        if self.repondu:
            return

        self.repondu = True
        self.arreter_chrono()
        q = self.questions[self.index]

        app = App.get_running_app()
        stats = app.obtenir_stats(q["matiere"])
        stats["total"] += 1

        correct = (choix_index == q["bonne"])

        if correct:
            self.score += 1
            self.message.text = "Bonne réponse !"
            self.message.color = GREEN
            stats["bonnes"] += 1
            self.serie_actuelle += 1
            self.meilleure_serie = max(self.meilleure_serie, self.serie_actuelle)
        else:
            bonne = q["choix"][q["bonne"]]
            if choix_index == -1:
                self.message.text = "Temps ecoule. Bonne réponse : " + bonne
            else:
                self.message.text = "Mauvaise réponse. Bonne réponse : " + bonne
            self.message.color = RED
            self.serie_actuelle = 0

        # Colore les boutons : bonne reponse en vert, mauvais choix en
        # rouge, et desactive tous les boutons pour empecher de
        # repondre deux fois.
        for i, b in enumerate(self.boutons_choix):
            b.disabled = True
            if i == q["bonne"]:
                b.background_color = GREEN
            elif i == choix_index:
                b.background_color = RED

        explication = q.get("explication", "")
        if explication:
            self.explication_label.text = explication
            self.explication_label.height = dp(60)
        else:
            self.explication_label.text = ""
            self.explication_label.height = dp(0)

        # Passage automatique a la question suivante apres un court
        # delai (plus long s'il y a une explication a lire).
        delai = 2.6 if explication else 1.4
        self.suivant_event = Clock.schedule_once(self._avancer_auto, delai)

    def _avancer_auto(self, dt):
        self.suivant_event = None
        self.question_suivante(None)

    def question_suivante(self, instance=None):
        if not self.repondu:
            return

        if self.suivant_event:
            self.suivant_event.cancel()
            self.suivant_event = None

        self.index += 1
        self.repondu = False
        self.afficher_question()

    def terminer(self):
        self.arreter_chrono()
        app = App.get_running_app()
        app.quiz_joues += 1

        total = max(1, self.total_questions)
        pourcentage = int((self.score / total) * 100)

        if pourcentage > app.meilleur_pourcentage:
            app.meilleur_pourcentage = pourcentage
            app.meilleur_score = self.score
            app.meilleur_total = self.total_questions

        app.total_pourcentage += pourcentage

        app.historique.append({
            "numero": app.quiz_joues,
            "classe": app.classe,
            "matiere": app.matiere,
            "score": self.score,
            "total": self.total_questions,
            "pourcentage": pourcentage
        })
        # On garde les 20 dernieres parties pour ne pas surcharger l'ecran
        app.historique = app.historique[-20:]

        nouveaux_badges = app.maj_badges()

        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(15)
        )

        if pourcentage >= 80:
            appreciation = "Excellent travail !"
        elif pourcentage >= 60:
            appreciation = "Tres bon resultat !"
        elif pourcentage >= 50:
            appreciation = "Resultat satisfaisant."
        else:
            appreciation = "Continue a t'entrainer !"

        principal.add_widget(titre("[b]QUIZ TERMINE[/b]", 30))

        principal.add_widget(
            Label(
                text="Score : " + str(self.score) + " / "
                     + str(self.total_questions) + "\n\n"
                     + str(pourcentage) + " %\n\n"
                     + appreciation
                     + ("\n\nMeilleure serie : " + str(self.meilleure_serie)
                        if self.meilleure_serie > 1 else ""),
                font_size=dp(24),
                bold=True,
                color=DARK,
                halign="center"
            )
        )

        if nouveaux_badges:
            noms = ", ".join(b["nom"] for b in nouveaux_badges)
            principal.add_widget(
                Label(
                    text="Nouveau(x) badge(s) débloqué(s) !\n" + noms,
                    font_size=dp(17),
                    bold=True,
                    color=ORANGE,
                    halign="center",
                    size_hint_y=None,
                    height=dp(70)
                )
            )

        principal.add_widget(
            bouton(
                "REJOUER",
                lambda x: self.demarrer_quiz()
            )
        )

        principal.add_widget(
            bouton(
                "VOIR MES RESULTATS",
                lambda x: self.manager.__setattr__("current", "resultats")
            )
        )

        principal.add_widget(
            bouton(
                "MON EXAMEN",
                lambda x: self.manager.__setattr__("current", "examen_resultat"),
                couleur=ORANGE
            )
        )

        principal.add_widget(
            bouton(
                "ACCUEIL",
                lambda x: self.manager.__setattr__("current", "accueil"),
                couleur=GREY
            )
        )

        self.add_widget(principal)


# =========================================================
# EXAMEN
# =========================================================

class Examen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = []
        self.reponses = []
        self.stats_matiere = {}
        self.index = 0
        self.repondu = False
        self.chrono_event = None
        self.temps_restant = TEMPS_PAR_QUESTION_EXAMEN
        self.suivant_event = None
        self.boutons_choix = []

    def on_pre_enter(self):
        self.demarrer_examen()

    def on_leave(self):
        self.arreter_chrono()
        if self.suivant_event:
            self.suivant_event.cancel()
            self.suivant_event = None

    def demarrer_examen(self):
        app = App.get_running_app()
        matieres = matieres_pour_classe(app)

        rng = random.Random()
        questions = []
        for matiere in matieres:
            if matiere not in BANQUE_PAR_MATIERE:
                continue
            deja_vues = app.examen_questions_vues.setdefault(matiere, set())
            nb = min(NB_QUESTIONS_PAR_MATIERE_EXAMEN, len(BANQUE_PAR_MATIERE[matiere]))
            questions.extend(
                selectionner_questions(matiere, nb, deja_vues, rng)
            )

        # Reorganiser l'examen comme le quiz : ordre des questions
        # et ordre des réponses variables à chaque nouvelle session.
        for q in questions:
            choix = list(q["choix"])
            bonne_texte = choix[q["bonne"]]
            rng.shuffle(choix)
            q["choix"] = choix
            q["bonne"] = choix.index(bonne_texte)

        self.questions = questions
        self.reponses = [None] * len(questions)
        self.stats_matiere = {m: {"bonnes": 0, "total": 0} for m in matieres}
        self.index = 0
        self.repondu = False
        self.afficher_question()

    def afficher_question(self):
        self.clear_widgets()

        if self.index >= len(self.questions):
            self.terminer_examen()
            return

        app = App.get_running_app()
        q = self.questions[self.index]
        coeffs = coefficients_pour_classe(app)
        coeff = coeffs.get(q["matiere"], 1)

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(12)
        )

        principal.add_widget(
            Label(
                text="EXAMEN - " + app.classe,
                font_size=dp(26),
                bold=True,
                color=ORANGE,
                size_hint_y=None,
                height=dp(48)
            )
        )

        principal.add_widget(
            Label(
                text="Question " + str(self.index + 1) + " / "
                     + str(len(self.questions))
                     + "\n" + q["matiere"] + "  (coefficient " + str(coeff) + ")",
                font_size=dp(17),
                color=GREY,
                halign="center",
                size_hint_y=None,
                height=dp(55)
            )
        )

        self.temps_restant = TEMPS_PAR_QUESTION_EXAMEN
        self.timer_label = Label(
            text="Temps restant : " + str(self.temps_restant) + " s",
            font_size=dp(16),
            bold=True,
            color=ORANGE,
            halign="center",
            size_hint_y=None,
            height=dp(35)
        )
        principal.add_widget(self.timer_label)

        question_label = Label(
            text=q["question"],
            font_size=dp(21),
            bold=True,
            color=DARK,
            halign="center",
            valign="middle",
            text_size=(Window.width - dp(35), None)
        )
        question_label.bind(
            texture_size=lambda instance, value:
            setattr(instance, "height", max(dp(90), value[1] + dp(20)))
        )
        principal.add_widget(question_label)

        grille = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None
        )
        grille.bind(minimum_height=grille.setter("height"))

        self.boutons_choix = []
        for i, choix in enumerate(q["choix"]):
            b = bouton(
                chr(65 + i) + ". " + choix,
                couleur=ORANGE,
                hauteur=62
            )
            b.bind(
                on_release=lambda btn, choix_index=i:
                self.verifier(choix_index)
            )
            grille.add_widget(b)
            self.boutons_choix.append(b)

        principal.add_widget(Label(text="", size_hint_y=None, height=dp(14)))
        principal.add_widget(grille)

        self.message = Label(
            text="Choisis une réponse.",
            font_size=dp(16),
            color=GREY,
            halign="center",
            size_hint_y=None,
            height=dp(45)
        )
        principal.add_widget(self.message)

        self.explication_label = Label(
            text="",
            font_size=dp(14),
            color=GREY,
            halign="center",
            valign="middle",
            text_size=(Window.width - dp(40), None),
            size_hint_y=None,
            height=dp(0)
        )
        principal.add_widget(self.explication_label)


        principal.add_widget(
            bouton(
                "QUITTER L'EXAMEN",
                lambda x: self.manager.__setattr__("current", "accueil"),
                couleur=(0.40, 0.40, 0.44, 1),
                hauteur=48
            )
        )

        self.add_widget(principal)
        self.demarrer_chrono()

    def demarrer_chrono(self):
        self.arreter_chrono()
        self.chrono_event = Clock.schedule_interval(self.tic_tac, 1)

    def arreter_chrono(self):
        if self.chrono_event:
            self.chrono_event.cancel()
            self.chrono_event = None

    def tic_tac(self, dt):
        self.temps_restant -= 1

        if self.temps_restant <= 0:
            self.timer_label.text = "Temps ecoule !"
            self.arreter_chrono()
            if not self.repondu:
                self.verifier(-1)
            return

        self.timer_label.text = "Temps restant : " + str(self.temps_restant) + " s"
        if self.temps_restant <= 5:
            self.timer_label.color = RED

    def verifier(self, choix_index):
        if self.repondu:
            return

        self.repondu = True
        self.arreter_chrono()
        q = self.questions[self.index]
        self.reponses[self.index] = choix_index

        stats = self.stats_matiere.setdefault(
            q["matiere"], {"bonnes": 0, "total": 0}
        )
        stats["total"] += 1

        correct = (choix_index == q["bonne"])

        if correct:
            stats["bonnes"] += 1
            self.message.text = "Bonne réponse !"
            self.message.color = GREEN
        else:
            bonne = q["choix"][q["bonne"]]
            if choix_index == -1:
                self.message.text = "Temps ecoule. Bonne réponse : " + bonne
            else:
                self.message.text = "Mauvaise réponse. Bonne réponse : " + bonne
            self.message.color = RED

        for i, b in enumerate(self.boutons_choix):
            b.disabled = True
            if i == q["bonne"]:
                b.background_color = GREEN
            elif i == choix_index:
                b.background_color = RED

        explication = q.get("explication", "")
        if explication:
            self.explication_label.text = explication
            self.explication_label.height = dp(60)
        else:
            self.explication_label.text = ""
            self.explication_label.height = dp(0)

        delai = 2.6 if explication else 1.4
        self.suivant_event = Clock.schedule_once(self._avancer_auto, delai)

    def _avancer_auto(self, dt):
        self.suivant_event = None
        self.question_suivante(None)

    def question_suivante(self, instance=None):
        if not self.repondu:
            return

        if self.suivant_event:
            self.suivant_event.cancel()
            self.suivant_event = None

        self.index += 1
        self.repondu = False
        self.afficher_question()

    def terminer_examen(self):
        self.arreter_chrono()
        app = App.get_running_app()

        coeffs = coefficients_pour_classe(app)
        notes_matiere = {}
        somme_ponderee = 0
        total_coeff = 0

        for matiere, stat in self.stats_matiere.items():
            total = max(1, stat["total"])
            note = round((stat["bonnes"] / total) * 20, 2)
            coeff = coeffs.get(matiere, 1)
            notes_matiere[matiere] = {
                "note": note,
                "bonnes": stat["bonnes"],
                "total": stat["total"],
                "coeff": coeff,
            }
            somme_ponderee += note * coeff
            total_coeff += coeff

        moyenne = round(somme_ponderee / total_coeff, 2) if total_coeff else 0.0
        admis = moyenne >= MOYENNE_ADMISSION

        niveau_ecole = construire_classement_niveau(moyenne, admis, NB_IA_ECOLE)
        niveau_regional = construire_classement_niveau(moyenne, admis, NB_IA_REGIONAL)
        niveau_national = construire_classement_niveau(moyenne, admis, NB_IA_NATIONAL)

        app.examen_session = {
            "classe": app.classe,
            "questions": list(self.questions),
            "reponses": list(self.reponses),
            "notes_matiere": notes_matiere,
            "moyenne": moyenne,
            "admis": admis,
            "niveaux": {
                "ecole": niveau_ecole,
                "regional": niveau_regional,
                "national": niveau_national,
            },
            # Champs generiques (echelle nationale) conserves pour
            # compatibilite avec les affichages generaux.
            "classement": niveau_national["classement"],
            "rang": niveau_national["rang"],
            "total_participants": niveau_national["total_participants"],
            "nb_admis": niveau_national["nb_admis"],
            "heure_disponible": time.time() + DUREE_CORRECTION_SECONDES,
        }

        self.manager.current = "examen_felicitations"


# =========================================================
# EXAMEN - FELICITATIONS / CORRECTION EN COURS
# =========================================================

class ExamenFelicitations(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_horloge = None

    def on_pre_enter(self):
        self.afficher()
        self.event_horloge = Clock.schedule_interval(self.maj_temps, 1)

    def on_leave(self):
        if self.event_horloge:
            self.event_horloge.cancel()
            self.event_horloge = None

    def nom_utilisateur(self):
        app = App.get_running_app()
        compte = getattr(app, "compte", None)
        if compte and compte.get("prenom"):
            return (compte.get("prenom", "") + " " + compte.get("nom", "")).strip()
        return "Candidat"

    def afficher(self):
        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(16)
        )

        principal.add_widget(titre("[b]FELICITATIONS[/b]", 30))

        principal.add_widget(
            Label(
                text=self.nom_utilisateur() + " !\n\n"
                     "Tu as termine ton examen avec succes.",
                font_size=dp(20),
                bold=True,
                color=GREEN,
                halign="center",
                size_hint_y=None,
                height=dp(90)
            )
        )

        self.label_attente = Label(
            text="",
            font_size=dp(17),
            color=ORANGE,
            halign="center",
            valign="middle",
            text_size=(Window.width - dp(50), None),
            size_hint_y=None,
            height=dp(120)
        )
        principal.add_widget(self.label_attente)
        self.maj_temps(0)

        principal.add_widget(
            bouton(
                "VOIR MON RESULTAT",
                lambda x: self.manager.__setattr__("current", "examen_resultat"),
                couleur=ORANGE
            )
        )

        principal.add_widget(
            bouton(
                "RETOUR A L'ACCUEIL",
                lambda x: self.manager.__setattr__("current", "accueil"),
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def maj_temps(self, dt):
        app = App.get_running_app()
        session = app.examen_session
        if not session:
            return

        restant = session.get("heure_disponible", 0) - time.time()

        if restant <= 0:
            self.label_attente.text = (
                "Les resultats sont disponibles !\n"
                "Rends-toi dans l'onglet Resultat pour les consulter."
            )
            self.label_attente.color = GREEN
            if self.event_horloge:
                self.event_horloge.cancel()
                self.event_horloge = None
            return

        minutes = formater_duree(restant)
        self.label_attente.text = (
            "La correction est en cours.\n"
            + NOM_CORRECTEUR + " est sur la correction des copies.\n"
            "Les resultats seront disponibles dans "
            + minutes + "."
        )
        self.label_attente.color = ORANGE


# =========================================================
# EXAMEN - MON RESULTAT
# =========================================================

class ExamenResultat(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_horloge = None

    def on_leave(self):
        if self.event_horloge:
            self.event_horloge.cancel()
            self.event_horloge = None

    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()
        session = app.examen_session

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10)
        )

        if not session:
            principal.add_widget(titre("[b]MON RESULTAT[/b]", 28))
            principal.add_widget(
                Label(
                    text="Aucun examen n'a encore ete passe.",
                    font_size=dp(17),
                    color=GREY,
                    halign="center"
                )
            )
            principal.add_widget(
                bouton(
                    "ACCUEIL",
                    lambda x: self.manager.__setattr__("current", "accueil"),
                    couleur=GREY
                )
            )
            self.add_widget(principal)
            return

        restant = session.get("heure_disponible", 0) - time.time()
        if restant > 0:
            attente = formater_duree(restant)
            principal.add_widget(titre("[b]MON RESULTAT[/b]", 28))
            principal.add_widget(
                Label(
                    text="La correction est en cours.\n"
                         + NOM_CORRECTEUR + " est sur la correction des copies.\n"
                         "Patienter encore " + attente + ".",
                    font_size=dp(18),
                    color=ORANGE,
                    halign="center",
                    valign="middle",
                    text_size=(Window.width - dp(50), None),
                    size_hint_y=None,
                    height=dp(130)
                )
            )
            principal.add_widget(
                bouton(
                    "ACCUEIL",
                    lambda x: self.manager.__setattr__("current", "accueil"),
                    couleur=GREY
                )
            )
            self.add_widget(principal)
            self.event_horloge = Clock.schedule_interval(
                lambda dt: self.on_pre_enter(), 1
            )
            return

        admis = session["admis"]
        couleur_statut = GREEN if admis else RED
        statut_texte = "ADMIS" if admis else "ECHOUE"

        principal.add_widget(
            titre("[b]MON RESULTAT[/b]\n" + session["classe"], 26)
        )

        scroll = ScrollView()
        contenu = GridLayout(cols=1, spacing=dp(8), size_hint_y=None)
        contenu.bind(minimum_height=contenu.setter("height"))

        for matiere, info in session["notes_matiere"].items():
            contenu.add_widget(
                Label(
                    text=matiere + "  -  Note : " + str(info["note"])
                         + " / 20  (coeff. " + str(info["coeff"]) + ")"
                         + "\n" + str(info["bonnes"]) + " bonnes reponses sur "
                         + str(info["total"]),
                    font_size=dp(16),
                    color=DARK,
                    halign="center",
                    size_hint_y=None,
                    height=dp(58)
                )
            )

        scroll.add_widget(contenu)
        principal.add_widget(scroll)

        principal.add_widget(
            Label(
                text="Moyenne générale : " + str(session["moyenne"]) + " / 20\n"
                     + statut_texte,
                font_size=dp(24),
                bold=True,
                color=couleur_statut,
                halign="center",
                size_hint_y=None,
                height=dp(80)
            )
        )

        principal.add_widget(
            Label(
                text="Ton rang : " + str(session["rang"]) + " / "
                     + str(session["total_participants"]),
                font_size=dp(17),
                color=GREY,
                halign="center",
                size_hint_y=None,
                height=dp(35)
            )
        )

        principal.add_widget(
            bouton(
                "VOIR LA CORRECTION",
                lambda x: self.manager.__setattr__("current", "examen_correction")
            )
        )

        principal.add_widget(
            Label(
                text="Voir mon classement :",
                font_size=dp(15),
                color=GREY,
                halign="center",
                size_hint_y=None,
                height=dp(28)
            )
        )

        principal.add_widget(
            bouton(
                "RANG ECOLE",
                lambda x: self.voir_classement("ecole"),
                couleur=ORANGE
            )
        )

        principal.add_widget(
            bouton(
                "RANG REGIONAL",
                lambda x: self.voir_classement("regional"),
                couleur=ORANGE
            )
        )

        principal.add_widget(
            bouton(
                "RANG NATIONAL",
                lambda x: self.voir_classement("national"),
                couleur=ORANGE
            )
        )

        principal.add_widget(
            bouton(
                "REFAIRE L'EXAMEN",
                lambda x: self.manager.__setattr__("current", "examen"),
                couleur=GREY
            )
        )

        principal.add_widget(
            bouton(
                "ACCUEIL",
                lambda x: self.manager.__setattr__("current", "accueil"),
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def voir_classement(self, niveau):
        app = App.get_running_app()
        app.niveau_classement = niveau
        self.manager.current = "examen_classement"


# =========================================================
# EXAMEN - CORRECTION
# =========================================================

class ExamenCorrection(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()
        session = app.examen_session

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10)
        )

        principal.add_widget(titre("[b]CORRECTION DE L'EXAMEN[/b]", 24))

        scroll = ScrollView()
        contenu = GridLayout(cols=1, spacing=dp(14), size_hint_y=None)
        contenu.bind(minimum_height=contenu.setter("height"))

        if not session:
            contenu.add_widget(
                Label(
                    text="Aucun examen a corriger.",
                    font_size=dp(17),
                    color=GREY,
                    size_hint_y=None,
                    height=dp(50)
                )
            )
        else:
            questions = session["questions"]
            reponses = session["reponses"]

            for i, q in enumerate(questions):
                choix_donne = reponses[i]
                bonne_reponse = q["choix"][q["bonne"]]

                if choix_donne is None or choix_donne == -1:
                    texte_reponse = "Pas de reponse (temps ecoule)"
                    couleur = RED
                else:
                    texte_reponse = q["choix"][choix_donne]
                    couleur = GREEN if choix_donne == q["bonne"] else RED

                bloc = BoxLayout(
                    orientation="vertical",
                    spacing=dp(4),
                    size_hint_y=None
                )

                label_question = Label(
                    text=str(i + 1) + ". [" + q["matiere"] + "] "
                         + q["question"],
                    font_size=dp(16),
                    bold=True,
                    color=DARK,
                    halign="left",
                    valign="middle",
                    text_size=(Window.width - dp(45), None),
                    size_hint_y=None
                )
                label_question.bind(
                    texture_size=lambda inst, val:
                    setattr(inst, "height", val[1] + dp(6))
                )

                label_reponse = Label(
                    text="Ta réponse : " + texte_reponse
                         + "\nBonne réponse : " + bonne_reponse,
                    font_size=dp(14),
                    color=couleur,
                    halign="left",
                    valign="middle",
                    text_size=(Window.width - dp(45), None),
                    size_hint_y=None
                )
                label_reponse.bind(
                    texture_size=lambda inst, val:
                    setattr(inst, "height", val[1] + dp(6))
                )

                explication = q.get("explication", "")
                label_explication = Label(
                    text=explication,
                    font_size=dp(13),
                    color=GREY,
                    halign="left",
                    valign="middle",
                    text_size=(Window.width - dp(45), None),
                    size_hint_y=None
                )
                label_explication.bind(
                    texture_size=lambda inst, val:
                    setattr(inst, "height", val[1] + dp(6))
                )

                bloc.add_widget(label_question)
                bloc.add_widget(label_reponse)
                bloc.add_widget(label_explication)
                bloc.bind(minimum_height=bloc.setter("height"))

                contenu.add_widget(bloc)

        scroll.add_widget(contenu)
        principal.add_widget(scroll)

        principal.add_widget(
            bouton(
                "RETOUR AU RESULTAT",
                lambda x: self.manager.__setattr__("current", "examen_resultat"),
                couleur=GREY
            )
        )

        self.add_widget(principal)


# =========================================================
# EXAMEN - CLASSEMENT
# =========================================================

NOMS_NIVEAUX = {
    "ecole": "RANG ECOLE",
    "regional": "RANG REGIONAL",
    "national": "RANG NATIONAL",
}


class ExamenClassement(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.event_horloge = None

    def on_leave(self):
        if self.event_horloge:
            self.event_horloge.cancel()
            self.event_horloge = None

    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()
        session = app.examen_session
        niveau = getattr(app, "niveau_classement", "national")
        titre_niveau = NOMS_NIVEAUX.get(niveau, "RANG NATIONAL")

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(10)
        )

        principal.add_widget(titre("[b]" + titre_niveau + "[/b]", 24))

        if not session:
            principal.add_widget(
                Label(
                    text="Aucun classement disponible.",
                    font_size=dp(17),
                    color=GREY,
                    halign="center"
                )
            )
            self.add_widget(principal)
            return

        restant = session.get("heure_disponible", 0) - time.time()
        if restant > 0:
            attente = formater_duree(restant)
            principal.add_widget(
                Label(
                    text="La correction est en cours.\n"
                         + NOM_CORRECTEUR + " est sur la correction des copies.\n"
                         "Patienter encore " + attente + ".",
                    font_size=dp(18),
                    color=ORANGE,
                    halign="center",
                    valign="middle",
                    text_size=(Window.width - dp(50), None),
                    size_hint_y=None,
                    height=dp(130)
                )
            )
            principal.add_widget(
                bouton(
                    "ACCUEIL",
                    lambda x: self.manager.__setattr__("current", "accueil"),
                    couleur=GREY
                )
            )
            self.add_widget(principal)
            self.event_horloge = Clock.schedule_interval(
                lambda dt: self.on_pre_enter(), 1
            )
            return

        donnees_niveau = session.get("niveaux", {}).get(niveau)
        if not donnees_niveau:
            donnees_niveau = {
                "classement": session["classement"],
                "rang": session["rang"],
                "total_participants": session["total_participants"],
                "nb_admis": session["nb_admis"],
            }

        if donnees_niveau:
            principal.add_widget(
                Label(
                    text="Admis : " + str(donnees_niveau["nb_admis"]) + " / "
                         + str(donnees_niveau["total_participants"])
                         + "   |   Ton rang : " + str(donnees_niveau["rang"]),
                    font_size=dp(16),
                    color=GREY,
                    halign="center",
                    size_hint_y=None,
                    height=dp(35)
                )
            )

            scroll = ScrollView()
            contenu = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
            contenu.bind(minimum_height=contenu.setter("height"))

            for i, c in enumerate(donnees_niveau["classement"], start=1):
                est_toi = c.get("est_utilisateur", False)
                couleur = BLUE if est_toi else (
                    GREEN if c["admis"] else RED
                )
                nom_affiche = c["nom"] + ("  <<< TOI" if est_toi else "")
                statut = "Admis" if c["admis"] else "Echoué"

                contenu.add_widget(
                    Label(
                        text=str(i) + ". " + nom_affiche + "  -  "
                             + str(c["moyenne"]) + "/20  (" + statut + ")",
                        font_size=dp(15),
                        bold=est_toi,
                        color=couleur,
                        halign="left",
                        valign="middle",
                        text_size=(Window.width - dp(40), None),
                        size_hint_y=None,
                        height=dp(34)
                    )
                )

            scroll.add_widget(contenu)
            principal.add_widget(scroll)

        principal.add_widget(
            bouton(
                "RETOUR AU RESULTAT",
                lambda x: self.manager.__setattr__("current", "examen_resultat"),
                couleur=GREY
            )
        )

        principal.add_widget(
            bouton(
                "ACCUEIL",
                lambda x: self.manager.__setattr__("current", "accueil"),
                couleur=GREY
            )
        )

        self.add_widget(principal)


# =========================================================
# RESULTATS
# =========================================================

class Resultats(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()

        if app.quiz_joues > 0:
            moyenne = int(app.total_pourcentage / app.quiz_joues)
            meilleur = str(app.meilleur_score) + " / " + str(app.meilleur_total)
        else:
            moyenne = 0
            meilleur = "--"

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(15)
        )

        principal.add_widget(titre("[b]MES RESULTATS[/b]", 30))

        principal.add_widget(
            Label(
                text="Quiz joues : " + str(app.quiz_joues) + "\n\n"
                     "Meilleur score : " + meilleur + "\n\n"
                     "Moyenne : " + str(moyenne) + " %\n\n"
                     "Continue a apprendre pour progresser !",
                font_size=dp(20),
                color=DARK,
                halign="center"
            )
        )

        principal.add_widget(
            bouton(
                "HISTORIQUE DES QUIZ",
                lambda x: self.manager.__setattr__("current", "historique")
            )
        )

        principal.add_widget(
            bouton(
                "MON EXAMEN",
                lambda x: self.manager.__setattr__("current", "examen_resultat"),
                couleur=ORANGE
            )
        )

        principal.add_widget(
            bouton(
                "ACCUEIL",
                lambda x: self.manager.__setattr__("current", "accueil")
            )
        )

        principal.add_widget(
            bouton(
                "REINITIALISER LES RESULTATS",
                self.reinitialiser,
                couleur=RED,
                hauteur=50
            )
        )

        self.add_widget(principal)

    def reinitialiser(self, instance):
        app = App.get_running_app()
        app.quiz_joues = 0
        app.meilleur_score = 0
        app.meilleur_total = 0
        app.meilleur_pourcentage = 0
        app.total_pourcentage = 0
        app.historique = []
        app.stats_matieres = {}
        app.badges_debloques = []
        app.examen_session = {}
        self.on_pre_enter()


# =========================================================
# HISTORIQUE
# =========================================================

class Historique(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        principal.add_widget(titre("[b]HISTORIQUE DES QUIZ[/b]", 25))

        scroll = ScrollView()

        contenu = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None
        )
        contenu.bind(minimum_height=contenu.setter("height"))

        if not app.historique:
            contenu.add_widget(
                Label(
                    text="Aucun quiz joue pour l'instant.",
                    font_size=dp(17),
                    color=GREY,
                    size_hint_y=None,
                    height=dp(50)
                )
            )
        else:
            for partie in reversed(app.historique):
                contenu.add_widget(
                    Label(
                        text="Partie n°" + str(partie["numero"])
                             + "  -  Classe : " + (partie["classe"] or "-")
                             + "\n" + partie.get("matiere", "-")
                             + "  -  Score : " + str(partie["score"])
                             + " / " + str(partie.get("total", "-"))
                             + "  (" + str(partie["pourcentage"]) + " %)",
                        font_size=dp(16),
                        color=DARK,
                        halign="center",
                        size_hint_y=None,
                        height=dp(60)
                    )
                )

        scroll.add_widget(contenu)
        principal.add_widget(scroll)

        principal.add_widget(
            bouton(
                "RETOUR AUX RESULTATS",
                lambda x: self.manager.__setattr__("current", "resultats"),
                couleur=GREY
            )
        )

        self.add_widget(principal)


# =========================================================
# PROFIL
# =========================================================

class Profil(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(15)
        )

        principal.add_widget(titre("[b]MON PROFIL[/b]", 30))

        compte = getattr(app, "compte", None)
        if compte:
            identite = (
                "Nom : " + compte.get("nom", "") + "\n"
                "Prenom : " + compte.get("prenom", "") + "\n"
                "Email : " + compte.get("email", "")
            )
        else:
            identite = "Aucun compte enregistre."

        principal.add_widget(
            Label(
                text=identite + "\n\n"
                     "Classe : " + (app.classe if app.classe else "Non renseignee")
                     + "\n\n"
                     "Quiz joues : " + str(app.quiz_joues)
                     + "\n\n"
                     "Progression : "
                     + str(min(100, app.quiz_joues * 5)) + " %",
                font_size=dp(20),
                color=DARK,
                halign="center"
            )
        )

        principal.add_widget(
            bouton(
                "ACCUEIL",
                lambda x: self.manager.__setattr__("current", "accueil")
            )
        )

        principal.add_widget(
            bouton(
                "SE DECONNECTER",
                self.se_deconnecter,
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def se_deconnecter(self, instance):
        app = App.get_running_app()
        app.connecte = False
        app.sauvegarder_compte()
        self.manager.current = "connexion"


# =========================================================
# PARAMETRES
# =========================================================

class Parametres(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        principal.add_widget(titre("[b]PARAMETRES[/b]", 30))

        son_text = "SON : ACTIVE" if app.son_active else "SON : DESACTIVE"

        principal.add_widget(
            bouton(
                son_text,
                self.changer_son
            )
        )

        principal.add_widget(
            bouton(
                "MODE SOMBRE",
                self.mode_sombre,
                couleur=GREY
            )
        )

        principal.add_widget(
            bouton(
                "REINITIALISER LES RESULTATS",
                self.reinitialiser,
                couleur=RED
            )
        )

        principal.add_widget(
            bouton(
                "AIDE / INFORMATIONS",
                lambda x: self.manager.__setattr__("current", "aide"),
                couleur=GREY
            )
        )

        principal.add_widget(
            bouton(
                "ACCUEIL",
                lambda x: self.manager.__setattr__("current", "accueil")
            )
        )

        self.add_widget(principal)

    def changer_son(self, instance):
        app = App.get_running_app()
        app.son_active = not app.son_active
        self.on_pre_enter()

    def mode_sombre(self, instance):
        # Fonction simple et fiable pour Pydroid/Kivy.
        # Un vrai theme sombre pourra etre ajoute plus tard.
        app = App.get_running_app()
        app.mode_sombre = not app.mode_sombre

        if app.mode_sombre:
            Window.clearcolor = (0.08, 0.09, 0.12, 1)
        else:
            Window.clearcolor = (0.94, 0.96, 1, 1)

        self.on_pre_enter()

    def reinitialiser(self, instance):
        app = App.get_running_app()
        app.quiz_joues = 0
        app.meilleur_score = 0
        app.meilleur_total = 0
        app.meilleur_pourcentage = 0
        app.total_pourcentage = 0
        app.historique = []
        app.stats_matieres = {}
        app.badges_debloques = []
        app.examen_session = {}
        quiz = self.manager.get_screen("quiz")
        quiz.numero_questionnaire = 0
        quiz.derniere_signature = None
        self.on_pre_enter()


# =========================================================
# AIDE / INFORMATIONS
# =========================================================

class Aide(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(12)
        )

        principal.add_widget(
            titre("[b]AIDE ET INFORMATIONS[/b]", 27)
        )

        texte = (
            "KOLIE QUIZ\n\n"
            "Comment jouer ?\n\n"
            "1. Choisis ton niveau : Primaire, College ou Lycee.\n"
            "2. Au lycee, choisis ta serie (SM, SS ou SE).\n"
            "3. Choisis ta classe, puis une matiere.\n"
            "4. Reponds aux questions avant la fin du chrono.\n"
            "5. Appuie sur QUESTION SUIVANTE.\n"
            "6. A la fin, ton score et ton pourcentage sont "
            "affiches.\n\n"
            "Le quiz melange les questions aleatoirement "
            "a chaque nouvelle partie.\n\n"
            "Les resultats sont conserves pendant que "
            "l'application reste ouverte.\n\n"
            "Version : 1.1\n"
            "Application educative KOLIE QUIZ"
        )

        scroll = ScrollView()

        label = Label(
            text=texte,
            font_size=dp(17),
            color=DARK,
            halign="left",
            valign="top",
            text_size=(Window.width - dp(50), None),
            size_hint_y=None
        )

        label.bind(
            texture_size=lambda instance, value:
            setattr(instance, "height", value[1] + dp(30))
        )

        scroll.add_widget(label)
        principal.add_widget(scroll)

        principal.add_widget(
            bouton(
                "RETOUR AUX PARAMETRES",
                lambda x: self.manager.__setattr__("current", "parametres"),
                couleur=GREY
            )
        )

        principal.add_widget(
            bouton(
                "ACCUEIL",
                lambda x: self.manager.__setattr__("current", "accueil")
            )
        )

        self.add_widget(principal)


# =========================================================
# APPLICATION
# =========================================================

# =========================================================
# INSCRIPTION (BIENVENUE)
# =========================================================

def champ_texte(hint, mot_de_passe=False):
    return TextInput(
        hint_text=hint,
        multiline=False,
        password=mot_de_passe,
        font_size=dp(17),
        size_hint_y=None,
        height=dp(48),
        padding=[dp(12), dp(12), dp(12), dp(12)]
    )


class Bienvenue(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()

        # Un compte inscrit ne peut plus s'inscrire une seconde fois :
        # il doit obligatoirement passer par la connexion.
        if app.compte:
            self.manager.current = "connexion"
            return

        self.clear_widgets()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(10)
        )

        principal.add_widget(
            Label(
                text="[b]BIENVENUE SUR[/b]\n[b]QUIZ PEPE JUSTIN KOLIE[/b]",
                markup=True,
                font_size=dp(24),
                color=BLUE,
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(90)
            )
        )

        principal.add_widget(
            Label(
                text="Cree ton compte pour commencer.",
                font_size=dp(16),
                color=GREY,
                halign="center",
                size_hint_y=None,
                height=dp(30)
            )
        )

        self.champ_nom = champ_texte("Nom")
        self.champ_prenom = champ_texte("Prenom")
        self.champ_email = champ_texte("E-mail")
        self.champ_mot_de_passe = champ_texte("Mot de passe", mot_de_passe=True)

        principal.add_widget(self.champ_nom)
        principal.add_widget(self.champ_prenom)
        principal.add_widget(self.champ_email)
        principal.add_widget(self.champ_mot_de_passe)

        self.message = Label(
            text="",
            font_size=dp(15),
            color=RED,
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )
        principal.add_widget(self.message)

        principal.add_widget(
            bouton("S'INSCRIRE", self.inscrire)
        )

        principal.add_widget(
            bouton(
                "DEJA INSCRIT ? SE CONNECTER",
                lambda x: self.manager.__setattr__("current", "connexion"),
                couleur=GREY
            )
        )

        self.add_widget(principal)

    def inscrire(self, instance):
        app = App.get_running_app()

        nom = self.champ_nom.text.strip()
        prenom = self.champ_prenom.text.strip()
        email = self.champ_email.text.strip()
        mot_de_passe = self.champ_mot_de_passe.text

        if not nom or not prenom or not email or not mot_de_passe:
            self.message.text = "Merci de remplir tous les champs."
            return

        app.compte = {
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "mot_de_passe": mot_de_passe,
        }
        app.connecte = True
        app.sauvegarder_compte()

        self.manager.current = "accueil"


# =========================================================
# CONNEXION
# =========================================================

class Connexion(Screen):
    def on_pre_enter(self):
        self.clear_widgets()

        app = App.get_running_app()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(25),
            spacing=dp(12)
        )

        principal.add_widget(
            Label(
                text="[b]CONNEXION[/b]\nQUIZ PEPE JUSTIN KOLIE",
                markup=True,
                font_size=dp(24),
                color=BLUE,
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(80)
            )
        )

        if not app.compte:
            principal.add_widget(
                Label(
                    text="Aucun compte n'est encore inscrit.",
                    font_size=dp(16),
                    color=GREY,
                    halign="center",
                    size_hint_y=None,
                    height=dp(35)
                )
            )
            principal.add_widget(
                bouton(
                    "S'INSCRIRE",
                    lambda x: self.manager.__setattr__("current", "bienvenue")
                )
            )
            self.add_widget(principal)
            return

        self.champ_email = champ_texte("E-mail")
        self.champ_mot_de_passe = champ_texte("Mot de passe", mot_de_passe=True)

        principal.add_widget(self.champ_email)
        principal.add_widget(self.champ_mot_de_passe)

        self.message = Label(
            text="",
            font_size=dp(15),
            color=RED,
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )
        principal.add_widget(self.message)

        principal.add_widget(
            bouton("SE CONNECTER", self.connecter)
        )

        self.add_widget(principal)

    def connecter(self, instance):
        app = App.get_running_app()
        email = self.champ_email.text.strip()
        mot_de_passe = self.champ_mot_de_passe.text

        if (email == app.compte.get("email")
                and mot_de_passe == app.compte.get("mot_de_passe")):
            app.connecte = True
            app.sauvegarder_compte()
            self.manager.current = "accueil"
        else:
            self.message.text = "E-mail ou mot de passe incorrect."


class KolieQuiz(App):
    classe = ""
    matiere = ""
    serie = ""
    mode_navigation = "quiz"  # "quiz" ou "examen", selon le bouton choisi

    examen_session = {}  # resultats du dernier examen passe
    niveau_classement = "national"  # echelle consultee dans le classement

    # Compte de l'utilisateur inscrit : {"nom", "prenom", "email",
    # "mot_de_passe"}. Vide tant que personne ne s'est inscrit.
    compte = {}
    connecte = False

    # Questions deja vues recemment, par matiere, pour eviter les
    # repetitions d'une partie a l'autre (quiz et examen sont
    # suivis separement).
    quiz_questions_vues = {}
    examen_questions_vues = {}

    quiz_joues = 0
    meilleur_score = 0
    meilleur_total = 0
    meilleur_pourcentage = 0
    total_pourcentage = 0

    son_active = True
    mode_sombre = False

    # Historique des parties : liste de dictionnaires
    # {"numero", "classe", "matiere", "score", "total", "pourcentage"}
    historique = []

    # Statistiques cumulees par matiere :
    # {"Sciences": {"bonnes": 0, "total": 0}, ...}
    stats_matieres = {}

    # Liste des identifiants de badges deja debloques
    badges_debloques = []

    def obtenir_stats(self, matiere):
        if matiere not in self.stats_matieres:
            self.stats_matieres[matiere] = {"bonnes": 0, "total": 0}
        return self.stats_matieres[matiere]

    def maj_badges(self):
        nouveaux = []
        for badge in BADGES:
            if badge["id"] not in self.badges_debloques:
                if badge["condition"](self):
                    self.badges_debloques.append(badge["id"])
                    nouveaux.append(badge)
        return nouveaux

    # ---------------------------------------------------------------
    # Persistance du compte utilisateur (inscription / connexion),
    # pour que l'application se souvienne de l'utilisateur meme apres
    # avoir ete fermee.
    # ---------------------------------------------------------------

    def chemin_fichier_compte(self):
        try:
            dossier = self.user_data_dir
        except Exception:
            dossier = "."
        return os.path.join(dossier, "compte_kolie_quiz.json")

    def charger_compte(self):
        try:
            with open(self.chemin_fichier_compte(), "r", encoding="utf-8") as f:
                data = json.load(f)
            self.compte = {
                "nom": data.get("nom", ""),
                "prenom": data.get("prenom", ""),
                "email": data.get("email", ""),
                "mot_de_passe": data.get("mot_de_passe", ""),
            }
            self.connecte = bool(data.get("connecte", False))
        except Exception:
            self.compte = {}
            self.connecte = False

    def sauvegarder_compte(self):
        try:
            dossier = self.user_data_dir
            os.makedirs(dossier, exist_ok=True)
            data = dict(self.compte)
            data["connecte"] = self.connecte
            with open(self.chemin_fichier_compte(), "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass

    def build(self):
        self.title = "KOLIE QUIZ"

        self.charger_compte()

        manager = ScreenManager()

        manager.add_widget(Bienvenue(name="bienvenue"))
        manager.add_widget(Connexion(name="connexion"))
        manager.add_widget(Accueil(name="accueil"))
        manager.add_widget(Classes(name="classes"))
        manager.add_widget(Primaire(name="primaire"))
        manager.add_widget(College(name="college"))
        manager.add_widget(Lycee(name="lycee"))
        manager.add_widget(NiveauLycee(name="niveau_lycee"))
        manager.add_widget(Matieres(name="matieres"))
        manager.add_widget(Quiz(name="quiz"))
        manager.add_widget(Examen(name="examen"))
        manager.add_widget(ExamenFelicitations(name="examen_felicitations"))
        manager.add_widget(ExamenResultat(name="examen_resultat"))
        manager.add_widget(ExamenCorrection(name="examen_correction"))
        manager.add_widget(ExamenClassement(name="examen_classement"))
        manager.add_widget(Resultats(name="resultats"))
        manager.add_widget(Historique(name="historique"))
        manager.add_widget(Profil(name="profil"))
        manager.add_widget(Parametres(name="parametres"))
        manager.add_widget(Aide(name="aide"))

        # Un compte deja inscrit ET connecte va directement au menu.
        # Un compte inscrit mais deconnecte (via "SE DECONNECTER")
        # doit se reconnecter. Sans aucun compte, on propose
        # l'inscription.
        if self.compte and self.connecte:
            manager.current = "accueil"
        elif self.compte:
            manager.current = "connexion"
        else:
            manager.current = "bienvenue"

        return manager


if __name__ == "__main__":
    KolieQuiz().run()
