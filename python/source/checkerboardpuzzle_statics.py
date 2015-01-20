B = -1
W = 1
colors = [B,W]
filled_factor = 10
B_filled = B * filled_factor
W_filled = W * filled_factor
filled = [B_filled, W_filled]
_ = 0
# valid and invalid field sums after performing a matrix addition
field_valid = [-2, 2] + colors + filled
field_invalid = [-11, -9, 11, 9, 0]
