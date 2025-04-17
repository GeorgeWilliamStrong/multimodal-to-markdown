# Unstructured Data ETL Pipelines

A collection of multimodal AI pipelines and models that let you transform *ANY* data modality (document, video, audio, image, web) to LLM-ready Markdown text.

Powered by [🔮 **Instill Core**](https://github.com/instill-ai/instill-core).

### Launch Instructions

Prerequisites:
- Python 3.11
- Docker Compose
- `pip install instill-sdk==0.17.0rc10`

See the [deployment overview](https://www.instill-ai.dev/docs/core/deployment) for more details.

**1. Fire up Instill Core 🔥**
```bash
git clone https://github.com/instill-ai/instill-core.git && cd instill-core

# Launch all services
make latest PROFILE=all
```

Follow the instructions [here](https://www.instill-ai.dev/docs/core/token) to create your Instill Core API token.

**2. Clone this repo**
```bash
cd .. && git clone https://github.com/GeorgeWilliamStrong/unstructured-etl.git && cd unstructured-etl
```

**3. Setup environment variables**
Run the command `make env` to create template `.env` file and then enter in your API tokens.

```bash
INSTILL_CORE_API_TOKEN=your_instill_core_api_token
OPENAI_API_TOKEN=your_openai_api_token
```

**4. Deploy pipelines**
This will automatically deploy all pipelines. Please note that models currently require manual deployment.
```bash
make all
```

---

## Working with documents 📄

There is no one-size-fits-all solution for document parsing because every document is different. Some may have simple text and formatting, while others include intricate tables, images, or specialized formatting like mathematical equations. A PDF could even be a scanned hand-written note.

Provided are a series of pipelines that let you transform any document to LLM-ready Markdown text. Depending on the complexity of the documents you have and their file format, you can choose between the following options:

#### 1. Heuristic document parser

This pipeline is great for fast and compute efficient processing of a wide range of file formats. However, it may struggle with documents that have complex layouts, tables, or images that may require OCR-based methods.

Pipeline recipe: `/pipelines/doc-heuristic.yaml`

Capable of parsing simple documents. Can take as input `.PDF`, `.DOCX`, `.DOC`, `.PPTX`, `.PPT`, `.HTML`, `.XLSX`, `.XLS`, `.CSV`, `.TXT` file formats.

**How it works**

This pipeline employs Instill Core's [document operator](https://www.instill-ai.dev/docs/component/operator/document#convert-to-markdown). To handle `.PDF` files, it uses the [pdfplumber](https://github.com/jsvine/pdfplumber) library to extract the Markdown text.

**How to use it?**

Trigger via cURL:
```bash
curl -X POST 'http://localhost:8080/v1beta/users/admin/pipelines/doc-heuristic/trigger' \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $INSTILL_CORE_API_TOKEN" \
--data '{
  "inputs": [
    {
      "file": "Please put your file base64 encoded string"
    }
  ]
}'
```

Trigger via Python:
```python
# Initialize the pipeline client
from instill.clients import init_pipeline_client
pipeline = init_pipeline_client(
    api_token="INSTILL_CORE_API_TOKEN",
    url="localhost:8080",
    secure=False
)

# Trigger the pipeline
response = pipeline.trigger(
    namespace_id="admin",
    pipeline_id="doc-heuristic",
    data=[{"file": BASE64_ENCODED_FILE}]
)
```

#### 2. Hybrid multimodal document parser

This pipeline is designed for robust, high-quality document parsing. It is able to handle complex layouts, tables, images, noise, handwritten or scanned documents. It is more computationally intensive and slower than the heuristic parser.

Pipeline recipe: `/pipelines/doc-multimodal-hybrid.yaml`

Capable of parsing highly complex documents containing complex layouts, tables, images, etc. Can take as input `.PDF`, `.DOCX`, `.DOC`, `.PPTX`, `.PPT` file formats.

Please see the related blog post [here](https://www.instill-ai.com/blog/make-complex-documents-rag-ready) to learn more, and you can also try the free demo [here](https://www.instill-ai.dev/demos/document-parser-gen-ai).

**How it works**

This pipeline employs a hybrid approach, utilising a visual language model to refine, correct, and enrich the initial output from the heuristic parsing strategy with corresponding page images. This results in substantially higher quality Markdown text at the cost of increased latency and compute resources.

See the flowchart below for an overview of the pipeline architecture.

<img src="/assets/images/doc-parsing-flow.svg" alt="Unstructured Data ETL Pipelines" width="400" height="auto">

**How to use it?**

Trigger via cURL:
```bash
curl -X POST 'http://localhost:8080/v1beta/users/admin/pipelines/doc-multimodal-hybrid/trigger' \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $INSTILL_CORE_API_TOKEN" \
--data '{
  "inputs": [
    {
      "document-input": "Please put your file base64 encoded string",
      "vlm-model": "Please put your value here"
    }
  ]
}'
```

Trigger via Python:
```python
# Initialize the pipeline client
from instill.clients import init_pipeline_client
pipeline = init_pipeline_client(
    api_token="INSTILL_CORE_API_TOKEN",
    url="localhost:8080",
    secure=False
)

# Trigger the pipeline
response = pipeline.trigger(
    namespace_id="admin",
    pipeline_id="doc-multimodal-hybrid",
    data=[{"file": BASE64_ENCODED_FILE, "vlm-model": "gpt-4o"}]
)
```

#### 3. Multi-model parser

This pipeline leverages [Docling](https://github.com/docling-project/docling) to parse complex `.PDF`, `.DOCX`, `.DOC`, `.PPTX`, `.PPT` file formats locally and reliably using a multi-model approach.

Model implementation: `/models/docling/v0.1.2/`

**How it works**

Legacy microsoft file formats (`.DOC` and `.ppt`) are first converted to their modern `.DOCX` and `.PPTX` equivalents. The Docling model instance then triggers a series of specialised models to parse the document. This combines specialised models for segmenting document layouts, performing OCR, extracting tables, and more.  By default, the current implementation is designed to run on available CUDA-enabled GPUs. See the `/models/docling/v0.1.2/model.py` file for more details.

**How to deploy the model?**
1. Run the following command to download the model weights locally.
```bash
pip install docling
docling-tools models download
cp -r $HOME/.cache/docling/models $HOME/path/to/model/version/docling-models
```
where `$HOME/path/to/model/version/docling-models` is in the same directory as the `model.py` and `instill.yaml` files.

2. Create a new model namespace called `admin/docling` using the Instill Core UI. See the [documentation](https://www.instill-ai.dev/docs/model/create/namespace) for more details.

3. Build the model image using the command:
```bash
instill build admin/docling -t v0.1.2
```

4. Test the model locally:
```bash
instill run admin/docling -t v0.1.2 -g -i "$(cat sample_payload.json)"
```

5. Login to Docker on Instill Core instance:
```bash
docker login localhost:8080
# username: admin
# password: $INSTILL_CORE_API_TOKEN
```

6. Push the model image to the Instill Core instance:
```bash
instill push admin/docling -t v0.1.2 -u localhost:8080
```

**How to use it?**

Once the model image has been deployed, you can use it similarly to a pipeline.

Trigger via cURL:
```bash
curl --location 'http://localhost:8080/v1beta/users/admin/docling/trigger' \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $INSTILL_CORE_API_TOKEN" \
--data '{
  "taskInputs": [
    {
      "data": {
        "doc-content": "Please put your file base64 encoded string"
      }
    }
  ]
}'
```

Trigger via Python:
```python
# Initialize the model client
from instill.clients import init_model_client
model = init_model_client(
    api_token="INSTILL_CORE_API_TOKEN",
    url="localhost:8080",
    secure=False
)

# Trigger the model
response = model.trigger(
    namespace_id="admin",
    model_id="docling",
    version="v0.1.2",
    task_inputs=[
        {
            "data": {
                "doc-content": BASE64_ENCODED_FILE
            }
        }
    ]
)
```
Note that the output from the model is a list of markdown strings, one for each page in the document.

---

## Working with images 📷

This pipeline uses a visual language model to analyze images and generate detailed, structured Markdown descriptions. It's designed to extract rich information from any image, making it suitable for a variety of use cases including content cataloging, accessibility descriptions, and preparing image content for LLMs.

Pipeline recipe: `/pipelines/image.yaml`

Capable of processing `.JPEG`, `.PNG`, `.GIF`, `.WEBP`, `.TIFF`, `.BMP` file formats.

**How it works**

The pipeline leverages OpenAI's GPT-4o vision capabilities to analyze the image content and generate a comprehensive Markdown description. The model is prompted to provide a structured analysis that includes an overall summary, identification of objects and entities, spatial relationships, and text extraction.

**How to use it?**

Trigger via cURL:
```bash
curl -X POST 'http://localhost:8080/v1beta/users/admin/pipelines/image/trigger' \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $INSTILL_CORE_API_TOKEN" \
--data '{
  "inputs": [
    {
      "image": "Please put your image base64 encoded string"
    }
  ]
}'
```

Trigger via Python:
```python
# Initialize the pipeline client
from instill.clients import init_pipeline_client
pipeline = init_pipeline_client(
    api_token="INSTILL_CORE_API_TOKEN",
    url="localhost:8080",
    secure=False
)

# Trigger the pipeline
response = pipeline.trigger(
    namespace_id="admin",
    pipeline_id="image",
    data=[{"image": BASE64_ENCODED_IMAGE}]
)
```

---

## Working with audio 🎧

This pipeline processes audio files by segmenting speech, transcribing each segment, and enhancing the transcription with proper formatting and timestamps. It's designed to handle various audio inputs and produce high-quality, readable transcripts in Markdown format.

Pipeline recipe: `/pipelines/audio.yaml`

Capable of processing `.MP3`, `.WAV`, `.AAC`, `.OGG`, `.FLAC`, `.M4A`, `.WMA`, `.AIFF` file formats.

**How it works**

The pipeline employs a multi-step approach:
1. Voice Activity Detection (VAD) identifies speech segments in the audio
2. Audio segmentation splits the file based on detected speech
3. Each segment is transcribed using OpenAI's Whisper model
4. A post-processing step enhances the transcription with proper formatting, punctuation, and timestamps
5. Finally, all segment transcriptions are merged into a single Markdown document

**How to use it?**

Trigger via cURL:
```bash
curl -X POST 'http://localhost:8080/v1beta/users/admin/pipelines/audio/trigger' \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $INSTILL_CORE_API_TOKEN" \
--data '{
  "inputs": [
    {
      "audio": "Please put your audio file base64 encoded string"
    }
  ]
}'
```

Trigger via Python:
```python
# Initialize the pipeline client
from instill.clients import init_pipeline_client
pipeline = init_pipeline_client(
    api_token="INSTILL_CORE_API_TOKEN",
    url="localhost:8080",
    secure=False
)

# Trigger the pipeline
response = pipeline.trigger(
    namespace_id="admin",
    pipeline_id="audio",
    data=[{"audio": BASE64_ENCODED_AUDIO}]
)
```

---

## Working with videos 🎥

This pipeline processes video files by extracting both audio and visual content, analyzing each separately, and then combining them into a comprehensive Markdown transcript. It's designed to capture both what is said and what is shown in the video.

Pipeline recipe: `/pipelines/video.yaml`

Capable of processing `.MP4`, `.AVI`, `.MOV`, `.WEBM`, `.MKV`, `.FLV`, `.WMV`, `.MPEG` file formats.

**How it works**

The pipeline employs a multi-stage approach:
1. Audio extraction from the video file
2. Voice Activity Detection (VAD) to identify speech segments
3. Audio segmentation and transcription using OpenAI's Whisper model
4. Frame extraction at regular intervals (every 4 seconds)
5. Visual analysis of extracted frames using OpenAI's GPT-4o-mini
6. Final combination of audio transcripts and visual analyses into a single enhanced Markdown document

**How to use it?**

Trigger via cURL:
```bash
curl -X POST 'http://localhost:8080/v1beta/users/admin/pipelines/video/trigger' \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $INSTILL_CORE_API_TOKEN" \
--data '{
  "inputs": [
    {
      "video": "Please put your video file base64 encoded string"
    }
  ]
}'
```

Trigger via Python:
```python
# Initialize the pipeline client
from instill.clients import init_pipeline_client
pipeline = init_pipeline_client(
    api_token="INSTILL_CORE_API_TOKEN",
    url="localhost:8080",
    secure=False
)

# Trigger the pipeline
response = pipeline.trigger(
    namespace_id="admin",
    pipeline_id="video",
    data=[{"video": BASE64_ENCODED_VIDEO}]
)
```

---

## Working with the web 🌐

This pipeline crawls and scrapes web content, transforming it into clean Markdown text. It's designed to extract meaningful content from websites while filtering out navigation elements, ads, and other non-essential content.

Pipeline recipe: `/pipelines/web.yaml`

Capable of handling dynamic content by imitating scrolling behaviour.

**How it works**

The pipeline follows a sequential process:
1. Web crawling to discover and index pages starting from a root URL
2. Link extraction from the crawled pages
3. Content scraping from each discovered page, focusing on main content elements
4. Conversion of the scraped content to clean Markdown format

The pipeline is configurable, allowing you to specify:
- Which HTML tags to include (paragraphs, headings, etc.)
- Maximum crawl depth from the root URL
- Maximum number of pages to crawl
- Timeout settings for dynamic content

**How to use it?**

Trigger via cURL:
```bash
curl -X POST 'http://localhost:8080/v1beta/users/admin/pipelines/web/trigger' \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $INSTILL_CORE_API_TOKEN" \
--data '{
  "inputs": [
    {
      "url": "https://example.com",
      "include-tags": ["p", "h1", "h2", "h3", "h4", "h5", "h6"],
      "max-depth": 2,
      "max-k": 10,
      "timeout": 0
    }
  ]
}'
```

Trigger via Python:
```python
# Initialize the pipeline client
from instill.clients import init_pipeline_client
pipeline = init_pipeline_client(
    api_token="INSTILL_CORE_API_TOKEN",
    url="localhost:8080",
    secure=False
)

# Trigger the pipeline
response = pipeline.trigger(
    namespace_id="admin",
    pipeline_id="web",
    data=[{
        "url": "https://example.com",
        "include-tags": ["p", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "code", "script", "style"],
        "max-depth": 2,
        "max-k": 10,
        "timeout": 0
    }]
)
```

---

## Create a knowledge base 💾

This pipeline lets you load extracted markdown text into [Artifact](https://www.instill-ai.dev/docs/artifact/introduction), a service within Instill Core that automates knowledge base creation by chunking, embedding, and indexing the markdown text into a vector database.

Pipeline recipe: `/pipelines/load-artifact.yaml`

**How it works**

The markdown text is first base64 encoded and then loaded into Artifact. If you select the option to create a new catalog (essentially your knowledge base), you must provide a catalog ID. If you select the option to use an existing catalog, you must provide the existing catalog ID. The encoded file is then processed by Artifact. This consistes of 3 steps:
1. Chunking the markdown text into smaller units using the Instill Core's [text operator](https://www.instill-ai.dev/docs/component/operator/text) with `strategy: Markdown` used to preserve coherent sections of text.
2. Embedding the chunks using the [OpenAI AI component](https://www.instill-ai.dev/docs/component/ai/openai#text-embeddings).
3. Indexing the chunks into the vector database.

Read the documentation [here](https://www.instill-ai.dev/docs/artifact/process-files) for further details on what goes on behind the scenes.

**How to use it?**

To use Artifact, you must first configure the `CFG_COMPONENT_SECRETS_OPENAI_APIKEY` Instill Core environment variable with your OpenAI API key. See the documentation [here](https://www.instill-ai.dev/docs/core/configuration#configuring-the-embedding-feature) for more details.

Trigger via cURL:
```bash
curl -X POST 'http://localhost:8080/v1beta/users/admin/pipelines/load-artifact/trigger' \
--header "Content-Type: application/json" \
--header "Authorization: Bearer $INSTILL_CORE_API_TOKEN" \
--data '{
  "inputs": [
    {
      "markdown": "Please put your extracted markdown text here",
      "filename": "my-filename",
      "create-new-catalog": true,
      "catalog-id": "my-new-catalog-id"
    }
  ]
}'
```

Trigger via Python:
```python
# Initialize the pipeline client
from instill.clients import init_pipeline_client
pipeline = init_pipeline_client(
    api_token="INSTILL_CORE_API_TOKEN",
    url="localhost:8080",
    secure=False
)

# Trigger the pipeline
response = pipeline.trigger(
    namespace_id="admin",
    pipeline_id="load-artifact",
    data=[{
        "markdown": "Please put your extracted markdown text here",
        "filename": "my-filename",
        "create-new-catalog": True,
        "catalog-id": "my-new-catalog-id"
    }]
)
```

Once your content is loaded into Artifact, you can build custom retrieval-augmented generation (RAG) pipelines or query it directly through the Artifact API.

---

## Why Instill Core?

Instill Core has been used to build these unstructured data ETL pipelines because of the following reasons:
1. Framework agnostic - can use [Model](https://www.instill-ai.dev/docs/model/introduction) service to deploy models from any framework (e.g. PyTorch, TensorFlow, scikit-learn, ONNX, etc.).
2. Build custom pipelines with a versatile range of out-of-the-box components.
3. MLOps practices are baked in - all pipelines and models automatically come with versioning and component-level observability so you can monitor your application in production.
4. Easy to deploy and scale - production-grade containerized deployment with Docker and Kubernetes means your POC can be production ready with no extra effort.

Hope you found this content useful! 🚀

If you have any questions, or want to learn more, please reach out to me on [LinkedIn](https://www.linkedin.com/in/georgewstrong/).