from rest_framework import status
from rest_framework.response import Response


class ListResourceMixin:
    def list(self, request, *args, **kwargs):
        resource = self.get_queryset()
        serializer = self.get_serializer(resource.list(), many=True)
        return Response(serializer.data)


class CreateResourceMixin:
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RetrieveResourceMixin:
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance.retrieve())
        return Response(serializer.data)


class UpdateResourceMixin:
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyResourceMixin:
    def destroy(self, request, pk):
        resource = self.get_object(pk)
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
