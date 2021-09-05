# PMCSN-FAIRY-TAILS ( Bencivenni&Pontis )
Progetto di Modellazione e Simulazione di Sistemi a Code

Si presenta il progetto elaborato per il Corso di Performance Modeling of Computer Systems and Networks presso l'Università di Roma Torvergata, nell'anno accademico 2020/2021.  
Lo studio introduce ed analizza due modelli che rappresentino, entro determinati margini di accuratezza, due sistemi a code utilizzabili per le casse dei supermercati. 
Il primo caso di studio ricalca quella che è la rete di code più comunemente sperimentata: procedendo nei passi di modellazione, simulazione ed analisi delle statistiche di output, sarà possibile delineare i limiti di questa tipologia di sistema, così da poter ideare e simulare un modello del tutto nuovo, che sia in grado di raggiungere obiettivi migliori ed agevolare l'esperienza per una larga parte dell'utenza.

UTILIZZO DEL PROGRAMMA - LINEE GUIDA

1) Per effettuare simulazioni all'orizzonte infinito (steady-state) con il metodo batch-means:
    - posizionarsi nella cartella ../PROGETTO PMCSN 2021
    - chiamare, da riga di comando:
        python ssq_abs_network.py [argv1:numeroDiRuns] [argv2:tempoDiSimulazione], per utilizzare il modello classico
        python msmq_sb.py [argv1:numeroDiRuns] [argv2:tempoDiSimulazione], per utilizzare il modello avanzato
    - seguire le istruzioni della UI, specificando il tipo di simulazione, i valori dei parametri b, k, e il seed iniziale.
        valori consigliati, in base a quanto sviluppato nel progetto: tempoDiSimulazione:600000, b:2048, k:64
    - visualizzare i risultati delle simulazioni nell'ultimo ensemble disponibile nella cartella ../PROGETTO PMCSN 2021/MG1_abs_network


2) Per effettuare simulazioni all'orizzonte finito (transienti) con il metodo delle repliche:
    - posizionarsi nella cartella ../PROGETTO PMCSN 2021
    - chiamare, da riga di comando:
        python ssq_abs_network.py [argv1:numeroDiRepliche] [argv2:tempoDiSimulazione], per utilizzare il modello classico
        python msmq_sb.py [argv1:numeroDiRepliche] [argv2:tempoDiSimulazione], per utilizzare il modello avanzato
    - seguire le istruzioni della UI, specificando il tipo di simulazione, e il seed iniziale.
    - visualizzare i risultati delle simulazioni nell'ultimo ensemble disponibile nella cartella ../PROGETTO PMCSN 2021/MSMQ_sb


