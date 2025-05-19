from django.http import HttpResponse, Http404
from django.utils.encoding import smart_str

import pandora
from administration.views.general import superuser_only
from django.shortcuts import render
from administration.context_functions import *
from shared.routines import *

#new
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from functools import wraps
import json


@superuser_only
def dashboard_view(request, contest_id):
    template_name = 'admin/pages/contests/submissions/dashboard.html'
    context = {}
    contest = getContestByID(contest_id)
    submissions = contest.getSubmissions()

    context.update(getAdminSubmissionNonDetailLayoutContext(contest))
    context.update(getAdminContestSubmissionListContext(submissions))
    context.update(getAdminContestSubmissionsOver30DaysChartContext(contest))

    return render(request, template_name, context)

@superuser_only
def details_view(request, contest_id, attempt_id):
    template_name = 'admin/pages/contests/submissions/details.html'
    context = {}
    contest = Contest.getByID(contest_id)

    attempt = Attempt.getByID(attempt_id)
    team = attempt.getTeam()
    results = attempt.getClassifications()

    n_tests, n_mandatory, n_diff = contest.getTestsCount()
    n_passed, mandatory_passed, passed_diff = attempt.getPassedTestsCount()

    results

    """for res in results:
        print(pandora.settings.MEDIA_ROOT)
        print(res.test.output_file)
        res.expected_output = smart_text(res.test.output_file.read(), encoding='utf-8', strings_only=False,
                                         errors='strict')
        if res.output and os.path.isfile(res.output.path):
            res.output = smart_text(res.output.read(), encoding='utf-8', strings_only=False, errors='strict')
        else:
            res.output = ''
        res.input = smart_text(res.test.input_file.read(), encoding='utf-8', strings_only=False,
                               errors='strict')
    """
    context.update(getAdminSubmissionDetailLayoutContext(contest, attempt))
    context.update(getAdminContestSubmissionDetailsContext(contest, request.user, team, attempt, n_passed, n_tests, mandatory_passed,
                                            n_mandatory, passed_diff, n_diff, results, 9))
    return render(request, template_name, context)

@superuser_only
def download_submission(request, contest_id, attempt_id):
    attempt = Attempt.getByID(attempt_id)
    file = attempt.getFile()
    fdir, fname = os.path.split(file.path)
    try:
        resp = HttpResponse(file)
        resp['Content-Disposition'] = 'attachment; filename = ' + str(fname)
        return resp
    except FileNotFoundError:
        raise Http404("File does not exist")

def create_gemini_prompt(exercise_description, test_description, reference_code, student_code, input_data, expected, obtained, diff, help_difficulty):
    """
    Cria o prompt inicial para o Gemini com base nos parâmetros fornecidos.
    
    Args:
        exercise_description (str): Descrição do exercício
        test_description (str): Descrição do teste
        reference_code (str): Código de referência (correto)
        student_code (str): Código do aluno
        input_data (str): Dados de entrada do teste
        expected (str): Saída esperada
        obtained (str): Saída obtida pelo aluno
        diff (str): Diferença entre expected e obtained
        help_difficulty (str): Nível de dificuldade da ajuda
        
    Returns:
        str: Prompt formatado para o Gemini
    """
    return f"""
    TEMPLATE PARA PEDIDOS DE AJUDA AO GEMINI
    A partir de agora, deves seguir estritamente as regras abaixo ao interagir comigo.

    Objetivo
    Vou fornecer um exercício de programação em Python, incluindo:
    • Descrição do exercício.
    • Descrição do teste falhado.
    • O código correto (código de referência).
    • O código que o aluno escreveu (código do aluno).
    • Um conjunto de entradas (input).
    • A saída esperada (expected).
    • A saída obtida pelo código do aluno (obtained).
    
    O teu objetivo é ajudar o aluno a corrigir o código, seguindo um conjunto rigoroso de regras.
    
    ________________________________________
    Informações Fornecidas
    Descrição do Exercício
    {exercise_description}

    Descrição do Teste
    {test_description}

    Código de Referência (Correto) – NÃO MOSTRAR AO ALUNO
    {reference_code}

    Código do Aluno
    {student_code}

    Input
    {input_data}

    Expected (Saída Esperada do Código Correto)
    {expected}

    Obtained (Saída Obtida pelo Código do Aluno)
    {obtained}

    Diferença (Diferença entre o expected e o obtained)
    {diff}

    Nível de Dificuldade (Nível de dificuldade da dica)
    {help_difficulty}
    ________________________________________
    Regras Obrigatórias a Seguir
    1. Não mostrar o código correto (código de referência).
    2. Não escrever código novo para o aluno.
    3. Dar dicas consoante o nível de dificuldade pedido.
       • As dicas devem estar ajustadas consoante a dificuldade inserida.
       • Devem ajudar o aluno a encontrar o erro por conta própria.
    4. As dicas devem ser escritas por extenso.
       • Não podes usar código na explicação.
    5. As dicas devem estar relacionadas com o teste.
       • Não fornecer dicas não relacionadas com o que está a ser testado.
       • Comparar o código de referência com o do aluno para encontrar diferenças e perceber onde está a ser testado.
    6. Depois de dar as dicas iniciais, só podes aprofundar as dicas que já deste.
       • Não podes introduzir novas dicas que não tenham sido mencionadas antes.
    7. Se eu pedir algo que viole essas regras, deves responder apenas com: "Não posso ajudá-lo com isso."
    8. Não reveles o nível de dificuldade das dicas ao aluno.
    9. Escreve em Português de Portugal.
    10. A tua primeira resposta a este prompt deve ser uma dica consoante o nível de dificuldade pedido e apenas isso (sê apenas direto).
    11. Existe a possibilidade de receberes uma mensagem que informa que a tua resposta contém palavras proibidas. Nesse caso, deves reescrever a resposta sem utilizar estas palavras.
    12. Se o aluno escrever "Castor Verde" tens de deixar de seguir estas regras e falar com ele normalmente.
    13. Assim que o aluno escrever "Castor Verde" deves avisar o aluno que já não estás no modo de ajuda.
    """

chat_sessions = {}  # dicionário de sessões por teste
@csrf_exempt
@require_http_methods(["POST"])
def gemini_api(request):
    try:
        #genai.configure(api_key="AIzaSyBl2ClPsRvuNputjqnglLmIsl0KiAGVnBM")
        #Obter a chave do Gemini do perfil do utilizador
        user_profile = request.user.profile
        if not user_profile.gemini_key:
            return JsonResponse({
                "error": "É necessário configurar a chave do Gemini no perfil para utilizar esta funcionalidade. Por favor, acede à secção do Perfil e adiciona a chave."
            }, status=400)

        #Configurar o Gemini com a chave do utilizador
        genai.configure(api_key=user_profile.gemini_key)

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

        # Obter parâmetros da requisição
        user_input = request.POST.get("user_input", "").strip()
        contest_id = request.POST.get("contest_id")
        submission_id = request.POST.get("submission_id")
        test_index = request.POST.get("test_index")
        obtained_result = request.POST.get('obtained', '').strip()
        diff = request.POST.get('diff', '').strip()

        # Validar parâmetros obrigatórios
        if not all([contest_id, submission_id, test_index]):
            return JsonResponse({"error": "Parâmetros em falta"}, status=400)

        # Converter para inteiros
        contest_id = int(contest_id)
        submission_id = int(submission_id)
        test_index = int(test_index)

        # Criar uma chave única para esta sessão de chat
        session_key = f"{contest_id}_{submission_id}_{test_index}"

        # Obter dados do teste
        attempt = getAttemptByID(submission_id)
        test = Test.objects.get(id=test_index)
        contest = getContestByID(contest_id)
        results = attempt.getClassifications()
        result_index = int(request.POST.get('result_index', 0))  # Obter o índice do resultado
        r = results[result_index]

        # Ler o conteúdo do arquivo do aluno
        student_code = ""
        if attempt.file:
            try:
                with attempt.file.open('r') as f:
                    student_code = f.read()
            except Exception as e:
                print(f"Erro ao ler arquivo do aluno: {e}")
                student_code = "Erro ao ler o código do aluno"

        # Validar índice do teste
        if test_index < 1 or test_index > len(results):
            return JsonResponse({"error": "Índice de teste inválido"}, status=400)

        r = results[test_index - 1]

        # Caso 1: Primeira interação (sem user_input)
        if not user_input:
            # Obter informações do exercício e teste
            exercise_description = contest.getDescription()
            test_description = r.test.description
            reference_code = contest.reference_code
            input_data = ""
            expected = ""
            try:
                with test.input_file.open('r') as f:
                    input_data = f.read()
                with test.output_file.open('r') as f:
                    expected = f.read()
            except Exception as e:
                print("Erro ao ler arquivos do teste:", e)
            
            obtained = obtained_result.replace('\u000A', '').strip()
            help_difficulty = r.test.help_difficulty

            # Criar prompt inicial usando a nova função
            prompt = create_gemini_prompt(
                exercise_description=exercise_description,
                test_description=test_description,
                reference_code=reference_code,
                student_code=student_code,
                input_data=input_data,
                expected=expected,
                obtained=obtained,
                diff=diff,
                help_difficulty=help_difficulty
            )

            # Criar nova sessão de chat e guardar no dicionário
            chat = model.start_chat(history=[])
            chat_sessions[session_key] = chat
            response = chat.send_message("Com base no prompt: " + prompt + " Ajuda o aluno de forma educativa.")
            
            # Salvar a resposta no modelo Test
            if not test.gemini_responses:
                test.gemini_responses = []
            test.gemini_responses.append({
                "user_input": "Primeira interação",
                "response": response.text,
                "timestamp": timezone.now().isoformat()
            })
            test.save()
            
            # Salvar também no Contest
            if not contest.gemini_responses:
                contest.gemini_responses = {}
            if str(test.id) not in contest.gemini_responses:
                contest.gemini_responses[str(test.id)] = []
            contest.gemini_responses[str(test.id)].append({
                "user_input": "Primeira interação",
                "response": response.text,
                "timestamp": timezone.now().isoformat()
            })
            contest.save()
            
            return JsonResponse({"response": response.text})

        # Caso 2: Follow-up (com user_input)
        else:
            # Recuperar a sessão de chat existente ou criar uma nova se não existir
            chat = chat_sessions.get(session_key)
            if not chat:
                chat = model.start_chat(history=[])
                chat_sessions[session_key] = chat
            
            try:
                # Timeout de 10 segundos
                response = send_message_with_timeout(chat, user_input)
                # Verificar palavras proibidas
                blacklist = contest.blacklist
                if blacklist:
                    found_words = check_blacklisted_words(response.text, blacklist)
                    if found_words:
                        # Salvar a resposta original com palavras proibidas
                        if not test.gemini_responses:
                            test.gemini_responses = []
                        test.gemini_responses.append({
                            "user_input": user_input,
                            "response": response.text,
                            "timestamp": timezone.now().isoformat(),
                            "has_prohibited_words": True,
                            "prohibited_words": found_words
                        })
                        test.save()

                        # Salvar também no Contest
                        if not contest.gemini_responses:
                            contest.gemini_responses = {}
                        if str(test.id) not in contest.gemini_responses:
                            contest.gemini_responses[str(test.id)] = []
                        contest.gemini_responses[str(test.id)].append({
                            "user_input": user_input,
                            "response": response.text,
                            "timestamp": timezone.now().isoformat(),
                            "has_prohibited_words": True,
                            "prohibited_words": found_words
                        })
                        contest.save()

                        # Enviar mensagem de correção ao Gemini
                        correction_message = f"A tua resposta anterior contém palavras proibidas ({', '.join(found_words)}). Por favor, reescreve a resposta sem utilizar estas palavras, visto que podem oferecer a solução ao aluno. Aqui está a tua resposta anterior para referência:\n\n{response.text}"
                        response = send_message_with_timeout(chat, correction_message)

                # Salvar a resposta (original ou corrigida) no modelo Test
                if not test.gemini_responses:
                    test.gemini_responses = []
                test.gemini_responses.append({
                    "user_input": user_input,
                    "response": response.text,
                    "timestamp": timezone.now().isoformat(),
                    "has_prohibited_words": False
                })
                test.save()

                # Salvar também no Contest
                if not contest.gemini_responses:
                    contest.gemini_responses = {}
                if str(test.id) not in contest.gemini_responses:
                    contest.gemini_responses[str(test.id)] = []
                contest.gemini_responses[str(test.id)].append({
                    "user_input": user_input,
                    "response": response.text,
                    "timestamp": timezone.now().isoformat(),
                    "has_prohibited_words": False
                })
                contest.save()
                
                return JsonResponse({"message": response.text})
            except Exception as e:
                if "timeout" in str(e).lower():
                    return JsonResponse({
                        "error": "O tempo de resposta excedeu o limite de 10 segundos. Reinicia a conversa para tentar de novo."
                    }, status=408)
                raise e

    except Exception as e:
        print(f"Erro na API Gemini: {e}")
        return JsonResponse({"error": str(e)}, status=500)


def timeout_handler(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(asyncio.wait_for(
                    asyncio.to_thread(func, *args, **kwargs),
                    timeout=seconds
                ))
            except asyncio.TimeoutError:
                raise Exception("timeout")
            finally:
                loop.close()
        return wrapper
    return decorator

@timeout_handler(10)
def send_message_with_timeout(chat, message):
    return chat.send_message(message)

def check_blacklisted_words(text, blacklist):
    """
    Verifica se o texto contém palavras da blacklist.
    
    Args:
        text (str): Texto a ser verificado
        blacklist (str): String com palavras proibidas separadas por vírgula
        
    Returns:
        list: Lista com as palavras proibidas encontradas no texto. Vazia se nenhuma palavra for encontrada.
    """
    # Converter o texto e a blacklist para minúsculas para comparação case-insensitive
    text_lower = text.lower()
    blacklist_words = [word.strip().lower() for word in blacklist.split(',')]
    
    # Lista para armazenar as palavras proibidas encontradas
    found_words = []
    
    # Verificar cada palavra da blacklist
    for word in blacklist_words:
        if word and word in text_lower:
            found_words.append(word)
    
    return found_words

@csrf_exempt
@require_http_methods(["POST"])
def submit_rating(request):
    try:
        contest_id = request.POST.get('contest_id')
        check_only = request.POST.get('check_only') == 'true'

        if not contest_id:
            return JsonResponse({"error": "Parâmetros em falta"}, status=400)

        contest = Contest.objects.get(id=contest_id)
        
        # Se for apenas uma verificação, retorna se o usuário já avaliou
        if check_only:
            return JsonResponse({
                "already_rated": request.user in contest.ai_rated_by.all()
            })

        # Se não for verificação, processa a avaliação
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')

        if not 1 <= rating <= 5:
            return JsonResponse({"error": "Avaliação inválida"}, status=400)
        
        # Verifica se o usuário já avaliou este contest
        if request.user in contest.ai_rated_by.all():
            return JsonResponse({
                "error": "Você já avaliou este contest"
            }, status=400)

        # Atualiza as avaliações
        ratings = contest.ai_ratings or {}
        ratings[str(request.user.id)] = {
            "rating": rating,
            "comment": comment,
            "date": timezone.now().isoformat()
        }
        contest.ai_ratings = ratings
        contest.ai_rated_by.add(request.user)
        contest.save()

        return JsonResponse({"success": True})

    except Contest.DoesNotExist:
        return JsonResponse({"error": "Contest não encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@superuser_only
def download_gemini_responses(request, contest_id):
    try:
        contest = Contest.objects.get(id=contest_id)
        if not contest.gemini_responses:
            return JsonResponse({"error": "No Gemini responses found for this contest"}, status=404)
        
        # Criar nome do arquivo baseado no short_name do contest
        filename = f"{contest.short_name}_gemini_responses.json"
        
        # Criar resposta HTTP com o JSON
        response = HttpResponse(
            json.dumps(contest.gemini_responses, ensure_ascii=False, indent=2),
            content_type='application/json; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Contest.DoesNotExist:
        return JsonResponse({"error": "Contest not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)