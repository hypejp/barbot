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
The converted database contains 38,388 entries; the referenced FreeDict
release lists 38,419 headwords. The exact source release used for the
conversion has not yet been independently verified.

The converted SQLite database is not included in this Git repository.

The dictionary data and the barbot source code are separate works.
The dictionary data remains subject to its original copyright and
CC BY-SA 3.0 license terms.
