import pandas as pd
import io

dataset = None

def load_dataset(contents: bytes) -> dict:
  global dataset #gör så att dataset pandas inte bara skapas i funktionen
  dataset = pd.read_csv(io.BytesIO(contents)) # tar råa bytes och gör dem tillett objekt som beter sig som en fil
  return {
    "rows": dataset.shape[0],
    "columns": dataset.columns.to_list(),
    "dtypes": dataset.dtypes.apply(str).to_dict()
  }