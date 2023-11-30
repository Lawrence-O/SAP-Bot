
import pickle

with open("./bin/data_final_7.pickle", "rb") as handle:
    data = pickle.load(handle)


print(data["info"])