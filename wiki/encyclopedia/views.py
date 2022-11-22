from django.shortcuts import render, redirect
from django import forms
import random
from . import util
from markdown2 import Markdown

markdowner = Markdown()

class SearchForm(forms.Form):
    search = forms.CharField(max_length=20)

class CreateForm(forms.Form):
    createTitle = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", 
            "placeholder": "Title", 
            "style": "margin-bottom: 10px;"}),
        label="Title",
        required=True
    )
    createText = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", 
            "placeholder": "Text"}), 
        label="Text",
        required=True
    )

class EditForm(forms.Form):
    editTitle = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", 
            "placeholder": "Title", 
            "style": "margin-bottom: 10px;"}),
        label="Edit Title",
        required=True
    )
    editText = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", 
            "placeholder": "Text"}), 
        label="Edit Text",
        required=True
    )

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def entry(request, title):
    entry = util.get_entry(title)
    content = markdowner.convert(entry)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content,
        "exists": title in util.list_entries(),
        "form": SearchForm()
    })

def search(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data["search"]
            # if query matches
            actualEntry = None
            lower = search.lower()
            potentialMatches = []
            for entry in util.list_entries():
                if entry.lower() == lower:
                    actualEntry = entry
                    return redirect(f"/wiki/{actualEntry}")
            # if query does not match, redirect to search results page
                if lower in entry.lower():
                    potentialMatches.append(entry)
            return render(request, "encyclopedia/searchResults.html", {
                "search": search,
                "entries": potentialMatches,
                "form": SearchForm()
            })
    # if request method is "GET" by typing /wiki/search in URL
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

def create(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["createTitle"]
            text = form.cleaned_data["createText"]
            lower = title.lower()
            for entry in util.list_entries():
                if entry.lower() == lower:
                    return render(request, "encyclopedia/create.html", {
                        "form": SearchForm(),
                        "createForm": CreateForm(),
                        "error": "An entry already exists with that title. Try to edit instead."
                    })
            formattedText = f"# {title}\n\n" + text
            util.save_entry(title, formattedText)
            return redirect(f"/wiki/{title}")

    return render(request, "encyclopedia/create.html", {
        "form": SearchForm(),
        "createForm": CreateForm(),
        "error": None
    })

def edit(request, title):
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["editTitle"]
            text = form.cleaned_data["editText"]
            util.save_entry(title, text)
            return redirect(f"/wiki/{title}")
    else:
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "title": title,
            "exists": title in util.list_entries(),
            "editForm": EditForm({
                "editTitle": title, 
                "editText": util.get_entry(title)})
        })

def randomPage(request):
    title = random.choice(util.list_entries())
    return redirect(f"/wiki/{title}")