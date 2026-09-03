# What is withheld, and why

This bundle releases the aggregate per-rollout results and a
self-contained verification script, and withholds two things:

1. **The task families** (the generators, the labeled example data, the
   held-out grading data). The families are a measurement instrument for
   evaluating frontier models; a released family cannot discriminate a
   model that has seen it. They carry a contamination canary and a
   disclosed development seed range with an undisclosed evaluation range.
   Releasing them would defeat their purpose.

2. **The raw agent transcripts.** Each rollout's transcript contains the
   task instruction, the labeled examples, and the agent's induced rule,
   which together would leak the withheld family, and it carries the
   canary GUID. The aggregate outcome of each rollout — its reward,
   whether it passed, and its token counts — is released in `records/`;
   the transcript that produced it is not.

The per-cell statistics named in this bundle's README recompute from the
aggregate per-rollout outcomes alone; statistics the paper computes from
the transcripts or the held-out data do not, and the README's notes say
which is which where the distinction matters. What is absent cannot
reconstruct the family or the transcript.
