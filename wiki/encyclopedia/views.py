from django.shortcuts import render
from django import forms
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
import markdown2
from random import choice

from .util import list_entries, get_entry, save_entry

class SearchEntryForm(forms.Form):
    entry = forms.CharField(label='',
                            widget=forms.TextInput(attrs={'placeholder': 'Type here'}))


class NewEntryForm(forms.Form):
    title = forms.CharField(label='',
                            widget=forms.TextInput(attrs={'placeholder': 'Name of entry'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Type your content here', 
                                                           'style': 'width: 70%; height: 200px;'}), label='')


class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label="", help_text="")

# Return a list of entries that have a name containing a specified substring
def list_entries_that_search_text_presented_in_entry(search_text):
    return [entry for entry in list_entries() if search_text.casefold() in entry.casefold()]


# Return True if a given title already exists in the list of all entries
def title_of_entry_already_in_entries(title):
    return title.casefold() in [entry.casefold() for entry in list_entries()]

# Render the index page with a list
def index(request):
    return render(request, f"encyclopedia/index.html", {
        "entries": list_entries(),
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })

#  Render the search page allowing users to search for entries by title.

def search(request):
    if request.method == "POST":
        form = SearchEntryForm(request.POST)
        if form.is_valid():
            searched_query = form.cleaned_data["entry"]
            if title_of_entry_already_in_entries(searched_query):
                return HttpResponseRedirect(f'/wiki/{searched_query}')
            return show_search_results(request, searched_query)
    return render(request, f"encyclopedia/search.html", {
        "search": "Search on the left",
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })
#     Render the page for a specific entry.
def show_entry(request, title):
    if title_of_entry_already_in_entries(title):
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(get_entry(title)),
            "page_title":    title,
            "form": SearchEntryForm(),
            "random_page": f'/wiki/{choice(list_entries())}'
        })
    return HttpResponseRedirect(reverse('wiki:error', args=(f"Requested entry '{title}' not exists",)))

#Render a page showing all entries whose title contains the search query.

def show_search_results(request, searched_query):
    matched_entries = list_entries_that_search_text_presented_in_entry(searched_query)
    if matched_entries:
        return render(request, "encyclopedia/searchResult.html", {
            "results": f"Results for your search '{searched_query}' are:",
            "matched_entries": matched_entries,
            "form": SearchEntryForm(),
            "random_page": f'/wiki/{choice(list_entries())}'
        })

    return render(request, "encyclopedia/search_result.html", {
        "results": f'There is no results for particular search: "{searched_query}"',
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })

#Create new entry
def newEntry(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if title_of_entry_already_in_entries(title):
                return HttpResponseRedirect(reverse('wiki:error', args=("Entry already exist",)))
            save_entry(title, content)
            return HttpResponseRedirect(reverse('wiki:entries', args=(title,)))
    return render(request, "encyclopedia/newEntry.html", {
        "new_entry_form": NewEntryForm(),
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })

# Allows a user to edit an existing entry and returns a rendered template
def edit_page(request, entry):
    content = get_entry(entry)
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            payload_content = form.cleaned_data["content"]
            save_entry(entry, payload_content)
            return HttpResponseRedirect(reverse('wiki:entries', args=(entry,)))
    return render(request, "encyclopedia/edit.html", {
        # initial value of textarea
        "edit_entry_form": EditEntryForm(initial={'content': content}, auto_id=False),
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}',
        "entry": entry,
    })


def show_error(request, error_message):
    return render(request, f"encyclopedia/error.html", {
        "error": error_message,
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })