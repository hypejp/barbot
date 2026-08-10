# BARBOT Design Notes

## Purpose

barbot supports the atmosphere of `##bar-jp`, a quiet IRC bar on Libera.Chat.
It is not the main character of the channel. The people in the channel are.

## Core principles

- Humans are the main characters.
- If unsure, stay silent.
- Do not interrupt an active conversation.
- Prefer a small, natural response over unnecessary chatter.
- Atmosphere is more important than feature count.
- barbot should feel present without demanding attention.

## Global audience

`##bar-jp` has members around the world.

Therefore barbot must not assume:

- a local time of day;
- morning, afternoon, evening, or night;
- a season;
- local weather.

Messages should make sense regardless of where or when a member is connected.

## Welcome behavior

Welcome messages are intentionally conservative.

- Only a nick that has actually JOINed `##bar-jp` may become a Welcome candidate.
- A Welcome candidate expires 60 seconds after JOIN.
- `hype` and `barbot` are never Welcome candidates.
- A nick that did not JOIN must not receive a Welcome merely because it speaks.
- After barbot sends a Welcome, that nick is removed from the candidate set.
- The existing low Welcome probability is retained so barbot stays quiet.

## Development policy

- Make one behavioral change at a time.
- Review the design before implementation.
- Keep production downtime short.
- Run a Python syntax check before deployment.
- Commit each meaningful change to Git before or immediately after deployment.
- Prefer reversible changes and keep production backups.
