from rest_framework import serializers
from .models import Post, SubPost
from django.contrib.auth import get_user_model

User = get_user_model()


class SubPostSerializer(serializers.ModelSerializer):
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SubPost
        fields = ["id", "title", "body", "post", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "post"]


class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    subposts = SubPostSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "body",
            "image",
            "author",
            "views_count",
            "like_count",
            "created_at",
            "updated_at",
            "subposts",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "views_count",
            "like_count",
        ]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        subposts_data = validated_data.pop("subposts", [])
        post = Post.objects.create(**validated_data)

        for subpost_data in subposts_data:
            SubPost.objects.create(post=post, **subpost_data)

        return post

    def update(self, instance, validated_data):
        if instance.author != self.context["request"].user:
            raise serializers.ValidationError("You cannot edit this post")

        subposts_data = validated_data.pop("subposts", None)
        instance.title = validated_data.get("title", instance.title)
        instance.body = validated_data.get("body", instance.body)
        instance.save()

        if subposts_data is not None:
            self._update_subposts(instance, subposts_data)

        return instance

    def _update_subposts(self, post, subposts_data):
        current_ids = set(post.subposts.values_list("id", flat=True))
        updated_ids = set()

        for subpost_data in subposts_data:
            subpost_id = subpost_data.get("id")
            if subpost_id and subpost_id in current_ids:
                subpost = SubPost.objects.get(id=subpost_id)
                for key, value in subpost_data.items():
                    if key != "id":
                        setattr(subpost, key, value)
                subpost.save()
                updated_ids.add(subpost_id)
            else:
                SubPost.objects.create(post=post, **subpost_data)

        ids_to_delete = current_ids - updated_ids
        if ids_to_delete:
            SubPost.objects.filter(id__in=ids_to_delete).delete()
