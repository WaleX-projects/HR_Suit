import numpy as np
import cv2
import insightface
import chromadb
from chromadb.config import Settings
import onnxruntime as ort

# -------- Load Face Model --------
model = insightface.app.FaceAnalysis(name="buffalo_l",
 root="./models",providers=['CPUExecutionProvider'])
model.prepare(ctx_id=0)

session = ort.InferenceSession("models/modelrgb.onnx")  

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




def preprocess(img):
    #img = cv2.resize(img, (80, 80))
    img = cv2.resize(img, (112, 112))
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2,0,1))
    img = np.expand_dims(img, axis=0)
    return img
    
    





def is_live(file):
    img = read_image(file)
    input_tensor = preprocess(img)

    outputs = session.run(
        None,
        {"input": input_tensor}
    )

    scores = outputs[0]

    # usually index 1 = "real face"
    real_score = scores[0][1]

    return real_score > 0.5  