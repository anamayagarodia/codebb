# codebb
Team DuckDuckGoose, 2nd place at Bloomberg Code B Hackathon March 3-4, 2017, with @robertriachi, @anamayagarodia, and @pratyushpal

This is a real-time Python AI for a large multiplayer Space Invaders-like game made by Bloomberg. We doubled the scores of nearly all other teams in Waterloo, and took one game off of a team of grad students and fourth years who had an actually optimal algorithm.

Rules:
- You control a spaceship with thrusters (using newline-separated commands over TCP)
- You have limited vision and can also place "scans" of arbitrary locations on the field
- You want to hit very small "mines" (10x10 on a field on 10,000x10,000) in order to "capture" them, at which point they will start generating income for you
- The game is played for 20 minutes, and the player with the largest resources mined wins

Features:
- Uses somewhat clever and somewhat arbitrary vector math to determine direction of thrusters given a target point. Almost always works, hitting the mine on the first pass.
- Uses a running queue of all known mine locations to be able to place scans optimally and "check back" on mines taken
  - First goes through an "explore" phase in order to find the locations of at least 80% of the mines on the field
  - Then begins a "circulation" phase to scan each of the mines that it has seen and go back to the ones that have been captured by others.
  - If it runs into a closer mine while waypointing to a particular mine, changes priority and goes for that one first. Slight hysteresis added to prevent infinite loops.
- Backs up a list of the mines it has "seen", since this is its single most valuable resource in case the program crashes
- Targets the nearest mine, with some weighting based on current direction of travel
- Prioritizes capturing mines owned by higher ranked teams (in this case, "exodia" was hardcoded)
