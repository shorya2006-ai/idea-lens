from groq import Groq

client = Groq(
    api_key="YOUR_GROQ_API_KEY"
)


def generate_groq_analysis(
    user_idea,
    matched_idea,
    similarity_score
):
    try:

        prompt = f"""
You are an enterprise innovation reviewer.

Submitted Idea:
{user_idea}

Matched Existing Idea:
{matched_idea}

Similarity Score:
{similarity_score}

Provide:

1. Duplicate Assessment
2. Similarity Analysis
3. Key Differences
4. Innovation Potential
5. Recommendation

Keep response concise and professional.
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Groq Error: {str(e)}"
