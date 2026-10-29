# Importance score (POC, tunable)

Owner, 2026-10-28: "score sound good and note down so we can tune it later."

| Score | Class | Set by | Put back after a compaction |
|---|---|---|---|
| 3 | W wall | "never", "always", "must", "wall", "once again", "why you not", "follow the rule", "report to me first" | always, word for word, never dropped for budget |
| 2 | D decision | "use ...", "switch to", "keep", "drop", "hold", "don't", an answer like "1" or "yes" | while open; a newer decision on the same thing replaces it |
| 1 | A ask | "add", "make", "run", "show", "fix", "I want", "I need", "please", and every question | while open; dropped first when over budget |
| 0 | closed | the agent runs `nv.py done ID`, the Stop hook (a question from the last prompt, once answered), or replaced (`>L9`) | no; it stays in the ledger file |

Knobs in `score.json`:

- `noise`: lines dropped before scoring (build logs, table rows, "continue"). Text inside `<pasted_content>` is dropped too.
- `question`: a question is always an ask, never a wall.
- `wall`, `decision`, `ask`: the patterns, checked in that order.
- `quote_min_words` (6), `said_max_chars` (200000): a clause of 6+ words found in my own recent replies is the owner quoting me, not the owner's words.
- The Stop hook closes only questions. A job ask stays open until the agent runs `nv.py done ID`: a wrong close would hide an ask the summary may also drop.
- `repeat_overlap` (0.6): how alike two lines must be to count as said again. Only a wall said again replaces the older wall; an ask said again stays an ask.
- `supersede_overlap` (0.5): how alike a new decision must be to replace an old one.
- `max_words` (25): a longer sentence is cut with "...". The full text stays in the transcript.
- `walls_every_n_prompts` (5): the walls are repeated into context every N messages, against mid-task drift.
- `restore_max_tokens` (600): the budget for the block put back after a compaction.
- `recall_words` (12): each decision and ask line in that block is cut to 12 words; walls stay word for word. The ledger keeps up to `max_words`.
- A new job ask is echoed with `(when finished: nv.py done ID; if you changed what was asked, say so and leave it open)`, so the agent knows how to close it. Owner, 2026-10-29: "if you changed what was asked, say so and leave it open".
- `tail_ref`: a tail under 3 words that points back ("run it") joins the clause before it, so it is not a second ask.

The agent may raise a score (`nv.py pin`) and never lowers one. The owner fixes anything by editing `.novibes/ledger.txt`.

Keep `.novibes/` out of git: it holds the owner's words and the agent's recent replies (`said.txt`, up to `said_max_chars`). A `|` or `\` in the owner's words is stored escaped (`\|`, `\\`) and read back as it was said.

## Tuning log

2026-10-29, from the real session replay (13 sessions, 76 compactions):

| change | why (measured) |
|---|---|
| dropped "again" and "rule" from walls; questions are asks | "Try again", "what is the cheek-weld rule?" were walls |
| noise lines and `<pasted_content>` dropped; quotes of my replies dropped | compiler logs and my own text pasted back were walls |
| a repeated ask no longer becomes a wall | "show me the numbers" said twice was a wall |
| Stop hook closes asks | nothing closed, so 213 items piled up |
| Stop hook closes questions only; jobs close by `nv.py done` | word-match closes: about 10 of 20 right, 4 clearly wrong (owner chose 4b) |
| recall lines cut to 12 words | at 600 tokens more lost items fit: see POC-REPORT.md (owner chose option 1) |

Wall precision on a fresh 20-wall sample: about 5 of 20 before, about 11 of 20 after. Pasted text with no tag is the main miss left.
