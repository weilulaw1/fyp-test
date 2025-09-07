from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def home_data(request):
    return Response({"message": "Hello from Django backend 🚀"})

@api_view(['GET'])
def file_new(request):
    return Response({"message":"New File Created"})

@api_view(['GET'])
def file_open(request):
    return Response({"message": "Opened file"})

@api_view(['GET'])
def file_save(request):
    return Response({"message": "File saved"})

@api_view(['GET'])
def edit_undo(request):
    return Response({"message": "Undo action"})

@api_view(['GET'])
def edit_redo(request):
    return Response({"message": "Redo action"})

@api_view(['GET'])
def toggle_sidebar(request):
    return Response({"message": "Sidebar toggled"})
