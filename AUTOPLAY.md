# Autoplay Lab

From a save's title screen, choose **Autoplay Lab**, select a class, and press **Play**.
Use **One move** to inspect an individual decision. Expand the lab header to choose
Cautious, Aggressive, or Experimental and Slow, Normal, or Fast speed.

The bot plays one run at a time. It pauses for manual action, the character sheet,
a hidden tab, an error, repeated actions without progress, or the end of a run.
After a run, choose **New run** to try another class. **Exit lab** returns to the
personal save selection; it asks before abandoning an unfinished test run.

## Saves and limitations

The lab uses `meta_v2_slotautoplay`; personal saves remain in `meta_v2_slot1` through
`meta_v2_slot3`. Lab mastery, credits, and unlocks belong only to the test save.
The latest 20 completed runs retain their outcome, build, and last 120 bot decisions.
Total test losses and the normal wins/starts counters also persist.

As in the existing game, an active run is held in memory: reloading or closing the
page ends it. This addition does not provide resumable runs, cloud backup, or a
guarantee against browser storage deletion. Results persist in local browser storage
when writes succeed. The bot has no network calls, paid API, or learning component.

Strategies are heuristics. Combat estimates use visible stats, weapon affinity,
armor, multi-hit weapons and ability descriptions. Event choices use their displayed
labels and descriptions, so new event wording may need strategy tuning. Experimental
adds variation to non-combat choices. Winning is not guaranteed.

## Files

- `autoplay.js`: controls, decision rules, isolated test lifecycle, and records.
- `autoplay.css`: compact expandable controls using the game's existing theme.
- `index.html`: action observation and run lifecycle hooks; displayed shop/relic/weapon metadata.
- `manifest.json` and `service-worker.js`: correctly named copies/replacement for the
  paths the existing page requests. The worker caches the game and bot assets. Old
  extensionless files remain in the repo for compatibility with existing references.

A new worker waits for old tabs to close before activation to avoid changing assets
mid-run. Load the updated game online once before expecting offline use.

## Verification

Run the dependency-free gameplay integration suite:

```sh
node tests/autoplay.simulation.cjs
```

It executes the real game and bot with a minimal DOM adapter and checks 21 seeded
runs (seven classes × three styles), save isolation, healing, disabled actions,
weapon switching, manual takeover, timer cancellation, background pause, sheet pause,
record persistence, victory recording, and offline asset paths. This verifies
logic; it does not verify actual browser rendering or service-worker behavior.

For the browser suite in a development checkout with Node.js:

```sh
npm install --no-save playwright
npx playwright install chromium
node tests/autoplay.test.cjs
```

The browser suite includes an actual service-worker offline reload and a mobile-size
screenshot. It was prepared but could not run in the implementation environment:
the browser binary download timed out and the available remote browser could not
access the local test server. A real iOS Home Screen/offline smoke test is still needed.
