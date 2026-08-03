from modules.hybrid_search import hybrid_search
from modules.rag import generate_answer

class CricketRAGPipeline:

    def search(self, query):
        return hybrid_search(query)

    def answer(self, query):
        return generate_answer(query)