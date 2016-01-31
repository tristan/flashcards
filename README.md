
## weighting calcaulations

- initial weight is `1048576` so that it can be divided by `2` `20` times.

- sum all card weights
- generate random number between 0 and card weights
- sort cards by score (desc) and last_seen (asc)
- traverse cards, summing up the scores until the random number has been passed
- if we get to a card with score 0, return that card

- successful match = weight /= 2
- failed match = weight = initial

## database migrations

the `migrations` directory contains `.sql` files to be run to migrate from the
commit hash contained in the filename to anything newer