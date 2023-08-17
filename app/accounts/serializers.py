"""
Serializers for the user API View.
"""
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from core.models import UserProfile
import PIL.Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import os.path


def resize_image(image):
    """
    Helper method that will analyse the uploaded image by user.
    If the image width is less than 200px and exception will be thrown.
    Else it will be resized and cropped to match square 200x200px.
    """

    img_name = image.name
    img_content_type = image.content_type
    # print(f'type(img_name): {type(img_name)}, {img_name}')
    image = PIL.Image.open(image)
    if image.width < 200:
        raise Exception('Image should be at least 200x200 px.')

    else:
        if image.height > image.width:
            """
            Image is portrait
            """
            updated_width = 200
            updated_height = int((200 * image.height) / image.width)
            image = image.resize((updated_width, updated_height), PIL.Image.ANTIALIAS)

            crop_left = 0
            crop_top = int((updated_height - updated_width) / 2)
            crop_right = updated_width
            crop_bottom = updated_width + crop_top

            # left, top, right, bottom
            resized_image = image.crop((crop_left, crop_top, crop_right, crop_bottom))

        else:
            """
            Image is landscape
            """
            updated_height = 200
            updated_width = int((updated_height * image.width) / image.height)
            image = image.resize((updated_width, updated_height), PIL.Image.ANTIALIAS)

            crop_left = int((updated_width - updated_height) / 2)
            crop_top = 0
            crop_right = crop_left + updated_height
            crop_bottom = updated_height
            # left, top, right, bottom
            resized_image = image.crop((crop_left, crop_top, crop_right, crop_bottom))

        # Create a BytesIO buffer to temporarily hold the resized image data
        buffer = BytesIO()

        # Save the resized image to the buffer in the same format as the uploaded image
        resized_image.save(buffer, format='JPEG')

        # Create an InMemoryUploadedFile from the buffer with the same name as the original
        resized_image_file = InMemoryUploadedFile(
            buffer,
            None,  # field_name, not needed in this case
            img_name,  # the original image filename
            img_content_type,  # content type of the original image
            resized_image.tell(),  # size of the resized image in bytes
            None,  # charset, not needed in this case
        )

        return resized_image_file


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object.
    Serializer is simply just a way to convert objects to and from python objects.
    It takes adjacent input that might be posted from the API and validates
    the input to make sure that it is secure and correct as part of validation rules.
    Then it converts it to either a python object that we can use or a model in
    our actual database. So there are different base classes that you can use for the serialization.
    Model serializers allow us to  automatically validate and save things to a specific model
    that we define in our serialization.
    """

    class Meta:
        """
        Here we tell Django what should be passed to Serializer
        """
        model = User
        # The only fields that we allow user to change
        # we don't include is_active or is_staff
        fields = ('first_name', 'last_name', 'email', 'username', 'password')
        # 'password': {'write_only': --> user will be able to set password,
        # but it will not be returned over API response
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """
        Override create method
        """
        user = User.objects.create_user(**validated_data)
        return user

    def validate_email(self, value):
        """
        Additional validation for emails
        If email already exists in the database 400 error will be returned
        """
        # check if the email already exists in the database
        if User.objects.filter(email=value).exists():
            # raise a validation error with a custom message
            raise serializers.ValidationError("This email is already taken.")
        # otherwise, return the value as it is
        return value

    def validate_password(self, value):
        """
       Additional validation for passwords
       If password is less than 6characters 400 error will be returned
       """
        # check if the password is shorter than 6 characters
        if len(value) < 6:
            # raise a validation error with a custom message
            raise serializers.ValidationError("The password must be at least 6 characters long.")
        # otherwise, return the value as it is
        return value

    def update(self, instance, validated_data):
        """Update and return user.
        We override the serializer update method
        """
        # None is the default value of the password
        # retrieve the password from the validated data
        # and them remove it from the dictionary
        password = validated_data.pop('password', None)
        # instance is the module instance that will be updated
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    # style={'input_type': 'password'}, --> will secure the password while using
    # browsable API
    # trim_whitespace=False, --> user may put space at the end of the password deliberately
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            # By raising this way the Error the View will get it and
            # return 404 error.
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    user_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    first_name = serializers.ReadOnlyField(source='user.first_name')
    last_name = serializers.ReadOnlyField(source='user.last_name')
    image = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = '__all__'

    def update(self, instance, validated_data):

        instance.bio = validated_data.get('bio', instance.bio)
        instance.location = validated_data.get('location', instance.location)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)

        uploaded_image = validated_data.get('image')  # Get the uploaded image from validated_data
        if uploaded_image:
            resized_image = resize_image(image=uploaded_image)  # Resize the uploaded image
            instance.image.delete()  # Delete the original image
            instance.image = resized_image
        instance.save()
        return instance
