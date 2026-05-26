import pandas as pd
import io

dataset = None

def load_dataset(contents: bytes) -> None:
  global dataset #gör så att dataset pandas inte bara skapas i funktionen
  dataset = pd.read_csv(io.BytesIO(contents)) # tar råa bytes och gör dem tillett objekt som beter sig som en fil