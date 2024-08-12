# SPARQL Templates

This package contains a collection of templates designed for generating SPARQL queries and questions. I will briefly describe the implemented templates and give examples.

## Template Types and Examples

### N-hop Templates

N-hop templates are used to retrieve information by traversing one or two relationships from given entity to another.

For instance:
```
Polish: Jakie {imię} ma {Ludwig van Beethoven}? - {Ludwig}
English: What is the {first name} of {Ludwig van Beethoven}? - {Ludwig}
```

We traverse the relationship "first_name" from the entity "Ludwig van Beethoven" to the answer entity "Ludwig".

### Reverse N-hop Templates

Reverse N-hop templates require performing a reverse jump.

For example:
```
Polish: Czyim {student} jest {Ferdinand Ries}? - {Ludwig van Beethoven}
English: Whose {student} is {Ferdinand Ries}? - {Ludwig van Beethoven}
```

Here, the question schema is inverted: ? -> student -> Rudolf Johann Habsburg. We traverse the relationship "student" from the answer entity "Rudolf Johann Habsburg" to the entity "Ludwig van Beethoven".

### Templates with Entity Mask

The entity mask is used to enrich the structure of the question: we address the answer without revealing it.

For example:
```
Polish: Jak nazywał się {kompozytor}, którego {przyczyna śmierci} jest {marskość wątroby}, a którego {miejsce śmierci} jest {Wiedeń}? - {Ludwig van Beethoven}
English: What was the name of the {composer} whose {cause of death} is {cirrhosis of the liver}, and whose {place of death} is {Vienna}? - {Ludwig van Beethoven}
```

The answer entity {Ludwig van Beethoven} was masked with the entity {composer}, which we used in our question.

## List of All Templates with Examples

1. **One-Hop Template**:
   - Polish: Jakie {imię} ma {Ludwig van Beethoven}? - {Ludwig}.
   - English: What is the {first name} of {Ludwig van Beethoven}? - {Ludwig}.

2. **One-Hop Template with Entity Mask**:
   - Polish: Jak nazywał się {miasto}, które jest {miejsce śmierci} {Ludwig van Beethoven}? - {Wiedeń}.
   - English: What was the name of the {city}, which is the {place of death} of {Ludwig van Beethoven}? - {Vienna}.

3. **Two-Hop Template**:
   - Polish: Jakie {obywatelstwo} ma {matka} {Ludwig van Beethoven}? - {Niemcy}.
   - English: What is the {country of citizenship} of {Ludwig van Beethoven}'s {mother}? - {Germany}.

4. **Reverse One-Hop Template**:
   - Polish: Czyim {student} jest {Carl Czerny}? - {Ludwig van Beethoven, Antonio Salieri}.
   - English: Whose {student} is {Carl Czerny}? - {Ludwig van Beethoven, Antonio Salieri}.

5. **Reverse One-Hop Template with Entity Mask**:
   - Polish: Jak nazywał się {kompozytor}, którego {rodzeństwo} jest {Kaspar Anton Karl van Beethoven}? - {Ludwig van Beethoven}.
   - English: What was the name of the {composer} whose {sibling} is {Kaspar Anton Karl van Beethoven}? - {Ludwig van Beethoven}.

6. **Reverse Two-Hop Template**:
   - Polish: Czyim {student} jest {Ferdinand Ries}, a {nauczyciel} jest {Joseph Haydn}? - {Ludwig van Beethoven}.
   - English: Whose {student} is {Ferdinand Ries}, and {teacher} is {Joseph Haydn}? - {Ludwig van Beethoven}.

7. **Reverse Two-Hop Template with Entity Mask**:
   - Polish: Jak nazywał się {kompozytor}, którego {przyczyna śmierci} jest {marskość wątroby}, a którego {miejsce śmierci} jest {Wiedeń}? - {Ludwig van Beethoven}.
   - English: What was the name of the {composer} whose {cause of death} is {cirrhosis of the liver}, and whose {place of death} is {Vienna}? - {Ludwig van Beethoven}.

8. **One-Hop and Reverse One-Hop Template with Entity Mask (mixed template)**:
   - Polish: Jakie {miejsce urodzenia} ma {kompozytor}, którego {ojcem} jest {Johann van Beethoven}? - {Bonn}.
   - English: What is the {place of birth} of the {composer} whose {father} is {Johann van Beethoven}? - {Bonn}.

