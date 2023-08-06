# FIXME: remove this when RSM and MAM are in wokkel
# XXX: the Monkey Patch is here and not in src/__init__ to avoir issues with pyjamas compilation
import wokkel
from sat_tmp.wokkel import pubsub as tmp_pubsub, rsm as tmp_rsm, mam as tmp_mam

wokkel.pubsub = tmp_pubsub
wokkel.rsm = tmp_rsm
wokkel.mam = tmp_mam
