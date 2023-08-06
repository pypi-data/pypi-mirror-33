import pandas as pd
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, LabelBinarizer, MultiLabelBinarizer


df = pd.DataFrame([{'x': 'a', 'y': 'b', 'z': 1}, {'x': 'c', 'y': 'c', 'z': 0}, {'x': 'b', 'y': 'a', 'z': 1},])
col_list = ['x', 'y']
enc = LabelEncoder()

label_encoders = {}
for col in col_list:
    enc = LabelEncoder()
    df[col] = enc.fit_transform(df[col])
    label_encoders[col] = enc

for col in col_list:
    enc = label_encoders[col]
    df[col] = enc.transform(df[col])


enc = OneHotEncoder(sparse=False)
enc.fit_transform(df[col_list])

output = [df]
one_hot_encoders = {}
for col in col_list:
    output.append(pd.get_dummies(df[col], prefix=col))
    del df[col]

df = pd.concat(output, axis=1)

# save the columns and order of columns
