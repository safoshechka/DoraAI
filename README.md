# DoraAI
DoraAI Telegram bot for MAI IT-center

## Структура проекта
- VideoParser
  
  Класс отвечает за парсинг Youtube-видео в текст.

  Функции:
  - ```def get_audio_from_youtube(self, cnt, url)```

    извлекает и сохраняет 1 канал звука из видео на Youtube по ссылке
  - ```def transcribe_audio(self, file)```
 
    посылает запрос к AssemblyAI на перевод аудио в текст
  - ```def add_video(self, url)```
  
    используя 2 предыдущие функции, превращает ссылку на видео в текст

  - ```def process_videos(self)```
 
    вызывает функцию ```add_video``` на наборе ссылок, которые ему переданы в ```config``` файле
  
- Talker
  
  Класс отвечает за парсинг Youtube-видео в текст.

  Функции:
  - ```def _init_texts(self)```

    загружает тексты для последующей обработки

  - ```def _init_embeddings(self)```

    инициализирует эмбеддинги

  - ```def _init_vec_store(self)```

    инициализирует векторное хранилище LanceDB

  - ```def _init_retriever(self)```

    инициализирует retriever из веторного хранилища

  - ```def _init_reorderer(self)```

    инициализирует reorderer

  - ```def _init_llm(self)```

    инициализирует LLM, в нашем случае ```llama3```

  - ```def _init_chain(self)```

    инициализирует StuffDocumentsChain на основании предыдущих компонентов

  - ```def boot(self)```

    вызывает функции ```_init_*```

  - ```def _query(self, query, reorder=True, show_results=True)```

    обрабатывает запрос, составляет список ссылок, релевантных этому запросу

  - ```def pretty_answer(self, query)```

    вызывает функцию ```_query``` и возвращает красивый ответ
  
- DoraAI
  
  Класс отвечает за работу Telegram бота

  - ```def run_bot(self)```

    запускает работу бота

      - ```def get_query(message)```

        обрабатывает запросы от пользователей, так же предусмотрена команда ```add_new_video_by_link``` для пользователей со статусом ```videos_adder```

