
## weighting calcaulations

- sum all card weights
- generate random number between 0 and card weights
- sort cards by score (desc) and last_seen (asc)
- traverse cards, summing up the scores until the random number has been passed
- if we get to a card with score 0, return that card

- successful match = weight -= 1
- failed match = weight = 100