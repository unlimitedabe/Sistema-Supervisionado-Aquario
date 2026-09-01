# Sistema Supervisionado de Aquário

Sistema acadêmico de **automação e supervisão de aquário**, integrando hardware baseado em Arduino a uma aplicação web desenvolvida em Python.

O projeto utiliza sensores para monitorar luminosidade, temperatura e nível da água e aciona automaticamente LED, buzzer e bomba de água de acordo com as condições detectadas.

Além da automação física, foi desenvolvido um sistema supervisório responsável por receber os dados do Arduino, armazenar os registros, apresentar o estado do aquário em tempo real e gerar relatórios.

Todo funcionamento e imagens pode ser visto nesse [Documento](Slide-Automatização_de_aquários.pdf) e neste [Video](Video_Pratica2.MP4) 

---

## Visão geral

O projeto foi desenvolvido com o objetivo de reduzir a necessidade de intervenção manual na manutenção de um aquário e permitir o acompanhamento contínuo de variáveis importantes para seu funcionamento.

O sistema integra:

```text
Sensores
   ↓
Arduino
   ↓
Lógica de controle
   ↓
Atuadores

        +

Arduino
   ↓
Comunicação serial
   ↓
Python / Flask
   ↓
SQLite
   ↓
Interface Web
   ↓
Alertas / Relatórios / Gráficos
```

---

## Funcionamento

O sistema trabalha com três variáveis principais.

### Luminosidade

Um sensor **LDR** monitora a luminosidade do ambiente.

De acordo com o valor medido, o Arduino controla um LED utilizado para representar o acionamento da iluminação.

### Temperatura

Um sensor de temperatura submersível monitora a temperatura da água.

Quando a temperatura ultrapassa o limite configurado, o sistema aciona um **buzzer** para indicar uma situação de alerta.

### Nível de água

Um sensor de nível monitora a quantidade de água disponível.

Quando é detectado nível baixo, o Arduino aciona uma **bomba de água** através de um módulo relé.

---

## Lógica de automação

A lógica utilizada no projeto foi representada por um diagrama Ladder.

De forma simplificada:

```text
Luminosidade
     ↓
    LDR
     ↓
    LED

Temperatura
     ↓
Sensor de temperatura
     ↓
   Buzzer

Nível de água
     ↓
Sensor de nível
     ↓
    Relé
     ↓
Bomba de água
```

Os limites definidos durante o projeto incluíam:

- acionamento da iluminação conforme o valor medido pelo LDR;
- acionamento do buzzer quando a temperatura ultrapassava 30 °C;
- acionamento da bomba quando o sensor identificava nível de água baixo.

---

## Sistema supervisório

Além da programação embarcada, foi desenvolvida uma aplicação responsável pela supervisão do aquário.

O sistema permite:

- receber dados enviados pelo Arduino;
- visualizar as medições em tempo real;
- visualizar o estado dos atuadores;
- registrar dados dos sensores;
- registrar eventos de alarme;
- alterar dinamicamente a interface em situações de alerta;
- gerar relatórios;
- gerar gráficos;
- enviar relatórios por e-mail.

---

## Arquitetura

```text
┌────────────────────────────┐
│          Sensores           │
│                             │
│ LDR | Temperatura | Nível   │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│        Arduino Uno          │
│                             │
│ Leitura + regras de controle│
└───────┬───────────┬────────┘
        │           │
        │           └─────────────────┐
        ▼                             ▼
┌──────────────────┐         ┌─────────────────┐
│    Atuadores      │         │ Comunicação     │
│                   │         │ Serial          │
│ LED               │         └────────┬────────┘
│ Buzzer            │                  │
│ Bomba + Relé      │                  ▼
└──────────────────┘        ┌─────────────────────┐
                            │ Python / Flask      │
                            │ Sistema supervisório│
                            └──────────┬──────────┘
                                       │
                            ┌──────────┴──────────┐
                            ▼                     ▼
                       ┌─────────┐          ┌───────────┐
                       │ SQLite  │          │ Interface │
                       └─────────┘          │ Web       │
                                            └─────┬─────┘
                                                  │
                                                  ▼
                                        Alertas / Relatórios
                                             / Gráficos
```

---

## Tecnologias utilizadas

### Sistema embarcado

- Arduino Uno;
- Arduino IDE;
- comunicação serial;
- sensores e atuadores.

### Backend

- Python;
- Flask;
- SQLite;
- Serial;
- Matplotlib.

### Frontend

- HTML;
- CSS;
- JavaScript;
- AJAX.

---

## Hardware

Foram utilizados:

- Arduino Uno;
- protoboard;
- sensor de luminosidade LDR;
- sensor de temperatura submersível;
- sensor de nível de água;
- LED;
- buzzer;
- bomba de água;
- relé de 5 V;
- fonte de alimentação adicional;
- resistores;
- capacitor;
- fios jumper.

---

## Monitoramento em tempo real

A interface apresenta simultaneamente:

```text
LDR           → valor de luminosidade
Temperatura   → temperatura da água
Nível         → estado do nível da água

LED           → ligado / desligado
Buzzer        → ligado / desligado
Bomba         → ligada / desligada
```

Quando alguma variável entra em uma condição de alerta, a interface é atualizada para comunicar visualmente a situação ao usuário.

---

## Persistência dos dados

O sistema utiliza **SQLite** para registrar:

- leituras dos sensores;
- estados dos atuadores;
- data e hora das medições;
- eventos de alarme.

Esses dados são posteriormente utilizados para a geração de relatórios e gráficos.

---

## Relatórios

O sistema supervisório permite gerar diferentes tipos de relatório.

### Relatório de dados

Apresenta o histórico das medições dos sensores e estados dos atuadores.

### Relatório de alarmes

Registra os eventos em que alguma condição configurada gerou um alerta.

### Relatório com gráficos

Utiliza **Matplotlib** para representar graficamente a evolução das variáveis monitoradas.

Os relatórios também podiam ser enviados por e-mail pelo sistema.

---

## Minha contribuição

O projeto acadêmico foi desenvolvido em equipe por:

- João Monferrari Salgado Fernandes;
- Rafael Campos Almeida;
- Rafael de Matos Abe.

Minha responsabilidade esteve concentrada no desenvolvimento do software responsável pela **automação e supervisão do sistema**.

Fui responsável por:

- desenvolver o código executado no Arduino;
- implementar a leitura dos sensores;
- implementar as regras de acionamento dos atuadores;
- controlar LED, buzzer e bomba de água;
- implementar a comunicação serial entre Arduino e computador;
- desenvolver o sistema supervisório em Python;
- desenvolver o backend utilizando Flask;
- integrar os dados recebidos do Arduino à aplicação;
- implementar o armazenamento em SQLite;
- implementar o monitoramento das variáveis;
- implementar os estados de alerta;
- desenvolver a interface web do supervisório;
- gerar relatórios dos dados registrados;
- gerar gráficos utilizando Matplotlib;
- integrar o envio dos relatórios por e-mail.

Minha atuação, portanto, cobriu o fluxo de software desde a **aquisição dos dados no microcontrolador até o processamento e apresentação das informações na aplicação web**.

---

## Contexto acadêmico

O projeto foi desenvolvido como atividade acadêmica da Escola Politécnica da **Pontifícia Universidade Católica de Goiás (PUC Goiás)**.

Além da implementação prática, o trabalho foi documentado por meio de artigo acadêmico e apresentação técnica.

---

## Status

Projeto acadêmico concluído.

Este repositório preserva o código desenvolvido durante o projeto e é mantido como parte do meu portfólio de desenvolvimento de software e sistemas embarcados.
