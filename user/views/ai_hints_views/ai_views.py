import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse

# Configuração da API Key (predefinida)
genai.configure(api_key="AIzaSyBl2ClPsRvuNputjqnglLmIsl0KiAGVnBM")

# Criar o modelo Gemini
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)
chat_session = model.start_chat(history=[])

def gemini_chat(request):
    template_name = 'user/pages/contests/chat_form.html'
    if request.method == "POST":
        user_input = request.POST.get("user_input", "")
        prompt = request.POST.get("prompt", "")

        full_prompt = f"Usando este prompt: {prompt}\nResponde a: {user_input}"
        response = chat_session.send_message(full_prompt)

        return JsonResponse({"response": response.text})

    return render(request, template_name)
