from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

sentence1 = "educated at"
sentence2 = "studied at"

emb1 = model.encode(sentence1, convert_to_tensor=True)
emb2 = model.encode(sentence2, convert_to_tensor=True)

similarity = util.pytorch_cos_sim(emb1, emb2)
print(similarity.item())