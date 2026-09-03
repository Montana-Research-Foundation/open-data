# What is withheld, and why

This bundle releases the aggregate result of every rollout that ran and
the consolidated gate-0 dataset the paper is written from, and withholds
three things.

1. **The task families.** One design in this paper was built as a task
   (the probed one); its generator, its labeled example data, and its
   held-out grading data are not released. A family is a measurement
   instrument for evaluating frontier models, and a released family
   cannot discriminate a model that has seen it. It carries a
   contamination canary and a disclosed development seed range with an
   undisclosed evaluation range.

2. **The raw agent transcripts.** Each rollout's transcript contains the
   task instruction, the sealed-instance behavior, and the method the
   agent submitted, which together would leak the family, and it carries
   the canary GUID. The aggregate outcome of each rollout is released in
   `records/`; the transcript that produced it is not.

3. **The screening spike directories.** Seven designs were retired before
   they were built, on measurements run in per-design spike directories
   that hold candidate generators, oracles, and sealed instances. Those
   are instruments of the same kind as a shipped family: three of the
   designs remain candidates for a later redesign, and releasing the
   spikes would leak them. Every number the paper takes from a spike is
   in `dataset.json` with the file it came from and the method that
   produced it, so the record of what was measured, where, and how is
   preserved with each number, without the instrument itself. The named
   files live in the internal research repository the paper was written
   in and are not public; the bundle's README records the commit of that
   repository the references were verified against.

The recounts `verify.py` performs run from the released aggregates
alone. What is absent cannot reconstruct a family, a transcript, or a
candidate design.
