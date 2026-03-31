import numpy as np
import cv2
import insightface
import chromadb
from chromadb.config import Settings


# -------- Load Face Model --------
model = insightface.app.FaceAnalysis(name="buffalo_l",
 root="./models",providers=['CPUExecutionProvider'])
model.prepare(ctx_id=0)

# -------- Setup ChromaDB --------


client = chromadb.PersistentClient(path="./chroma_face_db")

collection = client.get_or_create_collection(
    "faces",
    metadata={"hnsw:space": "cosine"}
)
# -------- Helper: Convert image --------
def read_image(file):
    contents = file.file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)




