
import csv

from pyDatalog.pyDatalog import assert_fact, load, ask, clear
from pyDatalog import pyDatalog, pyEngine

import logging
pyEngine.Logging = True
logging.basicConfig(level=logging.INFO)


class MotorLogico(object):
    def __init__(self, database, valid_relations, lan, load_database=False):
        
        self.valid_relations = valid_relations
        self.kb = []
        self.lan = lan
        self.database = database

        try:
            if(load_database):
                if(lan == []):
                    self.load_db()
                else:
                    self.load_db_by_language()
        except:
            self.kb = []


    def relacion_palabra_idioma(self, palabra, idioma):
        X = pyDatalog.Variable()
        Relation.hasLanAndWord[X,idioma, palabra]
        return X


    def relacion_hermandad(self, palabra1, palabra2):
        X = pyDatalog.Variable()
        Y = pyDatalog.Variable()
        Relation.siblings(X,Y,palabra1, palabra2)
        return X,Y

    def relacion_parent(self, palabra1, palabra2):
        X = pyDatalog.Variable()
        (Relation.parent(X, palabra1, palabra2))
        return X

    def relacion_primer_primos(self, palabra1, palabra2):
        W = pyDatalog.Variable()
        X = pyDatalog.Variable()
        Y = pyDatalog.Variable()
        Z = pyDatalog.Variable()
        (Relation.cousins(W,X,Y,Z,palabra1,palabra2))
        return Y,Z

    def relacion_tio(self, palabra1, palabra2):
        X = pyDatalog.Variable()
        Y = pyDatalog.Variable()
        Z = pyDatalog.Variable()
        return Relation.uncle(X,Y,Z,palabra1,palabra2)

    def relacion_ancestro(self, palabra1, palabra2):
        X = pyDatalog.Variable()
        Y = pyDatalog.Variable()
        return Relation.ancestro(X,palabra1,palabra2)

    def primos_aux(self,palabra1):
        X = pyDatalog.Variable()
        Y = pyDatalog.Variable()
        Relation.ancestor(X,Y,palabra1)
        return Y

    def relacion_primos_nivel(self, palabra1, palabra2):
        W = pyDatalog.Variable()
        X = pyDatalog.Variable()
        Y = pyDatalog.Variable()
        Z = pyDatalog.Variable()
        w1 = len(self.primos_aux(palabra1))
        w2 = len(self.primos_aux(palabra2))
        grade = len(Relation.ances(X,Y,palabra1,palabra2))
        level = max(w1,w2)-grade
        resultado = Relation.counsingrade(W,X,Y,Z,palabra1,palabra2)
        return (resultado, level)

    def palabras_originadas(self,palabra,idioma):
        X = pyDatalog.Variable()
        Result = pyDatalog.Variable()
        Relation.originatedWords(X,palabra,idioma,Result)
        return X,Result

    def idiomas_relacionados_palabra(self, palabra):
        X = pyDatalog.Variable()
        Result = pyDatalog.Variable()
        Relation.lanByWord(X,palabra,Result)
        Result = set(eval(str(Result)))
        return X,Result

    def palabras_comun_idiomas(self, idioma1, idioma2):
        returnList = []
        X,Result = self.palabras_comun_idiomas_aux(idioma1, idioma2)
        Result = set(eval(str(Result)))
        return X,Result

    def palabras_comun_idiomas_aux(self, idioma1, idioma2):
        X = pyDatalog.Variable()
        Y = pyDatalog.Variable()
        Z = pyDatalog.Variable()
        Result = pyDatalog.Variable()
        Relation.wordInCommon(X,Y,idioma1,idioma2,Z)
        return X,Z


    def contador_palabras_comun_idiomas(self, idioma1, idioma2):
        inferencias, resultado = self.palabras_comun_idiomas_aux(idioma1, idioma2)
        return inferencias, len(resultado)


    def mayor_aporte_a_idioma(self,idioma,test=False):
        inferencias, idiomas, porcentajes = self.aporte_idiomas(idioma,test)
        Result = pyDatalog.Variable()
        pyDatalog.create_terms("max_index")
        print(max_index(porcentajes)==Result)
        return inferencias, idiomas[int(str(Result.v()))],porcentajes.data[0][int(str(Result.v()))]
    
    #Retorna las inferencias, la lista de idiomas que aportaron y el porcentaje de cada una respectivamente
    def aporte_idiomas(self,idioma,test=False):
        if(self.lan == []):
            return self.aporte_idiomas_aux(idioma,self.get_idiomas_file(),test)
        else:
            return self.aporte_idiomas_aux(idioma,self.lan,test)
        
    def aporte_idiomas_aux(self,idioma,idiomas,test=False):
       X = pyDatalog.Variable()
       Result = pyDatalog.Variable()
       Porcentajes = pyDatalog.Variable()
       lan_kb = []
       inferences=[]
       idiomas_lista=[]
       percentages=[]
       total = 0
       pyDatalog.create_terms('lista_vacia')
       pyDatalog.create_terms('lista_porcentaje')
       
       
       for i in idiomas:
           if(i!=idioma):
               if(not test):
                   self.kb = []
                   self.lan = [i]
                   self.load_db_by_language()
               
               (lista_vacia(Relation.proportionPerLan(X,idioma,i))==Result)
               if(not Result.v()):
                   inferences += [Relation.proportionPerLan(X,idioma,i)]
                   idiomas_lista += [i]
                   total += len(Relation.proportionPerLan(X,idioma,i))
                   percentages += [len(Relation.proportionPerLan(X,idioma,i))]
       (lista_porcentaje(percentages,total)==Porcentajes)
       return inferences,idiomas_lista,Porcentajes



    def get_idiomas_file(self):
        try:
            idiomas_file = open("lan.txt","r")
            idiomas = []
            for row in idiomas_file:
                idiomas += [row.rstrip()]
            return idiomas
        except:
            return []

    def lista_porcentaje(self,lista,total):
        for i in lista:
            i /= total
        return lista
    def load_db_by_language(self):
        print("Idioma")
        self.kb=[]
        fd = open(self.database, encoding="utf8")
        rd = csv.reader(fd, delimiter="\t")
        cont = 0
        for row in rd:
          r_type = row[1]
          if(self.valid_relations != [] and r_type not in self.valid_relations):
              continue
          f_lan = row[0][0:3]
          s_lan = row[2][0:3]
          if(f_lan not in self.lan and s_lan not in self.lan):
              continue

          f_word = row[0][5:]
          s_word = row[2][5:]
          self.kb.append(Relation(f_lan, f_word, r_type, s_lan, s_word))
          cont += 1
        print(str(cont)+" filas leidas")

    def load_db_equals(self):
        print("Equals")
        fd = open(self.database, encoding="utf8")
        rd = csv.reader(fd, delimiter="\t")
        self.kb=[]
        words = []
        cont = 0
        for row in rd:
          r_type = row[1]
          add_to_kb = False
          if(self.valid_relations != [] and r_type not in self.valid_relations):
              continue
          f_lan = row[0][0:3]
          s_lan = row[2][0:3]
          if(f_lan not in self.lan and s_lan not in self.lan):
              continue
          f_word = row[0][5:]

          s_word = row[2][5:]
          if([f_word,f_lan] not in words ):
              words.append([f_word,f_lan])
              add_to_kb = True
          if([s_word,s_lan] not in words):
              words.append([s_word,s_lan])
              add_to_kb = True
          if(add_to_kb):
              self.kb.append(Relation(f_lan, f_word, r_type, s_lan, s_word))
              cont += 1
        print(str(cont)+" relaciones agregadas a kb")

    def load_db(self):
        print("Completa")
        fd = open(self.database, encoding="utf8")
        rd = csv.reader(fd, delimiter="\t")
        self.kb=[]
        for row in rd:
            r_type = row[1]
            if(self.valid_relations != [] and r_type not in self.valid_relations):
              continue
            f_lan = row[0][0:3]
            f_word = row[0][5:]
            s_lan = row[2][0:3]
            s_word = row[2][5:]
            self.kb.append(Relation(f_lan, f_word, r_type, s_lan, s_word))


class Relation(pyDatalog.Mixin):
    def __init__(self, first_lan, first_word, relation_type, second_lan, second_word):
        super(Relation, self).__init__()
        self.first_lan = first_lan
        self.first_word = first_word
        self.r_type = relation_type
        self.second_lan = second_lan
        self.second_word = second_word
    def __repr__(self):
        return self.first_lan + ": " + self.first_word + " " + self.r_type + " " + self.second_lan + ": " + self.second_word
    @pyDatalog.program()
    def _():

        # Determinar si dos palabras son hermanas
        Relation.parent(X,Word1,Word2) <=  (Relation.second_word[X]==Word2) & (Relation.first_word[X]==Word1) & (Relation.r_type[X]=='rel:derived')
        Relation.parent(X,Word1,Word2) <= (Relation.second_word[X]==Word2) & (Relation.first_word[X]==Word1) & (Relation.r_type[X]=='rel:has_derived_form')
        Relation.parent(X,Word1,Word2) <= (Relation.first_word[X]==Word2) & (Relation.second_word[X]==Word1) & (Relation.r_type[X]=='rel:is_derived_from')
        Relation.siblings(X,Y,Word1,Word2) <= Relation.parent(X,Z,Word1) & Relation.parent(Y,Z,Word2) & (X!=Y)

        # Determinar si dos palabras son primos primer nivel
        Relation.cousins(W,X,Y,Z,Word1,Word2) <= Relation.parent(W,A,Word1) & Relation.parent(X,B,Word2) & (A!=B) &Relation.siblings(Y,Z,A,B) 
        
        # Determinar si una palabra es tia de otra
        Relation.uncle(X,Y,Z,Word1,Word2) <= Relation.parent(X,A,Word2) & Relation.siblings(Y,Z,A,Word1)

        # Determinar ancestros de una palabra
        Relation.ancestor(X,Word1,Word2) <= (Relation.first_word[X]==Word2) & (Relation.second_word[X]==Word1) & (Relation.r_type[X]=='rel:is_derived_from')
        Relation.ancestor(X,Word1,Word2) <= (Relation.first_word[X]==Z) & (Relation.second_word[X]==Word1) & (Relation.r_type[X]=='rel:is_derived_from') & (Relation.ancestor(Y,Z,Word2))

        Relation.ances(X,Y,Word1,Word2) <= Relation.ancestor(X,A,Word1) & Relation.ancestor(Y,B,Word2) & (A==B)


        # Determinas si dos palabras son primos y devolver grado
        Relation.counsingrade(W,X,Y,Z,Word1,Word2) <= Relation.ancestor(W,A,Word1) & Relation.ancestor(X,B,Word2) & (A!=B) & Relation.siblings(Y,Z,A,B)


        # Determinar si una palabra esta relacionada con un idioma o no

        (Relation.hasLanAndWord[X,Lan,Word]==True) <= (Relation.first_word[X]==Word) & (Relation.first_lan[X]==Lan)
        (Relation.hasLanAndWord[X,Lan,Word]==True) <= (Relation.second_word[X]==Word) & (Relation.second_lan[X]==Lan)
        (Relation.hasLanAndWord[X,Lan,Word]==True) <= (Relation.second_word[X]==Word) &(Relation.first_lan[X]==Lan)
        (Relation.hasLanAndWord[X,Lan,Word]==True) <= (Relation.first_word[X]==Word) & (Relation.second_lan[X]==Lan)
        # Palabras originadas por otra
        Relation.originatedWords(X,Word,Lan,Result) <= (Relation.second_word[X]==Word) & (Relation.second_lan[X]==Lan) & (Relation.r_type[X]=='rel:is_derived_from') & ((Relation.first_word[X],Relation.first_lan[X])==Result)
        Relation.originatedWords(X,Word,Lan,Result) <= (Relation.first_word[X]==Word) & (Relation.first_lan[X]==Lan) & (Relation.r_type[X]=='rel:has_derived_form') & ((Relation.second_word[X],Relation.second_lan[X])==Result)
        Relation.originatedWords(X,Word,Lan,Result) <= (Relation.second_word[X]==Word) & (Relation.second_lan[X]==Lan) & (Relation.r_type[X]=='rel:etymology') & ((Relation.first_word[X],Relation.first_lan[X])==Result)
        Relation.originatedWords(X,Word,Lan,Result) <= (Relation.first_word[X]==Word) & (Relation.first_lan[X]==Lan) & (Relation.r_type[X]=='rel:etymological_origin_of') & ((Relation.second_word[X],Relation.second_lan[X])==Result)
        Relation.originatedWords(X,Word,Lan,Result) <= (Relation.first_word[X]==Word) & (Relation.first_lan[X]==Lan) & (Relation.r_type[X]=='rel:variant:orthography') & ((Relation.second_word[X],Relation.second_lan[X])==Result)
        # Idiomas relacionados con una palabra
        Relation.lanByWord(X,Word,Result) <= (Relation.second_word[X]==Word) & ((Relation.first_lan[X],Relation.second_lan[X])==Result)
        Relation.lanByWord(X,Word,Result) <= (Relation.first_word[X]==Word) & ((Relation.first_lan[X],Relation.second_lan[X])==Result)
        # Palabras comunes entre dos idiomas(Contar)
        (Relation.countWordInCommon[X,Y,Lan1,Lan2]==len_(Y)) <= (Relation.second_word[X] == Relation.second_word[Y]) & (Relation.second_lan[X]==Lan1) & (Relation.second_lan[Y]==Lan2) & (X!=Y)
        (Relation.countWordInCommon[X,Y,Lan1,Lan2]==len_(Y)) <= (Relation.first_word[X] == Relation.first_word[Y]) & (Relation.first_lan[X]==Lan1) & (Relation.first_lan[Y]==Lan2) & (X!=Y)
        (Relation.countWordInCommon[X,Y,Lan1,Lan2]==len_(Y)) <= (Relation.second_word[X] == Relation.first_word[Y]) &  (Relation.second_lan[X]==Lan1) & (Relation.first_lan[Y]==Lan2) & (X!=Y)
        (Relation.countWordInCommon[X,Y,Lan1,Lan2]==len_(Y)) <= (Relation.second_word[X] == Relation.first_word[Y]) &  (Relation.second_lan[X]==Lan2) & (Relation.first_lan[Y]==Lan1) & (X!=Y)
        # Palabras comunes entre dos idiomas(Listar)
        Relation.wordInCommon(X,Y,Lan1,Lan2,Z) <= (Relation.second_word[X] == Relation.second_word[Y]) & (Relation.second_lan[X]==Lan1) & (Relation.second_lan[Y]==Lan2) & (X!=Y)& (Relation.second_word[X] == Z)
        Relation.wordInCommon(X,Y,Lan1,Lan2,Z) <= (Relation.first_word[X] == Relation.first_word[Y])   & (Relation.first_lan[X]==Lan1) & (Relation.first_lan[Y]==Lan2)  & (X!=Y) & (Relation.first_word[X] == Z)
        Relation.wordInCommon(X,Y,Lan1,Lan2,Z) <= (Relation.second_word[X] == Relation.first_word[Y]) &  (Relation.second_lan[X]==Lan1) & (Relation.first_lan[Y]==Lan2)   & (X!=Y) & (Relation.second_word[X] == Z)
        Relation.wordInCommon(X,Y,Lan1,Lan2,Z) <= (Relation.second_word[X] == Relation.first_word[Y]) &  (Relation.second_lan[X]==Lan2) & (Relation.first_lan[Y]==Lan1)   & (X!=Y) & (Relation.second_word[X] == Z)
        # Aporte a idioma(Listar)
        Relation.proportionPerLan(X,BaseLan,GLan) <= (Relation.first_lan[X]==BaseLan) & (Relation.second_lan[X]==GLan) & (Relation.r_type[X]=='rel:etymology')
        Relation.proportionPerLan(X,BaseLan,GLan) <= (Relation.first_lan[X]==GLan) & (Relation.second_lan[X]==BaseLan) & (Relation.r_type[X]=='rel:etymological_origin_of')
        Relation.proportionPerLan(X,BaseLan,GLan) <= (Relation.first_lan[X]==GLan) & (Relation.second_lan[X]==BaseLan) & (Relation.r_type[X]=='rel:variant:orthography')
        Relation.proportionPerLan(X,BaseLan,GLan) <= (Relation.second_lan[X]==GLan) & (Relation.first_lan[X]==BaseLan) & (Relation.r_type[X]=='rel:has_derived_form')
        Relation.proportionPerLan(X,BaseLan,GLan) <= (Relation.first_lan[X]==BaseLan) & (Relation.second_lan[X]==GLan) & (Relation.r_type[X]=='rel:is_derived_from')
        Relation.proportionPerLan(X,BaseLan,GLan) <= (Relation.second_lan[X]==GLan) & (Relation.first_lan[X]==BaseLan) & (Relation.r_type[X]=='rel:derived')


#Funciones para usar en expresiones logicas

def lista_vacia(lista):
        if(lista==[]):
            return True
        return False
    
def lista_porcentaje(lista,total):
        for i in range(len(lista)):
            lista[i] /= total
        return lista
    
def max_index(lista):
    max_value = 0
    max_index = 0
    for i in range(len(lista)):
        if(lista.data[0][i]>max_value):
            max_value = lista[i]
            max_index = i
    return max_index

#motor = MotorLogico("basepruebas.tsv",[],["eng"],True)

def funcion():
    return motor.relacion_primos_nivel("d","k")




