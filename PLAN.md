# Dolphin folder buttons: a file the USB stick carries

A small app builds the Dolphin folder change on screen, backs up the current desktop file, and writes that change into the file. On this ThinkPad the app runs in a WSL window. You copy the file onto the Deck with a USB stick. The ThinkPad window does not talk to the Deck, to Steam, or to the network. On 15 Nov 2026 you also asked for the app to be installable on the Deck itself, and for that Deck copy to update itself from GitHub (S21). That part is under "On the Steam Deck". You said "Lets begin" the same day. The first step is the two screen readings.

Proposed tier: **small change** (you assign the tier). One reviewer after the app exists. The write is confined to the four D-pad bindings. Say if you want three, since the file you copy later replaces the Deck's desktop layout.

No pace table exists for this project, so no hours are promised. The first stage records the minutes it actually takes.

A plan reviewer was not started. Say if you want one before any build.

## Saying yes to this plan is a yes to these, by name

1. You copy the Deck's current `controller_neptune.vdf` into a folder first. The app copies that file into a new `backup-YYYYMMDD-HHMMSS` folder, checks the copy matches, and only then writes the changed `controller_neptune.vdf` and `where-to-put-this.txt`. No current file, or a failed backup, means it writes nothing.
2. The window is where you construct the change: four D-pad directions, each a key and a sub command. They start as the working layout. Hold stays B. The write changes only those bindings inside the current file. Every other byte stays. The app does not invent binding text. It uses the text found in your export.
3. The whole app runs in a WSL window on distro `devbox`. Tests run there too. No git remote unless you ask.
4. Project folder, once you approve: `C:\Users\rossm\OneDrive\Files\Coding Resources\steam-deck-dolphin\`.
5. The Deck copy is a later stage that you do by hand. The ThinkPad cannot pass that stage.
6. After you approve, the project-map stages file and summary are created from this plan. They are not created before that.
7. The window is the outline under "The window". One tkinter window, shown by WSLg. Light and dark. No second screen.
8. Tests run in WSL distro `devbox` with `python3 -m unittest`. They use a temp folder. They do not open the window and they do not touch a USB stick.
9. Install `python3-tk` in `devbox` (`sudo apt install python3-tk`). It is not installed now. The package candidate checked 14 Nov 2026 is `3.12.3-0ubuntu1`. Nothing else is installed.

## What done looks like

You copy the Deck's current `controller_neptune.vdf` onto the stick. On the window you set the four directions. They start as hold B with up parent, down open, left back, right forward. The app backs up the current file, checks the copy, then writes those four bindings into it. On the Deck, with Steam fully quit, you replace the live file with the one from the stick. The backup stays on the stick. You start Steam. In Dolphin the change you set is what the D-pad does while B is held, and the trackpad still moves the mouse. To undo, you copy the backup back.

## Rulings

| ID | Ross's words | What it closes |
|---|---|---|
| S1 | "How about we do a project on this a small app that essentially write to a file that we transfer by usb. Lets plan it out" (14 Nov 2026) | Plan only until this plan is approved. The app writes a file. Transfer is USB. |
| S2 | "Awesome working great now" (14 Nov 2026), after hold B with B emptied. Recorded in `Downloads\Steam-Deck-Dolphin-folder-buttons.md` | The layout is that note. Hold B, D-pad up/down/left/right = parent, open, back, forward. D-pad alone moves the highlight. A is Enter. X is the keyboard. Menu (three lines) stays Escape. |
| S3 | "Done B need release press or regular press?" (14 Nov 2026) | Neither. B has no command at all. |
| S4 | "Fine lets switch x to a as x it keyboard a is already assosciated with file movement" (14 Nov 2026), then A was dropped as the hold because letting go of A opened the folder | X stays the keyboard. A stays Enter. The hold is B. |
| S5 | "Cant see mode shift" and "the instructions are shit" (14 Nov 2026) | Any words he follows use the real labels: Steam menu, Settings, Controller, Desktop Layout. The long click path stays in the text file, not on the window. |
| S6 | "No I want an edit, that would be for the app to backup the existing files relating to the chnages to make" (14 Nov 2026) | Before the new layout is written, the app backs up each file that write would replace, and checks the copy. It does not write if that backup is missing or wrong. |
| S7 | "How about wsl to test it, in addition you havent mentioned the ui I could use to construct the changes" (14 Nov 2026) | Tests run in WSL. The window is where the four D-pad bindings are set before the file is written. |
| S8 | "And what is the feasibility of running the whole app in a wsl window" (14 Nov 2026) | The app runs in a WSL window. The feasibility check is the section below. |
| S9 | "Use a template for it for the moment, I will get the real thing across later" (14 Nov 2026) | Until the Deck export arrives, the stand-in is the stock desktop file already on this ThinkPad. Stage 1 does not pass on that file. |
| S10 | "Okay too simplistic, do you think I want this for one thing?" (14 Nov 2026) | The first drawing is rejected. The window is not a form for this one Dolphin change. |
| S11 | Chose "A list of binding changes" (14 Nov 2026) | Each row is a control, a key and a sub. The Dolphin four start in the list. He adds, edits or removes rows. Write applies the whole list after a backup. |
| S12 | "Not just for one offs, but a way for me to creat loads of controls and shortcuts to make it really useful and to also be able to remember what theya re" (14 Nov 2026) | The list is a saved library. Each shortcut has a name he writes. The names stay on this PC. He can keep adding them. |
| S13 | "Better but I want a bunch of dropdown options and operators that you can derive from the steam deck. So thinks like launch app x keyboard shortcut y. Think bigger, more practical" (14 Nov 2026) | Each shortcut picks an action from the Deck layout files, then the fields for that action. Keyboard shortcut is a key plus an optional second key. |
| S14 | "Ah but sweetie im sure we can tie a hotkey to a script come on be smarter" (14 Nov 2026) | Run script is an action. The control sends a hotkey. That hotkey runs a command or a script. Launching an app is that command. |
| S15 | "Better, can you make the ui a little nicer, so it should have a layer. What the addition is (name) and whether it is a shortcut or a system command etc. Click it takes you to the breakdown that you currently have. Also just improve the ui in general" (14 Nov 2026) | The first screen is a list: name and kind. A click opens the breakdown for that one shortcut. |
| S16 | "Also I want to get it installable on the steam deck itself, the arch linux interface needs to be steam deck friendly and simple, write this into the .md file" (15 Nov 2026) | The app has to be installable on the Steam Deck. The screen there is for Arch Linux, simple, and Steam Deck friendly. |
| S17 | "A" (15 Nov 2026), choosing the saved list over the four folder buttons only | The Deck screen is the saved list: name and kind, and a click opens that shortcut. Same list as the ThinkPad window. |
| S18 | "I would like the app to be able to summon the keyboard when required" (15 Nov 2026) | On the Deck, the app summons the keyboard when Name or Command is tapped. Menus do not. The code waits for the Deck build. How Desktop Mode is asked to show its keyboard has not been checked. |
| S19 | "Done looks great so far" (15 Nov 2026), after opening the Deck window | The Deck screen in `deck_app.py` stands. Do not redraw it unless he names a change. The keyboard summon and the install are still not done. |
| S20 | "Umm, I want an app that I can use, not a command to run" (15 Nov 2026) | On the Deck he opens Shortcuts. He does not type a command. The launcher is `Shortcuts.desktop`, in the same folder as `deck_app.py`. |
| S21 | "Also update functionality should ota via github" (15 Nov 2026) | Shortcuts checks a public GitHub repo when it opens. Update replaces `deck_app.py`, `layout.py`, `library.py`, `update.py` and `Shortcuts.desktop`. `shortcuts.json` and the controller file stay. He opens Shortcuts again afterwards. No repo is named yet. No new package. |

## Left out

- Building a VDF from scratch. A made-up file can wipe the trackpad, mouse, grips and keyboard. Unverified against his file: the exact tokens inside it. Those get listed only after his export is read.
- A general button editor, Guide Button Chord Layout, or any change to A or X. The window edits the four mode-shift directions only. Hold stays B.
- The app mounting the Deck, quitting Steam, or turning cloud sync off. The click path for cloud sync has not been checked, so the note will not invent one.
- Installing the app on the Deck from this ThinkPad. A Deck install is a later part, under "On the Steam Deck". It is not started. The ThinkPad app still does not push a file onto the Deck.
- Backing up the rest of Steam. The backup is only the files this change replaces. The known file is `controller_neptune.vdf` in the `413080` folder. Stage 1 adds a neighbour only if that read shows the change replaces it too. `configset_controller_neptune.vdf` sits in the parent `config` folder and is not in the list until that read says the change touches it.

## How the file is made

App id **413080** is Steam's desktop layout. On a Deck the active file is:

`/home/deck/.local/share/Steam/steamapps/common/Steam Controller Configs/<the one numbered folder>/config/413080/controller_neptune.vdf`

That path is from Valve's layout and from Steam discussions (tintingaroo, 6 Dec 2025, for Layout Details). It has not been opened on this Deck. Desktop Layout, the gear, Layout Details is how you confirm the live path. The account number is whatever single numbered folder is there. The app does not need it.

Controller configs can also come back from Steam's cloud (app 241100). If the old buttons return after a good copy, cloud sync put the old file back. Steam left running will also overwrite a file you just copied. Both stay as warnings in the text file.

There is no supported API to set the desktop layout. Export, then copy, is the method.

## Backup

The app cannot see the Deck. The current file is the one you copied into the folder you pick.

It backs up only the files this change would replace. The known one is `controller_neptune.vdf`. Each goes into a new folder named `backup-YYYYMMDD-HHMMSS` in that same folder. The copy is checked against the original before the new layout is written. An older backup is never overwritten and never deleted.

If that file is not in the folder, the app writes nothing. If the backup does not match, the app writes nothing and leaves the original in place.

The new file is the current file with the four on-screen bindings written in. Every other byte stays. The words for those bindings come from the export read in stage 1. A key with no text from that read cannot be written. A file with no mode-shift slots cannot be written. The app does not add a mode-shift group. Stage 1 says whether a stock file even has those slots. Adding them would be a later stage you would have to name.

## Cases

The app writes a file you will later put over a live config. Ross approves this table with the plan. Tests are written from it before the window code.

| Case | What the app must do |
|---|---|
| No folder picked | Write nothing. Status: pick a folder. |
| Seed missing, empty, or not the exported desktop file | Write nothing. Say the seed is missing. Do not invent a layout. |
| Seed lacks the hold-B mode shift or any of the four Dolphin directions, once those strings are known from his file | Write nothing. Name what is missing. |
| Folder not writable, or the stick is pulled | Write nothing with the final name. Say it failed. Leave any earlier backup folder as it was. |
| No `controller_neptune.vdf` in the folder | Write nothing. Say to copy the Deck's current file into the folder first. |
| The file has no mode-shift slots | Write nothing. Say this file has no mode shift to edit. |
| A key or sub on screen has no binding text from the export | Write nothing. Name the key. |
| The four on-screen bindings are already in the file | Say it is already this change. Do not make a backup. Do not write. |
| Those bindings differ, and the slots exist | Copy the file to `backup-YYYYMMDD-HHMMSS\controller_neptune.vdf`, check the copy matches byte for byte, then write only those four bindings. Every other byte stays. An older backup folder is left as it was. |
| The backup copy is missing or does not match | Write nothing. The original file stays. Remove only the incomplete new backup file. |
| Write of the new file is interrupted | The new bytes go to a temporary name, and `controller_neptune.vdf` keeps the old bytes until the temporary file matches the seed. If the replace fails, put the old bytes back from the backup just taken, then stop. |
| A second run, after a successful write, screen unchanged | The file now has the on-screen bindings, so this is the "already this change" case. The first backup is still the old bytes. |
| Any path outside the folder he picked | Never written. The only new names are the backup folder, `controller_neptune.vdf`, and `where-to-put-this.txt`. |

The placement note is the text below. The only part filled in at the time is the backup folder's name. Nothing in it comes from inside the VDF.

## The window

One window. This is where you construct the change. It is a tkinter window from distro `devbox`, drawn on the Windows desktop by WSLg. The font, buttons and dropdowns are tkinter's. Light and dark are both drawn. The window follows the Windows app theme by reading `AppsUseLightTheme`. No custom skin. The measured drawing, light and dark, is approved before any window code. Measurements are set on that drawing. This outline is the structure and the states.

Choose folder opens tkinter's folder picker, starting at `/mnt`, so a stick Windows has given a letter shows up as `/mnt/e` or whichever letter it was given.

Title bar: Folder buttons

Top to bottom, equal left and right margins:

1. One line: "Backs up the current file, then writes this change."
2. A row. Label "Folder". The path, one line, middle ellipsis when it is long. Button "Choose folder" on the same row, tops level with the path.
3. Section heading "Change", then one line: "Hold B, then the D-pad."
4. A table of four rows. Column headings: Direction, Key, Sub. Each Key and each Sub is a dropdown.

| Direction | Key starts as | Sub starts as |
|---|---|---|
| Up | Up Arrow | Left Alt |
| Down | Enter | none |
| Left | Left Arrow | Left Alt |
| Right | Right Arrow | Left Alt |

Key choices: Up Arrow, Down Arrow, Left Arrow, Right Arrow, Enter. Sub choices: Left Alt, none. Hold is the line in step 3. It is not a dropdown.

5. Button "Write", left edge level with the path.
6. One status line, left edge level with Write. It wraps to two lines, then stops.

No menus, no settings, no second window. The placement steps stay in `where-to-put-this.txt`.

Picking a folder fills the path and sets the status from that file and from the four dropdowns. Changing a dropdown updates the status the same way. Write stays off until a current file has mode-shift slots and the four dropdowns differ from what is in the file.

| What is true | Write | Status |
|---|---|---|
| Export was not read, so there is no binding text | Off | Seed is missing. |
| Export failed the layout check | Off | Names the missing part. |
| No folder chosen | Off | Empty. |
| Folder chosen, no current file | Off | No current file in this folder. |
| File has no mode-shift slots | Off | This file has no mode shift to edit. |
| A chosen key or sub has no binding text | Off | No binding text for that key. |
| The file already has these four bindings | Off | Already this change. Nothing to write. |
| The file differs, and the slots exist | On | Current file found. Write will back it up first. |
| Write succeeded | Off | Backed up to backup-YYYYMMDD-HHMMSS, then wrote this change. |
| Backup did not match | On | Backup failed. The current file was left as it was. |
| Folder not writable, or the stick was pulled | On | Could not write. The current file was left as it was. |
| New file could not be put in place | On | Could not write the layout. The previous file is in backup-YYYYMMDD-HHMMSS. |

While Write is running, the dropdowns and both buttons are off and the status reads "Backing up the current file." The window stays open until you close it. Closing it does not delete a backup.

## The text file, `where-to-put-this.txt`

```
The previous file is in backup-YYYYMMDD-HHMMSS, next to this note.
To put it back: quit Steam, then copy that backup over controller_neptune.vdf
in the Deck folder below. Do not copy the backup folder onto the Deck unless you are undoing this.

Quit Steam completely before you copy the new file. If Steam is open it will overwrite the file.

1. The file on the Deck is in the one numbered folder here:
   /home/deck/.local/share/Steam/steamapps/common/Steam Controller Configs/<that folder>/config/413080/controller_neptune.vdf

2. Copy this stick's controller_neptune.vdf over that file.

3. Start Steam. Open Dolphin.
   Hold B and press the D-pad. The four lines below are whatever the window wrote:
   Up, Down, Left, Right, each with its key and its sub.
   The D-pad alone still moves the highlight. A still opens. X is still the keyboard.

The live path is also under Desktop Layout, the gear, Layout Details.

If the old buttons come back, Steam's controller-config cloud put the old file back.
The click path for turning that off has not been checked.
```

## WSL window: feasibility

Feasible on this ThinkPad. Checked 14 Nov 2026, nothing was installed and no window was opened.

| Check | Result |
|---|---|
| Distro | `devbox`, WSL 2, running. Ubuntu. Python 3.12.3. |
| Display | `DISPLAY=:0`, `WAYLAND_DISPLAY=wayland-0`, Pulse socket under `/mnt/wslg`. WSLg is up. |
| Window toolkit | `python3-tk` is not installed. Apt has candidate `3.12.3-0ubuntu1`. zenity, yad and kdialog are not installed. |
| Drives | `C:` is `/mnt/c` and `D:` is `/mnt/d`, both read-write through 9p. `/etc/wsl.conf` does not turn automount off. |
| A USB stick | Not plugged in during the check, so a stick path was not seen. Windows gives the stick a letter. WSL then shows that letter under `/mnt`. The app does not take the USB device itself. usbipd is not used. |

The write still uses a temp file, a byte check, then a replace, and restores from the backup if the replace fails. A replace on a 9p mount is not an atomic disk replace. Pulling the stick mid-write is already a failure case.

## Tests in WSL

From the project folder, the behaviour tests are:

`wsl -d devbox -- python3 -m unittest`

They run the backup and the four-binding write against a temp folder inside the distro. They do not open the window, do not write to OneDrive, and do not touch a USB stick. The window is started from the same distro when you run the app. The look of the window is the layout check on the drawing, before any window code.

## Stages

Each stage starts only when you name it.

**Stage 1. Read his export.** Riskiest assumption: we do not have the file, and a guessed VDF is the thing that can wreck the rest of the desktop controls.

Claim: "The export on the ThinkPad is the file from this Deck. A read of it shows the B mode shift, the four Dolphin directions, the binding text for each key the window offers, and the other desktop groups still in the file."

Until that export arrives, the stand-in is `template\desktop_neptune.vdf`, copied from `C:\Program Files (x86)\Steam\controller_base\desktop_neptune.vdf` on this ThinkPad. It is the stock desktop layout. It has no mode shift, so the app must not write a Dolphin change into it. The read of the real export is still what lets stage 1 pass.

You export from the Deck (layout gear, Export Layout, personal save) and copy `controller_neptune.vdf` to the ThinkPad. The read lists where the four direction slots sit, the exact binding text for Up Arrow, Down Arrow, Left Arrow, Right Arrow, Enter, Left Alt, and none, and the groups that must survive (trackpad, mouse, grips, keyboard, or whatever the file actually contains). It says whether a stock file would have those slots. It also lists any other file beside that export which this change would replace. If the export is a single file, the backup list stays `controller_neptune.vdf`. If the export is not this layout, or a key the window offers has no binding text in it, stop. Nothing is written for the stick in this stage.

Runnable. No reviewer. This stage records the minutes.

**Stage 2. The window backs up, then writes.** The drawing matches the outline under "The window", light and dark, and you approve it before any window code.

Claim: "I put the export in a folder, change one direction on the screen, and run Write. The backup matches the export. The new file differs only in that one binding. The other three match the screen. where-to-put-this.txt is there."

Acceptance is the cases table, word for word. The tests run in WSL as under "Tests in WSL", on a copy of the export, never the Deck and never your real Steam folder.

One reviewer after the app meets that claim, combined lens. The reviewer does not touch the Deck, OneDrive outside the project folder, or a USB stick.

**Stage 3. You put it on the Deck.**

Claim: "Steam was fully quit, the stick's file replaced controller_neptune.vdf under 413080, the stick still has a backup of the file that was there before, Steam was started, and in Dolphin hold B does parent, open, back and forward, and the trackpad still moves the mouse."

You do this. The ThinkPad cannot pass it. Your confirmation is the gate.

**Stage 4. Install it on the Deck.** Started 15 Nov 2026, when you said "Lets begin".

Claim: "The app is installed on the Steam Deck. The screen is the Arch Linux one, simple, and usable on the Deck."

SteamOS is Arch Linux. The screen on the Deck is for the Deck. It is not the ThinkPad window carried across. You chose the saved list (S17). The full draft is `mockup\deck-v1.html`. You open Shortcuts inside the copied folder (S20). The folder copied to the Deck on 15 Nov is the older app. Nothing has been published to GitHub.

## On the Steam Deck

Ross, 15 Nov 2026: "Also I want to get it installable on the steam deck itself, the arch linux interface needs to be steam deck friendly and simple".

The app has to install on the Steam Deck itself. The interface there runs on Arch Linux. It has to be simple, and it has to be Steam Deck friendly: readable on the Deck, and usable with the Deck in desktop mode. It is a separate screen from the WSL window on the ThinkPad.

The ThinkPad app still only writes a file you copy by USB. It does not reach the Deck. The Deck copy, once this stage is named, is the one that runs on the machine.

Started 15 Nov 2026. You chose the saved list. The full draft is `mockup\deck-v1.html`. The screen build is `deck_app.py`. You open it with `Shortcuts.desktop` in that same folder (S20). The keyboard summon (S18) is not in this build. No package is chosen.

S21: when a public repo is named in `update.py`, Shortcuts asks GitHub once on open. If that copy is newer, Update is shown. Pressing it replaces the program files and leaves `shortcuts.json` and any controller file alone. Then open Shortcuts again. The repo line is still empty, so the check does not run. A private repo is not set up.

## After a yes

Project-map stages and summary, in the same turn as the approval, under `project-map\stages\` and `project-map\summaries\`. Work does not start until you then name Stage 1.

## Parked

From the stage 2 review on 14 Nov 2026. Not fixed. Ross picks.

- A layout that is already missing the closing quote on a binding can lose the next brace when that binding is replaced. A well-formed file does not do this.
- If `where-to-put-this.txt` is already a directory, the layout is still replaced and the note is not written. The status says the note could not be written.
- `apply_folder("")` says to copy the Deck file in. The window says "pick a folder." The window is the path he uses.
- Making a folder read-only with chmod does not stick on the Windows mount the stick uses. The failure path was run on the Linux temp disk.
