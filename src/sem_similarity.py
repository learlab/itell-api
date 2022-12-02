import nltk
from nltk.corpus import stopwords
from gensim.models import Doc2Vec
from scipy import spatial

source_dict_path = './assets/macroeconomics_2e_section.json'
model_path = './assets/doc2vec_model'

# Load the source_dict
data = open(source_dict_path)
source_dict = json.loads(data.read())

# Load the model
model = Doc2Vec.load(model_path)

# A function to tokenize the text
def tokenize_text(text):
    tokens = []
    for sent in nltk.sent_tokenize(text):
        for word in nltk.word_tokenize(sent):
            if len(word) < 2:
                continue
            tokens.append(word.lower())
    return tokens

# A function to get the score
def getSimilarity(summary, chapter):
    summary_embedding = model.infer_vector(tokenize_text(summary))
    section_embedding = model.infer_vector(tokenize_text(chapter))
    return 1 - spatial.distance.cosine(summary_embedding, section_embedding)
    
 
