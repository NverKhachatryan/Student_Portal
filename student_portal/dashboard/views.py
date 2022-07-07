from email import message
from multiprocessing import context
from urllib import request
from django.shortcuts import redirect, render
from . forms import *
from django.contrib import messages
from django.views import generic
import requests
import wikipedia
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home(request):
    return render(request, 'dashboard/home.html')

@login_required
def notes(request):
    if request.method == 'POST':
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(
                user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
        messages.success(
            request, f'Notes added from {request.user.username} successfully')
    form = NotesForm()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)

@login_required
def delete_note(request, pk=None):
    note = Notes.objects.get(id=pk)
    note.delete()
    messages.success(
        request, f'Notes deleted from {request.user.username} successfully')
    return redirect('notes')

class NotesDetailView(generic.DetailView):
    model = Notes

@login_required
def homework(request):
    if request.method == 'POST':
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(user=request.user, subject=request.POST['subject'], title=request.POST['title'],
                                 description=request.POST['description'], due=request.POST['due'], is_finished=finished)
            homeworks.save()
            messages.success( request, f'Homework added from {request.user.username} successfully')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {'homeworks': homework,
               'homeworks_done': homework_done, 'form': form}
    return render(request, 'dashboard/homework.html', context)


@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    homework.delete()
    return redirect('homework') 

@login_required
def youtube(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
    else:
        form = DashboardForm()
    context = {'form': form}
    return render(request, 'dashboard/youtube.html', context) 

@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todo = Todo(user=request.user, title=request.POST['title'], is_finished=finished)
            todo.save()
            messages.success( request, f'Todo added from {request.user.username} successfully')
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todo_done = True
    else:
        todo_done = False
    context = {'todos': todo, 'form': form, 'todos_done': todo_done}
    return render(request, 'dashboard/todo.html', context)

@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    todo.delete()
    return redirect('todo')

@login_required
def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        answer = r.json()
        books = answer['items']
        result_list = []
        for i in range(10):
            result_dict = {
                'title': books[i]['volumeInfo']['title'],
                'author': books[i]['volumeInfo']['authors'],
                'description': books[i]['volumeInfo']['description'],
                'image': books[i]['volumeInfo']['imageLinks']['thumbnail'],
                'link': books[i]['volumeInfo']['infoLink'],
                'categories': books[i]['volumeInfo']['categories'],
                'thumbnail': books[i]['volumeInfo']['imageLinks']['thumbnail'],
                'count': books[i]['volumeInfo']['pageCount'],
            }
            result_list.append(result_dict)
        context = {'results': result_list, 'form': form}
        return render(request, 'dashboard/books.html', context)
    else:        
        form = DashboardForm()
    context = {'form': form}
    return render(request, 'dashboard/books.html', context)

@login_required
def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics']['text'],
            audio = answer[0]['phonetics'][0]['audio'],
            definition = answer[0]['meanings'][0]['definitions'][0]['definition'],
            example = answer[0]['meanings'][0]['definitions'][0]['example'],
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms'],
            context = {'form':form, 'input':text, 'phonetics':phonetics, 'audio':audio, 'definition':definition, 'example':example, 'synonyms':synonyms}
        except:
            context = {'form':form, 'input':text, 'error':'No results found'}
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
        context = {'form': form}
    return render(request, 'dashboard/dictionary.html', context)

@login_required
def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {'form': form, 'title': search.title, 'link': search.url, 'details': search.summary}
        return render(request, 'dashboard/wiki.html', context)
    else:
        form = DashboardForm()
        context = {'form': form}
    return render(request, 'dashboard/wiki.html', context)


@login_required
def conversion(request):
    if request.method == 'POST':
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input) * 3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int(input) / 3} yard'
                context = {'form': form, 'm_form': measurement_form, 'input': True, 'answer': answer}

        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {'form': form, 'm_form': measurement_form, 'input': True}
            if 'input' in request.POST:
                first = request.POST['measure1'] 
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input) * 0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input) * 2.20462} pound'
                context = {'form': form, 'm_form': measurement_form, 'input': True, 'answer': answer}        
    else:
        form = ConversionForm()
        context = {'form': form}
    return render(request, 'dashboard/conversion.html', context)


@login_required
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:        
        form = UserRegisterForm()
    context = {'form': form}
    return render(request, 'dashboard/register.html', context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user)
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False

    if len(todos) == 0:
        todo_done = True
    else:
        todo_done = False
    context = {'homeworks': homeworks, 'todos': todos, 'homework_done': homework_done, 'todo_done': todo_done}     
    return render(request, 'dashboard/profile.html', context)