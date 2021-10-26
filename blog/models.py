from django.db import models


class AbstractModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Blog(AbstractModel):
    title = models.CharField("Title", max_length=50)
    description = models.TextField("Description", null=True)
    image = models.BinaryField(null=True)


class Comment(AbstractModel):
    content = models.TextField("Content")
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
