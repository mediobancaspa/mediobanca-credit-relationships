# Limitations

This document outlines the main limitations of the current model and implementation.

---

## Data dependency

The pipeline depends on:

- structure of the CSV dataset  
- consistency of entity naming  
- availability of a general network  

---

## Entity normalization

- ambiguity in names may affect node identity  
- lack of formal entity disambiguation  

---

## Aggregation

- aggregation removes temporal dimension  
- repeated relationships are merged  

---

## Visualization

- dense regions may reduce readability  
- arc diagram limits scalability  

---

## Generalization

The pipeline is not fully general:

- requires adaptation for different datasets  
- assumes specific data conventions  

---

## Interpretation

- relationships reflect recorded data, not necessarily causal or complete structures  
- absence of a link does not imply absence of a relationship  
