# barbot

A quiet IRC bar bot for ##bar-jp.

## Overview

barbot is a small IRC bot designed for the Libera.Chat channel `##bar-jp`.

Its goal is not to dominate conversations, but to help create the atmosphere of a quiet bar where people from around the world can relax and chat.

## Philosophy

- Humans are the main characters.
- If unsure, stay silent.
- No assumptions about time zones or seasons.
- Atmosphere is more important than features.

## Features

barbot provides small, optional features for IRC conversations:

- `!ping` — Check whether barbot is responding.
- `!dic [word]` — Look up English and Japanese words.
- `!menu` / `!drink [category]` — Explore the bar's drink menu.
- `!movie [title]` — Look up movie information.
- `!citypop` — Pick a random track from the city pop playlist.
- `!aor` — Pick a random track from the AOR playlist.
- `!loc [City, Country]` — Set your location for weather and local time commands.
- `!w [location]` — Check the weather.
- `!wt [location]` — Check the local time.
- `!remind` — Set a reminder.
- `!quote` — Manage and display quotes.
- `!seen [nick]` — Check when someone was last seen.
- `!help` — Display the command list.

Music commands also provide YouTube search links.

## Technical Details

- Written in Python.
- Runs on a Debian Linux VPS.
- Connects to Libera.Chat.
- Uses environment variables for external API keys.
- Includes automated unit tests.
- Developed and maintained by hype.

## Source Code and Licensing

The source code is publicly viewable, but no open-source license
has been granted at this time.

All rights are reserved unless otherwise stated.
The dictionary data described below has its own separate license.

## Status

🚧 Active development

## Author

hype

GitHub: https://github.com/hypejp/barbot

## Dictionary Data

barbot uses English-to-Japanese dictionary data from the FreeDict project.

### Source and Attribution

- Dictionary: English-日本語 (にほんご) FreeDict+WikDict dictionary (`eng-jpn`)
- Reference source release: 2025.11.23
- Maintainer and publisher: Karl Bartel
- Project: FreeDict (https://freedict.org/)
- Dictionary generation: WikDict (http://www.wikdict.com/)
- Original data: Wiktionary (https://www.wiktionary.org/), via DBnary
- License: Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)
- License URL: https://creativecommons.org/licenses/by-sa/3.0/

### Modifications and Distribution

The dictionary data has been converted to SQLite format for use by barbot.
The converted database is based on FreeDict eng-jpn release 2025.11.23.

The original TEI source was verified against the official FreeDict
2025.11.23 source archive using SHA-256 checksums.

The converted SQLite database contains 38,388 entries and 67,820
Japanese translations. All 67,820 translations were verified against
the official source release after whitespace normalization.

The official source contains 38,419 entries and 67,822 translations.
Entries without usable translations were excluded during conversion.

The converted SQLite database is not included in this Git repository.

The dictionary data and the barbot source code are separate works.
The dictionary data remains subject to its original copyright and
CC BY-SA 3.0 license terms.
