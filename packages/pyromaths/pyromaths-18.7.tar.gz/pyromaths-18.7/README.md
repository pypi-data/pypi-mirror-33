[Pyromaths](http://pyromaths.org/) est un programme qui a pour but de créer des exercices type de mathématiques niveau collège et lycée ainsi que leur corrigé. C'est ce qu'on appelle parfois un exerciseur. Contrairement à de nombreux autres projets, Pyromaths a pour objectif de proposer une correction véritablement détaillée des exercices proposés et pas seulement une solution.

Il permet par exemple de proposer des devoirs maison aux élèves et de leur distribuer ensuite la correction. Il peut aussi servir à des familles afin qu'un élève puisse travailler un point du programme et se corriger ensuite.

Si vous voulez participer à la traduction, consultez [cette page](https://framagit.org/pyromaths/pyromaths/blob/develop/pyromaths/data/locale/TRADUIRE.md).

# Utiliser Pyromaths

## Version en ligne

Il est possible d'utiliser Pyromaths sans l'installer, en utilisant [la version en ligne](http://enligne.pyromaths.org).

## Version de bureau

Pour GNU/Linux, Mac OS, Windows, visitez [la page d'installation](https://www.pyromaths.org/installer/).

# Développer Pyromaths

- Clonez le dépôt pour télécharger les sources.

        git clone https://framagit.org/pyromaths/pyromaths.git
        cd pyromaths

- Créer un virtualenv utilisant python3.

        virtualenv -ppython3 pyromaths-venv

- Installez les dépendances

        pip install -r requirements.txt

- Vous pouvez maintenant utiliser pyromaths, avec l'une ou l'autre des commandes suivantes.

        python -m pyromaths
        ./utils/pyromaths
