from rest_framework.renderers import DocumentationRenderer


class CustomRenderer(DocumentationRenderer):
    languages = ['python', 'javascript']
