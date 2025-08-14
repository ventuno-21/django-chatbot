from django.shortcuts import render, redirect
from django.contrib import messages
import openai
from openai import OpenAI
from .models import Past
from django.core.paginator import Paginator
import os
from dotenv import load_dotenv

load_dotenv()  # This loads the variables from .env into the environment
api_key = os.getenv("CHATGPT_API_KEY")
client = OpenAI(api_key=api_key)


def home(request):
    print("chatgpt_api_key =======", api_key)
    if request.method == "POST":
        question = request.POST.get("question", "")
        past_responses = request.POST.get("past_responses", "")

        try:
            client = OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    }
                ],
            )

            response_text = response.choices[0].message.content.strip()

            if past_responses.strip() == "NoNONOOAnswer":
                past_responses = response_text
            elif not past_responses.strip():
                past_responses = response_text
            else:
                past_responses = f"{past_responses}<br/><br/>{response_text}"

            record = Past(question=question, answer=response_text)
            record.save()

            return render(
                request,
                "home.html",
                {
                    "question": question,
                    "response": response_text,
                    "past_responses": past_responses,
                },
            )

        except Exception as e:
            print("OpenAI error =================>>", str(e), type(e))
            import traceback

            traceback.print_exc()
            return render(
                request,
                "home.html",
                {
                    "question": question,
                    "response": f"Error: {str(e)}",
                    "past_responses": past_responses,
                },
            )

    return render(request, "home.html", {})


def past(request):
    # Set up pagination
    p = Paginator(Past.objects.all(), 5)
    page = request.GET.get("page")
    pages = p.get_page(page)

    # Queried The Database
    past = Past.objects.all()

    # Get number of pages
    nums = "a" * pages.paginator.num_pages

    return render(request, "past.html", {"past": past, "pages": pages, "nums": nums})


def delete_past(request, Past_id):
    past = Past.objects.get(pk=Past_id)
    past.delete()
    messages.success(request, ("That Question and Answer have been deleted..."))
    return redirect("past")
