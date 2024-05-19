from langchain_community.document_transformers import LongContextReorder
from langchain_community.vectorstores import LanceDB
from langchain_community.llms import Ollama
import langchain_community.document_loaders
import langchain_community.embeddings
import langchain_text_splitters
import langchain.prompts
import langchain.chains
import warnings
import lancedb
import logging
import glob
import os

logger = logging.getLogger("__main__" + __name__)

warnings.filterwarnings("ignore")


class Talker:
    def __init__(self, config):
        self.config = config

        self.chunk_size = self.config["chunk_size"]
        self.chunk_overlap = self.config["chunk_overlap"]
        self.source_dir = self.config["source_dir"]
        self.api_key = self.config["api_key"]
        self.folder_id = self.config["folder_id"]
        self.db_dir = self.config["db_dir"]

        self.boot()

    def boot(self):
        self._init_texts()
        self._init_embeddings()
        self._init_vec_store()
        self._init_retriever()
        self._init_reorderer()
        self._init_llm()
        self._init_chain()

    def _init_texts(self):
        self.texts = []
        files = glob.glob(f"{self.source_dir}/*")
        for file in files:
            with open(file, "r") as f:
                string = f.read()
                self.texts.append(string)

        logger.info("Docs read: Done")
        logger.info(f"Amount of docs: {len(self.texts)}")

    def _init_embeddings(self):
        self.embeddings = langchain_community.embeddings.HuggingFaceEmbeddings(
            model_name="distiluse-base-multilingual-cased-v1"
        )

        logger.info("Embeddings init: Done")

    def _init_vec_store(self):
        os.makedirs(self.db_dir, exist_ok=True)

        db = lancedb.connect(self.db_dir)
        table = db.create_table(
            "vector_index",
            data=[
                {
                    "vector": self.embeddings.embed_query("Sample text"),
                    "text": "Hello World",
                    "id": "1",
                }
            ],
            mode="overwrite",
        )

        self.vec_store = LanceDB.from_texts(self.texts, self.embeddings, connection=db)
        logger.info("Vector store init: Done")

    def _init_retriever(self):
        self.retriever = self.vec_store.as_retriever(search_kwargs={"k": 10})
        logger.info("Retriever init: Done")

    def _init_reorderer(self):
        self.reorderer = LongContextReorder()
        logger.info("Reorderer init: Done")

    def _init_llm(self):
        self.llm = Ollama(model="llama3")

        logger.info("LLM init: Done")

    def _init_chain(self):
        document_prompt = langchain.prompts.PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )

        document_variable_name = "context"
        stuff_prompt_override = """
        Ты - чат-бот по имени Дора и главная собака института №8 Московского Авиационного Института, который отвечает на вопросы абитуриентов про Московский Авиационный Институт. Пиши в начале приветствие от лица института №8.
        Прочитай эту информацию:
        {context}
        Ответь на вопрос '{query}', используя информацию, которую ты прочитал. Ответ представь, не форматируя ответ.
        """

        prompt = langchain.prompts.PromptTemplate(
            template=stuff_prompt_override, input_variables=["context", "query"]
        )

        llm_chain = langchain.chains.LLMChain(llm=self.llm, prompt=prompt)
        self.chain = langchain.chains.StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt=document_prompt,
            document_variable_name=document_variable_name,
        )

        logger.info("Chain init: Done")

    def _query(self, query, reorder=True, show_results=True):
        results = self.retriever.get_relevant_documents(query)

        links = []
        if show_results:
            for x in results:
                links.append(x.page_content.split("\n")[0])
                logger.info(x.page_content)

        if reorder:
            results = self.reorderer.transform_documents(results)

        logger.info(f"New query: {query}")

        return [self.chain.run(input_documents=results, query=query), list(set(links))]

    def pretty_answer(self, query):
        llm_answer = self._query(query)

        answer = f"{llm_answer[0]}\n\nБолее подробно смотри тут:\n"
        for i, link in enumerate(llm_answer[1]):
            answer += f"{i}. {link}\n"

        return answer
