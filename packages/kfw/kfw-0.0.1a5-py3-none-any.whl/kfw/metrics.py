import keras.backend as K


def map3(y_true, y_pred):
    ap1 = K.in_top_k(y_pred, K.argmax(y_true, axis=-1), 1)
    ap2 = K.in_top_k(y_pred, K.argmax(y_true, axis=-1), 2)
    ap3 = K.in_top_k(y_pred, K.argmax(y_true, axis=-1), 3)
    ap1 = K.cast(ap1, 'float32')
    ap2 = K.cast(ap2, 'float32')
    ap3 = K.cast(ap3, 'float32')
    ap3 = ap3 - ap2
    ap2 = ap2 - ap1
    ap3 = ap3 / 3.
    ap2 = ap2 / 2.
    return K.mean(ap3 + ap2 + ap1)
