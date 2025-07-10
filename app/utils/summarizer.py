from transformers import pipeline
import traceback

# Initialize the pipeline once
summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    """
    Summarizes text with a final check to prevent summarizing short content.
    """
    if not text or len(text.strip().split()) < 15:
        return "The provided text is too short to generate a meaningful summary."

    try:
        # 1. Create word-based chunks
        words = text.split()
        chunk_size = 800
        text_chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

        if not text_chunks:
            return "Could not create valid text chunks."

        # 2. Get initial summaries for each chunk
        chunk_summaries = summarizer_pipeline(text_chunks, max_length=150, min_length=20, do_sample=False)
        
        # 3. Combine the summaries into a single text
        combined_summary = ' '.join([summ['summary_text'] for summ in chunk_summaries if summ.get('summary_text')]).strip()

        if not combined_summary:
            return "The content was too brief to summarize effectively."

        # 4. **NEW LOGIC**: If the combined summary is already short, return it directly.
        # This prevents summarizing an already concise text, which causes the cutoff issue.
        if len(combined_summary.split()) < 100:
            return combined_summary

        # 5. If the text is long enough, perform a final high-quality pass.
        max_len = min(250, len(combined_summary.split()))
        min_len = min(50, max_len // 2)
        
        final_summary_list = summarizer_pipeline(combined_summary, max_length=max_len, min_length=min_len, do_sample=False)
        
        final_summary = final_summary_list[0]['summary_text'].strip()

        return final_summary if final_summary else combined_summary

    except Exception as e:
        print(f"A critical error occurred in the summarization pipeline:")
        traceback.print_exc()
        return "Sorry, a critical error occurred while generating the summary."