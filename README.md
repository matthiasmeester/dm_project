# Data Mining UU final project

### Authors: Diederik Rijen, Simon Boerstra, Maarten de Koning and Matthias Meester

# Research Question: 
#### Research Question: How are specific language markers like sentence length, word length and  imperatives used during the COVID press conferences in relation with the infection rates?

## Sub Questions:
- Does the use of imperative change over time as a function of the infection rate?
- Do the language markers/keywords correlate with the number of infections, if so how noticeable is this correlation?
- Has language complexity (as defined by a function of the previously mentioned markers) changed over time?

## Method: 
- Topic modeling
- SpaCy language model for imperatives
- Language statistics such as Tf-idf and sentence length
- Compare language use to general language use, e.g.
  - What percentage of words can be found in the 10.000(?) basic Dutch words?; or
  - How does language use compare to Rutte in the past; or
  - How does language use NOS language use

## Dataset Sources:
- https://www.rijksoverheid.nl/onderwerpen/coronavirus-covid-19/coronavirus-beeld-en-video/videos-persconferenties
- https://www.rijksoverheid.nl/onderwerpen/coronavirus-covid-19/documenten?type=Mediatekst&pagina=7
- https://www.rijksoverheid.nl/documenten?trefwoord=Letterlijke+tekst+persconferentie+minister-president+Rutte&startdatum=13-03-2020&einddatum=31-01-2022&onderdeel=Alle+ministeries&type=Alle+documenten
- https://data.rivm.nl/covid-19/
- https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_cumulatief.csv
