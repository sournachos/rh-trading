# A step-child of `da_no_kelly_strangle.py` & 'history_repeats_itself.py`
# Let's try to make the buying decision based on the Delta value
# and the direction of the stock price based on the last 5, 10, 15 min
# aka Deltas to be somewhat close to 1.00 for CALLs and -1.00 for PUTs
# when their respective tendencies are identified from the stock price
# 
# My first thought is to make transactions often for small profits/losses
# and focus on an overall positive P/L result by EOD
# 