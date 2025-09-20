import google.generativeai as genai

async def get_LLM_Response(model: str, system_prompt: str, user_query: str):
    # Use ChatML format for the prompt
    chatml_prompt = (
        f"<|system|>\n{system_prompt}\n<|end|>\n"
        f"<|user|>\n{user_query}\n<|end|>\n"
    )
    generative_model = genai.GenerativeModel(model)
    response = await generative_model.generate_content_async(
        chatml_prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=500,
            temperature=0.0
        )
    )
    
    # Handle potential content filtering or empty responses
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if candidate.finish_reason == 1:  # STOP - normal completion
            try:
                return response.text.strip()
            except Exception:
                return "Response generated but could not be accessed. Please try again."
        elif candidate.finish_reason == 2:  # MAX_TOKENS
            try:
                return response.text.strip() if response.text else "Response was truncated due to length limits."
            except Exception:
                return "Response was truncated due to length limits."
        elif candidate.finish_reason == 3:  # SAFETY
            return "I cannot provide a response to this query due to safety concerns."
        elif candidate.finish_reason == 4:  # RECITATION
            return "I cannot provide a response to this query due to recitation concerns."
        else:
            return "I encountered an issue generating a response. Please try rephrasing your question."
    else:
        return "No response generated. Please try again with a different query."

