import os
import numpy as np
import json

NUM_PER_FILE = 298

if __name__ == "__main__":

    headers = ["ID", "Lieu", "Epoque", "Nom", "Titre"]
    ids = []
    places = []
    eras = []
    names = []
    titles = []

    for mo in range(1, 13):
        for day in range(1, 32):
            try:
                with open(f"./data/json/{mo:02d}-{day:02d}.json") as f:
                    day_data = json.load(f)

                for idx, saint_data in enumerate(day_data):
                    ids.append(f"{mo:02d}-{day:02d}-{idx:02d}")
                    places.append(saint_data["lieu"])
                    eras.append(saint_data["epoque"])
                    names.append(saint_data["nom"])
                    titles.append(saint_data["titre"])
            except FileNotFoundError:
                pass

    os.makedirs("./data/csv", exist_ok=True)
    for extract_idx, start_idx in enumerate(range(0, len(ids), NUM_PER_FILE)):
        ids_slice = [headers[0]] + ids[start_idx : start_idx + NUM_PER_FILE]
        places_slice = [headers[1]] + places[start_idx : start_idx + NUM_PER_FILE]
        eras_slice = [headers[2]] + eras[start_idx : start_idx + NUM_PER_FILE]
        names_slice = [headers[3]] + names[start_idx : start_idx + NUM_PER_FILE]
        titles_slice = [headers[4]] + titles[start_idx : start_idx + NUM_PER_FILE]
        np.savetxt(
            f"./data/csv/{extract_idx:02d}.csv",
            [
                p
                for p in zip(
                    ids_slice, places_slice, eras_slice, names_slice, titles_slice
                )
            ],
            delimiter=",",
            fmt="%s",
        )
