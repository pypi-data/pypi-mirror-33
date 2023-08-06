#!/bin/bash

# Installe les exercices de tests pour qu'ils puissent être compilés

set -e

DOCDIR=$(pwd)/$(dirname $0)
ROOT=$DOCDIR/../../..
TEMPLATEDIR=$ROOT/pyromaths/data/exercices/templates
EXERCICEDIR=$ROOT/pyromaths/ex/troisiemes

cd $TEMPLATEDIR
for template in $DOCDIR/*/*tex
do
  ln $template
done

cd $EXERCICEDIR
for exercice in $DOCDIR/*/*py
do
  ln $exercice
done
