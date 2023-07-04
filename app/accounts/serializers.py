"""
Serializers for the user API View.
"""
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _


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
        Here e tell Django what should be passed to Serializer
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
