# Imports
import vapoursynth as vs
# getting Vapoursynth core
import sys
import os
core = vs.core
# Import scripts
import vscmnet2 as cmnet2
clip = cmnet2.vs_read_video(source=VideoPath)
# --------------------------------------------------------------------------------------------
# Extract refs-edge extended
# The first 1% and the last 99% of frames are extracted with high threshold sensitivity (0.02)
# --------------------------------------------------------------------------------------------
fn_begin=int(round(clip.num_frames*0.01,0))
fn_end=int(round(clip.num_frames*0.99,0))
clip1 = clip[:fn_begin]
clip2 = clip[fn_begin:fn_end]
clip3 = clip[fn_end:]

clip_head = cmnet2.vs_extract_reference_frames(clip1, sc_threshold=0.02, sc_tht_ssim=0.80, sc_tht_offset=2, sc_min_int=10, sc_min_freq=10, ref_offset=0, sc_tht_white=0.70, sc_tht_black=0.09,  sc_framedir=RefDir, sc_algo=1, ref_ext="jpg", ref_jpg_quality=95, ref_override=False, sc_debug=False)

clip_mid = cmnet2.vs_extract_reference_frames(clip2, sc_threshold=float(ScThreshold), sc_tht_ssim=float(ScThtSSIM), sc_tht_offset=2, ref_offset=fn_begin, sc_min_int=int(SCMinINT), sc_min_freq=int(ScMultTht), sc_tht_white=0.70, sc_tht_black=0.09,  sc_framedir=RefDir, sc_algo=1, ref_ext="jpg", ref_jpg_quality=95, ref_override=bool(RefOverride), sc_debug=False)

clip_tail = cmnet2.vs_extract_reference_frames(clip3, sc_threshold=0.02, sc_tht_ssim=0.80, sc_tht_offset=2, sc_min_int=10, sc_min_freq=10, ref_offset=fn_end, sc_tht_white=0.70, sc_tht_black=0.09,  sc_framedir=RefDir, sc_algo=1, ref_ext="jpg", ref_jpg_quality=95, ref_override=False, sc_debug=False)

# --------------------------------------
clip = clip_head + clip_mid + clip_tail
# --------------------------------------
# adjusting output color from RGB24 to YUV420P10 for x265Model
clip = core.resize.Bicubic(clip=clip, format=vs.YUV420P10, matrix_s="709", range_in_s="full", range_s="limited") # additional resize to match target color sampling
# output
clip.set_output()

