from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text_into_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len
    )

    chunks = splitter.split_text(text)

    cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]

    return cleaned_chunks
