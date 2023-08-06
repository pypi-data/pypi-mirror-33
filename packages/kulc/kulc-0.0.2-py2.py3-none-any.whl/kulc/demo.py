import numpy as np
from keras.layers import Input, Dense, LSTM
from keras.models import Model
from attention import ExternalAttentionRNNWrapper

L = 14*14
D = 512

T = 20
V = 1024

lstm_units = 256

img_inp = Input(shape=(L, D))
caption_inp = Input(shape=(T, V))
lstm = LSTM(lstm_units)
ext_atn_wrapper = ExternalAttentionRNNWrapper(lstm)
output = ext_atn_wrapper([caption_inp, img_inp])

model = Model(inputs=[caption_inp, img_inp], outputs=output)
model.summary()
model.compile("adam", "mse")

# dummies
BS = 64
captions = np.empty((BS, T, V))
image_features = np.empty((BS, L, D))

out = model.predict([captions, image_features], batch_size=16, verbose=1)
print("out", out)