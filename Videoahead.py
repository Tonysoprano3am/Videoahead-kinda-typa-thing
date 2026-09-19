import td

# 1. CLEANUP ENGINE
root = op('/project1') if op('/project1') else op('/')
for child in root.children:
    child.destroy()

# =========================================================================
# 2. AUDIO CORE & FILTER CHOPs (Tracks the raw dB volume intensity)
# =========================================================================
audio_in = root.create(audiofileInCHOP, 'audio_source')
audio_in.par.file = "" # <-- Upload your audio file here

# Analyze the smooth tracking power of the music
audio_analyze = root.create(audioanalyzeCHOP, 'volume_analyzer')
audio_analyze.connect(audio_in)
audio_analyze.par.function = 'rmspower'

# Lag CHOP gives it that signature "elastic" fluid slide instead of choppy cuts
audio_lag = root.create(lagCHOP, 'smooth_elasticity')
audio_lag.connect(audio_analyze)
audio_lag.par.lag1 = 0.15  # Smooth attack
audio_lag.par.lag2 = 0.35  # Gentle release decay

# Math CHOP normalizes the audio wave values
audio_math = root.create(mathCHOP, 'audio_normalizer')
audio_math.connect(audio_lag)
audio_math.par.torange1 = 0
audio_math.par.torange2 = 1

# =========================================================================
# 3. TIMELINE & VIDEO CONFIGURATION
# =========================================================================
# We must use "Specify Index" mode to take manual control of the playhead
video_node = root.create(moviefileInTOP, 'video_playhead_source')
video_node.par.file = "" # <-- Upload your video file here (timelapses work best)
video_node.par.playmode = 'index' # Switches play control from timeline to Python math
video_node.par.indexunit = 'fraction' # 0.0 means start of video, 1.0 means end

# =========================================================================
# 4. UISATO TIME-WARP EXPRESSION ENGINE
# =========================================================================
# Custom Python Math: 
# Base time scrolls forward normally via TouchDesigner's clock (absTime.seconds * speed).
# The audio amplitude is multiplied and added directly to the timeline index.
# This causes the playhead to elastic-stretch forward on beats and snap back to the clock line on silences.

base_speed = 0.03  # How fast the video naturally moves forward
audio_push = 0.5   # How violently the beat flings the playhead forward

video_node.par.index.expr = f"((absTime.seconds * {base_speed}) + (op('audio_normalizer')['chan1'] * {audio_push})) % 1.0"

# =========================================================================
# 5. POST OUTPUT SETUP
# =========================================================================
final_out = root.create(outTOP, 'video_output_final')
final_out.connect(video_node)

print("Uisato-style Audio Reactive Playhead Engine successfully generated!")
