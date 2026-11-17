## Resolved - GO, 3 rounds, 2026-11-16T20:25:13Z

## Reviewer round 3 - Grok, 2026-11-16T20:25:13Z
**Verdict: GO**

R2.1 is in the plan body. Section 4 no longer builds or tests F8 after this GO. R2.2 is in the F6 row: `/mnt` on the Deck is unverified.

This GO closes the review. It does not start F6 or F8. F2 still does not change `layout.py` unless a new fixture fails first. No code has been changed.

## Reviewer round 2 - Grok, 2026-11-16T20:23:17Z
**Verdict: GO WITH CHANGES**

The withdrawals are in the plan body. F1, F3, F4, F5, F7 and the font change are gone. F2 waits on a failing fixture. F6 stays unbuilt until Ross names it.

### R2.1 Section 4 still builds F8  [BLOCKING]
The F8 row says the mode change waits until Ross names it. Section 4 item 3, under "after GO", adds the test that the mode is preserved. That is the change. Delete item 3, or say it does not run until Ross names F8. A GO is not that name.

### R2.2 /mnt on SteamOS is not checked  [SHOULD]
The F6 row says `/mnt` exists on Arch and SteamOS. That is not checked on his Deck. Say "if `/mnt` exists". Do not record it as a fact.

### What would change the verdict
Apply R2.1. R2.2 can be applied in the same edit. Then this review can close with GO. GO means the plan stands. It does not start F6 or F8, and F2 still does not change `layout.py` unless the new fixture fails first.

## Author response round 2 - Gemini, 2026-11-16T20:24:30Z

### R2.1 Section 4 still builds F8
**Accepted** - Removed item 3 from Section 4 (moved the `F8` `st_mode` test note out of the immediate post-GO verification list and marked `F8` verification as running only when Ross names `F8`).

### R2.2 /mnt on SteamOS is not checked
**Accepted** - Updated `F6` in Section 2 to say "if `/mnt` exists on Arch/SteamOS" (unverified on this Deck) rather than stating it as a fact.

### Plan changes this round
- Removed Section 4 item 3 (`F8` test) from the post-GO list so `F8` is not built or tested until Ross names it.
- Updated `F6` in Section 2 to mark `/mnt` on Arch/SteamOS as unverified ("if `/mnt` exists").

### Status
Applied BLOCKING changes; awaiting close

## Reviewer round 1 - Grok, 2026-11-16T20:20:00Z
**Verdict: NO-GO**

### R1.1 D1, keep the whole-list refusal  [BLOCKING]
Option B. `plan_text` refuses the whole write when a row cannot be written. `tests/test_layout.py` `test_script_row_blocks_the_whole_list` locks that, and the plan says the whole list is written or nothing is. Option A would write the layout and leave Files out. Ross has not chosen A. The click that did nothing was a disabled button. On the ThinkPad that button now stays clickable and shows the reason. Files still blocks, on purpose.

### R1.2 D2, keep group ids 0, 7 and 9  [BLOCKING]
Leave `SLOTS` as they are. Stage 1 is still open. His Deck export has not been read. On the stock template copied on this ThinkPad, group 9 is the active D-pad. A search that picks "the" group can bind the wrong one. Do not change the ids in this round.

### R1.3 The bindings parser  [SHOULD]
`_binding_spans` ends the block at the first `}`. In `template\desktop_neptune.vdf` there are 58 `"bindings"` blocks and none of them contain a nested brace, checked 16 Nov 2026. The first `}` is the close on that file. The activator search can leave its input and match a later one. That is not shown by a failing test here. Add a fixture that would write the wrong input before changing the parser. A missing closing quote is a different bug, and it is already parked. A brace walker does not fix it.

### R1.4 Do not redraw the Deck screen  [BLOCKING]
F5 adds scrollbars and a scrolling detail form. Ruling S19: do not redraw `deck_app.py` unless Ross names a change. He has not said the fields are clipped. No scrollbar in this round.

### R1.5 Folder start, not a new font  [SHOULD]
`choose_folder` does open `/mnt` when that directory exists (`deck_app.py`). That is right on the ThinkPad. Whether `/mnt` exists on his Deck is unverified. A Deck default of the Steam Controller Configs folder is reasonable. Do not switch the face to Noto Sans. That face was not checked on his Deck. The accepted drawing uses Segoe UI. Tk already falls back when a face is missing.

### R1.6 Whole-file token check  [COULD]
`part not in text` searches the whole file. The slot check still runs afterwards. Leave it unless a test shows a token accepted from the wrong place.

### R1.7 shortcuts.json  [COULD]
`save` writes the file directly, and `load` does not catch bad JSON. Not this round. Do not rewrite his shortcut list as part of a parser change.

### R1.8 Desktop file mode, before any publish  [SHOULD]
`_replace` writes a new file and replaces. A new file takes the process mask, so a `Shortcuts.desktop` that was executable can come back without that bit. No repo has been published, so this has not happened. Preserve the existing mode before the first publish. Do not bundle it with F1 to F5.

### R1.9 The test run  [SHOULD]
The plan runs tests in WSL distro `devbox`. I have not re-run them tonight. The last run in this project was 38 passed in devbox on 15 Nov, before this file. Windows `WinError 1314` on symlinks and `chmod` not sticking are the Windows runner. They are not Deck defects.

### What would change the verdict
Withdraw option A, leave the group ids, and leave the Deck screen as drawn. A parser change waits on a failing fixture. The folder start and the desktop-file mode can be separate small changes when Ross names them.

## Author response round 1 - Gemini, 2026-11-16T20:22:30Z

### R1.1 D1, keep the whole-list refusal
**Accepted** - Withdrew Option A (`F1`) from the plan body. `plan_text` keeps the whole-list refusal and `test_script_row_blocks_the_whole_list` stays unchanged.

### R1.2 D2, keep group ids 0, 7 and 9
**Accepted** - Withdrew `F4` from the plan body. `SLOTS` keeps group IDs `"0"`, `"7"`, and `"9"` while Stage 1 is open.

### R1.3 The bindings parser
**Accepted** - Updated `F2` in the plan body so any parser change is gated on adding a failing fixture/unit test first (showing `replace_bindings` matching a later input's activator when the target input lacks that activator), and removed the nested-brace / `"group"`-split parts since `template\desktop_neptune.vdf` has 58 `"bindings"` blocks with no nested braces.

### R1.4 Do not redraw the Deck screen
**Accepted** - Withdrew `F5` from the plan body per ruling S19. No scrollbars or detail-form redraw in `deck_app.py`.

### R1.5 Folder start, not a new font
**Accepted** - Removed the `FONT` change from `F6` in the plan body (`Segoe UI` stays). Kept only the `choose_folder` start-path fix (Steam Controller Configs if present, `/mnt` if `/mnt/c` exists, else `Path.home()`) as a separate small change when Ross names it.

### R1.6 Whole-file token check
**Accepted** - Withdrew `F3` from the plan body. `part not in text` stays as-is unless a test shows a false match.

### R1.7 shortcuts.json
**Accepted** - Withdrew `F7` from the plan body. `library.py` is left untouched in this round.

### R1.8 Desktop file mode, before any publish
**Accepted** - Kept `F8` (`update._replace` preserving existing file mode) as a separate small change before any repo publish, when Ross names it, not bundled with parser work.

### R1.9 The test run
**Accepted** - Updated section 1 of the plan body to note that the Windows `WinError 1314` / `chmod` results are Windows runner artefacts and that verification runs in `wsl -d devbox -- python3 -m unittest discover -s tests`.

### Plan changes this round
- Removed `F1` (Option A), `F3`, `F4` (`SLOTS` group IDs), `F5` (`deck_app.py` scrollbars/redraw), `F7` (`library.py`), and the `FONT` change from `F6`.
- Scoped `F2` to wait for a failing fixture/unit test showing cross-input activator bleed before touching `layout.py`.
- Separated `F6` (`choose_folder` start path) and `F8` (`update._replace` file mode) as standalone small changes when Ross names them.
- Updated section 1 and section 4 to note Windows runner artefacts vs `wsl -d devbox`.

### Status
Awaiting reviewer round 2

---
# Preamble

**Purpose:** Scoped fixes for `steam-deck-dolphin` (`layout.py`, `deck_app.py`, `update.py`), updated after Grok's round 1 review.

**Questions for the reviewer:**
1. With `F1`, `F3`, `F4`, `F5`, `F7`, and the `FONT` change withdrawn, does the scoped plan (`F2` gated on a failing fixture, plus `F6` folder start and `F8` file mode as separate small changes when Ross names them) earn `GO`?

**Verdict scale:** `GO` | `GO WITH CHANGES` | `NO-GO` | `QUESTIONS`

---

# Plan body: Proposed fixes for `steam-deck-dolphin`

## 1. Current state (checked)

- **Windows Python 3.14 test run (`python -m unittest discover -s tests -v`):** 33 passed, 4 errored (`WinError 1314` on `os.symlink`), 1 failed (`test_unwritable_folder_leaves_the_earlier_backup`, `chmod(0o555)` is POSIX-only). These 5 are Windows runner artefacts, not Deck defects.
- **WSL `devbox` test run:** unverified in this session (blocked by sandbox `Wsl/E_ACCESSDENIED`); last known run in `devbox` was 38 passed on 15 Nov 2026 (per reviewer round 1).

## 2. Proposed fixes

| ID | File / Symbol | Problem | Proposed fix |
|---|---|---|---|
| F2 | `layout.py` (`replace_bindings`, `_first_binding`) | `chunk.find('"%s"' % activator, input_at)` is not bounded to `input_name`'s `{ ... }` block, so a missing activator can match a later input's activator in the same group. | First add a failing fixture/unit test where the target input lacks `activator` and a later input in the same group has it. Then bound `_first_binding` and `replace_bindings` to the `input_name` `{ ... }` block. |
| F6 | `deck_app.py` (`choose_folder`) | `choose_folder` defaults to `/mnt` whenever `/mnt` exists (whether `/mnt` exists on his Arch/SteamOS Deck is unverified). | Separate small change when Ross names it: start in `~/.local/share/Steam/steamapps/common/Steam Controller Configs` if it exists, else `/mnt` when `/mnt/c` exists (WSL), else `str(Path.home())`. Keep `FONT = "Segoe UI"`. |
| F8 | `update.py` (`_replace`) | `os.replace` over a fresh `.updating` file resets file mode to `0644`, which can strip `+x` from `Shortcuts.desktop` on KDE/SteamOS. | Separate small change before any publish, when Ross names it: preserve existing `st_mode` on `_replace` when the target already exists. |

## 3. Open decisions

- None remaining.

## 4. Verification plan (after GO)

1. Run `wsl -d devbox -- python3 -m unittest discover -s tests -v` (all tests including symlink and `chmod` tests).
2. For `F2`, add the cross-input fixture first; only change `layout.py` if it fails, then confirm it passes.
3. Do not build or test `F6` or `F8` until Ross names them; do not touch live Steam folders or the Deck during this round.

---

# Changelog

| Round | Change | Reason |
|---|---|---|
| 0 | Initial draft published | Ready for Grok round 1 review |
| 1 | Withdrew `F1`, `F3`, `F4`, `F5`, `F7`, and `FONT` change; gated `F2` on a failing fixture; separated `F6` (folder start) and `F8` (file mode) | Addressed Grok round 1 `NO-GO` (`R1.1`–`R1.9`) |
| 2 | Removed `F8` test from Section 4 post-GO list; marked `/mnt` on Arch/SteamOS as unverified in `F6` | Addressed Grok round 2 `GO WITH CHANGES` (`R2.1`, `R2.2`) |
