import nltk
from nltk.corpus import stopwords
from gensim.models import Doc2Vec
from scipy import spatial

# a textbook split into sections
source_dict_path = '../assets/macroeconomics_2e_section.json'

# a custom pre-trained doc2vec model (gensim)
model_path = '../assets/doc2vec_model' 

english_stop_words = stopwords.words('english')

with open(source_dict_path, "r") as data:
    source_dict = json.loads(data.read())

model = Doc2Vec.load(model_path)

def tokenize_text(text):
    return [tok for tok in nltk.word_tokenize(text) if tok not in english_stop_words]

def get_similarity(summary, section):
    '''Return semantic similarity score based on summary and source text (section)
    summary: str
    section: str
    '''
    summary_embedding = model.infer_vector(tokenize_text(summary))
    section_embedding = model.infer_vector(tokenize_text(section))
    return 1 - spatial.distance.cosine(summary_embedding, section_embedding)
