conlang_generator

features that I need
    1. phonotactics
    2. the 1000 vocab
    3. constraints
    4. repair strategies.
I can read through the historicla linguistics book and implement features as I go

so we want things to be linear, and then have the syllabification algorithm change over time.
if syllabification fails, we repair
for starters we can use the SSP as our only constraint. if its impossible to syllabify the word and include enough nucleic material without violating SSP, we implement either epenthesis or deletion. we can add strategies for how to epenthesize later.